#!/usr/bin/env python3
"""
Setup script to create initial API key and test the application.
"""
import sys
import secrets
from datetime import datetime

# Add project root to path
sys.path.insert(0, '/Users/artemijvasilev/SateliteTracker2.0')

from src.database import SessionLocal, engine
from src.models import Base, APIKey
from sqlalchemy.orm import Session


def create_initial_api_key(name: str = "Initial Admin Key") -> str:
    """Create initial API key for testing."""
    db: Session = SessionLocal()

    try:
        # Check if API keys table exists and has any keys
        try:
            existing_keys = db.query(APIKey).all()
            if existing_keys:
                print(f"⚠️  Found {len(existing_keys)} existing API key(s)")
                for key in existing_keys:
                    print(f"   - {key.name}: ****{key.key[-4:]}")
                choice = input("\nCreate new key anyway? (y/n): ")
                if choice.lower() != 'y':
                    print("Skipping API key creation")
                    return None
        except Exception as e:
            print(f"Error checking existing keys: {e}")

        # Generate new API key
        new_key_str = f"stk_{secrets.token_urlsafe(32)}"

        new_key = APIKey(
            key=new_key_str,
            name=name,
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(new_key)
        db.commit()
        db.refresh(new_key)

        print(f"\n✅ API Key Created Successfully!")
        print(f"   ID: {new_key.id}")
        print(f"   Name: {new_key.name}")
        print(f"   Key: {new_key.key}")
        print(f"\n⚠️  Save this key securely - it won't be shown again!")
        print(f"   Use it in the X-API-Key header when making requests")

        return new_key.key

    except Exception as e:
        print(f"❌ Error creating API key: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def setup_database():
    """Create database tables."""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")


def main():
    """Main setup function."""
    print("=" * 60)
    print("SatelliteTracker API Setup")
    print("=" * 60)

    # Create database tables
    setup_database()

    # Create initial API key
    print("\nCreating initial API key...")
    api_key = create_initial_api_key()

    if api_key:
        print("\n" + "=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print("\nYou can now start the server with:")
        print("  uvicorn main:app --reload")
        print("\nOr run:")
        print("  python main.py")
        print("\nThen visit http://localhost:8000/docs for API documentation")
        print("\nExample request with your API key:")
        print(f"  curl -H 'X-API-Key: {api_key}' http://localhost:8000/api/v1/satellites/")
    else:
        print("\n⚠️  No API key created. You'll need one to use protected endpoints")


if __name__ == "__main__":
    main()
