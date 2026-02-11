#!/usr/bin/env python3
"""
Debug do teste original vegetariano para entender por que tofu não aparece
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "https://macro-safety-caps.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def debug_original_vegetarian():
    """Reproduz exatamente o teste original que falhou"""
    
    # Exatamente como no teste original
    signup_data = {
        "email": f"vegetariano_{int(time.time())}@test.com",
        "password": "TestPass123!"
    }
    
    signup_response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, headers=HEADERS)
    if signup_response.status_code != 200:
        print(f"❌ Signup failed: {signup_response.text}")
        return
    
    user_data = signup_response.json()
    user_id = user_data.get("user_id")
    print(f"✅ User created: {user_id}")
    
    # Exatamente como no teste original
    profile_data = {
        "id": user_id,
        "name": "Test Vegetariano",
        "age": 30,
        "sex": "masculino",
        "height": 175.0,
        "weight": 70.0,
        "goal": "bulking",
        "training_level": "intermediario",
        "weekly_training_frequency": 4,
        "available_time_per_session": 60,
        "dietary_restrictions": ["vegetariano"],
        "food_preferences": ["ovos", "arroz_branco", "feijao", "banana", "castanhas", "azeite"],  # SEM tofu!
        "meal_count": 6
    }
    
    profile_response = requests.post(f"{BASE_URL}/user/profile", json=profile_data, headers=HEADERS)
    if profile_response.status_code != 200:
        print(f"❌ Profile creation failed: {profile_response.text}")
        return
    
    print(f"✅ Profile created (SEM tofu nas preferências)")
    print(f"📋 Preferências: {profile_data['food_preferences']}")
    print(f"🚫 Restrições: {profile_data['dietary_restrictions']}")
    
    # Generate Diet
    diet_response = requests.post(f"{BASE_URL}/diet/generate?user_id={user_id}", headers=HEADERS)
    if diet_response.status_code != 200:
        print(f"❌ Diet generation failed: {diet_response.text}")
        return
    
    diet_data = diet_response.json()
    print(f"✅ Diet generated")
    
    # Análise detalhada
    print(f"\n🔍 ANÁLISE DETALHADA:")
    
    tofu_found = []
    total_protein = 0
    all_proteins = []
    
    for meal in diet_data.get("meals", []):
        meal_name = meal.get("name", "Unknown")
        print(f"\n🍽️ {meal_name}:")
        
        for food in meal.get("foods", []):
            name = food.get("name", "")
            grams = food.get("grams", 0)
            protein = food.get("protein", 0)
            
            print(f"  • {name}: {grams}g ({protein}g prot)")
            
            if "tofu" in name.lower():
                tofu_found.append(f"{meal_name}: {name} ({grams}g)")
            
            if protein > 5:
                all_proteins.append(f"{name} ({protein}g)")
            
            total_protein += protein
    
    print(f"\n📊 RESULTADOS:")
    print(f"  Proteína total: {total_protein}g")
    print(f"  Tofu encontrado: {tofu_found if tofu_found else 'NENHUM'}")
    print(f"  Todas as proteínas: {'; '.join(set(all_proteins))}")
    
    # Agora teste com tofu nas preferências
    print(f"\n" + "="*60)
    print(f"🧪 TESTE COMPARATIVO: ADICIONANDO TOFU NAS PREFERÊNCIAS")
    
    # Update profile to include tofu
    profile_data["food_preferences"] = ["tofu", "ovos", "arroz_branco", "feijao", "banana", "castanhas", "azeite"]
    
    profile_response2 = requests.post(f"{BASE_URL}/user/profile", json=profile_data, headers=HEADERS)
    if profile_response2.status_code != 200:
        print(f"❌ Profile update failed: {profile_response2.text}")
        return
    
    print(f"✅ Profile updated COM tofu nas preferências")
    print(f"📋 Novas preferências: {profile_data['food_preferences']}")
    
    # Generate new diet
    diet_response2 = requests.post(f"{BASE_URL}/diet/generate?user_id={user_id}", headers=HEADERS)
    if diet_response2.status_code != 200:
        print(f"❌ Diet generation 2 failed: {diet_response2.text}")
        return
    
    diet_data2 = diet_response2.json()
    print(f"✅ New diet generated")
    
    # Análise da nova dieta
    tofu_found2 = []
    total_protein2 = 0
    all_proteins2 = []
    
    for meal in diet_data2.get("meals", []):
        meal_name = meal.get("name", "Unknown")
        
        for food in meal.get("foods", []):
            name = food.get("name", "")
            grams = food.get("grams", 0)
            protein = food.get("protein", 0)
            
            if "tofu" in name.lower():
                tofu_found2.append(f"{meal_name}: {name} ({grams}g)")
            
            if protein > 5:
                all_proteins2.append(f"{name} ({protein}g)")
            
            total_protein2 += protein
    
    print(f"\n📊 RESULTADOS COM TOFU NAS PREFERÊNCIAS:")
    print(f"  Proteína total: {total_protein2}g")
    print(f"  Tofu encontrado: {tofu_found2 if tofu_found2 else 'NENHUM'}")
    print(f"  Todas as proteínas: {'; '.join(set(all_proteins2))}")
    
    print(f"\n🎯 CONCLUSÃO:")
    print(f"  Sem tofu nas preferências: {len(tofu_found)} ocorrências de tofu")
    print(f"  Com tofu nas preferências: {len(tofu_found2)} ocorrências de tofu")

if __name__ == "__main__":
    debug_original_vegetarian()