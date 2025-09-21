from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter(
    prefix="/travel",
    tags=["travel"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response
class Destination(BaseModel):
    name: str
    country: str
    description: str = ""

class TravelPlan(BaseModel):
    destination: str
    duration: int  # in days
    budget: float
    interests: List[str] = []

class TravelPlanResponse(BaseModel):
    id: str
    destination: str
    duration: int
    budget: float
    interests: List[str]
    status: str
    created_at: str

# Mock data for demonstration
travel_plans = []

@router.get("/")
async def get_travel_info():
    """Get general travel information"""
    return {
        "message": "Travel planning API",
        "endpoints": {
            "plans": "/travel/plans",
            "destinations": "/travel/destinations"
        }
    }

@router.get("/plans")
async def get_travel_plans():
    """Get all travel plans"""
    return {"plans": travel_plans}

@router.post("/plans")
async def create_travel_plan(plan: TravelPlan):
    """Create a new travel plan"""
    plan_id = f"plan_{len(travel_plans) + 1}"
    new_plan = TravelPlanResponse(
        id=plan_id,
        destination=plan.destination,
        duration=plan.duration,
        budget=plan.budget,
        interests=plan.interests,
        status="created",
        created_at="2024-01-01T00:00:00Z"  # In real app, use datetime.now()
    )
    travel_plans.append(new_plan.dict())
    return {"message": "Travel plan created successfully", "plan": new_plan}

@router.get("/plans/{plan_id}")
async def get_travel_plan(plan_id: str):
    """Get a specific travel plan by ID"""
    plan = next((p for p in travel_plans if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Travel plan not found")
    return plan

@router.get("/destinations")
async def get_popular_destinations():
    """Get popular travel destinations"""
    destinations = [
        {"name": "Paris", "country": "France", "description": "City of Light"},
        {"name": "Tokyo", "country": "Japan", "description": "Modern metropolis"},
        {"name": "Bali", "country": "Indonesia", "description": "Tropical paradise"},
        {"name": "New York", "country": "USA", "description": "The Big Apple"}
    ]
    return {"destinations": destinations}

@router.post("/destinations")
async def add_destination(destination: Destination):
    """Add a new destination"""
    return {
        "message": "Destination added successfully",
        "destination": destination.dict()
    }
