#!/usr/bin/env python3
"""
HashGuardian CLI - Text Integrity Checker
Usage: python cli.py [command] [options]
"""

import argparse
import sys
import json
from hasher import (
    compute_hash, compute_all_hashes, save_hash,
    verify_text, compare_texts, list_snapshots, delete_snapshot, ALGORITHMS
)


# ── ANSI Colors ──────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
  ██╗  ██╗ █████╗ ███████╗██╗  ██╗
  ██║  ██║██╔══██╗██╔════╝██║  ██║
  ███████║███████║███████╗███████║
  ██╔══██║██╔══██║╚════██║██╔══██║
  ██║  ██║██║  ██║███████║██║  ██║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
  {RESET}{DIM}  G U A R D I A N  —  Text Integrity Checker{RESET}
"""


def print_result(data: dict):
    """Pretty print a dictionary result."""
    print(json.dumps(data, indent=2))


def cmd_hash(args):
    """Hash a piece of text."""
    text = args.text or sys.stdin.read()
    if args.all:
        result = compute_all_hashes(text)
        print(f"\n{BOLD}Hashes for input text:{RESET}")
        for algo, h in result.items():
            print(f"  {CYAN}{algo:<8}{RESET} {h}")
    else:
        h = compute_hash(text, args.algorithm)
        print(f"\n  {CYAN}{args.algorithm}{RESET}: {BOLD}{h}{RESET}")


def cmd_save(args):
    """Save a text snapshot."""
    text = args.text or sys.stdin.read()
    entry = save_hash(args.label, text, args.algorithm)
    print(f"\n  {GREEN}✔ Snapshot saved!{RESET}")
    print(f"  Label     : {BOLD}{entry['label']}{RESET}")
    print(f"  Algorithm : {entry['algorithm']}")
    print(f"  Hash      : {entry['hash']}")
    print(f"  Saved at  : {entry['timestamp']}\n")


def cmd_verify(args):
    """Verify if text matches saved snapshot."""
    text = args.text or sys.stdin.read()
    result = verify_text(args.label, text)

    if result["status"] == "NOT_FOUND":
        print(f"\n  {YELLOW}⚠ {result['message']}{RESET}\n")
        return

    if result["is_intact"]:
        print(f"\n  {GREEN}{BOLD}✔ INTACT — Text has NOT been modified.{RESET}")
    else:
        print(f"\n  {RED}{BOLD}✘ MODIFIED — Text has been tampered with!{RESET}")

    print(f"\n  Label           : {result['label']}")
    print(f"  Algorithm       : {result['algorithm']}")
    print(f"  Original hash   : {DIM}{result['original_hash']}{RESET}")
    print(f"  Current hash    : {DIM}{result['current_hash']}{RESET}")
    print(f"  Original length : {result['original_length']} chars")
    print(f"  Current length  : {result['current_length']} chars")
    print(f"  Snapshot date   : {result['saved_at']}\n")


def cmd_compare(args):
    """Compare two texts directly."""
    if args.file1 and args.file2:
        text1 = open(args.file1).read()
        text2 = open(args.file2).read()
    else:
        print(f"\n  {YELLOW}Enter Text 1 (end with Ctrl+D):{RESET}")
        text1 = sys.stdin.read()
        print(f"\n  {YELLOW}Enter Text 2 (end with Ctrl+D):{RESET}")
        text2 = sys.stdin.read()

    result = compare_texts(text1, text2, args.algorithm)
    if result["identical"]:
        print(f"\n  {GREEN}{BOLD}✔ IDENTICAL — Both texts are the same.{RESET}")
    else:
        print(f"\n  {RED}{BOLD}✘ DIFFERENT — Texts do not match.{RESET}")

    print(f"\n  Algorithm : {result['algorithm']}")
    print(f"  Hash 1    : {result['hash_1']}")
    print(f"  Hash 2    : {result['hash_2']}")
    print(f"  Length 1  : {result['length_1']} chars")
    print(f"  Length 2  : {result['length_2']} chars\n")


def cmd_list(args):
    """List all saved snapshots."""
    snapshots = list_snapshots()
    if not snapshots:
        print(f"\n  {YELLOW}No snapshots saved yet.{RESET}\n")
        return
    print(f"\n  {BOLD}Saved Snapshots ({len(snapshots)}){RESET}")
    print(f"  {'Label':<20} {'Algorithm':<10} {'Saved At':<26} Hash")
    print(f"  {'-'*85}")
    for s in snapshots:
        h_short = s['hash'][:16] + "..."
        print(f"  {s['label']:<20} {s['algorithm']:<10} {s['timestamp']:<26} {DIM}{h_short}{RESET}")
    print()


def cmd_delete(args):
    """Delete a snapshot."""
    if delete_snapshot(args.label):
        print(f"\n  {GREEN}✔ Snapshot '{args.label}' deleted.{RESET}\n")
    else:
        print(f"\n  {YELLOW}⚠ Snapshot '{args.label}' not found.{RESET}\n")


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(
        prog="hashguardian",
        description="Text Integrity Checker using Cryptographic Hashing"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # hash
    p_hash = sub.add_parser("hash", help="Compute hash of text")
    p_hash.add_argument("text", nargs="?", help="Text to hash (or pipe via stdin)")
    p_hash.add_argument("-a", "--algorithm", default="sha256", choices=ALGORITHMS)
    p_hash.add_argument("--all", action="store_true", help="Show all algorithm hashes")

    # save
    p_save = sub.add_parser("save", help="Save a text snapshot")
    p_save.add_argument("label", help="Unique label for this snapshot")
    p_save.add_argument("text", nargs="?", help="Text to snapshot")
    p_save.add_argument("-a", "--algorithm", default="sha256", choices=ALGORITHMS)

    # verify
    p_verify = sub.add_parser("verify", help="Verify text against saved snapshot")
    p_verify.add_argument("label", help="Snapshot label to verify against")
    p_verify.add_argument("text", nargs="?", help="Current text to check")

    # compare
    p_compare = sub.add_parser("compare", help="Compare two texts directly")
    p_compare.add_argument("--file1", help="First file path")
    p_compare.add_argument("--file2", help="Second file path")
    p_compare.add_argument("-a", "--algorithm", default="sha256", choices=ALGORITHMS)

    # list
    sub.add_parser("list", help="List all saved snapshots")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a snapshot")
    p_delete.add_argument("label", help="Label of snapshot to delete")

    args = parser.parse_args()
    dispatch = {
        "hash": cmd_hash, "save": cmd_save, "verify": cmd_verify,
        "compare": cmd_compare, "list": cmd_list, "delete": cmd_delete,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
