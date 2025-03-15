-- Drop existing tables if they exist
DROP TABLE IF EXISTS food_recommendations;
DROP TABLE IF EXISTS user_profiles;

-- Create user_profiles table (extends auth.users)
CREATE TABLE user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create food_recommendations table to store recommendation history
CREATE TABLE food_recommendations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    climate TEXT NOT NULL,
    temperature DECIMAL NOT NULL,
    season TEXT NOT NULL,
    disease TEXT NOT NULL,
    recommended_food TEXT NOT NULL,
    nutritional_benefit TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_food_recommendations_user_id ON food_recommendations(user_id);
CREATE INDEX idx_food_recommendations_created_at ON food_recommendations(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_recommendations ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Allow new user registration
CREATE POLICY "Allow user registration" ON user_profiles
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view own recommendations" ON food_recommendations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own recommendations" ON food_recommendations
    FOR INSERT WITH CHECK (auth.uid() = user_id);