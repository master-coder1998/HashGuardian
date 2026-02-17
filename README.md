# 🔐 HashGuardian — Text Integrity Checker

> Detect whether text has been modified using cryptographic hashing.

HashGuardian lets you **snapshot** any text, then **verify** it later to detect even the tiniest change — a single character, an extra space, or a full rewrite.

---

## ✨ Features

- ✅ Hash any text using **MD5, SHA-1, SHA-256, or SHA-512**
- 📸 **Save snapshots** of text with a label to a local vault
- 🔍 **Verify** text against saved snapshots to detect tampering
- ↔️ **Compare** two texts directly (no snapshot needed)
- 📋 **List** and **delete** saved snapshots
- 🎨 Beautiful terminal output with color-coded results
- 🧪 Fully tested with **pytest** (30+ tests)

---

## 📁 Project Structure

```
hash_guardian/
├── hasher.py        # Core hashing logic (library)
├── cli.py           # CLI interface
├── test_hasher.py   # Unit tests (pytest)
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

```bash
git clone https://github.com/master-coder1998/HashGuardian-Text-Integrity-Checker.git
cd HashGuardian
pip install -r requirements.txt
```

---

## 💻 CLI Usage

### Hash text
```bash
python cli.py hash "Hello, World!"
python cli.py hash "Hello, World!" --all        # show all algorithms
python cli.py hash "Hello" -a md5               # use MD5
```

### Save a snapshot
```bash
python cli.py save my_doc "This is the original text."
python cli.py save contract "Terms and conditions..." -a sha512
```

### Verify text against snapshot
```bash
python cli.py verify my_doc "This is the original text."
# ✔ INTACT — Text has NOT been modified.

python cli.py verify my_doc "This is the modified text."
# ✘ MODIFIED — Text has been tampered with!
```

### Compare two texts directly
```bash
python cli.py compare --file1 original.txt --file2 received.txt
```

### Manage snapshots
```bash
python cli.py list              # show all snapshots
python cli.py delete my_doc     # delete a snapshot
```

---

## 🐍 Use as a Library

```python
from hasher import compute_hash, save_hash, verify_text, compare_texts

# Compute a hash
h = compute_hash("Hello World", algorithm="sha256")

# Save a snapshot
save_hash("my_label", "Original text here")

# Verify later
result = verify_text("my_label", "Original text here")
print(result["status"])   # "INTACT" or "MODIFIED"

# Compare two texts
result = compare_texts("text one", "text two")
print(result["identical"])  # False
```

---

## 🧪 Running Tests

```bash
pip install pytest
pytest test_hasher.py -v
```

---

## 🔬 How It Works

1. **Hashing** — Text is encoded to UTF-8 bytes and passed through a hash function (SHA-256 by default). This produces a fixed-length fingerprint unique to the content.
2. **Vault** — Snapshots are stored in a local `hash_vault.json` file with the label, hash, algorithm, length, and timestamp.
3. **Verification** — When verifying, the current text is re-hashed with the same algorithm and compared to the stored hash. Any change — even a single space — produces a completely different hash.

---

## 📦 Supported Algorithms

| Algorithm | Output Length | Notes |
|-----------|-------------|-------|
| MD5       | 32 hex chars | Fast, not collision-resistant |
| SHA-1     | 40 hex chars | Deprecated for security use |
| SHA-256   | 64 hex chars | ✅ Recommended default |
| SHA-512   | 128 hex chars | Highest security |

---

## 👤 Author

**master-coder1998**
- GitHub: [@master-coder1998](https://github.com/master-coder1998)

---

## 📄 License

MIT License — free to use and modify.
