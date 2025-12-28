package main

import (
	"fmt"
	"heritage/cryptocore/hash"
)

func main() {
	hash, err := hash.ArtifactHash([]byte("test_file"), []byte(`{"name":"test"}`))
	if err != nil {
		panic(err)
	}
	fmt.Printf("Hash: %s\n", hash)
}
