import pytest
from datetime import datetime
from unittest.mock import MagicMock


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer fake_token"}


def test_add_verification_audit(client, mock_db, auth_headers):
    # configure mock_db to accept execute and commit
    mock_db.execute.return_value = None
    mock_db.commit.return_value = None

    payload = {
        "diploma_id": 123,
        "status": "ORIGINAL",
        "enterprise_id": 5,
        "timestamp": datetime.utcnow().isoformat(),
    }
    response = client.post("/api/audit/verification", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    # verify that db.execute was called with text containing ms_tenant_id
    assert mock_db.execute.call_args[0][0].text.lower().startswith("insert into historique_operations")


def test_list_verifications_audit(client, mock_db, auth_headers):
    # simulate DB returning two history records
    mock_record = MagicMock()
    # necessary attributes for serialization later
    mock_record.historique_operations_id = 1
    mock_record.diplome_id = 123
    mock_record.type_operation = "VERIFICATION"
    mock_record.nouvel_hash = "ORIGINAL"
    mock_record.timestamp = datetime.utcnow()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_record]
    mock_db.execute.return_value = mock_result

    # test without enterprise filter
    response = client.get("/api/audit/verification", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["type_operation"] == "VERIFICATION"
    assert data[0]["diplome_id"] == 123

    # test with enterprise filter parameter
    response = client.get("/api/audit/verification?enterprise_id=5", headers=auth_headers)
    assert response.status_code == 200
