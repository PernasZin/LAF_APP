#!/usr/bin/env python3
"""
Test específico para investigar por que tofu não aparece na dieta vegetariana
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://fitness-timer-pro.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def test_tofu_issue():
    """Testa especificamente o problema do tofu"""
    
    # 1. Signup
    signup_data = {
        "email": f"tofu_test_{int(datetime.now().timestamp())}@test.com",
        "password": "TestPass123!"
    }
    
    signup_response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, headers=HEADERS)
    if signup_response.status_code != 200:
        print(f"❌ Signup failed: {signup_response.text}")
        return
    
    user_data = signup_response.json()
    user_id = user_data.get("user_id")
    print(f"✅ User created: {user_id}")
    
    # 2. Create Profile with explicit tofu preference
    profile_data = {
        "id": user_id,
        "name": "Tofu Test User",
        "age": 30,
        "sex": "masculino",
        "height": 175.0,
        "weight": 70.0,
        "goal": "bulking",
        "training_level": "intermediario",
        "weekly_training_frequency": 4,
        "available_time_per_session": 60,
        "dietary_restrictions": ["vegetariano"],
        "food_preferences": ["tofu", "ovos", "arroz_branco", "feijao", "banana"],  # tofu first!
        "meal_count": 6
    }
    
    profile_response = requests.post(f"{BASE_URL}/user/profile", json=profile_data, headers=HEADERS)
    if profile_response.status_code != 200:
        print(f"❌ Profile creation failed: {profile_response.text}")
        return
    
    print(f"✅ Profile created with tofu as first preference")
    
    # 3. Generate Diet multiple times to see consistency
    for i in range(3):
        print(f"\n🧪 TESTE {i+1}/3 - Geração de dieta")
        
        diet_response = requests.post(f"{BASE_URL}/diet/generate?user_id={user_id}", headers=HEADERS)
        if diet_response.status_code != 200:
            print(f"❌ Diet generation failed: {diet_response.text}")
            continue
        
        diet_data = diet_response.json()
        
        # Analisa presença de tofu
        tofu_found = []
        total_protein = 0
        
        for meal in diet_data.get("meals", []):
            meal_name = meal.get("name", "Unknown")
            for food in meal.get("foods", []):
                if "tofu" in food.get("name", "").lower() or "tofu" in food.get("key", "").lower():
                    tofu_found.append(f"{meal_name}: {food.get('name')} ({food.get('grams')}g, {food.get('protein')}g prot)")
                total_protein += food.get("protein", 0)
        
        if tofu_found:
            print(f"  ✅ Tofu encontrado: {'; '.join(tofu_found)}")
        else:
            print(f"  ❌ Tofu NÃO encontrado")
        
        print(f"  📊 Proteína total: {total_protein}g")
        
        # Lista todas as proteínas encontradas
        protein_sources = []
        for meal in diet_data.get("meals", []):
            for food in meal.get("foods", []):
                if food.get("protein", 0) > 5:  # Considera fonte proteica se >5g
                    protein_sources.append(f"{food.get('name')} ({food.get('protein')}g)")
        
        print(f"  🥩 Fontes proteicas: {'; '.join(set(protein_sources))}")

if __name__ == "__main__":
    test_tofu_issue()