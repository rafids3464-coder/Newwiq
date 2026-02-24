"""
WASTE IQ – Firestore Seed Script (LOCAL VERSION)
Run once to populate demo data.
Usage: python seed_firestore.py
"""

import uuid
from datetime import datetime, timezone, timedelta

import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth

# ─────────────────────────────────────────────────────────────
# Initialize Firebase using local JSON key
# ─────────────────────────────────────────────────────────────

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ─────────────────────────────────────────────────────────────
# Demo Users
# ─────────────────────────────────────────────────────────────

DEMO_USERS = [
    {"email": "household@wasteiq.demo", "password": "demo1234", "name": "Aisha Kumar",   "role": "household", "ward_id": "WARD_01"},
    {"email": "municipal@wasteiq.demo", "password": "demo1234", "name": "Ravi Nair",    "role": "municipal", "ward_id": "WARD_01"},
    {"email": "driver@wasteiq.demo",    "password": "demo1234", "name": "Suresh Thomas","role": "driver",    "ward_id": "WARD_01"},
    {"email": "admin@wasteiq.demo",     "password": "demo1234", "name": "Priya Admin",  "role": "admin",     "ward_id": None},
]

# ─────────────────────────────────────────────────────────────
# Ward Data
# ─────────────────────────────────────────────────────────────

WARDS = [
    {"ward_id": "WARD_01", "name": "Mananchira Ward", "city": "Kozhikode", "population": 12000},
    {"ward_id": "WARD_02", "name": "Nadakkavu Ward",  "city": "Kozhikode", "population": 9500},
]

# ─────────────────────────────────────────────────────────────
# Bin Data
# ─────────────────────────────────────────────────────────────

BINS_DATA = [
    {"ward_id": "WARD_01", "lat": 11.2588, "lng": 75.7804, "address": "Mananchira Square", "fill": 85.0},
    {"ward_id": "WARD_01", "lat": 11.2612, "lng": 75.7812, "address": "SM Street Junction", "fill": 60.0},
    {"ward_id": "WARD_02", "lat": 11.2490, "lng": 75.7720, "address": "Nadakkavu Junction", "fill": 72.0},
]

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def create_user_if_not_exists(email, password, name, role, ward_id):
    try:
        user = firebase_auth.get_user_by_email(email)
        print(f"✓ User exists: {email}")
        uid = user.uid
    except firebase_auth.UserNotFoundError:
        user = firebase_auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        uid = user.uid
        print(f"+ Created user: {email}")

    firebase_auth.set_custom_user_claims(uid, {"role": role})

    db.collection("users").document(uid).set({
        "uid": uid,
        "email": email,
        "name": name,
        "role": role,
        "ward_id": ward_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }, merge=True)

    db.collection("gamification").document(uid).set({
        "uid": uid,
        "total_points": 100,
        "weekly_points": 30,
        "level": "Starter",
    }, merge=True)

    return uid


def seed_wards():
    print("\nSeeding wards...")
    for w in WARDS:
        db.collection("wards").document(w["ward_id"]).set(w)
        print(f"+ Ward {w['ward_id']}")


def seed_bins(driver_uid):
    print("\nSeeding bins...")
    for b in BINS_DATA:
        bid = str(uuid.uuid4())
        db.collection("bins").document(bid).set({
            "bin_id": bid,
            "ward_id": b["ward_id"],
            "location": {
                "lat": b["lat"],
                "lng": b["lng"],
                "address": b["address"]
            },
            "fill_level": b["fill"],
            "status": "overflow" if b["fill"] >= 80 else "active",
            "assigned_driver": driver_uid,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        print(f"+ Bin at {b['address']}")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🌱 Seeding Waste IQ Firestore...\n")

    uids = {}

    print("Creating users...")
    for user in DEMO_USERS:
        uid = create_user_if_not_exists(
            user["email"],
            user["password"],
            user["name"],
            user["role"],
            user["ward_id"]
        )
        uids[user["role"]] = uid

    seed_wards()
    seed_bins(uids.get("driver"))

    print("\n✅ Seeding complete!\n")
    print("Login credentials:")
    print("Household : household@wasteiq.demo / demo1234")
    print("Municipal : municipal@wasteiq.demo / demo1234")
    print("Driver    : driver@wasteiq.demo / demo1234")
    print("Admin     : admin@wasteiq.demo / demo1234")