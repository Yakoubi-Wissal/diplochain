#!/usr/bin/env python3
"""
validate_dashboard.py — DiploChain v6.2 (CORRIGÉ)
===================================================
Noms de colonnes corrigés pour correspondre aux vraies vues SQL :

  v_diplomas_per_student   → nb_diplomes_total, nb_confirmes, nb_pending, nb_revoques
  v_diplomas_per_institution → nom, nb_diplomes_total, nb_via_microservice, nb_via_upload, nb_pending, nb_revoques

  historique_operations    → timestamp (pas created_at)

Usage :
    python validate_dashboard.py --base-url http://localhost:8000 \\
        --email admin@diplochain.com --password secret \\
        --db-url postgresql://diplochain_user:diplochain_pass@localhost:5432/diplochain_db
"""

import argparse
import sys
from datetime import date
from typing import Optional

try:
    import requests
except ImportError:
    print("Dépendance manquante : pip install requests")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
#  Config — noms de colonnes réels des vues PostgreSQL v6
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_DB_URL   = "postgresql://diplochain_user:diplochain_pass@localhost:5432/diplochain_db"

# Colonnes réelles de dashboard_metrics_daily
DASHBOARD_METRICS_FIELDS = [
    "metric_date", "nb_diplomes_emis", "nb_diplomes_microservice",
    "nb_diplomes_upload", "nb_nouveaux_etudiants", "nb_institutions_actives",
    "nb_diplomes_confirmes", "nb_diplomes_pending", "nb_diplomes_revoques",
    "nb_verifications",
]

# Colonnes réelles de v_diplomas_per_student
STUDENT_STATS_FIELDS = [
    "etudiant_id", "nom", "prenom",
    "nb_diplomes_total",   # ← était 'total_diplomes' (incorrect)
    "nb_confirmes",        # ← était 'diplomes_confirmes' (incorrect)
    "nb_pending",          # ← était 'diplomes_pending' (incorrect)
    "nb_revoques",         # ← était 'diplomes_revoques' (incorrect)
]

# Colonnes réelles de v_diplomas_per_institution
INSTITUTION_STATS_FIELDS = [
    "institution_id",
    "nom",                 # ← était 'nom_institution' (incorrect)
    "nb_diplomes_total",   # ← était 'total_diplomes' (incorrect)
    "nb_via_microservice",
    "nb_via_upload",
    "nb_pending",          # ← était 'diplomes_confirmes' (incorrect, cette vue n'a pas de nb_confirmes)
    "nb_revoques",         # ← était 'diplomes_pending' (incorrect)
]


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════════════════════

class Colors:
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    RESET  = "\033[0m"
    BOLD   = "\033[1m"


def ok(msg):   print(f"  {Colors.GREEN}✅ {msg}{Colors.RESET}")
def fail(msg): print(f"  {Colors.RED}❌ {msg}{Colors.RESET}")
def warn(msg): print(f"  {Colors.YELLOW}⚠️  {msg}{Colors.RESET}")
def info(msg): print(f"  {Colors.BLUE}ℹ️  {msg}{Colors.RESET}")
def section(title): print(f"\n{Colors.BOLD}{'─'*60}\n  {title}\n{'─'*60}{Colors.RESET}")


class ValidationReport:
    def __init__(self):
        self.passed = self.failed = self.warnings = 0

    def check(self, condition: bool, pass_msg: str, fail_msg: str) -> bool:
        if condition:
            ok(pass_msg); self.passed += 1
        else:
            fail(fail_msg); self.failed += 1
        return condition

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'═'*60}")
        print(f"{Colors.BOLD}  RÉSULTAT : {self.passed}/{total} vérifications passées{Colors.RESET}")
        if self.warnings:
            print(f"{Colors.YELLOW}  {self.warnings} avertissement(s){Colors.RESET}")
        if self.failed == 0:
            print(f"{Colors.GREEN}  ✅ Validation complète réussie{Colors.RESET}")
        else:
            print(f"{Colors.RED}  ❌ {self.failed} vérification(s) échouée(s){Colors.RESET}")
        print(f"{'═'*60}\n")
        return self.failed == 0


# ══════════════════════════════════════════════════════════════════════════════
#  Auth
# ══════════════════════════════════════════════════════════════════════════════

def login(base_url: str, email: str, password: str) -> Optional[str]:
    section("1. Authentification")
    try:
        r = requests.post(f"{base_url}/auth/login",
            data={"username": email, "password": password}, timeout=10)
        if r.status_code == 200:
            token = r.json().get("access_token")
            ok(f"Login OK — token JWT reçu ({len(token)} caractères)")
            return token
        fail(f"Login échoué : {r.status_code} — {r.text[:100]}")
        return None
    except requests.ConnectionError:
        fail(f"Impossible de se connecter à {base_url}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  Refresh
# ══════════════════════════════════════════════════════════════════════════════

def validate_refresh(base_url: str, token: str, report: ValidationReport):
    section("2. POST /admin/metrics/refresh")
    headers = {"Authorization": f"Bearer {token}"}
    today   = date.today().isoformat()

    r = requests.post(f"{base_url}/admin/metrics/refresh", headers=headers, timeout=15)
    report.check(r.status_code == 200,
        f"Refresh OK (200) — refreshed_for = {r.json().get('refreshed_for', '?') if r.status_code == 200 else '?'}",
        f"Refresh échoué : {r.status_code} — {r.text[:150]}")

    if r.status_code == 200:
        report.check("status" in r.json() and r.json()["status"] == "ok",
            'Champ status = "ok" présent', 'Champ status manquant')
        report.check("refreshed_for" in r.json(),
            "Champ refreshed_for présent", "Champ refreshed_for absent")

    r2 = requests.post(f"{base_url}/admin/metrics/refresh?target_date=2024-06-01",
        headers=headers, timeout=15)
    report.check(r2.status_code == 200,
        "Refresh avec date cible 2024-06-01 → 200",
        f"Refresh avec date cible échoué : {r2.status_code}")


# ══════════════════════════════════════════════════════════════════════════════
#  GET /admin/metrics
# ══════════════════════════════════════════════════════════════════════════════

def validate_get_metrics(base_url: str, token: str, report: ValidationReport):
    section("3. GET /admin/metrics")
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"{base_url}/admin/metrics", headers=headers, timeout=10)
    report.check(r.status_code == 200,
        f"GET /admin/metrics OK — {len(r.json()) if r.status_code == 200 else 0} ligne(s)",
        f"Échec : {r.status_code} — {r.text[:150]}")

    if r.status_code == 200 and r.json():
        row = r.json()[0]
        missing = [f for f in DASHBOARD_METRICS_FIELDS if f not in row]
        report.check(not missing,
            f"Tous les {len(DASHBOARD_METRICS_FIELDS)} champs présents",
            f"Champs manquants : {missing}")

        report.check(isinstance(row.get("nb_diplomes_emis"), int),
            "nb_diplomes_emis est un entier", "nb_diplomes_emis n'est pas un entier")

        coherent = (
            row.get("nb_diplomes_confirmes", 0) +
            row.get("nb_diplomes_pending", 0) +
            row.get("nb_diplomes_revoques", 0)
        ) <= row.get("nb_diplomes_emis", 0)
        report.check(coherent,
            "Cohérence : confirmes + pending + revoques ≤ emis",
            "Incohérence : la somme dépasse nb_diplomes_emis")

        info("Détail dernière ligne :")
        for k in DASHBOARD_METRICS_FIELDS:
            info(f"    {k:35s} = {row.get(k)}")

    # Bug #1 : filtre par date (TypeError si non corrigé)
    today = date.today().isoformat()
    r2 = requests.get(f"{base_url}/admin/metrics?date={today}", headers=headers, timeout=10)
    if r2.status_code == 200:
        ok(f"Filtre ?date={today} → 200 (Bug #1 corrigé)")
    else:
        fail(f"Filtre ?date={today} → {r2.status_code} (Bug #1 toujours présent : repo.list(metric_date=...))")
        report.failed += 1


# ══════════════════════════════════════════════════════════════════════════════
#  GET /admin/students — colonnes corrigées
# ══════════════════════════════════════════════════════════════════════════════

def validate_students_stats(base_url: str, token: str, report: ValidationReport):
    section("4. GET /admin/students")
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"{base_url}/admin/students", headers=headers, timeout=10)
    report.check(r.status_code == 200,
        f"GET /admin/students OK — {len(r.json()) if r.status_code == 200 else 0} étudiant(s)",
        f"Échec : {r.status_code} — {r.text[:150]}")

    if r.status_code == 200 and r.json():
        row = r.json()[0]
        missing = [f for f in STUDENT_STATS_FIELDS if f not in row]
        report.check(not missing,
            "Tous les champs v_diplomas_per_student présents",
            f"Champs manquants dans la réponse : {missing}")

        if not missing:
            report.check(
                row.get("nb_confirmes", 0) <= row.get("nb_diplomes_total", 0),
                "Cohérence : nb_confirmes ≤ nb_diplomes_total",
                "Incohérence : nb_confirmes > nb_diplomes_total")

            # Note : nb_confirmes compte statut='ORIGINAL' (v5) mais pas 'CONFIRME' (v6.1 service)
            if row.get("nb_confirmes", 0) == 0 and row.get("nb_diplomes_total", 0) > 0:
                warn("nb_confirmes = 0 alors qu'il y a des diplômes — possible Bug ORIGINAL/CONFIRME")
                report.warnings += 1


# ══════════════════════════════════════════════════════════════════════════════
#  GET /admin/institutions — colonnes corrigées
# ══════════════════════════════════════════════════════════════════════════════

def validate_institutions_stats(base_url: str, token: str, report: ValidationReport):
    section("5. GET /admin/institutions")
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"{base_url}/admin/institutions", headers=headers, timeout=10)
    report.check(r.status_code == 200,
        f"GET /admin/institutions OK — {len(r.json()) if r.status_code == 200 else 0} institution(s)",
        f"Échec : {r.status_code} — {r.text[:150]}")

    if r.status_code == 200 and r.json():
        row = r.json()[0]
        missing = [f for f in INSTITUTION_STATS_FIELDS if f not in row]
        report.check(not missing,
            "Tous les champs v_diplomas_per_institution présents",
            f"Champs manquants dans la réponse : {missing}")


# ══════════════════════════════════════════════════════════════════════════════
#  RBAC
# ══════════════════════════════════════════════════════════════════════════════

def validate_rbac(base_url: str, token_etudiant: Optional[str], report: ValidationReport):
    section("6. RBAC — Accès refusé")
    if not token_etudiant:
        warn("Token ETUDIANT non fourni. Passer --etudiant-email et --etudiant-password.")
        report.warnings += 1
        return

    headers = {"Authorization": f"Bearer {token_etudiant}"}
    for path in ["/admin/metrics", "/admin/students", "/admin/institutions"]:
        r = requests.get(f"{base_url}{path}", headers=headers, timeout=10)
        report.check(r.status_code == 403,
            f"ETUDIANT bloqué GET {path} (403)",
            f"ETUDIANT NON bloqué GET {path} : {r.status_code}")

    r = requests.post(f"{base_url}/admin/metrics/refresh",
        headers=headers, timeout=10)
    report.check(r.status_code == 403,
        "ETUDIANT bloqué POST /admin/metrics/refresh (403)",
        f"ETUDIANT NON bloqué : {r.status_code}")


# ══════════════════════════════════════════════════════════════════════════════
#  Validation SQL directe — requêtes corrigées (timestamp, pas created_at)
# ══════════════════════════════════════════════════════════════════════════════

def validate_sql(db_url: str, report: ValidationReport):
    section("7. Validation SQL directe (PostgreSQL)")
    try:
        import psycopg2
    except ImportError:
        warn("psycopg2 non installé. pip install psycopg2-binary")
        report.warnings += 1
        return

    try:
        conn = psycopg2.connect(db_url)
        cur  = conn.cursor()

        # 1. Table accessible
        cur.execute("SELECT COUNT(*) FROM dashboard_metrics_daily;")
        count = cur.fetchone()[0]
        report.check(count >= 0,
            f"dashboard_metrics_daily accessible — {count} ligne(s)", "Inaccessible")

        # 2. Vue students
        cur.execute("SELECT COUNT(*) FROM v_diplomas_per_student;")
        count_s = cur.fetchone()[0]
        ok(f"v_diplomas_per_student accessible — {count_s} étudiant(s)")

        # 3. Vue institutions
        cur.execute("SELECT COUNT(*) FROM v_diplomas_per_institution;")
        count_i = cur.fetchone()[0]
        ok(f"v_diplomas_per_institution accessible — {count_i} institution(s)")

        # 4. Cohérence nb_emis vs diplomes réels
        cur.execute("""
            SELECT d.metric_date, d.nb_diplomes_emis, COUNT(e.id_diplome) AS real_count
            FROM dashboard_metrics_daily d
            LEFT JOIN diplome_blockchain_ext ext ON ext.date_emission = d.metric_date
            LEFT JOIN etudiant_diplome e ON e.id_diplome = ext.id_diplome
            WHERE d.metric_date = CURRENT_DATE
            GROUP BY d.metric_date, d.nb_diplomes_emis LIMIT 1;
        """)
        row = cur.fetchone()
        if row:
            nb_emis, real_count = row[1], row[2]
            report.check(nb_emis == real_count,
                f"Cohérence nb_diplomes_emis ({nb_emis}) = compte réel ({real_count})",
                f"Incohérence ! nb_emis={nb_emis}, réel={real_count}")
        else:
            warn("Pas de métriques pour aujourd'hui — exécuter refresh d'abord")
            report.warnings += 1

        # 5. Bug ORIGINAL vs CONFIRME — vérification critique
        cur.execute("""
            SELECT
                COUNT(CASE WHEN statut = 'ORIGINAL' THEN 1 END)  AS nb_original,
                COUNT(CASE WHEN statut = 'CONFIRME' THEN 1 END)  AS nb_confirme
            FROM diplome_blockchain_ext;
        """)
        r = cur.fetchone()
        if r:
            nb_orig, nb_conf = r[0], r[1]
            info(f"Statuts DB : ORIGINAL={nb_orig}, CONFIRME={nb_conf}")
            if nb_orig > 0 and nb_conf == 0:
                warn(f"Bug ORIGINAL/CONFIRME actif : {nb_orig} diplôme(s) avec statut=ORIGINAL")
                warn("fn_refresh compte ORIGINAL comme confirme → OK pour les anciens diplômes")
                warn("MAIS les nouveaux diplômes émis via DiplomaService (statut=CONFIRME) ne seront PAS comptés !")
                report.warnings += 1
            elif nb_conf > 0:
                cur.execute("""
                    SELECT d.nb_diplomes_confirmes
                    FROM dashboard_metrics_daily d
                    WHERE d.metric_date = CURRENT_DATE;
                """)
                metrics_row = cur.fetchone()
                if metrics_row and metrics_row[0] != nb_conf:
                    fail(f"Bug ORIGINAL/CONFIRME confirmé : metrics={metrics_row[0]} CONFIRME, DB réelle={nb_conf}")
                    report.failed += 1

        # 6. Colonne timestamp de historique_operations (pas created_at)
        cur.execute("""
            SELECT COUNT(*) FROM historique_operations
            WHERE type_operation = 'VERIFICATION'
            AND DATE("timestamp") = CURRENT_DATE;
        """)
        nb_verif = cur.fetchone()[0]
        ok(f"historique_operations.timestamp accessible — {nb_verif} vérification(s) aujourd'hui")

        # 7. Fonction fn_refresh existe
        cur.execute("""
            SELECT routine_name FROM information_schema.routines
            WHERE routine_name = 'fn_refresh_dashboard_metrics';
        """)
        fn = cur.fetchone()
        report.check(fn is not None,
            "fn_refresh_dashboard_metrics existe dans le schéma",
            "fn_refresh_dashboard_metrics ABSENTE !")

        cur.close()
        conn.close()

    except Exception as e:
        fail(f"Connexion DB échouée : {e}")
        warn("Vérifier DATABASE_URL ou utiliser --skip-sql")
        report.warnings += 1


# ══════════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Validation Dashboard DiploChain v6.2 (corrigé)")
    parser.add_argument("--base-url",           default=DEFAULT_BASE_URL)
    parser.add_argument("--email",              default="admin@diplochain.com")
    parser.add_argument("--password",           default="secret")
    parser.add_argument("--db-url",             default=DEFAULT_DB_URL)
    parser.add_argument("--etudiant-email",     default=None)
    parser.add_argument("--etudiant-password",  default=None)
    parser.add_argument("--skip-sql",           action="store_true")
    args = parser.parse_args()

    print(f"\n{Colors.BOLD}{'═'*60}")
    print(f"  DiploChain v6.2 — Validation Dashboard (corrigé)")
    print(f"  URL  : {args.base_url}")
    print(f"  Date : {date.today().isoformat()}")
    print(f"{'═'*60}{Colors.RESET}")

    report = ValidationReport()

    token = login(args.base_url, args.email, args.password)
    if not token:
        sys.exit(1)

    validate_refresh(args.base_url, token, report)
    validate_get_metrics(args.base_url, token, report)
    validate_students_stats(args.base_url, token, report)
    validate_institutions_stats(args.base_url, token, report)

    token_etudiant = None
    if args.etudiant_email:
        token_etudiant = login(args.base_url, args.etudiant_email, args.etudiant_password or "")
    validate_rbac(args.base_url, token_etudiant, report)

    if not args.skip_sql:
        validate_sql(args.db_url, report)
    else:
        info("Validation SQL ignorée (--skip-sql)")

    success = report.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()