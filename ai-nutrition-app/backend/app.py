from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS

# In-memory database (replace with real DB in production)
users_db = {}
meals_db = {}

@app.route('/api/analyze', methods=['POST'])
def analyze_meal():
    """Analyze a meal and return nutritional information"""
    try:
        data = request.json
        
        # Extract food items
        food_items = data.get('food_items', [])
        
        # Simple nutrition calculation (in real app, use nutrition database)
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        
        for item in food_items:
            # Mock nutrition values based on food name
            food_name = item['name'].lower()
            quantity = item.get('quantity', 1)
            
            if 'apple' in food_name or 'banana' in food_name:
                total_calories += 100 * quantity
                total_protein += 0.5 * quantity
                total_carbs += 25 * quantity
            elif 'chicken' in food_name:
                total_calories += 200 * quantity
                total_protein += 30 * quantity
                total_fats += 10 * quantity
            elif 'rice' in food_name or 'pasta' in food_name:
                total_calories += 150 * quantity
                total_carbs += 35 * quantity
                total_protein += 3 * quantity
            elif 'salad' in food_name or 'vegetable' in food_name:
                total_calories += 50 * quantity
                total_protein += 2 * quantity
                total_carbs += 10 * quantity
            else:
                total_calories += 150 * quantity
                total_protein += 5 * quantity
                total_carbs += 20 * quantity
        
        # Calculate health risk
        user_bmi = calculate_bmi(data.get('weight', 70), data.get('height', 170))
        risk_score = 0
        
        if total_calories > 800:
            risk_score += 1
        if total_fats > 30:
            risk_score += 1
        
        risk_levels = ['Low Risk', 'Medium Risk', 'High Risk']
        risk_level = risk_levels[min(risk_score, 2)]
        
        # Generate recommendations
        recommendations = []
        if total_protein < 20:
            recommendations.append("Add more protein sources like chicken, fish, or beans")
        if total_calories > 600:
            recommendations.append("Consider smaller portion sizes for weight management")
        if len(food_items) < 3:
            recommendations.append("Try to include more food variety for balanced nutrition")
        
        if not recommendations:
            recommendations.append("Great meal choice! Well balanced.")
        
        # Prepare response
        response = {
            'analysis': {
                'nutrition_analysis': {
                    'calories': round(total_calories),
                    'protein': round(total_protein, 1),
                    'carbs': round(total_carbs, 1),
                    'fats': round(total_fats, 1),
                    'fiber': round(total_carbs * 0.1, 1)
                },
                'health_risk': {
                    'level': risk_level,
                    'score': risk_score,
                    'details': f'Based on {len(food_items)} food items with {round(total_calories)} calories'
                },
                'bmi': {
                    'value': round(user_bmi, 1),
                    'category': get_bmi_category(user_bmi)
                },
                'daily_targets': {
                    'calories': 2200,
                    'protein': 90,
                    'carbs': 275,
                    'fats': 73,
                    'fiber': 30
                },
                'recommendations': recommendations,
                'meal_score': max(0, min(100, 100 - (risk_score * 15))),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Save meal to database
        user_id = data.get('user_id', 'anonymous')
        if user_id not in meals_db:
            meals_db[user_id] = []
        
        meals_db[user_id].append({
            'foods': food_items,
            'analysis': response['analysis'],
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def calculate_bmi(weight, height):
    """Calculate BMI"""
    height_m = height / 100  # Convert cm to meters
    return weight / (height_m ** 2)

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

@app.route('/api/user-data/<user_id>', methods=['GET'])
def get_user_data(user_id):
    """Get user dashboard data"""
    # Mock user data
    user_data = {
        'user_profile': {
            'username': 'John Doe',
            'age': 30,
            'weight': 75,
            'height': 175,
            'goal': 'Maintain Weight',
            'activity_level': 'Moderately Active'
        },
        'current_status': {
            'bmi': {'value': 24.5, 'category': 'Normal'},
            'weight_trend': -0.5,
            'weekly_progress': 75
        },
        'history': {
            'last_7_days': {
                'avg_calories': 2150,
                'meals_logged': len(meals_db.get(user_id, [])),
                'avg_health_score': 82,
                'water_intake': 2.1
            }
        }
    }
    
    # Calculate real stats if meals exist
    if user_id in meals_db:
        user_meals = meals_db[user_id]
        if user_meals:
            total_calories = sum(m['analysis']['nutrition_analysis']['calories'] for m in user_meals)
            avg_calories = total_calories / len(user_meals)
            user_data['history']['last_7_days']['avg_calories'] = round(avg_calories)
            user_data['history']['last_7_days']['meals_logged'] = len(user_meals)
    
    return jsonify(user_data)

@app.route('/api/save-meal', methods=['POST'])
def save_meal():
    """Save a meal to user's history"""
    try:
        data = request.json
        user_id = data.get('user_id')
        meal_data = data.get('meal')
        
        if not user_id or not meal_data:
            return jsonify({'error': 'Missing user_id or meal data'}), 400
        
        if user_id not in meals_db:
            meals_db[user_id] = []
        
        meals_db[user_id].append({
            **meal_data,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'message': 'Meal saved successfully',
            'total_meals': len(meals_db[user_id])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/community-health', methods=['GET'])
def get_community_health():
    """Get community health statistics"""
    community_data = {
        'community_analysis': {
            'community_stats': {
                'sample_size': 1542,
                'avg_bmi': 25.8,
                'obesity_rate': 28.5,
                'avg_health_score': 76,
                'health_risk_distribution': {
                    'low_risk': 65,
                    'medium_risk': 25,
                    'high_risk': 10
                }
            }
        },
        'regional_data': {
            'North America': {'obesity_rate': 32.5, 'avg_bmi': 26.2},
            'Europe': {'obesity_rate': 22.8, 'avg_bmi': 24.8},
            'Asia': {'obesity_rate': 18.2, 'avg_bmi': 23.5}
        },
        'recent_posts': [
            {
                'id': 1,
                'user': 'Sarah M.',
                'content': 'Just completed my first week of healthy eating! Feeling great!',
                'likes': 24,
                'comments': 8,
                'timestamp': '2023-10-15T10:30:00'
            }
        ]
    }
    return jsonify(community_data)

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # Simple validation (in real app, use database)
    if email and password:
        user_id = email.replace('@', '_').replace('.', '_')
        
        # Create user if doesn't exist
        if user_id not in users_db:
            users_db[user_id] = {
                'email': email,
                'name': email.split('@')[0].title(),
                'joined': datetime.now().isoformat()
            }
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'name': users_db[user_id]['name'],
                'email': email
            },
            'token': 'mock-jwt-token'  # In real app, use JWT
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    """User registration"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Missing email or password'}), 400
    
    user_id = email.replace('@', '_').replace('.', '_')
    
    if user_id in users_db:
        return jsonify({'success': False, 'error': 'User already exists'}), 400
    
    # Create new user
    users_db[user_id] = {
        'email': email,
        'name': name or email.split('@')[0].title(),
        'joined': datetime.now().isoformat(),
        'profile': {
            'age': data.get('age', 25),
            'weight': data.get('weight', 70),
            'height': data.get('height', 170),
            'goal': 'Maintain Weight'
        }
    }
    
    return jsonify({
        'success': True,
        'user': {
            'id': user_id,
            'name': users_db[user_id]['name'],
            'email': email
        },
        'message': 'Registration successful'
    })

if __name__ == '__main__':
    print("Starting Nutrition API server...")
    print("API available at: http://localhost:5000")
    print("Endpoints:")
    print("  POST /api/analyze - Analyze a meal")
    print("  GET  /api/user-data/<user_id> - Get user data")
    print("  POST /api/save-meal - Save a meal")
    print("  GET  /api/community-health - Get community data")
    print("  POST /api/login - User login")
    print("  POST /api/register - User registration")
    app.run(debug=True, port=5000)