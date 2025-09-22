"""
Temporary mock data to replace MongoDB
Swap this out when database is ready
"""

from datetime import datetime
from typing import Dict, List, Any
import uuid

# Mock projects data (South India projects)
PROJECTS = {
    "KOD001": {
        "project_id": "KOD001",
        "token_id": 1,
        "name": "Kodagu Reforestation Initiative",
        "description": "Large-scale reforestation project restoring degraded coffee plantation lands in Kodagu district...",
        "project_type": "reforestation",
        "location": {
            "country": "IN",
            "region": "Karnataka",
            "coordinates": [12.3350, 75.5650],
            "address": "Madikeri Taluk, Kodagu District, Karnataka 571201, India"
        },
        "status": "active",
        "balances": {
            "total_issued": 8500,
            "total_retired": 1200,
            "circulating": 7300,
            "last_updated": datetime.now()
        },
        "created_at": datetime(2024, 9, 20, 8, 15),
        "updated_at": datetime.now()
    },
    "WAY001": {
        "project_id": "WAY001",
        "token_id": 2,
        "name": "Wayanad Micro-Hydro Renewable Energy Project",
        "description": "Installation of 15 micro-hydro power plants across tribal hamlets in Wayanad district...",
        "project_type": "renewable_energy",
        "location": {
            "country": "IN",
            "region": "Kerala",
            "coordinates": [11.6800, 76.0800],
            "address": "Sulthan Bathery Block, Wayanad District, Kerala 673591, India"
        },
        "status": "active",
        "balances": {
            "total_issued": 3200,
            "total_retired": 450,
            "circulating": 2750,
            "last_updated": datetime.now()
        },
        "created_at": datetime(2024, 9, 20, 9, 45),
        "updated_at": datetime.now()
    }
}

# Mock transactions
TRANSACTIONS = [
    {
        "tx_hash": "0x8f5c2a1b9e4d7c6f3a8e2d5b1c4f7a9e6d3b8c5f2a1e4d7c6f3a8e2d5b1c4f7a",
        "type": "project_registration",
        "details": {"project_id": "KOD001", "token_id": 1},
        "status": "confirmed",
        "timestamp": datetime(2024, 9, 20, 8, 15),
        "created_at": datetime(2024, 9, 20, 8, 15)
    }
]

# Mock users
USERS = {
    "0x742d35Cc6634C0532925a3b8D4A9598e6e0bC7a4": {
        "user_id": "USR001",
        "wallet_address": "0x742d35Cc6634C0532925a3b8D4A9598e6e0bC7a4",
        "email": "lakshmi.rao@kodagugreen.org",
        "profile": {
            "name": "Dr. Lakshmi N. Rao",
            "organization": "Kodagu Forest Conservation Society",
            "role": "project_developer"
        },
        "permissions": {
            "projects": ["KOD001"],
            "can_register": True,
            "can_mint": False
        }
    }
}

class MockDatabase:
    """Temporary mock database - replace with real MongoDB later"""
    
    def __init__(self):
        self.projects = PROJECTS
        self.transactions = TRANSACTIONS
        self.users = USERS
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project by ID"""
        return self.projects.get(project_id)
    
    def get_projects(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all projects with pagination"""
        project_list = list(self.projects.values())
        return project_list[skip:skip + limit]
    
    def get_transaction_history(self, project_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction history"""
        if project_id:
            return [tx for tx in self.transactions if tx['details'].get('project_id') == project_id]
        return self.transactions[-limit:]
    
    def store_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock project storage (in real app, save to MongoDB)"""
        # Generate mock token_id
        project_data['token_id'] = len(self.projects) + 1
        project_data['created_at'] = datetime.now()
        project_data['updated_at'] = datetime.now()
        
        # Add to mock storage
        project_id = project_data['project_id']
        self.projects[project_id] = project_data
        
        return project_data
    
    def log_transaction(self, tx_type: str, tx_hash: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Mock transaction logging"""
        tx_doc = {
            'tx_hash': tx_hash,
            'type': tx_type,
            'details': details,
            'status': 'confirmed',
            'timestamp': datetime.now(),
            'created_at': datetime.now()
        }
        self.transactions.append(tx_doc)
        return tx_doc
    
    def update_project_balance(self, project_id: str, new_balance: int):
        """Mock balance update"""
        if project_id in self.projects:
            project = self.projects[project_id]
            project['balances']['circulating'] += new_balance
            project['updated_at'] = datetime.now()

# Global mock database instance
mock_db = MockDatabase()