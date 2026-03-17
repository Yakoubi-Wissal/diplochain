import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from models import EtudiantDiplome, DiplomeBlockchainExt, StatutDiplome

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer fake_token"}

def test_get_metrics_authorized(client, mock_db, auth_headers):
    # Mock DB response
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    response = client.get("/admin/metrics", headers=auth_headers)
    assert response.status_code == 200

def test_emit_upload_router(client, mock_db, mock_blockchain, mock_ipfs, auth_headers):
    mock_diploma = MagicMock(spec=EtudiantDiplome)
    mock_diploma.id_diplome = 100
    mock_diploma.titre = "Test Router"
    mock_diploma.blockchain_ext = MagicMock(spec=DiplomeBlockchainExt)
    mock_diploma.blockchain_ext.statut = StatutDiplome.ORIGINAL
    
    # Mock return dict must satisfy DiplomeRead schema
    mock_response = {
        "id_diplome": 100,
        "titre": "Test Router",
        "mention": None,
        "date_emission": date.today().isoformat(),
        "hash_sha256": "hash123",
        "tx_id_fabric": None,
        "ipfs_cid": "cid123",
        "statut": "ORIGINAL",
        "generation_mode": "UPLOAD",
        "blockchain_retry_count": 0,
        "etudiant_id": "E123",
        "institution_id": 1,
        "specialite_id": None,
        "uploaded_by": 1,
        "annee_promotion": None,
        "created_at": date.today().isoformat(),
        "updated_at": None,
    }
    
    with patch("services.diploma_service.DiplomaService.emit_diploma", return_value=mock_diploma), \
         patch("routers.diplomes._to_response", return_value=mock_response):
        
        pdf_content = b"%PDF-1.4 dummy"
        files = {"pdf_file": ("test.pdf", pdf_content, "application/pdf")}
        data = {"titre": "Test Router", "etudiant_id": "E123", "institution_id": 1}
        
        response = client.post("/diplomes/emit/upload", files=files, data=data, headers=auth_headers)
        assert response.status_code == 201

def test_verify_diploma_router(client, mock_db):
    # verify via blockchain + ipfs
    bc_record = {
        "diplome_id": "100",
        "hash_sha256": "MOCKHASH",
        "ipfs_cid": "MOCKCID",
        "status": "ORIGINAL",
        "titre": "Engineering",
        "mention": "Computer Science",
        "date_emission": None,
    }
    # ipfs returns bytes that hash to MOCKHASH
    pdf_bytes = b"test"
    import hashlib
    assert hashlib.sha256(pdf_bytes).hexdigest() == "MOCKHASH"

    expected = {
        "diploma_id": "DIP-000100",
        "student": None,
        "university": None,
        "degree": "Engineering",
        "field_of_study": "Computer Science",
        "issue_date": None,
        "blockchain_hash": "MOCKHASH",
        "status": "VERIFIED",
    }

    with patch("services.fabric_service.fabric_service.query_diploma", return_value=bc_record), \
         patch("services.ipfs_service.ipfs_service.cat", return_value=pdf_bytes):
        response = client.get("/verify/100")
        assert response.status_code == 200
        assert response.json() == expected
