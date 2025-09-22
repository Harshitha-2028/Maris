from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Try without specific database first
MONGO_URI = os.getenv('MONGO_URI').rstrip('/')  # Remove trailing / if any
if not '/bluecarbon' in MONGO_URI:
    MONGO_URI += '/bluecarbon'  # Add if missing

print("🔍 Listing All Databases in Your Cluster")
print("=" * 50)

try:
    # Connect without specifying database
    base_uri = os.getenv('MONGO_URI').split('/')[0:3]
    base_uri = '/'.join(base_uri) + '/?retryWrites=true&w=majority'
    client = MongoClient(base_uri)
    
    # List ALL databases in the cluster
    databases = client.list_database_names()
    print("📁 All databases in your cluster:")
    for db in databases:
        print(f"   • {db}")
    
    # Show collections in each
    for db_name in databases:
        db = client[db_name]
        collections = db.list_collection_names()
        if collections:
            print(f"     └─ Collections in '{db_name}': {collections}")
        else:
            print(f"     └─ '{db_name}' is empty")
    
    print(f"\n✅ Connection successful!")
    print(f"📊 Total databases: {len(databases)}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    
finally:
    try:
        client.close()
    except:
        pass

