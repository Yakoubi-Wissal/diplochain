"""
workers/retry_worker.py  ▶ NOUVEAU v6
APScheduler — surveille les diplômes bloqués en PENDING_BLOCKCHAIN
et retente RegisterDiploma() toutes les 60 secondes.

Règle critique : le Retry Worker ne re-upload JAMAIS vers IPFS
et ne rappelle JAMAIS le microservice PDF.
Il utilise uniquement le hash_sha256 et ipfs_cid déjà stockés.
"""
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select, text
from core.config import settings

logger   = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def _process_pending_diplomas():
    """Retente RegisterDiploma() pour les diplômes PENDING_BLOCKCHAIN."""
    from database import AsyncSessionLocal
    from models import DiplomeBlockchainExt, EtudiantDiplome
    from schemas import StatutDiplome

    async with AsyncSessionLocal() as db:
        try:
            # Join with core to get etudiant_id
            result = await db.execute(
                select(DiplomeBlockchainExt)
                .join(DiplomeBlockchainExt.core)
                .where(DiplomeBlockchainExt.statut == StatutDiplome.PENDING_BLOCKCHAIN)
                .order_by(DiplomeBlockchainExt.created_at.asc())
                .limit(settings.RETRY_WORKER_BATCH_SIZE)
            )
            pending = result.scalars().all()

            if not pending:
                return

            logger.info(f"[RetryWorker] {len(pending)} diplôme(s) PENDING_BLOCKCHAIN à retraiter.")

            from services.fabric_service import fabric_service

            for diplome_ext in pending:
                try:
                    # diplome_ext.core links to EtudiantDiplome
                    # ▶ Utilise hash et CID déjà stockés — JAMAIS de ré-upload IPFS
                    tx_id = await fabric_service.register_diploma(
                        diplome_id=str(diplome_ext.id_diplome),
                        hash_sha256=diplome_ext.hash_sha256,
                        ipfs_cid=diplome_ext.ipfs_cid,
                        institution_id=str(diplome_ext.institution_id),
                        etudiant_id=str(diplome_ext.core.etudiant_id),
                        date_emission=str(diplome_ext.date_emission),
                    )
                    diplome_ext.tx_id_fabric = tx_id
                    diplome_ext.statut       = StatutDiplome.ORIGINAL
                    diplome_ext.updated_at   = datetime.utcnow()
                    logger.info(f"[RetryWorker] Diplôme {diplome_ext.id_diplome} → ORIGINAL (tx={tx_id})")

                except Exception as e:
                    diplome_ext.blockchain_retry_count += 1
                    diplome_ext.blockchain_last_retry   = datetime.utcnow()
                    logger.warning(f"[RetryWorker] Diplôme {diplome_ext.id_diplome} — échec #{diplome_ext.blockchain_retry_count} : {e}")

                    # Alerte si trop de tentatives
                    if diplome_ext.blockchain_retry_count >= settings.RETRY_WORKER_MAX_RETRIES:
                        logger.error(
                            f"[RetryWorker] ALERTE : diplôme {diplome_ext.id_diplome} bloqué "
                            f"après {diplome_ext.blockchain_retry_count} tentatives."
                        )
                        try:
                            from services.email_service import email_service
                            await email_service.send_retry_alert(
                                diplome_id=str(diplome_ext.id_diplome),
                                retry_count=diplome_ext.blockchain_retry_count,
                            )
                        except Exception:
                            pass

            await db.commit()

        except Exception as e:
            logger.error(f"[RetryWorker] Erreur globale : {e}")


async def _refresh_dashboard_metrics():
    """Rafraîchit les métriques du dashboard pour aujourd'hui."""
    from database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text("SELECT fn_refresh_dashboard_metrics(CURRENT_DATE)"))
            await db.commit()
            logger.info("[RetryWorker] Métriques dashboard rafraîchies.")
        except Exception as e:
            logger.error(f"[RetryWorker] Erreur rafraîchissement métriques : {e}")


def start_scheduler():
    """Démarre APScheduler avec les deux jobs v6.

    Safe to call multiple times; if the event loop is closed (e.g. during
    TestClient lifespan) we log and skip without raising.
    """
    try:
        # Job 1 : Retry PENDING_BLOCKCHAIN
        scheduler.add_job(
            _process_pending_diplomas,
            trigger=IntervalTrigger(seconds=settings.RETRY_WORKER_INTERVAL_SECONDS),
            id="retry_pending_diplomas",
            name="Retry PENDING_BLOCKCHAIN",
            replace_existing=True,
        )

        # Job 2 : Rafraîchissement métriques dashboard
        scheduler.add_job(
            _refresh_dashboard_metrics,
            trigger=IntervalTrigger(hours=settings.METRICS_REFRESH_INTERVAL_HOURS),
            id="refresh_dashboard_metrics",
            name="Refresh Dashboard Metrics",
            replace_existing=True,
        )

        scheduler.start()
        logger.info(
            f"[RetryWorker] Démarré — retry toutes les {settings.RETRY_WORKER_INTERVAL_SECONDS}s, "
            f"métriques toutes les {settings.METRICS_REFRESH_INTERVAL_HOURS}h."
        )
    except RuntimeError as e:
        # Usually raised when event loop is closed / not running
        logger.warning(f"[RetryWorker] impossible de démarrer le scheduler : {e}")
    except Exception as e:
        logger.error(f"[RetryWorker] erreur démarrage scheduler : {e}")


def stop_scheduler():
    """Arrête proprement APScheduler."""
    if scheduler.running:
        try:
            scheduler.shutdown(wait=False)
            logger.info("[RetryWorker] Arrêté.")
        except RuntimeError as e:
            logger.warning(f"[RetryWorker] impossible d'arrêter le scheduler : {e}")
        except Exception as e:
            logger.error(f"[RetryWorker] erreur arrêt scheduler : {e}")
