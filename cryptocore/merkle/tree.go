// cryptocore/merkle/tree.go
package merkle

import (
	"crypto/sha256"
	"encoding/hex"
)

type Tree struct {
	Root   string
	Leaves []string
	levels [][]string // internal
}

func NewTree(leaves []string) *Tree {
	if len(leaves) == 0 {
		return &Tree{Root: "", Leaves: leaves}
	}
	
	level := make([]string, len(leaves))
	copy(level, leaves)
	
	levels := [][]string{level}
	
	for len(level) > 1 {
		nextLevel := []string{}
		for i := 0; i < len(level); i += 2 {
			left := level[i]
			right := left
			if i+1 < len(level) {
				right = level[i+1]
			}
			nextLevel = append(nextLevel, hashPair(left, right))
		}
		levels = append(levels, nextLevel)
		level = nextLevel
	}
	
	return &Tree{
		Root:   level[0],
		Leaves: leaves,
		levels: levels,
	}
}

func hashPair(left, right string) string {
	h := sha256.New()
	h.Write([]byte(left))
	h.Write([]byte(right))
	return hex.EncodeToString(h.Sum(nil))
}
