"""
Test script to verify the implementation of the new structure management features
"""
import requests
import json
from datetime import datetime, date
import os

# Configuration
BASE_URL = "http://localhost:8000/api/v1"  # Adjust to your API URL
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Sample authentication token (you'll need to replace this with a real token)
TEST_TOKEN = os.environ.get("TEST_AUTH_TOKEN", "your-auth-token-here")
HEADERS["Authorization"] = f"Bearer {TEST_TOKEN}"

def test_barremage_endpoints():
    """Test the barremage cuves endpoints"""
    print("Testing barremage cuves endpoints...")
    
    # Test getting all barremages (should return list)
    try:
        response = requests.get(f"{BASE_URL}/barremage-cuves", headers=HEADERS)
        print(f"Get all barremages: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data.get('data', []))} barremage entries")
    except Exception as e:
        print(f"Error testing barremage endpoints: {e}")


def test_pompe_pistolet_endpoints():
    """Test the pompe and pistolet endpoints"""
    print("\nTesting pompe and pistolet endpoints...")
    
    # Test getting all pompes (should return list)
    try:
        response = requests.get(f"{BASE_URL}/pompes", headers=HEADERS)
        print(f"Get all pompes: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data.get('data', []))} pompe entries")
    except Exception as e:
        print(f"Error testing pompe endpoints: {e}")
    
    # Test getting all pistolets (should return list)
    try:
        response = requests.get(f"{BASE_URL}/pistolets", headers=HEADERS)
        print(f"Get all pistolets: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data.get('data', []))} pistolet entries")
    except Exception as e:
        print(f"Error testing pistolet endpoints: {e}")


def test_historique_prix_endpoints():
    """Test the historique prix endpoints"""
    print("\nTesting historique prix endpoints...")
    
    # Test getting historique prix carburants
    try:
        response = requests.get(f"{BASE_URL}/historique-prix-carburants", headers=HEADERS)
        print(f"Get historique prix carburants: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data.get('data', []))} historique prix carburant entries")
    except Exception as e:
        print(f"Error testing historique prix carburants endpoints: {e}")
    
    # Test getting historique prix articles
    try:
        response = requests.get(f"{BASE_URL}/historique-prix-articles", headers=HEADERS)
        print(f"Get historique prix articles: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data.get('data', []))} historique prix article entries")
    except Exception as e:
        print(f"Error testing historique prix articles endpoints: {e}")


def test_historique_index_pistolets_endpoint():
    """Test the historique index pistolets endpoint"""
    print("\nTesting historique index pistolets endpoint...")
    
    # Test getting historique index pistolets
    try:
        response = requests.get(f"{BASE_URL}/historique-index-pistolets", headers=HEADERS)
        print(f"Get historique index pistolets: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data.get('data', []))} historique index pistolet entries")
    except Exception as e:
        print(f"Error testing historique index pistolets endpoint: {e}")


def run_all_tests():
    """Run all tests"""
    print("Starting tests for new structure management features...\n")
    
    test_barremage_endpoints()
    test_pompe_pistolet_endpoints()
    test_historique_prix_endpoints()
    test_historique_index_pistolets_endpoint()
    
    print("\nTests completed!")


if __name__ == "__main__":
    run_all_tests()