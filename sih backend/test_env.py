import os
from dotenv import load_dotenv
import pathlib

print("🔍 Enhanced .env Configuration Test...")
print("=" * 60)

# Step 1: Check current working directory
current_dir = os.getcwd()
print(f"📍 Current working directory: {current_dir}")

# Step 2: Check if .env file exists
env_path = pathlib.Path(".env")
if env_path.exists():
    print(f"✅ .env file found at: {env_path.absolute()}")
    
    # Check file size
    file_size = env_path.stat().st_size
    print(f"📄 File size: {file_size} bytes")
    
    if file_size > 100:  # Reasonable size for config
        print("✅ .env file has content")
    else:
        print("⚠️  .env file is very small - might be empty")
        
    # Show first few lines
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()[:5]  # First 5 lines
            print("📝 First 5 lines of .env:")
            for i, line in enumerate(lines, 1):
                # Hide potential passwords
                if ':' in line and ('password' in line.lower() or '@' in line):
                    line = line.split(':')[0] + ": [HIDDEN]\n"
                print(f"   {i}: {line.strip()}")
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        
else:
    print(f"❌ .env file NOT found in: {env_path.absolute()}")
    print("💡 Create .env file in your project root (same level as test_env.py)")

print("\n" + "=" * 60)

# Step 3: Try to load environment variables
print("🔄 Loading environment variables...")
load_dotenv()

print("\n📋 Environment Variables Check:")
print("-" * 40)

variables = [
    "MONGO_URI", "RPC_URL", "CHAIN_ID", "CONTRACT_ADDRESS",
    "SECRET_KEY", "ADMIN_PRIVATE_KEY", "MINTER_PRIVATE_KEY"
]

all_loaded = True
for var in variables:
    value = os.getenv(var)
    if value:
        # Hide sensitive values
        display = f"{value[:20]}..." if len(value) > 20 else value
        status = "✅ Loaded"
    else:
        display = "NOT SET"
        status = "❌ Missing"
        all_loaded = False
    
    print(f"{var:<20} | {display:<30} | {status}")

# Step 4: Special MongoDB URI check
mongo_uri = os.getenv("MONGO_URI")
if mongo_uri:
    if "mongodb+srv://" in mongo_uri:
        print(f"\n✅ MongoDB URI format: Valid SRV connection")
    else:
        print(f"\n⚠️  MongoDB URI format: Check connection string")
else:
    print(f"\n❌ MongoDB URI: Not configured")

# Step 5: Check if python-dotenv is installed
try:
    from dotenv import load_dotenv
    print(f"\n✅ python-dotenv package: Installed")
except ImportError:
    print(f"\n❌ python-dotenv package: NOT INSTALLED")
    print("💡 Run: pip install python-dotenv")

print("\n" + "=" * 60)
if all_loaded:
    print("🎉 All environment variables loaded successfully!")
else:
    print("⚠️  Some environment variables are missing - check .env file")