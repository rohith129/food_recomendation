from flask import Flask, request, render_template, redirect, url_for, session, flash
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
import urllib.parse
import re
import random

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Load the dataset
df = pd.read_excel("Food_Recommendation_Climate_Disease.xlsx")

# Common foods list (these should have corresponding images in static/images/foods/)
common_foods = [
    "Apple", "Avocado", "Banana", "Berries", "Broccoli", "Carrot", "Chicken", 
    "Cucumber", "Fish", "Garlic", "Ginger", "Grapes", "Green Tea", "Guava", 
    "Honey", "Kale", "Lemon", "Mango", "Nuts", "Oats", "Olive Oil", "Orange", 
    "Papaya", "Pineapple", "Spinach", "Turmeric", "Watermelon", "Yogurt"
]

# Food image dictionary
food_images = {
    "Apple": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?auto=format&w=500&h=350&fit=crop",
    "Avocado": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&w=500&h=350&fit=crop",
    "Banana": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&w=500&h=350&fit=crop",
    "Berries": "https://images.unsplash.com/photo-1563746924237-f4471479790f?auto=format&w=500&h=350&fit=crop",
    "Broccoli": "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?auto=format&w=500&h=350&fit=crop",
    "Carrot": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&w=500&h=350&fit=crop",
    "Chicken": "https://images.unsplash.com/photo-1587593810167-a84920ea0781?auto=format&w=500&h=350&fit=crop",
    "Cucumber": "https://images.unsplash.com/photo-1566486189376-d5f21e25aae4?auto=format&w=500&h=350&fit=crop",
    "Fish": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&w=500&h=350&fit=crop",
    "Garlic": "https://images.unsplash.com/photo-1615478503562-ec2d8aa0e24e?auto=format&w=500&h=350&fit=crop",
    "Ginger": "https://images.unsplash.com/photo-1603604136878-53288037f9fe?auto=format&w=500&h=350&fit=crop",
    "Grapes": "https://images.unsplash.com/photo-1596363505729-4190a9506133?auto=format&w=500&h=350&fit=crop",
    "Green Tea": "https://images.unsplash.com/photo-1627435601361-ec25f5b1d0e5?auto=format&w=500&h=350&fit=crop",
    "Guava": "https://images.unsplash.com/photo-1536511132770-e5058c7e8c46?auto=format&w=500&h=350&fit=crop",
    "Honey": "https://images.unsplash.com/photo-1587049352851-8d4e89133924?auto=format&w=500&h=350&fit=crop",
    "Kale": "https://images.unsplash.com/photo-1515192458632-28d43f54dc04?auto=format&w=500&h=350&fit=crop",
    "Lemon": "https://images.unsplash.com/photo-1590502593747-42a996133562?auto=format&w=500&h=350&fit=crop",
    "Mango": "https://images.unsplash.com/photo-1605027990121-cbae9e0642df?auto=format&w=500&h=350&fit=crop",
    "Nuts": "https://images.unsplash.com/photo-1611413784787-775b466e5089?auto=format&w=500&h=350&fit=crop",
    "Oats": "https://images.unsplash.com/photo-1586201695753-01738f7a8127?auto=format&w=500&h=350&fit=crop",
    "Olive Oil": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&w=500&h=350&fit=crop",
    "Orange": "https://images.unsplash.com/photo-1611080626919-7cf5a9041525?auto=format&w=500&h=350&fit=crop",
    "Papaya": "https://images.unsplash.com/photo-1526318472351-c75fcf070305?auto=format&w=500&h=350&fit=crop",
    "Pineapple": "https://images.unsplash.com/photo-1589820296156-2454bb08ddab?auto=format&w=500&h=350&fit=crop",
    "Spinach": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&w=500&h=350&fit=crop",
    "Turmeric": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&w=500&h=350&fit=crop",
    "Watermelon": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&w=500&h=350&fit=crop",
    "Yogurt": "https://images.unsplash.com/photo-1604877610233-dd3bd77fc3b7?auto=format&w=500&h=350&fit=crop",
}

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # More secure secret key

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session["user_id"] = response.user.id
            return redirect(url_for("home"))
        except Exception as e:
            flash("Invalid email or password")
            return redirect(url_for("login"))
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        # Basic validation
        if not email or not password or not confirm_password:
            flash("All fields are required")
            return redirect(url_for("register"))
            
        # Email format validation
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            flash("Please enter a valid email address")
            return redirect(url_for("register"))
            
        # Password validation
        if len(password) < 8:
            flash("Password must be at least 8 characters long")
            return redirect(url_for("register"))
            
        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("register"))
        
        try:
            # Attempt to create auth user
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "email": email
                    }
                }
            })
            
            if not auth_response.user:
                flash("Registration failed. Please try again.")
                return redirect(url_for("register"))
            
            # Create user profile
            profile_data = {
                "id": auth_response.user.id,
                "email": email
            }
            
            profile_response = supabase.table("user_profiles").insert(profile_data).execute()
            
            if not profile_response.data:
                # If profile creation fails, attempt to delete the auth user
                try:
                    supabase.auth.admin.delete_user(auth_response.user.id)
                except Exception as cleanup_error:
                    print(f"Failed to cleanup auth user: {cleanup_error}")
                flash("Registration failed. Please try again.")
                return redirect(url_for("register"))
            
            session["registration_success"] = True
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
                
        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                flash("This email is already registered")
            elif "password" in error_msg.lower():
                flash("Password is too weak. Please use a stronger password")
            else:
                print(f"Registration error: {error_msg}")
                flash("Registration failed. Please try again.")
            return redirect(url_for("register"))
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    # Generate random default values for the form
    climates = ["Humid", "Cold", "Hot", "Dry", "Moderate"]
    seasons = ["Summer", "Winter", "Spring", "Autumn"]
    diseases = [
        "Acid Reflux", "Allergies", "Anemia", "Anxiety", "Arthritis", 
        "Asthma", "Cancer", "Cold", "Constipation", "Depression", 
        "Diabetes", "Flu", "Heart Disease", "Heat Stroke", 
        "High Cholesterol", "Hypertension", "IBS", "Migraine", 
        "Obesity", "Osteoporosis"
    ]
    
    default_values = {
        "climate": random.choice(climates),
        "temperature": round(random.uniform(-10, 40), 1),  # Random temperature between -10 and 40°C
        "season": random.choice(seasons),
        "disease": random.choice(diseases)
    }
    
    return render_template("index.html", defaults=default_values)

@app.route("/predict", methods=["POST"])
def predict():
    # Get input data from the form
    climate = request.form["climate"]
    temperature = float(request.form["temperature"])
    season = request.form["season"]
    disease = request.form["disease"]

    # Validate temperature range
    if temperature < -20 or temperature > 50:
        flash("Temperature must be between -20°C and 50°C for accurate recommendations.")
        return redirect(url_for("home"))

    # Filter the dataset based on input conditions
    filtered_df = df[
        (df['Climate'] == climate) &
        (df['Season'] == season) &
        (df['Disease'] == disease)
    ]

    # If no exact match, find the closest temperature match
    if len(filtered_df) == 0:
        filtered_df = df[
            (df['Climate'] == climate) &
            (df['Season'] == season) &
            (df['Disease'] == disease)
        ]
        # Find the row with the closest temperature
        if len(filtered_df) > 0:
            filtered_df['temp_diff'] = abs(filtered_df['Temperature (°C)'] - temperature)
            filtered_df = filtered_df.sort_values('temp_diff').head(1)

    if len(filtered_df) > 0:
        recommended_food = filtered_df['Recommended Food'].iloc[0]
        nutritional_benefit = filtered_df['Nutritional Benefit'].iloc[0]
    else:
        recommended_food = "No specific recommendation found"
        nutritional_benefit = "Please try different combinations"

    # Store the results in session
    session["climate"] = climate
    session["temperature"] = temperature
    session["season"] = season
    session["disease"] = disease
    session["recommended_food"] = recommended_food
    session["nutritional_benefit"] = nutritional_benefit

    # Redirect to the result page
    return redirect(url_for("result"))

@app.route("/result")
def result():
    # Retrieve the stored session data
    recommended_food = session.get("recommended_food")
    
    # Get image URL for the recommended food
    food_image_url = None
    
    # Convert recommended food to a URL-friendly filename
    if recommended_food:
        # Check if we have a local image
        food_filename = re.sub(r'[^a-zA-Z0-9]', '_', recommended_food.lower()) + '.jpg'
        local_path = f'static/images/foods/{food_filename}'
        
        if os.path.exists(local_path):
            # Use local image if available
            food_image_url = url_for('static', filename=f'images/foods/{food_filename}')
        else:
            # Fallback to unsplash for foods without local images
            encoded_food = urllib.parse.quote_plus(recommended_food)
            food_image_url = f"https://source.unsplash.com/500x350/?{encoded_food},food"
    
    return render_template("result.html",
                           climate=session.get("climate"),
                           temperature=session.get("temperature"),
                           season=session.get("season"),
                           disease=session.get("disease"),
                           recommended_food=recommended_food,
                           nutritional_benefit=session.get("nutritional_benefit"),
                           food_image_url=food_image_url)

if __name__ == "__main__":
    app.run(debug=True)
