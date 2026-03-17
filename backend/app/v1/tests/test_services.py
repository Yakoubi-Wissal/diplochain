import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date
from services.diploma_service import DiplomaService
from models import User, EtudiantDiplome, StatutDiplome

@pytest.mark.asyncio
async def test_emit_diploma_success(mock_db, mock_blockchain, mock_ipfs):
    # Setup
    service = DiplomaService(mock_db)
    admin = User(id_user=1)
    
    with patch("services.diploma_service.ipfs_service", mock_ipfs), \
         patch("services.diploma_service.blockchain_client", mock_blockchain):
        
        # Execute
        result = await service.emit_diploma(
            admin=admin,
            pdf_bytes=b"pdf_content",
            hash_sha256="hash123",
            titre="Test Diploma",
            etudiant_id="E123",
            institution_id=1,
            specialite_id="S1",
            mention="Bien",
            annee_promotion="2024",
            session_diplome="Principale",
            id_annexe=1,
            num_diplome=1,
            date_diplome=date.today(),
            date_liv_diplome=date.today(),
            generation_mode="UPLOAD"
        )
        # the service now returns a tuple (core, ext)
        assert isinstance(result, tuple)
        core, ext = result
        assert isinstance(core, EtudiantDiplome)
        assert core.etudiant_id == "E123"
        mock_ipfs.add_bytes.assert_called_once()
        mock_blockchain.register_diploma_hash.assert_called_once()
        assert mock_db.commit.called

@pytest.mark.asyncio
async def test_revoke_diploma_success(mock_db, mock_blockchain):
    # Setup
    service = DiplomaService(mock_db)
    admin = User(id_user=1)
    
    # Mock repository return
    mock_diploma = MagicMock(spec=EtudiantDiplome)
    mock_diploma.id_diplome = 1
    mock_diploma.blockchain_ext = MagicMock()
    mock_diploma.blockchain_ext.statut = StatutDiplome.ORIGINAL
    mock_diploma.blockchain_ext.tx_id_fabric = "tx_old"
    
    with patch.object(service.diploma_repo, "get_with_ext", return_value=mock_diploma), \
         patch("services.diploma_service.blockchain_client", mock_blockchain):
        
        # Execute
        result = await service.revoke_diploma(
            diplome_id=1,
            actor=admin,
            commentaire="Test revocation"
        )
        
        # Assertions
        assert result.blockchain_ext.statut == StatutDiplome.REVOQUE
        mock_blockchain.revoke_diploma.assert_called_once_with("tx_old")
        assert mock_db.commit.called
