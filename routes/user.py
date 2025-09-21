from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models
class User(BaseModel):
    name: str
    email: str
    preferences: Dict[str, Any] = {}

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    preferences: Dict[str, Any]
    created_at: str

# Mock data
users = []

@router.get("/")
async def get_user_info():
    """Get general user API information"""
    return {
        "message": "User management API",
        "endpoints": {
            "users": "/user/users",
            "profile": "/user/profile"
        }
    }

@router.get("/users")
async def get_users():
    """Get all users"""
    return {"users": users}

@router.post("/users")
async def create_user(user: User):
    """Create a new user"""
    user_id = f"user_{len(users) + 1}"
    new_user = UserResponse(
        id=user_id,
        name=user.name,
        email=user.email,
        preferences=user.preferences,
        created_at="2024-01-01T00:00:00Z"
    )
    users.append(new_user.dict())
    return {"message": "User created successfully", "user": new_user}

@router.get("/profile")
async def get_user_profile():
    """Get current user profile (mock endpoint)"""
    return {
        "id": "user_1",
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {
            "theme": "dark",
            "language": "en",
            "currency": "USD"
        }
    }

@router.put("/profile")
async def update_profile(user_data: Dict[str, Any]):
    """Update user profile"""
    return {
        "message": "Profile updated successfully",
        "updated_data": user_data
    }
