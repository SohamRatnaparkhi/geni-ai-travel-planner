from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import json
import os
import uuid
import time
import google.generativeai as genai
from constants.prompts import ACTIVITIES_PROMPT, RESTAURANTS_PROMPT, ACCOMMODATION_PROMPT

load_dotenv()

router = APIRouter(
    prefix="/destination",
    tags=["destination"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response

class DestinationRequest(BaseModel):
    place: str
    days: int
    budget: float  # in rupees
    custom_ins: str = ""  # Custom user preferences like "vegetarian food, historic sites, no clubs"

class DestinationResponse(BaseModel):
    place: str
    days: int
    budget: float
    activities: List[str] = []
    food: List[str] = []
    accommodations: List[str] = []
    processing_status: str = "processing"
    error: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    created_at: float
    destinations: List[DestinationResponse]

# Mock data for demonstration
travel_plans = []

# Google Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","your-api-key-here")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')

# Task storage for background processing
tasks_storage = {}

def parse_simple_response(response_text: str, response_type: str) -> List[str]:
    """Parse simple AI response to extract arrays"""
    try:
        # Clean the response text
        cleaned_text = response_text.strip()

        # Try to find JSON-like structure in the response
        import re

        # Look for the specific array based on response type
        if response_type == "activities":
            array_match = re.search(r'"activities"\s*:\s*\[(.*?)\]', cleaned_text, re.DOTALL)
        elif response_type == "food":
            array_match = re.search(r'"food"\s*:\s*\[(.*?)\]', cleaned_text, re.DOTALL)
        elif response_type == "accommodations":
            array_match = re.search(r'"accommodations"\s*:\s*\[(.*?)\]', cleaned_text, re.DOTALL)
        else:
            return []

        if array_match:
            array_content = array_match.group(1)
            # Extract individual items from the array
            items = []
            for match in re.finditer(r'"(.*?)"', array_content):
                items.append(match.group(1))
            return items

        # If no array found, try to split by lines
        lines = [line.strip().strip('"').strip("'") for line in cleaned_text.split('\n') if line.strip()]
        return [line for line in lines if len(line) > 10]  # Filter out very short lines

    except Exception as e:
        return [f"Error parsing {response_type}: {str(e)}"]

def process_destination_background(task_id: str, destination_request: DestinationRequest):
    """Background task to process a single destination"""
    try:
        place = destination_request.place
        days = destination_request.days
        budget = destination_request.budget
        custom_ins = destination_request.custom_ins

        print(f"DEBUG: Starting background processing for {place} with custom preferences: {custom_ins}")

        # Initialize task
        tasks_storage[task_id] = {
            "task_id": task_id,
            "status": "processing",
            "message": f"Processing {place}",
            "created_at": time.time(),
            "destinations": [
                {
                    "place": place,
                    "days": days,
                    "budget": budget,
                    "custom_ins": custom_ins,
                    "processing_status": "processing"
                }
            ]
        }

        print(f"DEBUG: Task initialized for {place}")


        try:
            print(f"DEBUG: Starting AI calls for {place}")

            # Generate activities
            activities_prompt = ACTIVITIES_PROMPT.format(destination=place, days=days, budget=budget, custom_ins=destination_request.custom_ins)
            print(f"DEBUG: Making AI call for activities...")
            activities_response = model.generate_content(activities_prompt)
            print(f"DEBUG: Activities response received, length: {len(activities_response.text)}")
            activities_list = parse_simple_response(activities_response.text, "activities")
            print(f"DEBUG: Activities parsed: {len(activities_list)} items")

            # Generate food recommendations
            food_prompt = RESTAURANTS_PROMPT.format(destination=place, budget=budget, custom_ins=destination_request.custom_ins)
            print(f"DEBUG: Making AI call for food...")
            food_response = model.generate_content(food_prompt)
            print(f"DEBUG: Food response received, length: {len(food_response.text)}")
            food_list = parse_simple_response(food_response.text, "food")
            print(f"DEBUG: Food parsed: {len(food_list)} items")

            # Generate accommodation recommendations
            accommodation_prompt = ACCOMMODATION_PROMPT.format(destination=place, days=days, budget=budget, custom_ins=destination_request.custom_ins)
            print(f"DEBUG: Making AI call for accommodations...")
            accommodation_response = model.generate_content(accommodation_prompt)
            print(f"DEBUG: Accommodations response received, length: {len(accommodation_response.text)}")
            accommodation_list = parse_simple_response(accommodation_response.text, "accommodations")
            print(f"DEBUG: Accommodations parsed: {len(accommodation_list)} items")

            print(f"DEBUG: All AI calls completed for {place}")

        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            activities_list = [f"Error getting activities: {str(e)}"]
            food_list = [f"Error getting food: {str(e)}"]
            accommodation_list = [f"Error getting accommodations: {str(e)}"]

        # Update task with results
        print(f"DEBUG: Updating task status to completed for {place}")
        tasks_storage[task_id] = {
            "task_id": task_id,
            "status": "completed",
            "message": f"Successfully processed {place}",
            "created_at": time.time(),
            "destinations": [
                {
                    "place": place,
                    "days": days,
                    "budget": budget,
                    "activities": activities_list,
                    "food": food_list,
                    "accommodations": accommodation_list,
                    "processing_status": "completed"
                }
            ]
        }
        print(f"DEBUG: Task status updated for {place}. Current tasks in storage: {len(tasks_storage)}")

    except Exception as e:
        # Handle any unexpected errors
        tasks_storage[task_id] = {
            "task_id": task_id,
            "status": "error",
            "message": f"Failed to process {place}: {str(e)}",
            "created_at": time.time(),
            "destinations": [
                {
                    "place": destination_request.place,
                    "days": destination_request.days,
                    "budget": destination_request.budget,
                    "processing_status": "error",
                    "error": str(e)
                }
            ]
        }

# Old synchronous functions removed - now using background processing

@router.post("/process", response_model=TaskResponse)
async def process_destinations(
    destinations: List[DestinationRequest],
    background_tasks: BackgroundTasks
) -> TaskResponse:
    """Process multiple destinations in background tasks"""
    if not destinations:
        raise HTTPException(status_code=400, detail="No destinations provided")

    # Create task ID
    task_id = str(uuid.uuid4())

    # Initialize task storage
    tasks_storage[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "message": f"Starting background processing for {len(destinations)} destinations",
        "created_at": time.time(),
        "destinations": [
            {
                "place": dest.place,
                "days": dest.days,
                "budget": dest.budget,
                "processing_status": "pending"
            }
            for dest in destinations
        ]
    }

    # Start background processing for each destination
    for destination in destinations:
        background_tasks.add_task(process_destination_background, task_id, destination)

    # Return task information immediately
    return TaskResponse(
        task_id=task_id,
        status="processing",
        message=f"Started processing {len(destinations)} destinations in background",
        created_at=time.time(),
        destinations=[
            {
                "place": dest.place,
                "days": dest.days,
                "budget": dest.budget,
                "processing_status": "processing"
            }
            for dest in destinations
        ]
    )

@router.get("/task-status/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str) -> TaskResponse:
    """Get the status of a background processing task"""
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = tasks_storage[task_id]

    # Convert destinations to proper format
    destinations = []
    for dest in task_data["destinations"]:
        destinations.append(DestinationResponse(**dest))

    return TaskResponse(
        task_id=task_data["task_id"],
        status=task_data["status"],
        message=task_data["message"],
        created_at=task_data["created_at"],
        destinations=destinations
    )

@router.get("/")
async def get_travel_info():
    """Get general travel information"""
    return {
        "message": "Travel planning API with background processing",
        "endpoints": {
            "process_destinations": "/travel/process-destinations",
            "task_status": "/travel/task-status/{task_id}",
            "test_gemini": "/travel/test-gemini"
        }
    }