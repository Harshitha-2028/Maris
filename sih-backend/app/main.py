"""
BlueCarbon API Server - Integrated with Blockchain + MongoDB
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, timezone
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
    projects = db_client.get_projects()
    total_projects = len(projects)
    total_credits = sum(p.get("balances", {}).get("total_issued", 0) for p in projects)

    return {
        "message": "🌿 BlueCarbon API - South India Carbon Registry",
        "version": "1.0.0",
        "status": "ready",
        "projects": total_projects,
        "total_credits_issued": total_credits,
        "network": "Celo Alfajores",
        "contract_in_use": bluecarbon_client.contract_address,
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
    return db_client.get_projects(limit=limit, skip=skip)

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
        raise HTTPException(status_code=400, detail=f"Project '{request.project_id}' already exists")

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

    return {"success": True, "tx": tx, "message": f"Project '{request.name}' registered successfully!"}

@app.post("/credits/issue")
async def issue_credits(
    request: IssueCreditsRequest, minter_token: str = Depends(verify_minter_token)
):
    """Issue carbon credits (Minter only)"""
    project = db_client.get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{request.project_id}' not found")

    tx = bluecarbon_client.issue_credits(
        request.to_address,
        request.project_id,
        request.amount,
        request.proof_cid,
        os.getenv("MINTER_PRIVATE_KEY"),
    )

    db_client.update_project_balance(request.project_id, request.amount, operation="issue")
    db_client.log_transaction("credit_issuance", tx["tx_hash"], request.dict())

    return {"success": True, "tx": tx, "message": f"{request.amount} credits issued successfully!"}

@app.post("/credits/retire")
async def retire_credits(request: RetireCreditsRequest):
    """Retire carbon credits"""
    project = db_client.get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{request.project_id}' not found")

    if project.get("balances", {}).get("circulating", 0) < request.amount:
        raise HTTPException(status_code=400, detail=f"Insufficient credits. Available: {project.get('balances', {}).get('circulating', 0)}")

    token_id = bluecarbon_client.get_project_token_id(request.project_id)
    tx = bluecarbon_client.retire_credits(token_id, request.amount, os.getenv("USER_PRIVATE_KEY"))

    db_client.update_project_balance(request.project_id, request.amount, operation="retire")
    db_client.log_transaction("credit_retirement", tx["tx_hash"], request.dict())

    return {"success": True, "tx": tx, "message": f"{request.amount} credits retired successfully!"}

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

    return {"address": Web3.to_checksum_address(address), "project_id": project_id, "token_id": token_id, "balance": balance}

# =======================
#   REGISTRY ROUTES
# =======================
@app.get("/registry/{name}")
async def get_registry_entry(name: str):
    """Fetch the contract address for a given name from the registry"""
    try:
        addr = bluecarbon_client.registry.functions.getContract(name).call()
        if addr == "0x0000000000000000000000000000000000000000":
            raise HTTPException(status_code=404, detail=f"No contract found for '{name}'")
        return {"name": name, "address": addr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/registry/update")
async def update_registry_entry(
    name: str, new_address: str, admin_token: str = Depends(verify_admin_token)
):
    """Update the registry with a new contract address (Admin only)"""
    try:
        acct = bluecarbon_client.w3.eth.account.from_key(os.getenv("ADMIN_PRIVATE_KEY"))
        nonce = bluecarbon_client.w3.eth.get_transaction_count(acct.address)

        txn = bluecarbon_client.registry.functions.updateContract(name, new_address).build_transaction(
            {
                "from": acct.address,
                "nonce": nonce,
                "chainId": int(os.getenv("CHAIN_ID")),
                "gas": 300000,
                "gasPrice": bluecarbon_client.w3.eth.gas_price,
            }
        )

        result = bluecarbon_client._send_transaction(txn, os.getenv("ADMIN_PRIVATE_KEY"))
        return {"success": True, "tx": result, "message": f"Registry updated: {name} → {new_address}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =======================
#   ANALYTICS ROUTES
# =======================
@app.get("/analytics/plots-overview")
async def plots_overview():
    total_plots = db_client.plots.count_documents({})
    plots_by_type = list(db_client.plots.aggregate([
        {"$group": {"_id": "$Project_Type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    return {"total_plots": total_plots, "by_type": plots_by_type}

@app.get("/analytics/ndvi-by-project")
async def ndvi_by_project():
    pipeline = [
        {"$group": {"_id": "$Project_Type", "avgNDVI": {"$avg": "$NDVI"}}},
        {"$sort": {"avgNDVI": -1}}
    ]
    return {"ndvi": list(db_client.plots.aggregate(pipeline))}

@app.get("/analytics/biomass-trend")
async def biomass_trend():
    pipeline = [
        {"$group": {
            "_id": "$Monitoring_Year",
            "avgAbove": {"$avg": "$Biomass_above_kg"},
            "avgBelow": {"$avg": "$Biomass_below_kg"},
            "total": {"$sum": {"$add": ["$Biomass_above_kg", "$Biomass_below_kg"]}}
        }},
        {"$sort": {"_id": 1}}
    ]
    return {"biomass": list(db_client.plots.aggregate(pipeline))}

@app.get("/analytics/fluxes")
async def fluxes():
    co2 = list(db_client.plots.aggregate([
        {"$group": {"_id": "$Monitoring_Year", "avgCO2": {"$avg": "$CO2_Flux_mg_m2_day"}}},
        {"$sort": {"_id": 1}}
    ]))
    ch4 = list(db_client.plots.aggregate([
        {"$group": {"_id": "$Monitoring_Year", "avgCH4": {"$avg": "$CH4_Flux_mg_m2_day"}}},
        {"$sort": {"_id": 1}}
    ]))
    return {"co2": co2, "ch4": ch4}

@app.get("/analytics/ndvi-monthly")
async def ndvi_monthly():
    pipeline = [
        {"$addFields": {"month": {"$month": "$Timestamp"}, "year": {"$year": "$Timestamp"}}},
        {"$group": {"_id": {"year": "$year", "month": "$month"}, "avgNDVI": {"$avg": "$NDVI"}}},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    return {"trend": list(db_client.plots.aggregate(pipeline))}

# Startup
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting BlueCarbon API...")
    print(f"🔗 Contract in use from registry: {bluecarbon_client.contract_address}")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
