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


# Non day-wise itinerary: place cards
class ItineraryPlacesRequest(BaseModel):
    destination_city: str
    interests: List[str] = Field(default_factory=list)
    max_places: int = Field(default=8, ge=1, le=30)


class ItineraryPlaceCard(BaseModel):
    city: str
    place_name: str
    speciality: str
    tips: List[str] = Field(default_factory=list)
    photo_prompts: List[str] = Field(default_factory=list)
    image_urls: List[str] = Field(default_factory=list)


class ItineraryPlacesResponse(BaseModel):
    destination_city: str
    places: List[ItineraryPlaceCard]


# Food outlets via Perplexity
class FoodOptionsRequest(BaseModel):
    city: str
    cuisine_preferences: List[str] = Field(default_factory=list)
    price_level: Optional[str] = Field(default=None, description="$, $$, $$$")
    recency_filter: Optional[str] = None


class FoodOutlet(BaseModel):
    name: str
    cuisine: Optional[str] = None
    price_level: Optional[str] = None
    area_or_neighborhood: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    booking_tips: Optional[str] = None
    source_url: Optional[str] = None


class FoodOptionsResponse(BaseModel):
    city: str
    outlets: List[FoodOutlet]


