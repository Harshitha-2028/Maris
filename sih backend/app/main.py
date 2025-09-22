"""
BlueCarbon API Server - Integrated with Blockchain + MongoDB
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from web3 import Web3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import blockchain + db
from app.blockchain import bluecarbon_client
from app.database import db_client

# Create FastAPI app
app = FastAPI(
    title="BlueCarbon API - South India Carbon Registry",
    description="API for managing carbon credits from South Indian projects",
    version="1.0.0",
)


# =======================
#   AUTH (very simple)
# =======================
security = HTTPBearer()


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "admin-token-123":
        raise HTTPException(status_code=401, detail="Invalid admin token")
    return credentials.credentials


def verify_minter_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "minter-token-456":
        raise HTTPException(status_code=401, detail="Invalid minter token")
    return credentials.credentials


# =======================
#   Pydantic Models
# =======================
class RegisterProjectRequest(BaseModel):
    project_id: str
    metadata_cid: str
    name: str
    description: str
    project_type: str
    location: str

    @validator("project_id")
    def project_id_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("project_id cannot be empty")
        return v.strip()


class IssueCreditsRequest(BaseModel):
    to_address: str
    project_id: str
    amount: int
    proof_cid: str

    @validator("to_address")
    def validate_address(cls, v):
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)

    @validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class RetireCreditsRequest(BaseModel):
    project_id: str
    amount: int

    @validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


# =======================
#   ROUTES
# =======================
@app.get("/")
async def root():
    total_projects = db_client.projects.count_documents({})
    total_credits = sum(p["balances"]["total_issued"] for p in db_client.get_projects())

    return {
        "message": "🌿 BlueCarbon API - South India Carbon Registry",
        "version": "1.0.0",
        "status": "ready",
        "projects": total_projects,
        "total_credits_issued": total_credits,
        "network": "Celo Alfajores",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "database": db_client.db.name,
        "blockchain": {
            "connected": bluecarbon_client.w3.is_connected(),
            "contract": bluecarbon_client.contract_address,
        },
        "projects_count": db_client.projects.count_documents({}),
    }


@app.get("/projects")
async def list_projects(limit: int = 10, skip: int = 0):
    """List all projects from DB"""
    projects = db_client.get_projects(limit=limit, skip=skip)
    return projects


@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    project = db_client.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return project


@app.post("/projects/register")
async def register_project(
    request: RegisterProjectRequest, admin_token: str = Depends(verify_admin_token)
):
    """Register a new carbon project (Admin only)"""
    if db_client.get_project(request.project_id):
        raise HTTPException(
            status_code=400, detail=f"Project '{request.project_id}' already exists"
        )

    tx = bluecarbon_client.register_project(
        request.project_id, request.metadata_cid, os.getenv("ADMIN_PRIVATE_KEY")
    )

    project_data = {
        "project_id": request.project_id,
        "name": request.name,
        "description": request.description,
        "project_type": request.project_type,
        "location": request.location,
        "status": "active",
        "balances": {"total_issued": 0, "total_retired": 0, "circulating": 0},
    }
    db_client.store_project(project_data)
    db_client.log_transaction("project_registration", tx["tx_hash"], project_data)

    return {
        "success": True,
        "tx": tx,
        "message": f"Project '{request.name}' registered successfully!",
    }


@app.post("/credits/issue")
async def issue_credits(
    request: IssueCreditsRequest, minter_token: str = Depends(verify_minter_token)
):
    """Issue carbon credits (Minter only)"""
    project = db_client.get_project(request.project_id)
    if not project:
        raise HTTPException(
            status_code=404, detail=f"Project '{request.project_id}' not found"
        )

    tx = bluecarbon_client.issue_credits(
        request.to_address,
        request.project_id,
        request.amount,
        request.proof_cid,
        os.getenv("MINTER_PRIVATE_KEY"),
    )

    db_client.update_project_balance(request.project_id, request.amount, operation="issue")
    db_client.log_transaction("credit_issuance", tx["tx_hash"], request.dict())

    return {
        "success": True,
        "tx": tx,
        "message": f"{request.amount} credits issued successfully!",
    }


@app.post("/credits/retire")
async def retire_credits(request: RetireCreditsRequest):
    """Retire carbon credits"""
    project = db_client.get_project(request.project_id)
    if not project:
        raise HTTPException(
            status_code=404, detail=f"Project '{request.project_id}' not found"
        )

    if project["balances"]["circulating"] < request.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient credits. Available: {project['balances']['circulating']}",
        )

    token_id = bluecarbon_client.get_project_token_id(request.project_id)
    tx = bluecarbon_client.retire_credits(
        token_id, request.amount, os.getenv("USER_PRIVATE_KEY")
    )

    db_client.update_project_balance(request.project_id, request.amount, operation="retire")
    db_client.log_transaction("credit_retirement", tx["tx_hash"], request.dict())

    return {
        "success": True,
        "tx": tx,
        "message": f"{request.amount} credits retired successfully!",
    }


@app.get("/projects/{project_id}/history")
async def get_project_history(project_id: str, limit: int = 50):
    """Get project history"""
    return db_client.get_transaction_history(project_id, limit)


@app.get("/balance/{address}/{project_id}")
async def get_balance(address: str, project_id: str):
    """Get balance of an address for a project"""
    if not Web3.is_address(address):
        raise HTTPException(status_code=400, detail="Invalid address")

    token_id = bluecarbon_client.get_project_token_id(project_id)
    balance = bluecarbon_client.get_balance_of(address, token_id)

    return {
        "address": Web3.to_checksum_address(address),
        "project_id": project_id,
        "token_id": token_id,
        "balance": balance,
    }


# Startup
if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting BlueCarbon API...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
