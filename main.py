import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from services.ai_service import analyze_crop_image
from services.weather_service import get_weather_data
from services.decision_engine import assess_treatment_conditions

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AgriShield API",
    description="Climate-Resilient AgriTech Crop advisory platform.",
    version="1.0.0"
)

# CORS Configuration for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "AgriShield Backend"}

@app.post("/api/analyze")
async def analyze_crop(
    file: UploadFile = File(...),
    crop: str = Form("Tomato"),
    scenario: str = Form(None),
    lat: float = Form(28.6139),  # Default: New Delhi
    lon: float = Form(77.2090)
):
    """
    Main analysis endpoint. Accepts leaf photo and context parameters.
    Fetches real-time weather and evaluates treatments.
    """
    logger.info(f"Analysis requested for crop: {crop}, scenario: {scenario}, lat: {lat}, lon: {lon}")
    
    # 1. Read uploaded file bytes
    try:
        image_bytes = await file.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
    except Exception as e:
        logger.error(f"Failed to read upload file: {e}")
        raise HTTPException(status_code=400, detail="Unable to read the uploaded leaf image.")

    # 2. Perform AI crop disease detection
    try:
        diagnosis = analyze_crop_image(image_bytes, crop_hint=crop, scenario=scenario)
    except Exception as e:
        logger.error(f"Disease detection failed: {e}")
        raise HTTPException(status_code=500, detail="AI Disease analysis service failed.")
        
    # 3. Retrieve Live Weather / Forecast
    try:
        if scenario and scenario in ["healthy", "tomato_late_blight", "corn_common_rust", "rice_blast"]:
            logger.info(f"Using mock weather for demo scenario: {scenario}")
            if scenario == "healthy":
                weather = {
                    "source": "demo_scenario",
                    "lat": lat,
                    "lon": lon,
                    "temp": 28.5,
                    "humidity": 55,
                    "wind_speed": 6.5,
                    "rain": 0.0,
                    "precipitation": 0.0,
                    "condition": "Clear Sky",
                    "weather_code": 0,
                    "max_rain_probability_12h": 10,
                    "forecast": [
                        {"date": "Today", "temp_max": 30.0, "temp_min": 22.0, "condition": "Clear Sky", "precipitation_sum": 0.0, "precipitation_probability": 10},
                        {"date": "Tomorrow", "temp_max": 29.0, "temp_min": 21.0, "condition": "Partly Cloudy", "precipitation_sum": 0.0, "precipitation_probability": 15},
                        {"date": "Day After", "temp_max": 28.0, "temp_min": 20.0, "condition": "Clear Sky", "precipitation_sum": 0.0, "precipitation_probability": 5}
                    ]
                }
            elif scenario == "tomato_late_blight":
                weather = {
                    "source": "demo_scenario",
                    "lat": lat,
                    "lon": lon,
                    "temp": 25.0,
                    "humidity": 88,
                    "wind_speed": 6.5,
                    "rain": 0.0,
                    "precipitation": 0.0,
                    "condition": "Overcast",
                    "weather_code": 3,
                    "max_rain_probability_12h": 75,
                    "forecast": [
                        {"date": "Today", "temp_max": 26.0, "temp_min": 21.0, "condition": "Heavy Rain", "precipitation_sum": 12.5, "precipitation_probability": 85},
                        {"date": "Tomorrow", "temp_max": 25.0, "temp_min": 20.0, "condition": "Moderate Rain", "precipitation_sum": 8.0, "precipitation_probability": 75},
                        {"date": "Day After", "temp_max": 27.0, "temp_min": 22.0, "condition": "Partly Cloudy", "precipitation_sum": 0.5, "precipitation_probability": 30}
                    ]
                }
            elif scenario == "corn_common_rust":
                weather = {
                    "source": "demo_scenario",
                    "lat": lat,
                    "lon": lon,
                    "temp": 28.5,
                    "humidity": 55,
                    "wind_speed": 18.2,
                    "rain": 0.0,
                    "precipitation": 0.0,
                    "condition": "Partly Cloudy",
                    "weather_code": 2,
                    "max_rain_probability_12h": 10,
                    "forecast": [
                        {"date": "Today", "temp_max": 30.0, "temp_min": 22.0, "condition": "Partly Cloudy", "precipitation_sum": 0.0, "precipitation_probability": 10},
                        {"date": "Tomorrow", "temp_max": 29.0, "temp_min": 21.0, "condition": "Clear Sky", "precipitation_sum": 0.0, "precipitation_probability": 10},
                        {"date": "Day After", "temp_max": 28.0, "temp_min": 20.0, "condition": "Clear Sky", "precipitation_sum": 0.0, "precipitation_probability": 5}
                    ]
                }
            elif scenario == "rice_blast":
                weather = {
                    "source": "demo_scenario",
                    "lat": lat,
                    "lon": lon,
                    "temp": 34.5,
                    "humidity": 55,
                    "wind_speed": 6.5,
                    "rain": 0.0,
                    "precipitation": 0.0,
                    "condition": "Clear Sky",
                    "weather_code": 0,
                    "max_rain_probability_12h": 10,
                    "forecast": [
                        {"date": "Today", "temp_max": 36.0, "temp_min": 26.0, "condition": "Clear Sky", "precipitation_sum": 0.0, "precipitation_probability": 10},
                        {"date": "Tomorrow", "temp_max": 35.0, "temp_min": 25.0, "condition": "Clear Sky", "precipitation_sum": 0.0, "precipitation_probability": 10},
                        {"date": "Day After", "temp_max": 34.0, "temp_min": 24.0, "condition": "Clear Sky", "precipitation_sum": 0.0, "precipitation_probability": 5}
                    ]
                }
        else:
            weather = get_weather_data(lat, lon)
    except Exception as e:
        logger.error(f"Weather lookup failed: {e}")
        raise HTTPException(status_code=500, detail="Weather intelligence service failed.")
        
    # 4. Process Decision / Risk Advisory
    try:
        advisory = assess_treatment_conditions(diagnosis, weather)
    except Exception as e:
        logger.error(f"Decision engine failure: {e}")
        raise HTTPException(status_code=500, detail="Decision engine failed to generate advice.")

    # 5. Format and return response
    return {
        "success": True,
        "crop": crop,
        "location": {"lat": lat, "lon": lon},
        "diagnosis": diagnosis,
        "weather": weather,
        "advisory": advisory
    }

@app.get("/api/weather")
def fetch_weather(lat: float = 28.6139, lon: float = 77.2090):
    """Utility endpoint to fetch current weather independent of analysis."""
    try:
        return get_weather_data(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend build directory if it exists (for unified production deployment)
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))
if os.path.exists(frontend_dist):
    logger.info(f"Frontend dist found at {frontend_dist}. Mounting static assets.")
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    logger.warning("Frontend build directory ('../frontend/dist') not found. Serving API routes only.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
