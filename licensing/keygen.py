"""
License Key Generator - Options Backtesting System
===================================================
Run this PRIVATELY on your machine. Never distribute this file or private.key.

FIRST TIME SETUP (run once to generate your key pair):
    py licensing/keygen.py --setup

GENERATE A 30-DAY KEY:
    py licensing/keygen.py --email customer@example.com --name "John Doe"

GENERATE A CUSTOM DURATION KEY:
    py licensing/keygen.py --email customer@example.com --name "John Doe" --days 60

The key printed to the console is what you email to the customer.
"""

import argparse
import base64
import json
import os
import sys
import uuid
from datetime import date, timedelta

KEYS_DIR = os.path.join(os.path.dirname(__file__), 'keys')
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, 'private.key')
VALIDATOR_PATH = os.path.join(os.path.dirname(__file__), 'validator.py')


def _check_cryptography():
    try:
        import cryptography  # noqa: F401
    except ImportError:
        print("ERROR: 'cryptography' package not installed.")
        print("Run: py -m pip install cryptography")
        sys.exit(1)


def _generate_keypair():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PublicFormat, PrivateFormat, NoEncryption
    )
    private_key = Ed25519PrivateKey.generate()
    pub_bytes = private_key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    priv_bytes = private_key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
    return priv_bytes, pub_bytes


def _load_private_key():
    from cryptography.hazmat.primitives.serialization import load_der_private_key
    with open(PRIVATE_KEY_PATH, 'rb') as f:
        priv_b64 = f.read().strip()
    priv_bytes = base64.b64decode(priv_b64)
    return load_der_private_key(priv_bytes, password=None)


def setup():
    """Generate Ed25519 key pair and embed public key into validator.py."""
    _check_cryptography()

    if os.path.exists(PRIVATE_KEY_PATH):
        print("Key pair already exists.")
        print(f"  Private key: {PRIVATE_KEY_PATH}")
        print("\nDelete that file and re-run --setup to regenerate (this invalidates ALL existing keys).")
        return

    print("Generating Ed25519 key pair...")
    priv_bytes, pub_bytes = _generate_keypair()

    os.makedirs(KEYS_DIR, exist_ok=True)

    # Save private key as base64
    with open(PRIVATE_KEY_PATH, 'wb') as f:
        f.write(base64.b64encode(priv_bytes))

    # Create .gitignore in keys/ so private key is never committed
    gitignore_path = os.path.join(KEYS_DIR, '.gitignore')
    with open(gitignore_path, 'w') as f:
        f.write("# Never commit the private key\nprivate.key\n")

    # Embed public key into validator.py - only replace the PUBLIC_KEY_B64 assignment line
    pub_b64 = base64.b64encode(pub_bytes).decode()
    with open(VALIDATOR_PATH, 'r') as f:
        lines = f.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.startswith('PUBLIC_KEY_B64 ='):
            lines[i] = f'PUBLIC_KEY_B64 = "{pub_b64}"\n'
            updated = True
            break

    if not updated:
        print("WARNING: Could not find PUBLIC_KEY_B64 in validator.py. Update it manually.")
    else:
        with open(VALIDATOR_PATH, 'w') as f:
            f.writelines(lines)
        print(f"  Public key embedded in: {VALIDATOR_PATH}")

    print(f"  Private key saved to:   {PRIVATE_KEY_PATH}")
    print()
    print("=" * 60)
    print("IMPORTANT: Keep private.key secret.")
    print("  - Never share it")
    print("  - Never include it in the installer or dist/")
    print("  - Back it up securely (losing it means you can't generate new keys)")
    print("=" * 60)
    print()
    print("Setup complete. You can now generate license keys.")


def generate_key(email, name, days):
    """Generate and print a license key for a customer."""
    _check_cryptography()

    if not os.path.exists(PRIVATE_KEY_PATH):
        print("ERROR: Private key not found.")
        print("Run: py licensing/keygen.py --setup")
        sys.exit(1)

    private_key = _load_private_key()

    exp_date = (date.today() + timedelta(days=days)).isoformat()
    uid = str(uuid.uuid4())[:8].upper()

    payload = {
        "uid": uid,
        "name": name,
        "email": email,
        "exp": exp_date
    }

    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    sig_bytes = private_key.sign(payload_bytes)

    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode().rstrip('=')
    sig_b64 = base64.urlsafe_b64encode(sig_bytes).decode().rstrip('=')

    key = f"OB-{payload_b64}.{sig_b64}"

    print()
    print("=" * 60)
    print(f"  Customer : {name}")
    print(f"  Email    : {email}")
    print(f"  Expires  : {exp_date}  ({days} days from today)")
    print(f"  Key ID   : {uid}")
    print("=" * 60)
    print()
    print(key)
    print()

    return key


def main():
    parser = argparse.ArgumentParser(
        description='Options Backtesting System - License Key Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--setup', action='store_true',
                        help='Generate key pair (run once on your machine)')
    parser.add_argument('--email', type=str, help='Customer email address')
    parser.add_argument('--name', type=str, help='Customer full name')
    parser.add_argument('--days', type=int, default=30,
                        help='License duration in days (default: 30)')

    args = parser.parse_args()

    if args.setup:
        setup()
    elif args.email and args.name:
        generate_key(args.email, args.name, args.days)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  py licensing/keygen.py --setup")
        print("  py licensing/keygen.py --email user@example.com --name \"John Doe\"")
        print("  py licensing/keygen.py --email user@example.com --name \"John Doe\" --days 60")


if __name__ == '__main__':
    main()
