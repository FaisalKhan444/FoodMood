from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from geopy.distance import geodesic
import folium
import webbrowser

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Assuming your model functions are already defined above
@app.get("/fast_food", response_class=HTMLResponse)
async def fast_food(request: Request):
    # Load restaurant data
    json_file = "food_panda_lhr_data.json"
    restaurants = load_data(json_file)

    # Get user's location (replace with actual implementation)
    user_location = get_location()
    if not user_location:
        return {"error": "User location not found"}

    # Get meal time and filter restaurants
    meal_time = get_meal_time()
    food_category = "Fast Food"  # Hardcoded for this route, or dynamically get from the user
    search_radius_km = 5.0  # Example radius
    filtered_results = filter_restaurants(user_location, meal_time, search_radius_km, food_category, restaurants)

    # If you want to show the map directly in the HTML response, save it as an HTML file
    if filtered_results:
        food_map = folium.Map(location=user_location, zoom_start=13)
        marker_cluster = MarkerCluster().add_to(food_map)
        for place in filtered_results:
            folium.Marker(
                location=[place["lat"], place["lon"]],
                popup=place["name"]
            ).add_to(marker_cluster)
        map_filename = "static/food_places_map.html"
        food_map.save(map_filename)
        
        return templates.TemplateResponse("fast_food.html", {"request": request, "map_filename": map_filename})

    return {"error": "No places found"}
