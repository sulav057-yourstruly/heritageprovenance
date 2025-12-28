// cryptocore/hash/artifact_hash.go
package hash

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
)

// ArtifactHash computes deterministic identity
func ArtifactHash(fileBytes []byte, metadataBytes []byte) (string, error) {
	if len(fileBytes) == 0 {
		return "", fmt.Errorf("file cannot be empty")
	}
	
	h := sha256.New()
	h.Write(fileBytes)
	h.Write(metadataBytes)
	return hex.EncodeToString(h.Sum(nil)), nil
}
