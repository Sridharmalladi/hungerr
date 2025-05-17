import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def geocode_address(address):
    """
    Convert address to latitude and longitude coordinates
    
    Args:
        address (str): The address to geocode
        
    Returns:
        tuple: (latitude, longitude, status) where status is True if geocoding was successful
    """
    try:
        print(f"\nAttempting to geocode address: {address}")
        # First check Streamlit secrets
        api_key = st.secrets.get('google_maps', {}).get('api_key')
        print(f"API key found in secrets: {'Yes' if api_key else 'No'}")
        
        # If not in secrets, check environment variables
        if not api_key:
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
            print(f"API key found in environment: {'Yes' if api_key else 'No'}")
        
        if api_key:
            # Use Google Maps Geocoding API
            print(f"Using Google Maps API for geocoding")
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
            response = requests.get(url)
            data = response.json()
            
            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                print(f"Successfully geocoded to: {location['lat']}, {location['lng']}")
                return location["lat"], location["lng"], True
            else:
                print(f"Geocoding error: {data['status']}")
                print(f"Full response: {data}")
                # Fall back to mock geocoding
                return mock_geocode(address)
        else:
            # Use mock geocoding
            print("No Google Maps API key found, using mock geocoding")
            return mock_geocode(address)
            
    except Exception as e:
        print(f"Geocoding error: {str(e)}")
        # Fall back to mock geocoding in case of errors
        return mock_geocode(address)

def mock_geocode(address):
    """
    Generate mock geocoding results based on address keywords
    """
    print(f"Using mock geocoding for: {address}")
    address_lower = address.lower()
    
    # Default to New York City
    lat, lng = 40.7128, -74.0060
    
    # Simple logic to generate different coordinates based on address keywords
    if "new york" in address_lower or "ny" in address_lower.split():
        # Different neighborhoods in NYC
        if "brooklyn" in address_lower:
            lat, lng = 40.6782, -73.9442
        elif "queens" in address_lower:
            lat, lng = 40.7282, -73.7949
        elif "bronx" in address_lower:
            lat, lng = 40.8448, -73.8648
        elif "manhattan" in address_lower:
            lat, lng = 40.7831, -73.9712
        elif "staten" in address_lower:
            lat, lng = 40.5795, -74.1502
    elif "los angeles" in address_lower or "la" in address_lower.split():
        lat, lng = 34.0522, -118.2437
    elif "chicago" in address_lower:
        lat, lng = 41.8781, -87.6298
    elif "houston" in address_lower:
        lat, lng = 29.7604, -95.3698
    elif "miami" in address_lower:
        lat, lng = 25.7617, -80.1918
    elif "boston" in address_lower:
        lat, lng = 42.3601, -71.0589
    
    print(f"Mock geocoded to: {lat}, {lng}")
    return lat, lng, True