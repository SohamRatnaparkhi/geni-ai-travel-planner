from fastapi import APIRouter, HTTPException
from typing import List, Any
from pydantic import BaseModel
import os
from google.genai import types as genai_types
from services.gemini_service import async_gemini_generate_content, async_generate_image_files
from services.perplexity_service import PerplexityService
from models.schemas import (
    ItineraryRequest,
    ItineraryResponse,
    TravelOptionsRequest,
    TravelOptionsResponse,
)
from prompts.system_itinerary import SYSTEM_PROMPT_ITINERARY
from prompts.system_travel_options import SYSTEM_PROMPT_TRAVEL_OPTIONS
from utils.files import static_dir, ensure_dir

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
            "destinations": "/travel/destinations",
            "itinerary": "/travel/itinerary",
            "options": "/travel/options"
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


@router.post("/itinerary", response_model=ItineraryResponse)
async def generate_itinerary(payload: ItineraryRequest) -> Any:
    try: 
        system_prompt = SYSTEM_PROMPT_ITINERARY

        user_prompt = (
            f"Home: {payload.home_city}\n"
            f"Destination: {payload.destination_city}\n"
            f"Days: {payload.num_days}\n"
            f"Interests: {', '.join(payload.interests) if payload.interests else 'general'}\n"
            "Generate an end-to-end itinerary as per schema."
        )

        contents = [
            genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=user_prompt)],
            )
        ]

        # Structured schema for itinerary
        response_schema = genai_types.Schema(
            type=genai_types.Type.OBJECT,
            required=["home_city", "destination_city", "num_days", "days"],
            properties={
                "home_city": genai_types.Schema(type=genai_types.Type.STRING),
                "destination_city": genai_types.Schema(type=genai_types.Type.STRING),
                "num_days": genai_types.Schema(type=genai_types.Type.INTEGER),
                "days": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        required=["day", "summary", "entities"],
                        properties={
                            "day": genai_types.Schema(type=genai_types.Type.INTEGER),
                            "summary": genai_types.Schema(type=genai_types.Type.STRING),
                            "route_info": genai_types.Schema(type=genai_types.Type.STRING),
                            "entities": genai_types.Schema(
                                type=genai_types.Type.ARRAY,
                                items=genai_types.Schema(
                                    type=genai_types.Type.OBJECT,
                                    required=[
                                        "name",
                                        "speciality",
                                        "places_to_visit",
                                        "photo_prompts",
                                    ],
                                    properties={
                                        "name": genai_types.Schema(type=genai_types.Type.STRING),
                                        "speciality": genai_types.Schema(type=genai_types.Type.STRING),
                                        "places_to_visit": genai_types.Schema(
                                            type=genai_types.Type.ARRAY,
                                            items=genai_types.Schema(
                                                type=genai_types.Type.OBJECT,
                                                required=["name", "description"],
                                                properties={
                                                    "name": genai_types.Schema(type=genai_types.Type.STRING),
                                                    "description": genai_types.Schema(type=genai_types.Type.STRING),
                                                },
                                            ),
                                        ),
                                        "photo_prompts": genai_types.Schema(
                                            type=genai_types.Type.ARRAY,
                                            items=genai_types.Schema(type=genai_types.Type.STRING),
                                        ),
                                    },
                                ),
                            ),
                        },
                    ),
                ),
                "overall_tips": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(type=genai_types.Type.STRING),
                ),
            },
        )

        default_response = {
            "home_city": payload.home_city,
            "destination_city": payload.destination_city,
            "num_days": payload.num_days,
            "days": [],
            "overall_tips": [],
        }

        data = await async_gemini_generate_content(
            model="gemini-2.5-pro",
            contents=contents,
            system_prompt=system_prompt,
            response_schema=response_schema,
            temperature=0.35,
            top_p=0.9,
            max_output_tokens=4096,
            timeout=120,
            default_response=default_response,
        )

        # Generate images for each entity using photo_prompts
        image_base_url = "/static"
        dest_slug = payload.destination_city.lower().replace(" ", "-")
        output_dir = os.path.join(static_dir(), f"itineraries/{dest_slug}")
        ensure_dir(output_dir)

        for day in data.get("days", []):
            for entity in day.get("entities", []):
                prompts = entity.get("photo_prompts", [])[:2]
                if not prompts:
                    entity["image_urls"] = []
                    continue
                files = await async_generate_image_files(
                    prompts=prompts,
                    output_dir=output_dir,
                    base_file_name=entity.get("name", "entity").lower().replace(" ", "-"),
                )
                # Convert to served URLs
                entity["image_urls"] = [
                    f"{image_base_url}/{os.path.relpath(fp, static_dir())}" for fp in files
                ]

        return ItineraryResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/options", response_model=TravelOptionsResponse)
async def travel_options(payload: TravelOptionsRequest) -> Any:
    try:
        user_prompt = (
            f"Origin: {payload.origin_city}\n"
            f"Destination: {payload.destination_city}\n"
            "List practical travel options by mode as per schema."
        )

        svc = PerplexityService()
        result = await svc.chat_completion(
            system_prompt=SYSTEM_PROMPT_TRAVEL_OPTIONS,
            user_prompt=user_prompt,
            model="sonar",
            temperature=0.2,
            top_p=0.9,
            max_tokens=1400,
            web_search_options={"search_context_size": "high"},
            recency_filter=payload.recency_filter,
        )

        # Debug: Log the response structure
        print(f"DEBUG: Full response: {result}")

        # Extract assistant message content; expect JSON accordance to schema
        choices = result.get("choices", [])
        text = ""
        if choices:
            msg = choices[0].get("message", {})
            text = msg.get("content", "")
            print(f"DEBUG: Extracted text: {text[:200]}...")  # First 200 chars

        # Expect JSON payload; attempt to parse
        import json
        data = None
        if text:
            try:
                data = json.loads(text)
                print(f"DEBUG: Successfully parsed JSON")
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON parsing failed: {e}")
                print(f"DEBUG: Failed text: {text}")
                # Try to clean up the text if it has formatting issues
                try:
                    # Remove any leading/trailing non-JSON content
                    start_idx = text.find('{')
                    end_idx = text.rfind('}') + 1
                    if start_idx != -1 and end_idx > start_idx:
                        cleaned_text = text[start_idx:end_idx]
                        data = json.loads(cleaned_text)
                        print(f"DEBUG: Successfully parsed cleaned JSON")
                    else:
                        raise ValueError("No JSON object found in text")
                except Exception as clean_error:
                    print(f"DEBUG: Cleaned JSON parsing also failed: {clean_error}")
                    data = None

        if data is None:
            print("DEBUG: Using fallback structure")
            # Fallback minimal structure
            data = {
                "origin": payload.origin_city,
                "destination": payload.destination_city,
                "travel_options": {
                    "train": [],
                    "bus": [],
                    "car_taxi": [],
                    "car_transport": [],
                    "part_load_transport": [],
                    "flight": []
                }
            }

        # Ensure required top-level fields based on the expected schema
        data.setdefault("origin", payload.origin_city)
        data.setdefault("destination", payload.destination_city)
        data.setdefault("travel_options", {
            "train": [],
            "bus": [],
            "car_taxi": [],
            "car_transport": [],
            "part_load_transport": [],
            "flight": []
        })

        # Convert from travel_options format to modes format for schema compatibility
        if "travel_options" in data:
            # Convert from travel_options dict to modes list format
            modes_list = []
            travel_options = data.get("travel_options", {})

            for mode_name, options in travel_options.items():
                if options:  # Only add modes that have options
                    modes_list.append({
                        "mode": mode_name,
                        "options": options
                    })

            # Update data with the converted format
            data["modes"] = modes_list
            del data["travel_options"]

        # Ensure we have the expected field names
        data["origin_city"] = data.pop("origin", payload.origin_city)
        data["destination_city"] = data.pop("destination", payload.destination_city)

        return TravelOptionsResponse(**data)
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
