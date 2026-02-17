"""
Merkle tree construction and inclusion proof generation.
"""
import hashlib
from typing import List, Tuple

def sha256_hash(data: bytes) -> str:
    """Compute SHA-256 hash, return hex string."""
    return hashlib.sha256(data).hexdigest()

def merkle_root(event_hashes: List[str]) -> str:
    """
    Compute Merkle root from list of event hashes.
    Uses binary tree structure with SHA-256.
    """
    if not event_hashes:
        return sha256_hash(b"")
    
    if len(event_hashes) == 1:
        return event_hashes[0]
    
    # Convert hex strings to bytes for hashing
    def hash_pair(a: str, b: str) -> str:
        return sha256_hash(bytes.fromhex(a) + bytes.fromhex(b))
    
    # Build tree level by level
    current_level = event_hashes.copy()
    
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            if i + 1 < len(current_level):
                next_level.append(hash_pair(current_level[i], current_level[i + 1]))
            else:
                # Odd number of nodes, duplicate the last one
                next_level.append(hash_pair(current_level[i], current_level[i]))
        current_level = next_level
    
    return current_level[0]

def merkle_proof(event_hash: str, event_hashes: List[str]) -> Tuple[str, List[str]]:
    """
    Generate Merkle inclusion proof for a specific event hash.
    Returns (merkle_root, proof_path) where proof_path is list of sibling hashes.
    """
    if event_hash not in event_hashes:
        raise ValueError(f"Event hash {event_hash} not in list")
    
    root = merkle_root(event_hashes)
    
    # Build proof path by traversing tree
    def hash_pair(a: str, b: str) -> str:
        return sha256_hash(bytes.fromhex(a) + bytes.fromhex(b))
    
    proof_path = []
    current_level = event_hashes.copy()
    current_index = event_hashes.index(event_hash)
    
    while len(current_level) > 1:
        sibling_index = current_index ^ 1  # XOR to get sibling
        if sibling_index < len(current_level):
            proof_path.append(current_level[sibling_index])
        else:
            # No sibling (odd number), duplicate self
            proof_path.append(current_level[current_index])
        
        # Move to parent level
        next_level = []
        next_index = current_index // 2
        for i in range(0, len(current_level), 2):
            if i + 1 < len(current_level):
                next_level.append(hash_pair(current_level[i], current_level[i + 1]))
            else:
                next_level.append(hash_pair(current_level[i], current_level[i]))
        current_level = next_level
        current_index = next_index
    
    return root, proof_path

def verify_merkle_proof(event_hash: str, proof_path: List[str], merkle_root: str) -> bool:
    """
    Verify that event_hash is included in the Merkle tree with given root.
    """
    current = event_hash
    
    def hash_pair(a: str, b: str) -> str:
        return sha256_hash(bytes.fromhex(a) + bytes.fromhex(b))
    
    for sibling in proof_path:
        # Determine order: if current < sibling (lexicographically), left child, else right
        if current < sibling:
            current = hash_pair(current, sibling)
        else:
            current = hash_pair(sibling, current)
    
    return current == merkle_root

