"""
HashGuardian - Text Integrity Checker
Detects whether text has been modified by comparing cryptographic hashes.
"""

import hashlib
import json
import os
import datetime
from pathlib import Path


ALGORITHMS = ["md5", "sha1", "sha256", "sha512"]
VAULT_FILE = "hash_vault.json"


def compute_hash(text: str, algorithm: str = "sha256") -> str:
    """Compute hash of given text using specified algorithm."""
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unsupported algorithm. Choose from: {ALGORITHMS}")
    h = hashlib.new(algorithm)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def compute_all_hashes(text: str) -> dict:
    """Compute hashes using all supported algorithms."""
    return {algo: compute_hash(text, algo) for algo in ALGORITHMS}


def save_hash(label: str, text: str, algorithm: str = "sha256") -> dict:
    """Save a hash snapshot to the vault."""
    vault = load_vault()
    entry = {
        "label": label,
        "algorithm": algorithm,
        "hash": compute_hash(text, algorithm),
        "length": len(text),
        "timestamp": datetime.datetime.now().isoformat(),
    }
    vault[label] = entry
    save_vault(vault)
    return entry


def verify_text(label: str, text: str) -> dict:
    """Verify if text matches the saved hash snapshot."""
    vault = load_vault()
    if label not in vault:
        return {"status": "NOT_FOUND", "message": f"No snapshot found for label '{label}'"}

    entry = vault[label]
    current_hash = compute_hash(text, entry["algorithm"])
    original_hash = entry["hash"]
    is_intact = current_hash == original_hash

    return {
        "status": "INTACT" if is_intact else "MODIFIED",
        "label": label,
        "algorithm": entry["algorithm"],
        "original_hash": original_hash,
        "current_hash": current_hash,
        "original_length": entry["length"],
        "current_length": len(text),
        "saved_at": entry["timestamp"],
        "is_intact": is_intact,
    }


def compare_texts(text1: str, text2: str, algorithm: str = "sha256") -> dict:
    """Compare two texts directly without saving."""
    hash1 = compute_hash(text1, algorithm)
    hash2 = compute_hash(text2, algorithm)
    return {
        "algorithm": algorithm,
        "hash_1": hash1,
        "hash_2": hash2,
        "identical": hash1 == hash2,
        "length_1": len(text1),
        "length_2": len(text2),
    }


def load_vault() -> dict:
    """Load the hash vault from disk."""
    if Path(VAULT_FILE).exists():
        with open(VAULT_FILE, "r") as f:
            return json.load(f)
    return {}


def save_vault(vault: dict):
    """Save the hash vault to disk."""
    with open(VAULT_FILE, "w") as f:
        json.dump(vault, f, indent=2)


def list_snapshots() -> list:
    """List all saved snapshots."""
    vault = load_vault()
    return list(vault.values())


def delete_snapshot(label: str) -> bool:
    """Delete a snapshot from the vault."""
    vault = load_vault()
    if label in vault:
        del vault[label]
        save_vault(vault)
        return True
    return False
