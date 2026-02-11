#!/usr/bin/env python3
"""
🔍 FOCUSED VALIDATION - MULTIPLE OF 10 RULE
Check existing diets for violations of the critical multiple of 10 rule
"""

import requests
import json

BASE_URL = "https://macro-safety-caps.preview.emergentagent.com/api"

# User IDs from previous test
user_ids = [
    "9cd1b9c0-980a-436a-9c2d-4c0cf9e984a7",  # Maria Santos
    "4d9e4af5-092b-48bb-a558-c6b90f47acbe",  # Pedro Costa  
    "09c35663-5528-4f8a-8c3e-4793301d7681",  # Ana Oliveira
    "0d5df151-0bb5-49a6-91cd-ed62c9abcc01",  # Carlos Ferreira
    "d9c80b56-cd57-4d59-bec6-2fcebb224e08",  # Lucia Mendes
    "bb4d39f9-6c1e-455a-bcd8-672e10e122f5",  # Roberto Lima
    "18cd69c2-012c-4f0d-96c9-0c9b66fb1267"   # Fernanda Souza
]

profile_names = [
    "Maria Santos", "Pedro Costa", "Ana Oliveira", "Carlos Ferreira",
    "Lucia Mendes", "Roberto Lima", "Fernanda Souza"
]

def check_multiple_of_10_violations():
    """Check all diets for multiple of 10 violations"""
    total_violations = 0
    total_foods = 0
    
    print("🔍 VALIDAÇÃO CRÍTICA - MÚLTIPLOS DE 10")
    print("=" * 60)
    
    for i, user_id in enumerate(user_ids):
        profile_name = profile_names[i]
        print(f"\n📋 Verificando {profile_name}...")
        
        try:
            response = requests.get(f"{BASE_URL}/diet/{user_id}")
            if response.status_code != 200:
                print(f"❌ Erro ao buscar dieta: {response.status_code}")
                continue
                
            diet = response.json()
            profile_violations = 0
            profile_foods = 0
            
            for meal_idx, meal in enumerate(diet.get("meals", [])):
                meal_name = meal.get("name", f"Meal {meal_idx + 1}")
                
                for food in meal.get("foods", []):
                    grams = food.get("grams", 0)
                    food_name = food.get("name", "Unknown")
                    profile_foods += 1
                    total_foods += 1
                    
                    if grams % 10 != 0:
                        profile_violations += 1
                        total_violations += 1
                        print(f"🚨 VIOLAÇÃO: {meal_name} - {food_name}: {grams}g")
            
            if profile_violations == 0:
                print(f"✅ {profile_name}: TODOS os {profile_foods} alimentos são múltiplos de 10")
            else:
                print(f"❌ {profile_name}: {profile_violations} violações em {profile_foods} alimentos")
                
        except Exception as e:
            print(f"❌ Erro ao processar {profile_name}: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"📊 RESULTADO FINAL:")
    print(f"🥗 Total de alimentos verificados: {total_foods}")
    print(f"🚨 Total de violações encontradas: {total_violations}")
    
    if total_violations == 0:
        print(f"🏆 APROVADO: 100% dos alimentos são múltiplos de 10")
    else:
        violation_rate = (total_violations / total_foods) * 100 if total_foods > 0 else 0
        print(f"❌ REPROVADO: {violation_rate:.1f}% dos alimentos violam a regra")
        print(f"⚠️  SISTEMA PRECISA DE CORREÇÃO URGENTE!")
    
    return total_violations == 0

if __name__ == "__main__":
    check_multiple_of_10_violations()