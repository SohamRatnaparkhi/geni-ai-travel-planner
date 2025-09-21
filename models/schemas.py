from typing import List, Optional
from pydantic import BaseModel, Field


class ItineraryRequest(BaseModel):
    home_city: str
    destination_city: str
    num_days: int = Field(default=4, ge=1, le=14)
    interests: List[str] = Field(default_factory=list)


class ItineraryPlace(BaseModel):
    name: str
    description: str


class ItineraryEntity(BaseModel):
    name: str
    speciality: str
    places_to_visit: List[ItineraryPlace]
    photo_prompts: List[str] = Field(default_factory=list)
    image_urls: List[str] = Field(default_factory=list)


class ItineraryDay(BaseModel):
    day: int
    summary: str
    entities: List[ItineraryEntity]
    route_info: Optional[str] = None


class ItineraryResponse(BaseModel):
    home_city: str
    destination_city: str
    num_days: int
    days: List[ItineraryDay]
    overall_tips: List[str] = Field(default_factory=list)


class TravelOptionsRequest(BaseModel):
    origin_city: str
    destination_city: str
    recency_filter: Optional[str] = None  # e.g., 'month', 'week'


class TravelSource(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None


class TravelOption(BaseModel):
    route_name: str
    carriers: List[str] = Field(default_factory=list)
    duration: Optional[str] = None
    price: Optional[str] = None
    frequency: Optional[str] = None
    airports_or_stations: List[str] = Field(default_factory=list)
    transfers: Optional[str] = None
    booking_tips: Optional[str] = None
    sources: List[TravelSource] = Field(default_factory=list)


class TravelMode(BaseModel):
    mode: str  # flight, train, bus, car, ferry
    options: List[TravelOption]


class TravelOptionsResponse(BaseModel):
    origin_city: str
    destination_city: str
    modes: List[TravelMode]


