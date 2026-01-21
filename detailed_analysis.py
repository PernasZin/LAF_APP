#!/usr/bin/env python3
"""
ANÁLISE DETALHADA DE PREFERÊNCIAS ALIMENTARES - LAF Backend Testing
Analisa em detalhes quais alimentos aparecem nas dietas geradas.
"""

import requests
import json
from typing import Dict, List, Any

# Configuração
BASE_URL = "https://nutriworkout-4.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def get_diet_details(user_id: str) -> Dict:
    """Get detailed diet information"""
    try:
        response = requests.get(f"{BASE_URL}/diet/{user_id}", headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao buscar dieta para {user_id}: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Exceção ao buscar dieta para {user_id}: {e}")
        return {}

def analyze_diet_foods(diet_plan: Dict, profile_name: str, preferences: List[str]):
    """Analyze foods in diet plan"""
    print(f"\n🔍 ANÁLISE DETALHADA - {profile_name}")
    print("=" * 60)
    
    all_foods = []
    
    for i, meal in enumerate(diet_plan.get("meals", [])):
        meal_name = meal.get("name", f"Refeição {i+1}")
        meal_time = meal.get("time", "")
        print(f"\n🍽️ {meal_name} ({meal_time}):")
        
        for food in meal.get("foods", []):
            food_key = food.get("key", "")
            food_name = food.get("name", "")
            food_grams = food.get("grams", 0)
            food_calories = food.get("calories", 0)
            
            print(f"   • {food_name} ({food_key}) - {food_grams}g - {food_calories}kcal")
            all_foods.append({
                "key": food_key,
                "name": food_name,
                "meal": meal_name,
                "grams": food_grams,
                "calories": food_calories
            })
    
    # Análise de preferências
    print(f"\n📊 ANÁLISE DE PREFERÊNCIAS:")
    print(f"Preferências solicitadas: {preferences}")
    
    found_preferences = []
    missing_preferences = []
    
    # Mapeamento de preferências
    food_mappings = {
        "batata_doce": ["batata_doce", "batata doce", "sweet_potato"],
        "tilapia": ["tilapia", "tilápia"],
        "abacate": ["abacate", "avocado"],
        "morango": ["morango", "strawberry"],
        "macarrao": ["macarrao", "macarrão", "pasta", "massa"],
        "carne_moida": ["carne_moida", "carne moída", "ground_beef", "patinho"],
        "banana": ["banana"],
        "castanhas": ["castanhas", "castanha", "nuts", "nozes"],
        "aveia": ["aveia", "oat", "oats"],
        "salmao": ["salmao", "salmão", "salmon"],
        "mamao": ["mamao", "mamão", "papaya"],
        "amendoim": ["amendoim", "peanut", "pasta_amendoim"],
        "arroz_integral": ["arroz_integral", "arroz integral", "brown_rice"],
        "atum": ["atum", "tuna"],
        "laranja": ["laranja", "orange"],
        "azeite": ["azeite", "olive_oil", "azeite_oliva"],
        "feijao": ["feijao", "feijão", "beans"],
        "whey_protein": ["whey", "whey_protein", "proteina"],
        "maca": ["maca", "maçã", "apple"],
        "cottage": ["cottage", "queijo_cottage"],
        "tapioca": ["tapioca"],
        "peru": ["peru", "turkey"],
        "melancia": ["melancia", "watermelon"],
        "granola": ["granola"]
    }
    
    all_food_text = " ".join([f["key"] + " " + f["name"] for f in all_foods]).lower()
    
    for pref in preferences:
        pref_lower = pref.lower()
        variations = food_mappings.get(pref_lower, [pref_lower])
        
        found = False
        found_in = []
        
        for variation in variations:
            for food in all_foods:
                if variation in food["key"].lower() or variation in food["name"].lower():
                    found = True
                    found_in.append(f"{food['name']} em {food['meal']}")
        
        if found:
            found_preferences.append(pref)
            print(f"   ✅ {pref}: {', '.join(found_in)}")
        else:
            missing_preferences.append(pref)
            print(f"   ❌ {pref}: NÃO ENCONTRADO")
    
    # Mostrar alimentos alternativos que apareceram
    print(f"\n🔄 ALIMENTOS ALTERNATIVOS ENCONTRADOS:")
    protein_foods = []
    carb_foods = []
    
    for food in all_foods:
        food_lower = food["name"].lower() + " " + food["key"].lower()
        
        # Proteínas
        if any(p in food_lower for p in ["frango", "chicken", "peito", "breast", "peixe", "fish"]):
            protein_foods.append(f"{food['name']} ({food['meal']})")
        
        # Carboidratos
        if any(c in food_lower for c in ["arroz", "rice", "batata", "potato", "pao", "bread"]):
            carb_foods.append(f"{food['name']} ({food['meal']})")
    
    if protein_foods:
        print(f"   🥩 Proteínas: {', '.join(set(protein_foods))}")
    if carb_foods:
        print(f"   🍚 Carboidratos: {', '.join(set(carb_foods))}")
    
    return {
        "found": found_preferences,
        "missing": missing_preferences,
        "total_foods": len(all_foods),
        "success_rate": len(found_preferences) / len(preferences) * 100
    }

def main():
    """Main analysis function"""
    print("🔍 ANÁLISE DETALHADA DE PREFERÊNCIAS ALIMENTARES - LAF")
    print("=" * 80)
    
    # Perfis para análise
    profiles = [
        {
            "user_id": "pref-test-1",
            "name": "PERFIL 1 - BATATA DOCE + TILÁPIA + ABACATE + MORANGO",
            "preferences": ["batata_doce", "tilapia", "abacate", "morango"]
        },
        {
            "user_id": "pref-test-2", 
            "name": "PERFIL 2 - MACARRÃO + CARNE MOÍDA + BANANA + CASTANHAS",
            "preferences": ["macarrao", "carne_moida", "banana", "castanhas"]
        },
        {
            "user_id": "pref-test-3",
            "name": "PERFIL 3 - AVEIA + SALMÃO + MAMÃO + AMENDOIM", 
            "preferences": ["aveia", "salmao", "mamao", "amendoim"]
        },
        {
            "user_id": "pref-test-4",
            "name": "PERFIL 4 - ARROZ INTEGRAL + ATUM + LARANJA + AZEITE",
            "preferences": ["arroz_integral", "atum", "laranja", "azeite"]
        },
        {
            "user_id": "pref-test-5",
            "name": "PERFIL 5 - FEIJÃO + WHEY + MAÇÃ + COTTAGE",
            "preferences": ["feijao", "whey_protein", "maca", "cottage"]
        },
        {
            "user_id": "pref-test-6",
            "name": "PERFIL 6 - TAPIOCA + PERU + MELANCIA + GRANOLA",
            "preferences": ["tapioca", "peru", "melancia", "granola"]
        }
    ]
    
    total_success = 0
    total_profiles = len(profiles)
    
    for profile in profiles:
        diet_plan = get_diet_details(profile["user_id"])
        if diet_plan:
            result = analyze_diet_foods(diet_plan, profile["name"], profile["preferences"])
            total_success += result["success_rate"]
        else:
            print(f"\n❌ Não foi possível analisar {profile['name']}")
    
    # Resumo final
    avg_success = total_success / total_profiles if total_profiles > 0 else 0
    print(f"\n" + "=" * 80)
    print(f"📊 RESUMO FINAL DA ANÁLISE")
    print(f"=" * 80)
    print(f"Taxa média de sucesso das preferências: {avg_success:.1f}%")
    
    if avg_success >= 75:
        print("✅ SISTEMA DE PREFERÊNCIAS FUNCIONANDO BEM")
    elif avg_success >= 50:
        print("⚠️ SISTEMA DE PREFERÊNCIAS PARCIALMENTE FUNCIONAL")
    else:
        print("❌ SISTEMA DE PREFERÊNCIAS PRECISA DE MELHORIAS")

if __name__ == "__main__":
    main()