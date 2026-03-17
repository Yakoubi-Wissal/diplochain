# use the generic diploma schema to avoid circular imports
# earlier versions accidentally referenced a non-imported DiplomeResponse
# which caused NameError during serialization.  the Pydantic schema is
# defined as DiplomeRead so use that consistently.
from schemas import DiplomeRead
from models import EtudiantDiplome, DiplomeBlockchainExt


def to_diplome_response(core: EtudiantDiplome, ext: DiplomeBlockchainExt) -> DiplomeRead:
    return DiplomeRead(
        id_diplome=core.id_diplome,
        titre=ext.titre,
        mention=ext.mention,
        date_emission=ext.date_emission,
        hash_sha256=ext.hash_sha256,
        tx_id_fabric=ext.tx_id_fabric,
        ipfs_cid=ext.ipfs_cid,
        statut=ext.statut,
        generation_mode=ext.generation_mode,
        blockchain_retry_count=ext.blockchain_retry_count,
        etudiant_id=core.etudiant_id,
        institution_id=ext.institution_id,
        specialite_id=ext.specialite_id,
        uploaded_by=ext.uploaded_by,
        annee_promotion=ext.annee_promotion,
        created_at=ext.created_at,
        updated_at=ext.updated_at,
    )
