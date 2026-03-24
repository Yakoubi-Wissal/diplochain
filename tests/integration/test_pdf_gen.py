
import requests
import json
import os

GATEWAY_URL = "http://localhost:8000/api/pdf/generate-diploma"

payload = {
    "template_id": "standard_v1",
    "student": {
        "nom": "DOE",
        "prenom": "John",
        "date_naissance": "2000-01-01",
        "numero_etudiant": "STU12345"
    },
    "diploma": {
        "titre": "Master in Computer Science",
        "mention": "Tres Bien",
        "date_emission": "2024-06-15",
        "annee_promotion": "2024"
    },
    "institution": {
        "nom": "University of Technology",
        "logo_url": "http://example.com/logo.png",
        "responsable": "Prof. Smith"
    }
}

print(f"Sending request to {GATEWAY_URL}...")
try:
    response = requests.post(GATEWAY_URL, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! PDF generated.")
        print(f"Content Type: {response.headers.get('Content-Type')}")
        print(f"Content Length: {len(response.content)} bytes")
        with open("test_diploma.pdf", "wb") as f:
            f.write(response.content)
        print("PDF saved to test_diploma.pdf")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
