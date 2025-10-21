# census_app/backfill_holders.py
from sqlalchemy import text
from census_app.db import engine

def backfill_holders():
    with engine.begin() as conn:
        # Get all holder users
        users = conn.execute(text("SELECT id, username FROM users WHERE role = 'Holder'")).mappings().all()

        for user in users:
            # Check if holder already exists for this user
            existing = conn.execute(
                text("SELECT id FROM holders WHERE owner_id = :uid"),
                {"uid": user["id"]}
            ).fetchone()

            if not existing:
                # Create holder record
                conn.execute(text("""
                    INSERT INTO holders (name, location, owner_id, status, submitted_at)
                    VALUES (:name, '', :owner_id, 'active', NOW())
                """), {
                    "name": user["username"],
                    "owner_id": user["id"]
                })
                print(f"✅ Created holder for user {user['username']} (id={user['id']})")
            else:
                print(f"➡️ Holder already exists for {user['username']} (id={user['id']})")

if __name__ == "__main__":
    backfill_holders()
    print("🎉 Backfill complete!")
