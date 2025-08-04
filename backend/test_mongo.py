import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Load environment variables
load_dotenv()

def test_mongo_connection():
    """Test MongoDB connection with detailed error reporting"""
    
    # Get the MongoDB URI
    mongo_uri = os.getenv("MONGO_URI")
    print(f"Testing connection with URI: {mongo_uri[:50]}...")
    
    if not mongo_uri:
        print("❌ MONGO_URI not found in environment variables")
        return False
    
    try:
        # Test with different connection options
        print("\n🔍 Testing connection options...")
        
        # Option 1: Basic connection
        print("1. Testing basic connection...")
        client1 = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client1.admin.command('ping')
        print("✅ Basic connection successful!")
        client1.close()
        
        # Option 2: With enhanced SSL settings
        print("2. Testing with enhanced SSL settings...")
        client2 = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            ssl=True,
            ssl_cert_reqs='CERT_NONE',
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            tlsInsecure=True,
            directConnection=False,
            retryWrites=True,
            w='majority'
        )
        client2.admin.command('ping')
        print("✅ Enhanced SSL connection successful!")
        client2.close()
        
        # Option 3: Try without SSL (for testing)
        print("3. Testing without SSL (fallback)...")
        try:
            # Remove SSL from URI temporarily
            uri_without_ssl = mongo_uri.replace('mongodb+srv://', 'mongodb://')
            client3 = MongoClient(uri_without_ssl, serverSelectionTimeoutMS=5000)
            client3.admin.command('ping')
            print("✅ Non-SSL connection successful!")
            client3.close()
        except Exception as e:
            print(f"⚠️ Non-SSL connection also failed: {e}")
        
        return True
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ Server selection timeout: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if your IP is whitelisted in MongoDB Atlas")
        print("2. Verify your database user exists and has correct permissions")
        print("3. Check if your MongoDB Atlas cluster is active")
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🧪 MongoDB Connection Test")
    print("=" * 40)
    
    success = test_mongo_connection()
    
    if success:
        print("\n🎉 MongoDB connection test passed!")
    else:
        print("\n💡 Try these steps:")
        print("1. Go to MongoDB Atlas → Network Access → Add IP Address")
        print("2. Go to MongoDB Atlas → Database Access → Check user permissions")
        print("3. Verify your cluster is active")
        print("4. Try resetting your database user password") 