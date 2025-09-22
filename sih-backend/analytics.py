# analytics.py
from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from bson.json_util import dumps
import os
import json

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# DB Connection
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "bluecarbon")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# -----------------------------
# 1. Plots overview
# -----------------------------
@router.get("/plots-overview")
def plots_overview():
    total_plots = db.plots.count_documents({})
    plots_by_type = list(db.plots.aggregate([
        {"$group": {"_id": "$Project_Type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    return {"total_plots": total_plots, "by_type": plots_by_type}

# -----------------------------
# 2. NDVI averages
# -----------------------------
@router.get("/ndvi-by-project")
def ndvi_by_project():
    pipeline = [
        {"$group": {"_id": "$Project_Type", "avgNDVI": {"$avg": "$NDVI"}}},
        {"$sort": {"avgNDVI": -1}}
    ]
    return {"ndvi": list(db.plots.aggregate(pipeline))}

@router.get("/ndvi-by-project-source")
def ndvi_by_project_source():
    pipeline = [
        {"$group": {"_id": {"type": "$Project_Type", "source": "$Data_Source"}, "avgNDVI": {"$avg": "$NDVI"}}},
        {"$sort": {"_id.type": 1, "_id.source": 1}}
    ]
    return {"ndvi": list(db.plots.aggregate(pipeline))}

# -----------------------------
# 3. Biomass trends
# -----------------------------
@router.get("/biomass-trend")
def biomass_trend():
    pipeline = [
        {"$group": {
            "_id": "$Monitoring_Year",
            "avgAbove": {"$avg": "$Biomass_above_kg"},
            "avgBelow": {"$avg": "$Biomass_below_kg"},
            "total": {"$sum": {"$add": ["$Biomass_above_kg", "$Biomass_below_kg"]}}
        }},
        {"$sort": {"_id": 1}}
    ]
    return {"biomass": list(db.plots.aggregate(pipeline))}

# -----------------------------
# 4. Fluxes
# -----------------------------
@router.get("/fluxes")
def fluxes():
    co2 = list(db.plots.aggregate([
        {"$group": {"_id": "$Monitoring_Year", "avgCO2": {"$avg": "$CO2_Flux_mg_m2_day"}}},
        {"$sort": {"_id": 1}}
    ]))
    ch4 = list(db.plots.aggregate([
        {"$group": {"_id": "$Monitoring_Year", "avgCH4": {"$avg": "$CH4_Flux_mg_m2_day"}}},
        {"$sort": {"_id": 1}}
    ]))
    return {"co2": co2, "ch4": ch4}

# -----------------------------
# 5. NDVI trend (monthly)
# -----------------------------
@router.get("/ndvi-monthly")
def ndvi_monthly():
    pipeline = [
        {"$addFields": {"month": {"$month": "$Timestamp"}, "year": {"$year": "$Timestamp"}}},
        {"$group": {"_id": {"year": "$year", "month": "$month"}, "avgNDVI": {"$avg": "$NDVI"}}},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    return {"trend": list(db.plots.aggregate(pipeline))}
