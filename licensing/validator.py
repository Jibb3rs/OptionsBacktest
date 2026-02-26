"""
License Validator - Options Backtesting System
Ships with the application. Uses embedded public key for offline validation.
"""

import os
import json
import base64
from datetime import date, datetime

# Ed25519 public key (DER format, base64 encoded)
# This is set automatically when you run: py licensing/keygen.py --setup
PUBLIC_KEY_B64 = "MCowBQYDK2VwAyEAQTTkX7hmbMQYD8uDbsay23zKLdNmvtI7vDIDC40MpJw="

# Where the license file lives on the user's machine (cross-platform)
from core.paths import user_data_dir as _user_data_dir

def _license_file():
    return str(_user_data_dir() / 'license.key')

# Keep for backward compat — resolved at call time, not import time
LICENSE_FILE = None  # use _license_file() instead

WARNING_DAYS = 7  # show warning banner this many days before expiry


def _get_public_key():
    """Load the embedded Ed25519 public key."""
    from cryptography.hazmat.primitives.serialization import load_der_public_key
    key_bytes = base64.b64decode(PUBLIC_KEY_B64)
    return load_der_public_key(key_bytes)


def _parse_key(key_str):
    """
    Parse a license key string.
    Format: OB-{base64url_payload}.{base64url_signature}
    Returns (payload_bytes, sig_bytes, payload_dict) or (None, None, None) on error.
    """
    key_str = key_str.strip()

    if key_str.startswith("OB-"):
        key_str = key_str[3:]

    try:
        # Split at last dot to separate payload and signature
        dot_idx = key_str.rfind(".")
        if dot_idx == -1:
            return None, None, None

        payload_b64 = key_str[:dot_idx]
        sig_b64 = key_str[dot_idx + 1:]

        # Pad base64url strings to multiple of 4
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
        sig_bytes = base64.urlsafe_b64decode(sig_b64 + "==")
        payload_dict = json.loads(payload_bytes.decode('utf-8'))

        return payload_bytes, sig_bytes, payload_dict
    except Exception:
        return None, None, None


def validate_key(key_str):
    """
    Validate a license key string (does not save it).

    Returns:
        (is_valid: bool, message: str, payload: dict | None)
    """
    payload_bytes, sig_bytes, payload = _parse_key(key_str)

    if payload is None:
        return False, "Invalid key format. Check the key and try again.", None

    # Verify cryptographic signature
    try:
        pub_key = _get_public_key()
        pub_key.verify(sig_bytes, payload_bytes)
    except Exception:
        return False, "License key is not valid.", None

    # Check expiry date
    try:
        exp_date = datetime.strptime(payload['exp'], "%Y-%m-%d").date()
        today = date.today()

        if today > exp_date:
            days_ago = (today - exp_date).days
            return False, f"License expired {days_ago} day(s) ago. Please renew your subscription.", payload

        days_left = (exp_date - today).days
        name = payload.get('name', '')
        msg = f"Licensed to {name}. {days_left} day(s) remaining." if name else f"{days_left} day(s) remaining."
        return True, msg, payload

    except (KeyError, ValueError):
        return False, "License key is malformed.", None


def load_stored_license():
    """
    Load and validate the license saved on this machine.

    Returns:
        (is_valid: bool, message: str, payload: dict | None)
    """
    lf = _license_file()
    if not os.path.exists(lf):
        return False, "No license found.", None

    try:
        with open(lf, 'r') as f:
            key_str = f.read().strip()
        return validate_key(key_str)
    except Exception:
        return False, "Could not read license file.", None


def is_expiring_soon():
    """Returns (True, days_left) if license is valid but within WARNING_DAYS, else (False, -1)."""
    is_valid, _, payload = load_stored_license()
    if not is_valid or payload is None:
        return False, -1
    try:
        exp_date = datetime.strptime(payload['exp'], "%Y-%m-%d").date()
        days_left = (exp_date - date.today()).days
        return days_left <= WARNING_DAYS, days_left
    except Exception:
        return False, -1


def save_license(key_str):
    """Save a validated license key to the user's data folder."""
    lf = _license_file()
    os.makedirs(os.path.dirname(lf), exist_ok=True)
    with open(lf, 'w') as f:
        f.write(key_str.strip())


def get_license_info():
    """
    Returns a short status string for display in the UI (e.g. status bar).
    Returns None if no valid license.
    """
    is_valid, message, _ = load_stored_license()
    return message if is_valid else None
