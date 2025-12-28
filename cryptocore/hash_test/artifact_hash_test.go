package hash_test

import (
	"testing"
	"heritage/cryptocore/hash"
)

func TestArtifactHash_Deterministic(t *testing.T) {
	file := []byte("same_file")
	meta := []byte(`{"name":"same"}`)
	
	h1, err1 := hash.ArtifactHash(file, meta)
	h2, err2 := hash.ArtifactHash(file, meta)
	
	if err1 != nil || err2 != nil {
		t.Fatalf("Unexpected error: %v, %v", err1, err2)
	}
	
	if h1 != h2 {
		t.Fatalf("Hash not deterministic: %s != %s", h1, h2)
	}
}

func TestArtifactHash_EmptyFile(t *testing.T) {
	_, err := hash.ArtifactHash([]byte{}, []byte(`{}`))
	if err == nil {
		t.Fatal("Should reject empty file")
	}
}
