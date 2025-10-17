import requests
import time

BASE_URL = "http://localhost:5000/api"


def seed_user_data():
    print("🌱 Seeding user interaction data...")

    interactions = [
        # User 1 - Fitness Enthusiast
        ("user1", 2, "view"),  # Running Shoes
        ("user1", 4, "view"),  # Yoga Mat
        ("user1", 6, "view"),  # Smart Watch
        ("user1", 7, "view"),  # Protein Powder
        ("user1", 10, "view"),  # Water Bottle
        ("user1", 2, "purchase"),  # Buy Running Shoes
        ("user1", 4, "purchase"),  # Buy Yoga Mat

        # User 2 - Tech Professional
        ("user2", 1, "view"),  # Wireless Headphones
        ("user2", 5, "view"),  # Laptop Stand
        ("user2", 6, "view"),  # Smart Watch
        ("user2", 8, "view"),  # Desk Lamp
        ("user2", 9, "view"),  # Bluetooth Speaker
        ("user2", 5, "purchase"),  # Buy Laptop Stand
        ("user2", 8, "purchase"),  # Buy Desk Lamp

        # User 3 - Home Enthusiast
        ("user3", 3, "view"),  # Coffee Maker
        ("user3", 8, "view"),  # Desk Lamp
        ("user3", 3, "purchase"),  # Buy Coffee Maker
    ]

    for user_id, product_id, action in interactions:
        data = {
            "user_id": user_id,
            "product_id": product_id,
            "action": action
        }
        try:
            response = requests.post(f"{BASE_URL}/interaction", json=data)
            if response.status_code == 200:
                print(f"✅ Logged: {user_id} - {action} product {product_id}")
            time.sleep(0.1)  # Small delay to ensure order
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n✅ Data seeding complete!")
    print("\nTest the API:")
    print("  curl http://localhost:5000/api/recommendations/user1")
    print("  curl http://localhost:5000/api/recommendations/user2")
    print("  curl http://localhost:5000/api/recommendations/user3")


if __name__ == "__main__":
    try:
        seed_user_data()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API server")
        print("Make sure the Flask server is running: python app.py")