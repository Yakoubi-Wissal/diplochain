// =============================================================================
// DiploChain — chaincode/diplochain/diplochain.go
// Hyperledger Fabric 2.5 | Go 1.20+
// Fonctions : RegisterDiploma · QueryDiploma · RevokeDiploma · QueryByInstitution
// Correspond exactement aux specs de DiploChain_Final_v3.docx section 10.2
// =============================================================================

package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// =============================================================================
// Structures de données — alignées sur diplome_blockchain_ext
// =============================================================================

// DiplomaRecord représente un diplôme ancré on-chain.
// Correspond à : diplome_blockchain_ext + etudiant_diplome (clés externes)
type DiplomaRecord struct {
	ObjectType    string    `json:"objectType"`    // "DiplomaRecord" — pour les requêtes CouchDB
	DiplomeID     string    `json:"diplome_id"`    // etudiant_diplome.id_diplome (cast string)
	HashSHA256    string    `json:"hash_sha256"`   // diplome_blockchain_ext.hash_sha256 (64 chars UNIQUE)
	IpfsCID       string    `json:"ipfs_cid"`      // diplome_blockchain_ext.ipfs_cid
	InstitutionID string    `json:"institution_id"` // institution.institution_id
	EtudiantID    string    `json:"etudiant_id"`   // etudiant.etudiant_id
	DateEmission  string    `json:"date_emission"` // diplome_blockchain_ext.date_emission
	Statut        string    `json:"statut"`        // "ORIGINAL" | "REVOQUE"
	TxID          string    `json:"tx_id"`         // TX_ID Fabric de RegisterDiploma
	CreatedAt     string    `json:"created_at"`
	UpdatedAt     string    `json:"updated_at"`
	RevokedAt     string    `json:"revoked_at"`
	RevocationMotif string  `json:"revocation_motif"`
}

// DiploChainContract est le smart contract principal
type DiploChainContract struct {
	contractapi.Contract
}

// =============================================================================
// RegisterDiploma — ancre un diplôme on-chain
// Appelé par blockchain-service POST /blockchain/register
// Retourne le TX_ID stocké dans diplome_blockchain_ext.tx_id_fabric
// =============================================================================
func (c *DiploChainContract) RegisterDiploma(
	ctx contractapi.TransactionContextInterface,
	diplomeID string,
	hashSHA256 string,
	ipfsCID string,
	institutionID string,
	etudiantID string,
	dateEmission string,
) (string, error) {

	// Validation des paramètres requis
	if diplomeID == "" || hashSHA256 == "" || ipfsCID == "" || institutionID == "" {
		return "", fmt.Errorf("RegisterDiploma: diplomeID, hashSHA256, ipfsCID et institutionID sont requis")
	}
	if len(hashSHA256) != 64 {
		return "", fmt.Errorf("RegisterDiploma: hashSHA256 doit faire exactement 64 caractères (SHA-256 hex)")
	}

	// Vérifier que ce diplôme n'existe pas déjà (idempotence)
	existing, err := ctx.GetStub().GetState(diplomeID)
	if err != nil {
		return "", fmt.Errorf("RegisterDiploma: erreur lecture ledger : %v", err)
	}
	if existing != nil {
		// Vérifier si c'est un re-submit (retry-worker-service)
		var existingRecord DiplomaRecord
		if jsonErr := json.Unmarshal(existing, &existingRecord); jsonErr == nil {
			if existingRecord.HashSHA256 == hashSHA256 {
				// Même hash = re-submission idempotente → retourner le TX_ID existant
				return existingRecord.TxID, nil
			}
		}
		return "", fmt.Errorf("RegisterDiploma: diplôme %s déjà enregistré avec un hash différent", diplomeID)
	}

	// Vérifier l'unicité du hash SHA-256 par requête composite key
	hashKey, err := ctx.GetStub().CreateCompositeKey("hash", []string{hashSHA256})
	if err != nil {
		return "", fmt.Errorf("RegisterDiploma: création composite key hash : %v", err)
	}
	hashExists, err := ctx.GetStub().GetState(hashKey)
	if err != nil {
		return "", fmt.Errorf("RegisterDiploma: vérification unicité hash : %v", err)
	}
	if hashExists != nil {
		return "", fmt.Errorf("RegisterDiploma: hash SHA-256 %s déjà enregistré (double émission détectée)", hashSHA256)
	}

	now := time.Now().UTC().Format(time.RFC3339)
	txID := ctx.GetStub().GetTxID()

	diploma := DiplomaRecord{
		ObjectType:    "DiplomaRecord",
		DiplomeID:     diplomeID,
		HashSHA256:    hashSHA256,
		IpfsCID:       ipfsCID,
		InstitutionID: institutionID,
		EtudiantID:    etudiantID,
		DateEmission:  dateEmission,
		Statut:        "ORIGINAL",
		TxID:          txID,
		CreatedAt:     now,
		UpdatedAt:     now,
		RevokedAt:     "",
		RevocationMotif: "",
	}

	diplomaJSON, err := json.Marshal(diploma)
	if err != nil {
		return "", fmt.Errorf("RegisterDiploma: sérialisation JSON : %v", err)
	}

	// Écriture principale : clé = diplomeID
	if err := ctx.GetStub().PutState(diplomeID, diplomaJSON); err != nil {
		return "", fmt.Errorf("RegisterDiploma: écriture ledger : %v", err)
	}

	// Index composite hash → diplomeID (unicité SHA-256)
	if err := ctx.GetStub().PutState(hashKey, []byte(diplomeID)); err != nil {
		return "", fmt.Errorf("RegisterDiploma: index hash : %v", err)
	}

	// Index composite institutionID → diplomeID (QueryByInstitution)
	instKey, _ := ctx.GetStub().CreateCompositeKey("institution~diplome", []string{institutionID, diplomeID})
	if err := ctx.GetStub().PutState(instKey, []byte{}); err != nil {
		return "", fmt.Errorf("RegisterDiploma: index institution : %v", err)
	}

	// Événement Fabric (consommable par les listeners)
	eventPayload := fmt.Sprintf(`{"event":"DiplomeRegistered","diplome_id":"%s","institution_id":"%s","tx_id":"%s"}`,
		diplomeID, institutionID, txID)
	ctx.GetStub().SetEvent("DiplomeRegistered", []byte(eventPayload))

	return txID, nil
}

// =============================================================================
// QueryDiploma — interroge un diplôme par son ID
// Appelé par verification-service (source de vérité on-chain)
// =============================================================================
func (c *DiploChainContract) QueryDiploma(
	ctx contractapi.TransactionContextInterface,
	diplomeID string,
) (*DiplomaRecord, error) {

	if diplomeID == "" {
		return nil, fmt.Errorf("QueryDiploma: diplomeID requis")
	}

	diplomaJSON, err := ctx.GetStub().GetState(diplomeID)
	if err != nil {
		return nil, fmt.Errorf("QueryDiploma: erreur lecture ledger : %v", err)
	}
	if diplomaJSON == nil {
		return nil, fmt.Errorf("QueryDiploma: diplôme %s introuvable on-chain", diplomeID)
	}

	var diploma DiplomaRecord
	if err := json.Unmarshal(diplomaJSON, &diploma); err != nil {
		return nil, fmt.Errorf("QueryDiploma: désérialisation : %v", err)
	}

	return &diploma, nil
}

// =============================================================================
// VerifyDiploma — vérifie l'authenticité par hash SHA-256 (vérification publique)
// Retourne le diplôme si le hash correspond, erreur sinon
// =============================================================================
func (c *DiploChainContract) VerifyDiploma(
	ctx contractapi.TransactionContextInterface,
	diplomeID string,
	hashSHA256 string,
) (*DiplomaRecord, error) {

	diploma, err := c.QueryDiploma(ctx, diplomeID)
	if err != nil {
		return nil, err
	}

	if diploma.HashSHA256 != hashSHA256 {
		return nil, fmt.Errorf("VerifyDiploma: hash SHA-256 invalide — falsification détectée")
	}

	if diploma.Statut == "REVOQUE" {
		return nil, fmt.Errorf("VerifyDiploma: diplôme %s a été révoqué le %v — motif: %s",
			diplomeID, diploma.RevokedAt, diploma.RevocationMotif)
	}

	return diploma, nil
}

// =============================================================================
// RevokeDiploma — révoque un diplôme (SUPER_ADMIN ou ADMIN_INSTITUTION)
// Met à jour statut → "REVOQUE" dans le ledger
// Correspond à historique_operations.type_operation = 'REVOCATION'
// =============================================================================
func (c *DiploChainContract) RevokeDiploma(
	ctx contractapi.TransactionContextInterface,
	diplomeID string,
	motif string,
) (string, error) {

	if diplomeID == "" {
		return "", fmt.Errorf("RevokeDiploma: diplomeID requis")
	}

	diploma, err := c.QueryDiploma(ctx, diplomeID)
	if err != nil {
		return "", err
	}

	if diploma.Statut == "REVOQUE" {
		return "", fmt.Errorf("RevokeDiploma: diplôme %s est déjà révoqué", diplomeID)
	}

	now := time.Now().UTC().Format(time.RFC3339)
	diploma.Statut = "REVOQUE"
	diploma.UpdatedAt = now
	diploma.RevokedAt = now
	diploma.RevocationMotif = motif

	diplomaJSON, err := json.Marshal(diploma)
	if err != nil {
		return "", fmt.Errorf("RevokeDiploma: sérialisation : %v", err)
	}

	if err := ctx.GetStub().PutState(diplomeID, diplomaJSON); err != nil {
		return "", fmt.Errorf("RevokeDiploma: écriture ledger : %v", err)
	}

	txID := ctx.GetStub().GetTxID()

	eventPayload := fmt.Sprintf(`{"event":"DiplomeRevoque","diplome_id":"%s","tx_id":"%s","motif":"%s"}`,
		diplomeID, txID, motif)
	ctx.GetStub().SetEvent("DiplomeRevoque", []byte(eventPayload))

	return txID, nil
}

// =============================================================================
// QueryByInstitution — liste tous les diplômes d'une institution
// Utilise l'index composite institution~diplome
// =============================================================================
func (c *DiploChainContract) QueryByInstitution(
	ctx contractapi.TransactionContextInterface,
	institutionID string,
) ([]*DiplomaRecord, error) {

	if institutionID == "" {
		return nil, fmt.Errorf("QueryByInstitution: institutionID requis")
	}

	iterator, err := ctx.GetStub().GetStateByPartialCompositeKey("institution~diplome", []string{institutionID})
	if err != nil {
		return nil, fmt.Errorf("QueryByInstitution: itérateur : %v", err)
	}
	defer iterator.Close()

	var diplomas []*DiplomaRecord

	for iterator.HasNext() {
		item, err := iterator.Next()
		if err != nil {
			return nil, fmt.Errorf("QueryByInstitution: lecture itérateur : %v", err)
		}

		// Extraire le diplomeID depuis la composite key
		_, compositeKeyParts, err := ctx.GetStub().SplitCompositeKey(item.Key)
		if err != nil || len(compositeKeyParts) < 2 {
			continue
		}
		diplomeID := compositeKeyParts[1]

		diploma, err := c.QueryDiploma(ctx, diplomeID)
		if err != nil {
			continue
		}
		diplomas = append(diplomas, diploma)
	}

	return diplomas, nil
}

// =============================================================================
// GetDiplomaHistory — historique des modifications d'un diplôme
// Pour audit et traçabilité (complète historique_operations PostgreSQL)
// =============================================================================
func (c *DiploChainContract) GetDiplomaHistory(
	ctx contractapi.TransactionContextInterface,
	diplomeID string,
) ([]map[string]interface{}, error) {

	if diplomeID == "" {
		return nil, fmt.Errorf("GetDiplomaHistory: diplomeID requis")
	}

	iterator, err := ctx.GetStub().GetHistoryForKey(diplomeID)
	if err != nil {
		return nil, fmt.Errorf("GetDiplomaHistory: %v", err)
	}
	defer iterator.Close()

	var history []map[string]interface{}

	for iterator.HasNext() {
		item, err := iterator.Next()
		if err != nil {
			return nil, fmt.Errorf("GetDiplomaHistory: itérateur : %v", err)
		}

		entry := map[string]interface{}{
			"tx_id":     item.TxId,
			"timestamp": item.Timestamp,
			"is_delete": item.IsDelete,
		}

		if !item.IsDelete {
			var diploma DiplomaRecord
			if jsonErr := json.Unmarshal(item.Value, &diploma); jsonErr == nil {
				entry["statut"] = diploma.Statut
				entry["hash_sha256"] = diploma.HashSHA256
			}
		}

		history = append(history, entry)
	}

	return history, nil
}

// =============================================================================
// main
// =============================================================================
func main() {
	chaincode, err := contractapi.NewChaincode(&DiploChainContract{})
	if err != nil {
		panic(fmt.Sprintf("DiploChain chaincode: erreur création : %v", err))
	}

	if err := chaincode.Start(); err != nil {
		panic(fmt.Sprintf("DiploChain chaincode: erreur démarrage : %v", err))
	}
}
