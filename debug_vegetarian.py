#!/usr/bin/env python3
"""
Análise detalhada da dieta vegetariana para debug
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://fitfood-debug.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def create_vegetarian_user():
    """Cria usuário vegetariano e analisa dieta detalhadamente"""
    
    # 1. Signup
    signup_data = {
        "email": f"debug_vegetariano_{int(datetime.now().timestamp())}@test.com",
        "password": "TestPass123!"
    }
    
    signup_response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, headers=HEADERS)
    if signup_response.status_code != 200:
        print(f"❌ Signup failed: {signup_response.text}")
        return
    
    user_data = signup_response.json()
    user_id = user_data.get("user_id")
    print(f"✅ User created: {user_id}")
    
    # 2. Create Profile
    profile_data = {
        "id": user_id,
        "name": "Debug Vegetariano",
        "age": 30,
        "sex": "masculino",
        "height": 175.0,
        "weight": 70.0,
        "goal": "bulking",
        "training_level": "intermediario",
        "weekly_training_frequency": 4,
        "available_time_per_session": 60,
        "dietary_restrictions": ["vegetariano"],
        "food_preferences": ["ovos", "arroz_branco", "feijao", "banana", "castanhas", "azeite", "tofu"],
        "meal_count": 6
    }
    
    profile_response = requests.post(f"{BASE_URL}/user/profile", json=profile_data, headers=HEADERS)
    if profile_response.status_code != 200:
        print(f"❌ Profile creation failed: {profile_response.text}")
        return
    
    print(f"✅ Profile created successfully")
    
    # 3. Generate Diet
    diet_response = requests.post(f"{BASE_URL}/diet/generate?user_id={user_id}", headers=HEADERS)
    if diet_response.status_code != 200:
        print(f"❌ Diet generation failed: {diet_response.text}")
        return
    
    diet_data = diet_response.json()
    print(f"✅ Diet generated successfully")
    
    # 4. Análise detalhada
    print("\n📋 ANÁLISE DETALHADA DA DIETA VEGETARIANA")
    print("=" * 60)
    
    total_protein = 0
    total_calories = 0
    
    for i, meal in enumerate(diet_data.get("meals", [])):
        meal_name = meal.get("name", f"Refeição {i+1}")
        meal_time = meal.get("time", "N/A")
        
        print(f"\n🍽️ {meal_name} ({meal_time})")
        print("-" * 40)
        
        meal_protein = 0
        meal_calories = 0
        
        for food in meal.get("foods", []):
            name = food.get("name", "N/A")
            grams = food.get("grams", 0)
            protein = food.get("protein", 0)
            carbs = food.get("carbs", 0)
            fat = food.get("fat", 0)
            calories = food.get("calories", 0)
            
            print(f"  • {name}: {grams}g (P:{protein}g C:{carbs}g F:{fat}g = {calories}kcal)")
            
            meal_protein += protein
            meal_calories += calories
            total_protein += protein
            total_calories += calories
        
        print(f"  📊 Total da refeição: {meal_protein}g proteína, {meal_calories}kcal")
    
    print(f"\n🎯 TOTAIS FINAIS:")
    print(f"  Proteína total: {total_protein}g")
    print(f"  Calorias totais: {total_calories}kcal")
    
    # 5. Verificações específicas
    print(f"\n🔍 VERIFICAÇÕES ESPECÍFICAS:")
    
    # Buscar tofu
    tofu_found = False
    tofu_locations = []
    for meal in diet_data.get("meals", []):
        for food in meal.get("foods", []):
            if "tofu" in food.get("name", "").lower() or "tofu" in food.get("key", "").lower():
                tofu_found = True
                tofu_locations.append(f"{meal.get('name')} - {food.get('name')} ({food.get('grams')}g)")
    
    if tofu_found:
        print(f"  ✅ Tofu encontrado: {'; '.join(tofu_locations)}")
    else:
        print(f"  ❌ Tofu NÃO encontrado na dieta")
    
    # Buscar carnes (não deveria ter)
    meat_keywords = ["frango", "chicken", "patinho", "beef", "carne", "tilapia", "fish", "peixe", "salmao", "peru"]
    meat_found = []
    for meal in diet_data.get("meals", []):
        for food in meal.get("foods", []):
            food_name = food.get("name", "").lower()
            food_key = food.get("key", "").lower()
            for meat in meat_keywords:
                if meat in food_name or meat in food_key:
                    meat_found.append(f"{meal.get('name')} - {food.get('name')} ({food.get('grams')}g)")
    
    if meat_found:
        print(f"  ❌ CARNES ENCONTRADAS (VIOLAÇÃO): {'; '.join(meat_found)}")
    else:
        print(f"  ✅ Nenhuma carne encontrada (correto para vegetariano)")
    
    # Verificar ovos
    eggs_locations = []
    for meal in diet_data.get("meals", []):
        for food in meal.get("foods", []):
            if "ovo" in food.get("name", "").lower() or "egg" in food.get("name", "").lower():
                eggs_locations.append(f"{meal.get('name')} - {food.get('name')} ({food.get('grams')}g)")
    
    if eggs_locations:
        print(f"  🥚 Ovos encontrados: {'; '.join(eggs_locations)}")
    else:
        print(f"  ❌ Ovos NÃO encontrados")
    
    # Verificar proteína adequada
    if total_protein >= 100:
        print(f"  ✅ Proteína adequada: {total_protein}g (≥100g)")
    else:
        print(f"  ❌ Proteína insuficiente: {total_protein}g (mínimo 100g)")
    
    return user_id, diet_data

if __name__ == "__main__":
    create_vegetarian_user()