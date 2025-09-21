# Travel Planner API

A comprehensive FastAPI backend for AI-powered travel planning using Google Gemini AI.

## Features

- 🚀 **Parallel Processing**: Process multiple destinations simultaneously
- 🤖 **Google Gemini AI**: Powered by Google's advanced AI for travel recommendations
- 📊 **Comprehensive Data**: Activities, restaurants, and accommodation for each destination
- 💰 **Budget-aware**: All recommendations respect your budget constraints
- ⚡ **Fast**: Parallel processing for quick results

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Google Gemini AI
1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set environment variable:
```bash
export GEMINI_API_KEY=your_api_key_here
# or on Windows
set GEMINI_API_KEY=your_api_key_here
```

### 3. Start the Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Process Destinations (Background Processing)
**POST** `/travel/process-destinations`

Start background processing of multiple destinations with AI-powered recommendations.

**Request Body:**
```json
{
  "destinations": [
    {
      "place": "Jaipur",
      "days": 3,
      "budget": 15000,
      "custom_ins": "vegetarian food, historic sites, no clubs, budget-friendly"
    },
    {
      "place": "Goa",
      "days": 5,
      "budget": 25000,
      "custom_ins": "beach activities, seafood, luxury hotels, adventure sports"
    }
  ]
}
```

**Request Fields:**
- `place`: Destination name (required)
- `days`: Number of days for the trip (required)
- `budget`: Total budget in INR (required)
- `custom_ins`: Custom user preferences like "vegetarian food, historic sites, luxury hotels" (optional)

**Response (Immediate):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Started processing 2 destinations in background",
  "created_at": 1699123456.789,
  "destinations": [
    {
      "place": "Jaipur",
      "days": 3,
      "budget": 15000,
      "processing_status": "processing"
    }
  ]
}
```

### Get Task Status
**GET** `/travel/task-status/{task_id}`

Poll the server to check the status of a background processing task.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "Successfully processed Jaipur",
  "created_at": 1699123456.789,
  "destinations": [
    {
      "place": "Jaipur",
      "days": 3,
      "budget": 15000,
      "processing_status": "completed",
      "activities": { ... },
      "restaurants": { ... },
      "accommodation": { ... }
    }
  ]
}
```

### Available Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /travel/process-destinations` - Start background processing
- `GET /travel/task-status/{task_id}` - Check processing status
- `GET /travel/plans` - Get travel plans
- `POST /travel/plans` - Create travel plan
- `GET /travel/destinations` - Popular destinations
- `GET /user/users` - Get users
- `POST /user/users` - Create user

## Architecture

### Background Processing Architecture
- **Immediate Response**: Returns task ID instantly for frontend polling
- **Background Processing**: Each destination processed in background tasks
- **Parallel AI Calls**: For each destination, 3 AI tasks run in parallel:
  - Activities & things to do
  - Restaurants & local foods
  - Accommodation recommendations
- **Status Tracking**: Real-time status updates via task polling

### AI Prompts
The system uses 3 detailed prompts for different aspects:
1. **Activities**: Comprehensive activity recommendations with timing, costs, and tips
2. **Restaurants**: Restaurant recommendations with cuisines, pricing, and local delicacies
3. **Accommodation**: Hotel recommendations based on budget and duration

## Example Usage

### Step 1: Start Background Processing
```bash
# Start processing destinations in background
curl -X POST "http://localhost:8000/travel/process-destinations" \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Started processing 2 destinations in background",
  "created_at": 1699123456.789,
  "destinations": [...]
}
```

### Step 2: Poll for Status
```bash
# Check processing status
curl "http://localhost:8000/travel/task-status/550e8400-e29b-41d4-a716-446655440000"
```

**Response (while processing):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Processing Jaipur",
  "destinations": [...]
}
```

**Response (when completed):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "Successfully processed Jaipur",
  "destinations": [
    {
      "place": "Jaipur",
      "processing_status": "completed",
      "activities": { ... },
      "restaurants": { ... },
      "accommodation": { ... }
    }
  ]
}
```

## Response Structure

Each destination response includes:
- **Activities**: Categorized activities with costs, timing, and tips
- **Restaurants**: Restaurant recommendations with cuisines and pricing
- **Accommodation**: Hotel options with amenities and location details
- **Budget Breakdown**: Detailed cost analysis
- **Processing Status**: Real-time status tracking

## Simple & Robust Design

The API uses a simplified approach for maximum reliability:
- AI returns simple objects with 3 arrays (activities, food, accommodations)
- No complex JSON parsing required
- Detailed prompts ensure specific, real recommendations
- Each response contains actual places and restaurants, not generic suggestions
- Background processing with task status polling
- Custom user preferences support through `custom_ins` field
- Comprehensive debugging and error handling

## Debugging

The API includes extensive debugging features to help troubleshoot issues:

### Debug Endpoints
- `GET /travel/test-gemini` - Test if Gemini API is working
- Console logs show detailed processing information
- Background task status updates in real-time

### Debug Information
When processing requests, you'll see console output like:
```
DEBUG: API Key configured: your-key...
DEBUG: Starting background processing for Pune with custom preferences: vegetarian food, historic sites
DEBUG: Task initialized for Pune
DEBUG: Making AI call for activities...
DEBUG: Activities response received, length: 1234
DEBUG: Task status updated for Pune. Current tasks in storage: 1
```

### Troubleshooting

1. **API Key Issues**: Use `GET /travel/test-gemini` to check if your API key is working
2. **Processing Delays**: Check console logs for detailed progress information
3. **Stuck Processing**: The debug logs will show exactly where processing is failing

## Error Handling

The API includes comprehensive error handling for:
- Invalid destinations
- AI processing failures
- Budget constraints
- Network issues
- Custom preference parsing errors

## Technology Stack

- **FastAPI**: Modern Python web framework
- **Google Gemini AI**: Advanced AI for content generation
- **AsyncIO**: Parallel processing capabilities
- **Pydantic**: Data validation and serialization
