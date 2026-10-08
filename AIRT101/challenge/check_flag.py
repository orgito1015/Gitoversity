"""Verify an AIRT101 flag by its SHA-256 hash. Standard library only.

Usage: python3 check_flag.py 'GITO{...}'
"""
import hashlib
import sys

HASHES = {
    "309b4858b8d380a95e72e4d5fc5269ee5b23390acadd40e20eb2ae8563a807aa": "Flag 1 (direct prompt injection)",
    "3dd1a35451e8cfe30861cc3c3b50c3fd487407ebb1e910cc42e93c1e65f93596": "Flag 2 (indirect prompt injection)",
}


def check(flag):
    """Return the name of the flag that matches, or None."""
    return HASHES.get(hashlib.sha256(flag.strip().encode()).hexdigest())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 check_flag.py 'GITO{...}'")
    name = check(sys.argv[1])
    print(f"PASS: {name}" if name else "FAIL")
    sys.exit(0 if name else 1)
