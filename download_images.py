"""
Script to download food images from Unsplash and save them locally.
This only needs to be run once to set up the local image library.
"""

import os
import re
import requests
import time

# Create directory if it doesn't exist
os.makedirs('static/images/foods', exist_ok=True)

# Common foods list and their Unsplash image URLs (updated with working URLs)
food_images = {
    # Images that downloaded successfully keep their original URLs
    "Apple": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?auto=format&w=500&h=350&fit=crop",
    "Avocado": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&w=500&h=350&fit=crop",
    "Banana": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&w=500&h=350&fit=crop",
    "Broccoli": "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?auto=format&w=500&h=350&fit=crop",
    "Carrot": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&w=500&h=350&fit=crop",
    "Chicken": "https://images.unsplash.com/photo-1587593810167-a84920ea0781?auto=format&w=500&h=350&fit=crop",
    "Cucumber": "https://images.unsplash.com/photo-1566486189376-d5f21e25aae4?auto=format&w=500&h=350&fit=crop",
    "Fish": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&w=500&h=350&fit=crop",
    "Garlic": "https://images.unsplash.com/photo-1615478503562-ec2d8aa0e24e?auto=format&w=500&h=350&fit=crop",
    "Grapes": "https://images.unsplash.com/photo-1596363505729-4190a9506133?auto=format&w=500&h=350&fit=crop",
    "Green Tea": "https://images.unsplash.com/photo-1627435601361-ec25f5b1d0e5?auto=format&w=500&h=350&fit=crop",
    "Guava": "https://images.unsplash.com/photo-1536511132770-e5058c7e8c46?auto=format&w=500&h=350&fit=crop",
    "Honey": "https://images.unsplash.com/photo-1587049352851-8d4e89133924?auto=format&w=500&h=350&fit=crop",
    "Lemon": "https://images.unsplash.com/photo-1590502593747-42a996133562?auto=format&w=500&h=350&fit=crop",
    "Mango": "https://images.unsplash.com/photo-1605027990121-cbae9e0642df?auto=format&w=500&h=350&fit=crop",
    "Olive Oil": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&w=500&h=350&fit=crop",
    "Papaya": "https://images.unsplash.com/photo-1526318472351-c75fcf070305?auto=format&w=500&h=350&fit=crop",
    "Spinach": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&w=500&h=350&fit=crop",
    "Turmeric": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&w=500&h=350&fit=crop",
    "Watermelon": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&w=500&h=350&fit=crop",
    
    # Updated URLs for images that failed
    "Berries": "https://images.unsplash.com/photo-1591287083773-9a102f5ecece?auto=format&w=500&h=350&fit=crop",
    "Ginger": "https://images.unsplash.com/photo-1615485500834-bc10199bc727?auto=format&w=500&h=350&fit=crop",
    "Kale": "https://images.unsplash.com/photo-1524179091875-bf99a9a6af57?auto=format&w=500&h=350&fit=crop",
    "Nuts": "https://images.unsplash.com/photo-1570651851409-93d5add773d7?auto=format&w=500&h=350&fit=crop",
    "Oats": "https://images.unsplash.com/photo-1614961233913-a5113a4a34ed?auto=format&w=500&h=350&fit=crop",
    "Orange": "https://images.unsplash.com/photo-1582979512210-99b6a53386f9?auto=format&w=500&h=350&fit=crop",
    "Pineapple": "https://images.unsplash.com/photo-1550258987-190a2d41a8ba?auto=format&w=500&h=350&fit=crop",
    "Yogurt": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&w=500&h=350&fit=crop",
}

# Download each image and save it locally
count = 0
for food, url in food_images.items():
    count += 1
    print(f"Downloading image {count}/{len(food_images)}: {food}")
    
    # Create a filename-friendly version of the food name
    filename = re.sub(r'[^a-zA-Z0-9]', '_', food.lower()) + '.jpg'
    filepath = os.path.join('static/images/foods', filename)
    
    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"  - Skipping {filename} (already exists)")
        continue
    
    try:
        # Download the image
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Save the image
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"  - Saved {filename}")
        
        # Respect Unsplash's rate limits (max 50 requests per hour)
        time.sleep(1.5)
        
    except Exception as e:
        print(f"  - Error downloading {food}: {e}")

print(f"\nDownloaded {count} food images to static/images/foods/") 