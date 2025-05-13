import requests
import json
from geopy.distance import geodesic
from datetime import datetime

# Load JSON data
def load_data(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        return []

# Get user's location from external HTML geolocation
def get_location():
    try:
        with open("user_location.json", "r") as f:
            data = json.load(f)
        lat, lng = float(data.get("latitude")), float(data.get("longitude"))
        print(f"User Location: Latitude {lat}, Longitude {lng}")
        return lat, lng
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"Error fetching location from user_location.json: {e}")
        return None

# Categorize food types
def categorize_food(food_list):
    if not food_list or not isinstance(food_list, list):
        return "Other"
    
    categories = {
        "Fast Food": ["Fast Food", "Burgers", "Pizza", "Sandwiches", "Fried Chicken", "Hot dogs", "Snacks-Street Food"],
        "Desi": ["Pakistani", "Karahi", "Tandoor", "Biryani", "Paratha", "Roll Paratha", "Nihari", "BBQ"],
        "Sweets": ["Desserts", "Ice Cream", "Cakes & Bakery", "Sweets", "Cupcakes", "Waffle", "Pancakes", "Crepes"],
        "Beverages": ["Beverage", "Juices", "Ice Cream Shakes", "Tea", "Coffee", "Lassi", "Smoothie Bowl"],
        "Chinese": ["Chinese", "Noodles", "Rice"],
        "Italian": ["Italian", "Pasta", "Thin Crust Pizza"],
        "American": ["American", "Steaks"],
        "Middle Eastern": ["Lebanese", "Middle Eastern", "Turkish"],
        "Other": ["Thai", "Japanese", "Mexican", "Afghani", "Singaporean", "Seafood", "Healthy", "International"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in food_list for keyword in keywords):
            return category
    return "Other"

# Get meal time
def get_meal_time():
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return "Breakfast"
    elif 12 <= current_hour < 18:
        return "Lunch"
    else:
        return "Dinner"

# Filter restaurants
def filter_restaurants(user_location, meal_time, search_radius_km, food_category, restaurants):
    filtered_places = []
    null_fields_log = []
    
    for place in restaurants:
        # Initialize place data with defaults
        place_data = {
            "name": place.get("name", "Unknown") if place.get("name") is not None else "Unknown",
            "lat": place.get("lat"),
            "lon": place.get("lon"),
            "food": place.get("food", ["Unknown"]) if place.get("food") is not None else ["Unknown"],
            "rating": place.get("rating(out of 5)", "N/A") if place.get("rating(out of 5)") is not None else "N/A",
            "rating_count": place.get("rating_count", 0) if place.get("rating_count") is not None else 0
        }
        
        # Log null fields
        null_fields = [key for key, value in place.items() if value is None]
        if null_fields:
            null_fields_log.append(f"Restaurant '{place_data['name']}': null fields - {', '.join(null_fields)}")
        
        # Validate location
        try:
            place_data["lat"] = float(place_data["lat"])
            place_data["lon"] = float(place_data["lon"])
        except (TypeError, ValueError):
            null_fields_log.append(f"Restaurant '{place_data['name']}': Invalid or null lat/lon")
            continue
        
        # Compute distance
        try:
            rest_location = (place_data["lat"], place_data["lon"])
            distance_km = geodesic(user_location, rest_location).km
        except (ValueError, TypeError) as e:
            null_fields_log.append(f"Restaurant '{place_data['name']}': Distance calculation failed - {e}")
            continue
        
        # Categorize food
        place_data["category"] = categorize_food(place_data["food"])
        
        # Filter by radius and category
        if (distance_km <= search_radius_km and 
            (food_category == "All" or place_data["category"] == food_category)):
            place_data["distance_km"] = round(distance_km, 2)
            filtered_places.append(place_data)
    
    # Sort by distance and rating
    filtered_places.sort(key=lambda x: (
        x["distance_km"],
        -float(x["rating"]) if x["rating"] not in ["N/A", None] else 0,
        -x["rating_count"] if x["rating_count"] else 0
    ))
    
    # Limit to top 50 for performance
    filtered_places = filtered_places[:50]
    
    # Print null fields log
    if null_fields_log:
        print("Null or Invalid Data Detected:")
        for log in null_fields_log:
            print(f" - {log}")
    
    return filtered_places

# Save filtered places to JSON
def save_places_to_json(places):
    if not places:
        print("No places to save to JSON.")
        return
    
    # Prepare data for JSON output
    output_data = [
        {
            "name": place["name"],
            "lat": place["lat"],
            "lon": place["lon"],
            "food": place["food"]
        }
        for place in places
    ]
    
    # Save to JSON file
    output_filename = "filtered_places.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        print(f"Filtered places saved to {output_filename}")
    except IOError as e:
        print(f"Error saving JSON file: {e}")

# Main execution
if __name__ == "__main__":
    # Load restaurant data
    json_file = "food_panda_lhr_data.json"
    restaurants = load_data(json_file)
    if not restaurants:
        print("No restaurant data loaded. Exiting.")
        exit()

    # Get user location
    user_location = get_location()
    if not user_location:
        print("Please ensure geolocation is enabled and user_location.json is available.")
        exit()

    # Get meal time
    meal_time = get_meal_time()
    print(f"Current Meal Time: {meal_time}")

    # Get user preferences
    print("Available Food Categories: All, Fast Food, Desi, Sweets, Beverages, Chinese, Italian, American, Middle Eastern, Other")
    food_category = input("Enter food category (or 'All'): ")
    if food_category not in ["All", "Fast Food", "Desi", "Sweets", "Beverages", "Chinese", "Italian", "American", "Middle Eastern", "Other"]:
        food_category = "All"
        print("Invalid category. Defaulting to 'All'.")

    try:
        search_radius_km = float(input("Enter search radius in km: "))
    except ValueError:
        print("Invalid input. Defaulting to 5 km.")
        search_radius_km = 5.0

    # Filter restaurants
    filtered_results = filter_restaurants(user_location, meal_time, search_radius_km, food_category, restaurants)

    if filtered_results:
        print(f"Found {len(filtered_results)} places within {search_radius_km} km for {food_category}.")
        save_places_to_json(filtered_results)
    else:
        print("No places found within the specified radius or category.")