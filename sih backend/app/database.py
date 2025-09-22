"""
BlueCarbon Database Layer - MongoDB Connection
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

load_dotenv()


class BlueCarbonDatabase:
    """MongoDB connection for BlueCarbon API"""

    def __init__(self):
        # Connect to MongoDB
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client["bluecarbon"]  # Your database name

        # Collections
        self.projects = self.db["projects"]
        self.transactions = self.db["transactions"]
        self.users = self.db["users"]

        # Test connection
        try:
            self.client.admin.command("ping")
            print(f"✅ Connected to MongoDB '{self.db.name}' database")
            print(f"   📊 Projects: {self.projects.count_documents({})}")
            print(f"   💸 Transactions: {self.transactions.count_documents({})}")
            print(f"   👥 Users: {self.users.count_documents({})}")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise

    # ----------------- PROJECTS -----------------
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        return self.projects.find_one({"project_id": project_id})

    def get_projects(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Get list of projects with pagination"""
        pipeline = [
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
        ]
        return list(self.projects.aggregate(pipeline))

    def store_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store new project"""
        try:
            # Ensure required fields
            project_data["created_at"] = datetime.now(timezone.utc)
            project_data["updated_at"] = datetime.now(timezone.utc)
            if "status" not in project_data:
                project_data["status"] = "active"
            if "balances" not in project_data:
                project_data["balances"] = {
                    "total_issued": 0,
                    "total_retired": 0,
                    "circulating": 0,
                    "last_updated": project_data["created_at"],
                }

            result = self.projects.insert_one(project_data)
            project_data["_id"] = str(result.inserted_id)
            print(f"✅ Project stored: {project_data['project_id']}")
            return project_data
        except Exception as e:
            print(
                f"❌ Failed to store project {project_data.get('project_id', 'unknown')}: {e}"
            )
            raise

    def update_project_balance(
        self, project_id: str, amount: int, operation: str = "issue"
    ):
        """Update project balances"""
        try:
            inc_updates = {}
            if operation == "issue":
                inc_updates = {
                    "balances.total_issued": amount,
                    "balances.circulating": amount,
                }
            elif operation == "retire":
                inc_updates = {
                    "balances.total_retired": amount,
                    "balances.circulating": -amount,
                }
            else:
                raise ValueError(f"Unknown operation: {operation}")

            result = self.projects.update_one(
                {"project_id": project_id},
                {
                    "$inc": inc_updates,
                    "$set": {
                        "updated_at": datetime.now(timezone.utc),
                        "balances.last_updated": datetime.now(timezone.utc),
                    },
                },
            )

            if result.modified_count > 0:
                print(
                    f"💰 Updated balance for {project_id}: "
                    f"{'+' if operation == 'issue' else '-'}{amount}"
                )
            else:
                print(f"⚠️  No project found: {project_id}")

        except Exception as e:
            print(f"❌ Failed to update balance for {project_id}: {e}")
            raise

    # ----------------- TRANSACTIONS -----------------
    def log_transaction(
        self, tx_type: str, tx_hash: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log blockchain transaction"""
        try:
            project_id = details.get("project_id")
            doc = {
                "type": tx_type,
                "tx_hash": tx_hash,
                "project_id": project_id,  # 🔑 top-level
                "details": details,
                "status": "confirmed",
                "timestamp": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
            }

            result = self.transactions.insert_one(doc)
            doc["_id"] = str(result.inserted_id)
            print(f"📝 Transaction logged: {tx_hash[:16]}... for project {project_id}")
            return doc
        except Exception as e:
            print(f"❌ Failed to log transaction: {e}")
            raise

    def get_transaction_history(
        self, project_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get transaction history for a project or all"""
        query = {} if not project_id else {"project_id": project_id}

        pipeline = [
            {"$match": query},
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
        ]

        return list(self.transactions.aggregate(pipeline))

    # ----------------- USERS -----------------
    def get_user_by_wallet(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Get user by wallet address"""
        return self.users.find_one({"wallet_address": wallet_address})

    def get_user_balance(self, wallet_address: str, project_id: str) -> int:
        """Get user's balance for specific project"""
        user = self.get_user_by_wallet(wallet_address)
        if not user or "balances" not in user:
            return 0

        for balance in user.get("balances", []):
            if balance.get("project_id") == project_id:
                return balance.get("balance", 0)
        return 0


# Global database instance
db_client = BlueCarbonDatabase()
