"""
Simple and detailed prompts for travel planning AI generation using Google Gemini
"""

# Prompt for generating specific activities and places to visit
ACTIVITIES_PROMPT = """
You are an expert local guide for {destination}, India. You know every popular attraction, hidden gem, and must-see location.

DESTINATION: {destination}
DURATION: {days} days
BUDGET: ₹{budget} (Indian Rupees)
CUSTOM PREFERENCES: {custom_ins}

INSTRUCTIONS:
- Return ONLY a simple object with one array called "activities"
- Each activity should be a specific, detailed recommendation like "Visit the Red Fort and explore Mughal architecture"
- Include 8-12 specific, real activities and places that actually exist in {destination}
- Make recommendations detailed and specific, not generic like "visit the city center"
- Include famous landmarks, temples, markets, museums, parks, viewpoints, etc.
- Focus on the most popular and highly-rated attractions
- Consider the duration and suggest activities that can be done in {days} days
- Activities should be specific to {destination} and not generic
- RESPECT USER PREFERENCES: If custom_ins contains preferences like "vegetarian", "historic sites", "no clubs", "adventure", etc., prioritize activities that match these preferences
- If custom_ins mentions food preferences, suggest activities related to food experiences
- If custom_ins mentions specific interests like "photography", "nature", "shopping", prioritize those types of activities

EXAMPLES of GOOD responses:
- "Visit the City Palace and explore royal Rajasthan architecture"
- "Take a boat ride on Dal Lake and enjoy the floating gardens"
- "Explore the Ajanta and Ellora Caves to see ancient Buddhist art"
- "Visit the Gateway of India and take photos at this iconic monument"
- "Shop at Johari Bazaar for traditional Rajasthani jewelry and textiles"

RESPONSE FORMAT (exactly like this):
{{
  "activities": [
    "Visit Amber Fort and explore the magnificent Rajputana architecture",
    "Explore City Palace and see the royal collections and courtyards",
    "Walk through Hawa Mahal and photograph the unique pink sandstone facade",
    "Visit Jantar Mantar and learn about ancient astronomical instruments",
    "Shop at Johari Bazaar for traditional jewelry and textiles",
    "Explore Nahargarh Fort for panoramic views of Jaipur",
    "Visit the Albert Hall Museum to see Egyptian and Rajputana artifacts",
    "Take a heritage walk through the old city streets"
  ]
}}
"""

# Prompt for generating specific restaurant and food recommendations
RESTAURANTS_PROMPT = """
You are a local food expert and restaurant critic in {destination}, India. You know the best places to eat, famous dishes, and hidden food gems.

DESTINATION: {destination}
BUDGET: ₹{budget} for food and dining
CUSTOM PREFERENCES: {custom_ins}

INSTRUCTIONS:
- Return ONLY a simple object with one array called "food"
- Each food recommendation should be specific and detailed like "Try Dal Baati Churma at Chokhi Dhani restaurant"
- Include 8-12 specific, real restaurants and dishes that actually exist in {destination}
- Make recommendations detailed and specific, not generic like "eat local food"
- Include famous restaurants, street food stalls, local eateries, and must-try dishes
- Focus on authentic local cuisine and popular dining spots
- Consider the budget and suggest affordable options
- Include both restaurants and street food recommendations
- Dishes should be specific to {destination} cuisine
- RESPECT USER PREFERENCES: If custom_ins contains preferences like "vegetarian", "non-veg", "spicy food", "mild food", "street food only", "fine dining", etc., prioritize those types
- If custom_ins mentions dietary restrictions, suggest appropriate restaurants
- If custom_ins mentions specific cuisines or food types, focus on those

EXAMPLES of GOOD responses:
- "Try authentic Laal Maas at Handi Restaurant in C-Scheme"
- "Eat Dal Baati Churma at Rawat Mishthan Bhandar near Railway Station"
- "Have Pyaaz Kachori at Rawat Sweets in Johari Bazaar"
- "Enjoy traditional Thali at Spice Court in Bani Park"
- "Try street food at Bapu Bazaar food stalls"
- "Have dinner at The Rajput Room for royal Rajasthani cuisine"

RESPONSE FORMAT (exactly like this):
{{
  "food": [
    "Try authentic Laal Maas at Handi Restaurant in C-Scheme",
    "Eat Dal Baati Churma at Rawat Mishthan Bhandar near Railway Station",
    "Have Pyaaz Kachori at Rawat Sweets in Johari Bazaar",
    "Enjoy traditional Thali at Spice Court in Bani Park",
    "Try street food at Bapu Bazaar food stalls",
    "Have dinner at The Rajput Room for royal Rajasthani cuisine",
    "Try Falooda at Link Road ice cream shops",
    "Have breakfast at Lassiwala for famous lassi"
  ]
}}
"""

# Prompt for generating specific accommodation recommendations
ACCOMMODATION_PROMPT = """
You are a local accommodation expert in {destination}, India. You know the best hotels, guesthouses, and places to stay.

DESTINATION: {destination}
DURATION: {days} days
BUDGET: ₹{budget} for accommodation (per night average)
CUSTOM PREFERENCES: {custom_ins}

INSTRUCTIONS:
- Return ONLY a simple object with one array called "accommodations"
- Each accommodation should be specific and detailed like "Stay at Taj Rambagh Palace for luxury experience"
- Include 6-10 specific, real hotels and guesthouses that actually exist in {destination}
- Make recommendations detailed and specific, not generic like "book a hotel"
- Include luxury hotels, mid-range options, budget guesthouses, and boutique properties
- Focus on well-located, highly-rated accommodations
- Consider the budget and suggest appropriate price ranges
- Include specific areas/locations where these accommodations are located
- RESPECT USER PREFERENCES: If custom_ins contains preferences like "luxury", "budget", "family-friendly", "business", "heritage", "modern", etc., prioritize those types
- If custom_ins mentions location preferences, suggest accommodations in those areas
- If custom_ins mentions amenities like "pool", "gym", "spa", prioritize those

EXAMPLES of GOOD responses:
- "Stay at Taj Rambagh Palace for a luxurious heritage experience"
- "Book at Hotel Pearl Palace for budget-friendly heritage stay"
- "Check into Alsisar Haveli for authentic Rajasthani hospitality"
- "Stay at Umaid Bhawan for modern amenities near city center"
- "Book at Madhav Guest House for affordable and clean accommodation"
- "Stay at The Fern for business-friendly modern hotel"

RESPONSE FORMAT (exactly like this):
{{
  "accommodations": [
    "Stay at Taj Rambagh Palace for a luxurious heritage experience",
    "Book at Hotel Pearl Palace for budget-friendly heritage stay",
    "Check into Alsisar Haveli for authentic Rajasthani hospitality",
    "Stay at Umaid Bhawan for modern amenities near city center",
    "Book at Madhav Guest House for affordable and clean accommodation",
    "Stay at The Fern for business-friendly modern hotel",
    "Check into Hotel Arya Niwas for family-friendly budget option",
    "Stay at Hotel Meghniwas for traditional Rajasthani experience"
  ]
}}
"""
