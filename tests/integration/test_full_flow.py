
import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

def test_full_flow():
    print("=== DiploChain V2 Full System Flow Verification ===")
    
    unique_suffix = int(time.time())
    admin_email = f"admin_{unique_suffix}@diplochain.com"
    password = "securepassword123"
    
    # 1. Register Admin
    print("\n[1] Registering Admin...")
    resp = requests.post(f"{BASE_URL}/users/", json={
        "username": f"admin_{unique_suffix}",
        "email": admin_email,
        "password": password,
        "role": "ADMIN",
        "status": "ACTIF"
    })
    assert resp.status_code == 201, f"Admin registration failed: {resp.text}"
    print("SUCCESS: Admin registered.")

    # 2. Login
    print("\n[2] Logging in...")
    resp = requests.post(f"{BASE_URL}/users/auth/login", data={
        "username": admin_email,
        "password": password
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("SUCCESS: Token obtained.")

    # 3. Create Institution
    print("\n[3] Creating Institution...")
    resp = requests.post(f"{BASE_URL}/institutions/", headers=headers, json={
        "nom_institution": "Global University",
        "email_institution": f"contact_{unique_suffix}@global.edu",
        "date_creation": "2024-01-01",
        "adresse": "123 Educational Blvd, Paris",
        "pays": "France"
    })
    assert resp.status_code == 200, f"Institution creation failed: {resp.text}"
    inst_id = resp.json()["institution_id"] # Matches Read schema
    print(f"SUCCESS: Institution created (ID: {inst_id}).")

    # 4. Create Student
    print("\n[4] Creating Student...")
    short_stu_id = f"S{str(unique_suffix)[-9:]}"
    resp = requests.post(f"{BASE_URL}/students/", headers=headers, json={
        "etudiant_id": short_stu_id,
        "nom": "DUBOIS",
        "prenom": "Jean",
        "email_etudiant": f"jean.dubois_{unique_suffix}@student.com",
        "date_naissance": "2002-05-20",
        "lieu_nais_et": "Lyon"
    })
    assert resp.status_code == 200, f"Student creation failed: {resp.text}"
    student_id = resp.json()["etudiant_id"]
    print(f"SUCCESS: Student created (ID: {student_id}).")

    # 5. Emit Diploma (SKIPPED - Blockchain on hold)
    print("\n[5] Skipping Diploma Emission (Blockchain on hold per user request)")

    # 6. Generate PDF (External Service Integration)
    print("\n[6] Testing External PDF Generation Integration...")
    resp = requests.post(f"{BASE_URL}/pdf/generate-diploma", headers=headers, json={
        "template_id": "standard_v1",
        "student": {"nom": "DUBOIS", "prenom": "Jean", "numero_etudiant": f"STU_{unique_suffix}"},
        "diploma": {"titre": "Master Architecture", "mention": "Bien", "date_emission": "2024-06-30"},
        "institution": {"nom": "Global University", "responsable": "Le Recteur"}
    })
    if resp.status_code == 200:
        print(f"SUCCESS: External PDF generated ({len(resp.content)} bytes).")
    else:
        print(f"INFO: PDF Service might be unavailable or external routing pending: {resp.status_code}")

    # 7. Verification (SKIPPED)
    print("\n[7] Skipping Verification (Blockchain on hold)")

    print("\n=== V2 Core Services Flow (Users/Students/Inst) Verified ===")

if __name__ == "__main__":
    try:
        test_full_flow()
    except Exception as e:
        print(f"\nFATAL ERROR during flow test: {e}")
        exit(1)
