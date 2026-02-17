"""
Tests for HashGuardian - Text Integrity Checker
Run: pytest test_hasher.py -v
"""

import pytest
import os
import json
from hasher import (
    compute_hash, compute_all_hashes, save_hash,
    verify_text, compare_texts, list_snapshots,
    delete_snapshot, ALGORITHMS, VAULT_FILE
)

TEST_VAULT = "test_vault.json"


@pytest.fixture(autouse=True)
def use_test_vault(monkeypatch, tmp_path):
    """Redirect vault to a temp file for each test."""
    import hasher
    vault_path = tmp_path / "vault.json"
    monkeypatch.setattr(hasher, "VAULT_FILE", str(vault_path))


# ── compute_hash ──────────────────────────────────────────────

class TestComputeHash:
    def test_sha256_known_value(self):
        h = compute_hash("hello")
        assert h == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    def test_md5_known_value(self):
        h = compute_hash("hello", "md5")
        assert h == "5d41402abc4b2a76b9719d911017c592"

    def test_sha1_known_value(self):
        h = compute_hash("hello", "sha1")
        assert h == "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"

    def test_sha512_returns_128_chars(self):
        h = compute_hash("hello", "sha512")
        assert len(h) == 128

    def test_all_algorithms_work(self):
        for algo in ALGORITHMS:
            h = compute_hash("test", algo)
            assert isinstance(h, str) and len(h) > 0

    def test_different_texts_give_different_hashes(self):
        assert compute_hash("hello") != compute_hash("Hello")

    def test_same_text_always_same_hash(self):
        assert compute_hash("consistency") == compute_hash("consistency")

    def test_empty_string(self):
        h = compute_hash("")
        assert isinstance(h, str) and len(h) == 64  # sha256

    def test_unicode_text(self):
        h = compute_hash("héllo wörld 🔐")
        assert isinstance(h, str) and len(h) == 64

    def test_invalid_algorithm_raises(self):
        with pytest.raises(ValueError):
            compute_hash("hello", "fakehash")


# ── compute_all_hashes ────────────────────────────────────────

class TestComputeAllHashes:
    def test_returns_all_algorithms(self):
        result = compute_all_hashes("test")
        assert set(result.keys()) == set(ALGORITHMS)

    def test_all_values_are_strings(self):
        result = compute_all_hashes("test")
        for v in result.values():
            assert isinstance(v, str)


# ── save_hash & verify_text ───────────────────────────────────

class TestSaveAndVerify:
    def test_save_returns_entry(self):
        entry = save_hash("mysnap", "original text")
        assert entry["label"] == "mysnap"
        assert entry["algorithm"] == "sha256"
        assert "hash" in entry
        assert "timestamp" in entry

    def test_verify_intact(self):
        save_hash("snap1", "the quick brown fox")
        result = verify_text("snap1", "the quick brown fox")
        assert result["status"] == "INTACT"
        assert result["is_intact"] is True

    def test_verify_modified(self):
        save_hash("snap2", "original content")
        result = verify_text("snap2", "modified content")
        assert result["status"] == "MODIFIED"
        assert result["is_intact"] is False

    def test_verify_not_found(self):
        result = verify_text("nonexistent", "some text")
        assert result["status"] == "NOT_FOUND"

    def test_verify_tracks_length(self):
        save_hash("snap3", "hello")
        result = verify_text("snap3", "hello world")
        assert result["original_length"] == 5
        assert result["current_length"] == 11

    def test_save_with_md5(self):
        save_hash("snap_md5", "test", algorithm="md5")
        result = verify_text("snap_md5", "test")
        assert result["is_intact"] is True

    def test_single_char_change_detected(self):
        save_hash("snap4", "Hello World")
        result = verify_text("snap4", "Hello world")  # lowercase w
        assert result["is_intact"] is False

    def test_whitespace_change_detected(self):
        save_hash("snap5", "hello world")
        result = verify_text("snap5", "hello  world")  # extra space
        assert result["is_intact"] is False


# ── compare_texts ─────────────────────────────────────────────

class TestCompareTexts:
    def test_identical_texts(self):
        result = compare_texts("same", "same")
        assert result["identical"] is True

    def test_different_texts(self):
        result = compare_texts("text one", "text two")
        assert result["identical"] is False

    def test_returns_both_hashes(self):
        result = compare_texts("a", "b")
        assert "hash_1" in result and "hash_2" in result

    def test_empty_strings(self):
        result = compare_texts("", "")
        assert result["identical"] is True

    def test_custom_algorithm(self):
        result = compare_texts("hello", "hello", algorithm="md5")
        assert result["algorithm"] == "md5"
        assert result["identical"] is True


# ── list & delete ─────────────────────────────────────────────

class TestListAndDelete:
    def test_list_empty_vault(self):
        assert list_snapshots() == []

    def test_list_after_saves(self):
        save_hash("a", "text a")
        save_hash("b", "text b")
        snaps = list_snapshots()
        assert len(snaps) == 2

    def test_delete_existing(self):
        save_hash("to_delete", "bye")
        assert delete_snapshot("to_delete") is True
        assert verify_text("to_delete", "bye")["status"] == "NOT_FOUND"

    def test_delete_nonexistent(self):
        assert delete_snapshot("ghost") is False

    def test_overwrite_snapshot(self):
        save_hash("over", "version 1")
        save_hash("over", "version 2")
        result = verify_text("over", "version 2")
        assert result["is_intact"] is True
