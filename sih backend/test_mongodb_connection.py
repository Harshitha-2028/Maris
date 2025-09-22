from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

print("🔗 Testing MongoDB Atlas Connection...")
print("=" * 50)

# Get connection string
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    print("❌ MONGO_URI not found!")
    exit(1)

print(f"🔑 Using connection: {mongo_uri[:40]}...")

try:
    # Create client with timeout
    client = MongoClient(
        mongo_uri, 
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000
    )
    
    # Test 1: Ping the server
    print("\n1️⃣ Testing ping...")
    ping_result = client.admin.command('ping')
    print(f"✅ Ping successful: {ping_result}")
    
    # Test 2: List databases
    print("\n2️⃣ Listing databases...")
    databases = client.list_database_names()
    print(f"📁 Available databases: {databases}")
    
    # Test 3: Access bluecarbon database
    print("\n3️⃣ Accessing bluecarbon database...")
    db = client['bluecarbon']
    
    # List collections
    collections = db.list_collection_names()
    print(f"📂 Collections: {collections if collections else 'None (empty database)'}")
    
    # Test 4: Test write operation
    print("\n4️⃣ Testing write operation...")
    test_collection = db['test_connection']
    test_doc = {
        "message": "Connection test successful!",
        "timestamp": datetime.utcnow(),
        "environment": "development"
    }
    
    insert_result = test_collection.insert_one(test_doc)
    print(f"✅ Insert successful! Document ID: {insert_result.inserted_id}")
    
    # Test 5: Test read operation
    print("\n5️⃣ Testing read operation...")
    retrieved_doc = test_collection.find_one({"_id": insert_result.inserted_id})
    print(f"✅ Read successful! Retrieved: {retrieved_doc['message']}")
    
    # Clean up test document
    test_collection.delete_one({"_id": insert_result.inserted_id})
    print("🧹 Cleaned up test document")
    
    print("\n" + "=" * 50)
    print("🎉 MongoDB connection is working perfectly!")
    print("✅ All tests passed - ready to insert sample data!")
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # Provide specific troubleshooting
    if "authentication failed" in str(e).lower():
        print("\n🔧 AUTHENTICATION ISSUE:")
        print("   • Check username/password in MONGO_URI")
        print("   • URL-encode special characters in password")
        print("   • Verify user exists in Atlas → Database Access")
    elif "server selection timeout" in str(e).lower():
        print("\n🔧 NETWORK ISSUE:")
        print("   • Check Atlas → Network Access → Add your IP")
        print("   • Try adding ?directConnection=true to MONGO_URI")
    elif "connection refused" in str(e).lower():
        print("\n🔧 CLUSTER ISSUE:")
        print("   • Check if your Atlas cluster is paused")
        print("   • Resume cluster in Atlas dashboard")
    
finally:
    try:
        client.close()
        print("🔌 Connection closed")
    except:
        pass