#!/usr/bin/env python3
"""Database initialization helper for Schema v6.0.
"""

import asyncio
import argparse
from sqlalchemy import select, text
from database import engine, AsyncSessionLocal
from models import (
    Base, Role, RoleExt, User, UserExt, UserRole, UserRoleExt, 
    StatutUserDiploChain
)
from core.security import hash_password


async def create_tables():
    # Ensure the full v6 SQL script has been applied so that functions, views,
    # and other database objects defined there exist.  This runs in addition to
    # SQLAlchemy's metadata-based table creation.
    async with engine.begin() as conn:
        # create the database function needed for dashboard metrics.  this is a
        # trimmed copy of the SQL from the v6 migration file; keeping it here
        # ensures tests and the API can call the function without requiring the
        # entire migration script to be executed.
        # create or replace the function itself
        await conn.exec_driver_sql(
            """
            CREATE OR REPLACE FUNCTION public.fn_refresh_dashboard_metrics(
                p_date DATE DEFAULT (NOW() AT TIME ZONE 'Africa/Tunis')::DATE
            ) RETURNS VOID LANGUAGE plpgsql AS $$
            BEGIN
                INSERT INTO public.dashboard_metrics_daily (
                    metric_date,
                    nb_diplomes_emis,
                    nb_diplomes_microservice,
                    nb_diplomes_upload,
                    nb_nouveaux_etudiants,
                    nb_institutions_actives,
                    nb_diplomes_confirmes,
                    nb_diplomes_pending,
                    nb_diplomes_revoques,
                    nb_verifications,
                    updated_at
                )
                SELECT
                    p_date,
                    COUNT(*),
                    COUNT(CASE WHEN d.generation_mode = 'MICROSERVICE' THEN 1 END),
                    COUNT(CASE WHEN d.generation_mode = 'UPLOAD' THEN 1 END),
                    (SELECT COUNT(*)
                     FROM public.user_ext ue
                     JOIN public."UserRole" ur ON ur.user_id = ue.user_id
                     JOIN public."ROLE" r      ON r.id_role   = ur.role_id
                     WHERE r.code = 'ETUDIANT'
                       AND DATE(ue.created_at) = p_date),
                    COUNT(DISTINCT d.institution_id),
                    COUNT(CASE WHEN d.statut IN ('ORIGINAL','CONFIRME') THEN 1 END),
                    (SELECT COUNT(*) FROM public.diplome_blockchain_ext
                     WHERE statut = 'PENDING_BLOCKCHAIN'),
                    COUNT(CASE WHEN d.statut = 'REVOQUE' THEN 1 END),
                    (SELECT COUNT(*)
                     FROM public.historique_operations h
                     WHERE h.type_operation = 'VERIFICATION'
                       AND DATE(h."timestamp") = p_date),
                    NOW() AT TIME ZONE 'Africa/Tunis'
                FROM public.diplome_blockchain_ext d
                WHERE DATE(d.date_emission) = p_date
                ON CONFLICT (metric_date) DO UPDATE SET
                    nb_diplomes_emis         = EXCLUDED.nb_diplomes_emis,
                    nb_diplomes_microservice = EXCLUDED.nb_diplomes_microservice,
                    nb_diplomes_upload       = EXCLUDED.nb_diplomes_upload,
                    nb_nouveaux_etudiants    = EXCLUDED.nb_nouveaux_etudiants,
                    nb_institutions_actives  = EXCLUDED.nb_institutions_actives,
                    nb_diplomes_confirmes    = EXCLUDED.nb_diplomes_confirmes,
                    nb_diplomes_pending      = EXCLUDED.nb_diplomes_pending,
                    nb_diplomes_revoques     = EXCLUDED.nb_diplomes_revoques,
                    nb_verifications         = EXCLUDED.nb_verifications,
                    updated_at               = NOW() AT TIME ZONE 'Africa/Tunis';
                RAISE NOTICE 'Métriques du % rafraîchies avec succès.', p_date;
            END;
            $$;
            """
        )
        # add a comment in a separate statement
        await conn.exec_driver_sql(
            """
            COMMENT ON FUNCTION public.fn_refresh_dashboard_metrics(DATE) IS
                'Dashboard metrics helper - idempotent upsert, invoked by API';
            """
        )

        # make sure SQLAlchemy-managed tables exist as well (idempotent)
        await conn.run_sync(Base.metadata.create_all)

        # ensure dashboard views exist (mirrors migration logic and works even
        # if we later alter the script)
        await conn.execute(text(
            """
            CREATE OR REPLACE VIEW public.v_diplomas_per_student AS
            SELECT
                e.etudiant_id,
                e.nom,
                e.prenom,
                e.email_etudiant AS email,
                ue.numero_etudiant,
                COUNT(ed.id_diplome) AS nb_diplomes_total,
                COUNT(CASE WHEN dbe.statut IN ('ORIGINAL','CONFIRME') THEN 1 END) AS nb_confirmes,
                COUNT(CASE WHEN dbe.statut = 'PENDING_BLOCKCHAIN' THEN 1 END) AS nb_pending,
                COUNT(CASE WHEN dbe.statut = 'REVOQUE' THEN 1 END) AS nb_revoques,
                MAX(dbe.date_emission) AS derniere_emission
            FROM public.etudiant e
            LEFT JOIN public.user_ext ue ON ue.user_id = e.id_user
            LEFT JOIN public.etudiant_diplome ed ON ed.etudiant_id = e.etudiant_id
            LEFT JOIN public.diplome_blockchain_ext dbe ON dbe.id_diplome = ed.id_diplome
            GROUP BY
                e.etudiant_id, e.nom, e.prenom, e.email_etudiant, ue.numero_etudiant
            ORDER BY nb_diplomes_total DESC;
            """))
        await conn.execute(text(
            """
            CREATE OR REPLACE VIEW public.v_diplomas_per_institution AS
            SELECT
                i.institution_id,
                i.nom_institution AS nom,
                ibc.code,
                ibc.status AS statut,
                COUNT(dbe.id_diplome) AS nb_diplomes_total,
                COUNT(CASE WHEN dbe.generation_mode = 'MICROSERVICE' THEN 1 END) AS nb_via_microservice,
                COUNT(CASE WHEN dbe.generation_mode = 'UPLOAD' THEN 1 END) AS nb_via_upload,
                COUNT(CASE WHEN dbe.statut = 'PENDING_BLOCKCHAIN' THEN 1 END) AS nb_pending,
                COUNT(CASE WHEN dbe.statut = 'REVOQUE' THEN 1 END) AS nb_revoques,
                MAX(dbe.date_emission) AS derniere_emission
            FROM public.institution i
            LEFT JOIN public.institution_blockchain_ext ibc ON ibc.institution_id = i.institution_id
            LEFT JOIN public.diplome_blockchain_ext dbe ON dbe.institution_id = i.institution_id
            GROUP BY
                i.institution_id, i.nom_institution, ibc.code, ibc.status
            ORDER BY nb_diplomes_total DESC;
            """))
    print("✅ Database tables and views synchronized.")


async def seed_data(admin_email: str, admin_pwd: str):
    async with AsyncSessionLocal() as session:
        # 1. Seed Roles
        roles_to_seed = [
            {"code": "SUPER_ADMIN", "label": "Super Administrateur", "desc": "Accès total au système"},
            {"code": "ADMIN_INSTITUTION", "label": "Administrateur Institution", "desc": "Gère les diplômes de son institution"},
            {"code": "ETUDIANT", "label": "Étudiant", "desc": "Consulte et partage ses diplômes"},
            {"code": "ENTREPRISE", "label": "Entreprise / Recruteur", "desc": "Vérifie l'authenticité des diplômes"},
        ]

        for r_data in roles_to_seed:
            result = await session.execute(select(Role).where(Role.code == r_data["code"]))
            role = result.scalar_one_or_none()
            if not role:
                # Core Role (integer ID will be handled by SERIAL or we can assign one)
                # Let's use specific IDs for predictable seeding if needed, 
                # but standard SERIAL is fine if we fetch them back.
                role = Role(code=r_data["code"], label_role=r_data["label"])
                session.add(role)
                await session.flush() # Get the ID
                
                # Extension Role
                role_ext = RoleExt(
                    id_role=role.id_role,
                    description=r_data["desc"],
                    permissions=["ALL"] if r_data["code"] == "SUPER_ADMIN" else [],
                    is_active=True
                )
                session.add(role_ext)
                print(f"➕ Created role {r_data['code']}")
            else:
                print(f"ℹ️ Role {r_data['code']} already exists")

        await session.commit()

        # 2. Seed Super Admin
        result = await session.execute(select(User).where(User.email == admin_email))
        admin = result.scalar_one_or_none()
        if not admin:
            # Core User
            admin = User(
                email=admin_email,
                password=hash_password(admin_pwd),
                status="ACTIF" # Core status is varchar
            )
            session.add(admin)
            await session.flush()

            # Extension User
            admin_ext = UserExt(
                user_id=admin.id_user,
                nom="Super",
                prenom="Admin",
                statut_diplochain=StatutUserDiploChain.ACTIF,
                niveau_acces="GLOBAL",
                permissions=["ALL"]
            )
            session.add(admin_ext)

            # Assign Role
            res_role = await session.execute(select(Role).where(Role.code == "SUPER_ADMIN"))
            sa_role = res_role.scalar_one()
            
            user_role = UserRole(user_id=admin.id_user, role_id=sa_role.id_role)
            session.add(user_role)
            await session.flush()

            user_role_ext = UserRoleExt(
                user_id=admin.id_user,
                role_id=sa_role.id_role,
                nom="Super Admin Role Assignment",
                is_active=True
            )
            session.add(user_role_ext)

            await session.commit()
            print(f"➕ Created superadmin {admin_email}")
        else:
            print(f"ℹ️ Superadmin {admin_email} already exists")

        # ensure minimal test data for diplomas (institution & student)
        from models import Institution, Etudiant
        # institution id=1
        res_inst = await session.execute(select(Institution).where(Institution.institution_id == 1))
        if not res_inst.scalar_one_or_none():
            # create a default institution; we avoid manually specifying the
            # primary key so that the underlying sequence advances normally.
            inst = Institution(
                nom_institution="Test Institution",
            )
            session.add(inst)
            await session.flush()  # obtain institution_id
            print(f"➕ Created test institution id={inst.institution_id}")
        # etudiant E001
        res_et = await session.execute(select(Etudiant).where(Etudiant.etudiant_id == "E001"))
        if not res_et.scalar_one_or_none():
            et = Etudiant(
                etudiant_id="E001",
                email_etudiant="e001@example.com",
                nom="Test",
                prenom="Student",
                id_user=admin.id_user if admin else None
            )
            session.add(et)
            print("➕ Created test student E001")
        await session.commit()


async def drop_schema():
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
    print("🧹 Schema public reset")


async def run_init(reset: bool, seed_admin: list):
    if reset:
        await drop_schema()
    
    # We don't necessarily call create_tables() if we used script_db_v6.sql
    # but it's good to have it as a sync.
    await create_tables()
    
    if seed_admin:
        email, pwd = seed_admin
        await seed_data(email, pwd)


def main():
    parser = argparse.ArgumentParser(description="Initialise database v6.0")
    parser.add_argument("--reset", action="store_true", help="Reset schema")
    parser.add_argument("--seed-admin", nargs=2, metavar=("EMAIL", "PWD"), help="Seed superadmin")
    args = parser.parse_args()

    asyncio.run(run_init(args.reset, args.seed_admin))


if __name__ == "__main__":
    main()
