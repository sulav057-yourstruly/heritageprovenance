"""
Cryptographic utilities: hashing, canonical JSON, Ed25519 signing.
"""
import hashlib
import json
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
import base64

def compute_cid(file_bytes: bytes) -> str:
    """Compute SHA-256 Content Identifier (CID) from file bytes."""
    return hashlib.sha256(file_bytes).hexdigest()

def canonical_json(data: Dict[str, Any]) -> bytes:
    """
    Canonicalize JSON for stable hashing/signing.
    Uses sorted keys, no whitespace, UTF-8 encoding.
    """
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')

def hash_event(event_data: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of canonical event payload."""
    canonical = canonical_json(event_data)
    return hashlib.sha256(canonical).hexdigest()

def generate_keypair() -> tuple[str, str]:
    """Generate Ed25519 keypair, returns (private_key_b64, public_key_b64)."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    priv_b64 = base64.b64encode(
        private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
    ).decode('ascii')
    
    pub_b64 = base64.b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    ).decode('ascii')
    
    return priv_b64, pub_b64

def derive_keypair_from_seed(seed: str) -> tuple[str, str]:
    """
    Derive a deterministic Ed25519 keypair from a seed string.
    For MVP: allows consistent keypair generation for the same actor.
    NOT cryptographically secure for production - use proper key derivation.
    """
    # Use SHA-256 to derive 32 bytes from seed
    seed_bytes = hashlib.sha256(seed.encode('utf-8')).digest()
    
    # Ed25519 private keys are 32 bytes
    private_key = Ed25519PrivateKey.from_private_bytes(seed_bytes)
    public_key = private_key.public_key()
    
    priv_b64 = base64.b64encode(seed_bytes).decode('ascii')
    pub_b64 = base64.b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    ).decode('ascii')
    
    return priv_b64, pub_b64

def sign_event(event_data: Dict[str, Any], private_key_b64: str) -> str:
    """
    Sign canonical event payload with Ed25519 private key.
    Returns base64-encoded signature.
    """
    private_key_bytes = base64.b64decode(private_key_b64)
    private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    
    canonical = canonical_json(event_data)
    signature = private_key.sign(canonical)
    
    return base64.b64encode(signature).decode('ascii')

def verify_signature(event_data: Dict[str, Any], signature_b64: str, public_key_b64: str) -> bool:
    """
    Verify Ed25519 signature on canonical event payload.
    Returns True if valid, False otherwise.
    """
    try:
        public_key_bytes = base64.b64decode(public_key_b64)
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        
        signature = base64.b64decode(signature_b64)
        canonical = canonical_json(event_data)
        
        public_key.verify(signature, canonical)
        return True
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Signature verification failed: {e}")
        logger.error(f"Event data: {event_data}")
        logger.error(f"Canonical bytes: {canonical.hex()[:50]}...")
        return False

