import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import ssl

# Load environment variables
load_dotenv()

def create_mongo_client():
    """Create MongoDB client with multiple fallback options"""
    
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI not found in environment variables")
    
    # Method 1: Try with minimal SSL settings
    try:
        print("🔍 Trying Method 1: Minimal SSL settings...")
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        client.admin.command('ping')
        print("✅ Method 1 successful!")
        return client
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Try with explicit SSL settings
    try:
        print("🔍 Trying Method 2: Explicit SSL settings...")
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            ssl=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        client.admin.command('ping')
        print("✅ Method 2 successful!")
        return client
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Try with insecure TLS
    try:
        print("🔍 Trying Method 3: Insecure TLS...")
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            ssl=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            tlsInsecure=True
        )
        client.admin.command('ping')
        print("✅ Method 3 successful!")
        return client
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    # Method 4: Try without SSL (if URI allows)
    try:
        print("🔍 Trying Method 4: Without SSL...")
        uri_without_ssl = mongo_uri.replace('mongodb+srv://', 'mongodb://')
        client = MongoClient(
            uri_without_ssl,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        client.admin.command('ping')
        print("✅ Method 4 successful!")
        return client
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
    
    # If all methods fail
    raise ConnectionFailure("All MongoDB connection methods failed")

def test_robust_connection():
    """Test the robust connection method"""
    print("🧪 Testing Robust MongoDB Connection")
    print("=" * 50)
    
    try:
        client = create_mongo_client()
        print("\n🎉 MongoDB connection successful!")
        
        # Test database operations
        db = client["meeting_scheduler"]
        collections = db.list_collection_names()
        print(f"📊 Available collections: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ All connection methods failed: {e}")
        print("\n💡 Troubleshooting suggestions:")
        print("1. Check your internet connection")
        print("2. Verify MongoDB Atlas cluster is active")
        print("3. Check if your IP is whitelisted")
        print("4. Try updating Python SSL libraries")
        print("5. Consider using a different MongoDB URI format")
        return False

if __name__ == "__main__":
    test_robust_connection() 