"""Verify a WEB101 flag by its SHA-256 hash. Standard library only.

Usage: python3 check_flag.py 'GITO{...}'
"""
import hashlib
import sys

HASHES = {
    "d8fdee51340ad128a07bffdb8c6ded424f9eda76b26f92514a228b8ba63313a9": "Flag 1 (broken access control / IDOR)",
    "ba0a8d58836063cf434d9f403647340c7bcf678e7ec2aea09a1965f585a295ca": "Flag 2 (recon / information disclosure)",
}


def check(flag):
    return HASHES.get(hashlib.sha256(flag.strip().encode()).hexdigest())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 check_flag.py 'GITO{...}'")
    name = check(sys.argv[1])
    print(f"PASS: {name}" if name else "FAIL")
    sys.exit(0 if name else 1)
