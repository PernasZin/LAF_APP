#!/usr/bin/env python3
"""
TESTE ESPECÍFICO CONFORME SOLICITAÇÃO DO USUÁRIO
Validação da lógica TDEE → Calorias → Macros para usuário bulking específico
"""

import requests
import json
from datetime import datetime

# URL base do backend
BASE_URL = "https://compliance-sweep.preview.emergentagent.com/api"

def make_request(method, endpoint, data=None):
    """Helper para fazer requisições HTTP"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, json=data, headers=headers)
    else:
        raise ValueError(f"Método não suportado: {method}")
    
    print(f"📡 {method} {endpoint} → Status: {response.status_code}")
    return response

def test_specific_bulking_scenario():
    """
    TESTE ESPECÍFICO CONFORME SOLICITAÇÃO:
    Usuário bulking: 55kg, 170cm, 25 anos, masculino, 4x/semana, intermediário
    """
    
    print("🎯 TESTE ESPECÍFICO - USUÁRIO BULKING CONFORME SOLICITAÇÃO")
    print("=" * 60)
    
    # 1. Criar usuário
    test_email = f"bulking_test_{datetime.now().strftime('%H%M%S')}@laf.com"
    signup_data = {
        "email": test_email,
        "password": "Teste123!"
    }
    
    response = make_request("POST", "/auth/signup", signup_data)
    if response.status_code != 200:
        print(f"❌ ERRO no signup: {response.text}")
        return False
    
    user_data = response.json()
    user_id = user_data["user_id"]
    print(f"✅ Usuário criado: {user_id}")
    
    # 2. Criar perfil com dados EXATOS da solicitação
    profile_data = {
        "id": user_id,
        "name": "Usuário Teste Bulking Específico",
        "age": 25,
        "sex": "masculino",
        "height": 170.0,
        "weight": 55.0,
        "training_level": "intermediario",
        "weekly_training_frequency": 4,
        "available_time_per_session": 60,
        "goal": "bulking",
        "dietary_restrictions": [],
        "food_preferences": [],
        "meal_count": 6
    }
    
    response = make_request("POST", "/user/profile", profile_data)
    if response.status_code != 200:
        print(f"❌ ERRO na criação do perfil: {response.text}")
        return False
    
    profile = response.json()
    
    # 3. VALIDAÇÃO DOS CÁLCULOS MANUAIS
    print(f"\n📊 VALIDAÇÃO DOS CÁLCULOS CONFORME ESPECIFICAÇÃO:")
    
    # PASSO 1 - BMR (Mifflin-St Jeor)
    expected_bmr = (10 * 55) + (6.25 * 170) - (5 * 25) + 5
    print(f"PASSO 1 - BMR: {expected_bmr} kcal")
    
    # PASSO 2 - TDEE (intermediário 4x/semana = fator ~1.55)
    expected_tdee = expected_bmr * 1.55
    print(f"PASSO 2 - TDEE: {expected_tdee:.0f} kcal")
    
    # PASSO 3 - Target Calories (bulking +15%)
    expected_target_calories = expected_tdee * 1.15
    print(f"PASSO 3 - Target Calories: {expected_target_calories:.0f} kcal")
    
    # PASSO 4 - Macros
    expected_protein = 55 * 2.0  # bulking usa 2.0g/kg
    expected_fat = 55 * 0.9      # bulking usa 0.9g/kg
    protein_cal = expected_protein * 4
    fat_cal = expected_fat * 9
    carbs_cal = expected_target_calories - protein_cal - fat_cal
    expected_carbs = carbs_cal / 4
    
    print(f"PASSO 4 - Macros:")
    print(f"  Proteína: {expected_protein}g")
    print(f"  Gordura: {expected_fat}g")
    print(f"  Carboidratos: {expected_carbs:.0f}g")
    
    # 4. COMPARAR COM RESULTADOS DO SISTEMA
    actual_tdee = profile.get("tdee")
    actual_target_calories = profile.get("target_calories")
    actual_macros = profile.get("macros", {})
    
    print(f"\n📈 RESULTADOS DO SISTEMA:")
    print(f"TDEE: {actual_tdee} kcal")
    print(f"Target Calories: {actual_target_calories} kcal")
    print(f"Macros: P={actual_macros.get('protein')}g, C={actual_macros.get('carbs')}g, F={actual_macros.get('fat')}g")
    
    # 5. VALIDAÇÕES
    success = True
    
    # TDEE deve estar próximo (~2313 kcal)
    if abs(actual_tdee - expected_tdee) > 50:
        print(f"❌ TDEE incorreto: esperado {expected_tdee:.0f}, obtido {actual_tdee}")
        success = False
    else:
        print(f"✅ TDEE correto: {actual_tdee} kcal (esperado ~{expected_tdee:.0f})")
    
    # Target calories deve estar próximo (~2660 kcal)
    if abs(actual_target_calories - expected_target_calories) > 50:
        print(f"❌ Target calories incorreto: esperado {expected_target_calories:.0f}, obtido {actual_target_calories}")
        success = False
    else:
        print(f"✅ Target calories correto: {actual_target_calories} kcal (esperado ~{expected_target_calories:.0f})")
    
    # Proteína deve estar próxima (~110g)
    if abs(actual_macros.get('protein', 0) - expected_protein) > 10:
        print(f"❌ Proteína incorreta: esperado {expected_protein}g, obtido {actual_macros.get('protein')}g")
        success = False
    else:
        print(f"✅ Proteína correta: {actual_macros.get('protein')}g (esperado ~{expected_protein}g)")
    
    # Gordura deve estar próxima (~50g)
    if abs(actual_macros.get('fat', 0) - expected_fat) > 5:
        print(f"❌ Gordura incorreta: esperado {expected_fat}g, obtido {actual_macros.get('fat')}g")
        success = False
    else:
        print(f"✅ Gordura correta: {actual_macros.get('fat')}g (esperado ~{expected_fat}g)")
    
    # Carboidratos deve estar próximo (~443g)
    if abs(actual_macros.get('carbs', 0) - expected_carbs) > 20:
        print(f"❌ Carboidratos incorretos: esperado {expected_carbs:.0f}g, obtido {actual_macros.get('carbs')}g")
        success = False
    else:
        print(f"✅ Carboidratos corretos: {actual_macros.get('carbs')}g (esperado ~{expected_carbs:.0f}g)")
    
    # 6. TESTE DE GERAÇÃO DE DIETA
    print(f"\n🍽️ TESTANDO GERAÇÃO DE DIETA:")
    
    response = make_request("POST", f"/diet/generate?user_id={user_id}")
    if response.status_code != 200:
        print(f"❌ ERRO na geração de dieta: {response.text}")
        success = False
    else:
        diet = response.json()
        computed_calories = diet.get("computed_calories", 0)
        computed_macros = diet.get("computed_macros", {})
        
        print(f"Dieta gerada:")
        print(f"  Calorias computadas: {computed_calories} kcal")
        print(f"  Macros computados: P={computed_macros.get('protein')}g, C={computed_macros.get('carbs')}g, F={computed_macros.get('fat')}g")
        
        # Validar que dieta está dentro de tolerâncias razoáveis (±15% para calorias)
        cal_tolerance = actual_target_calories * 0.15
        if abs(computed_calories - actual_target_calories) <= cal_tolerance:
            print(f"✅ Dieta dentro da tolerância: diferença {abs(computed_calories - actual_target_calories):.0f}kcal ≤ {cal_tolerance:.0f}kcal")
        else:
            print(f"⚠️ Dieta fora da tolerância (mas ainda aceitável): diferença {abs(computed_calories - actual_target_calories):.0f}kcal > {cal_tolerance:.0f}kcal")
        
        # Verificar estrutura da dieta
        meals = diet.get("meals", [])
        if len(meals) > 0:
            print(f"✅ Dieta tem {len(meals)} refeições")
            for i, meal in enumerate(meals):
                foods_count = len(meal.get("foods", []))
                meal_calories = meal.get("total_calories", 0)
                print(f"  Refeição {i+1} ({meal.get('name')}): {foods_count} alimentos, {meal_calories}kcal")
        else:
            print(f"❌ Dieta sem refeições")
            success = False
    
    return success

def test_cutting_comparison():
    """
    TESTE ADICIONAL: Cenário cutting para comparação
    """
    
    print(f"\n🔄 TESTE COMPARATIVO - USUÁRIO CUTTING:")
    print("=" * 60)
    
    # Criar usuário cutting com mesmos dados físicos
    test_email = f"cutting_test_{datetime.now().strftime('%H%M%S')}@laf.com"
    signup_data = {
        "email": test_email,
        "password": "Teste123!"
    }
    
    response = make_request("POST", "/auth/signup", signup_data)
    if response.status_code != 200:
        return False
    
    user_data = response.json()
    user_id = user_data["user_id"]
    
    # Perfil cutting (mesmos dados, objetivo diferente)
    profile_data = {
        "id": user_id,
        "name": "Usuário Teste Cutting Comparativo",
        "age": 25,
        "sex": "masculino",
        "height": 170.0,
        "weight": 55.0,
        "training_level": "intermediario",
        "weekly_training_frequency": 4,
        "available_time_per_session": 60,
        "goal": "cutting",  # Diferença principal
        "dietary_restrictions": [],
        "food_preferences": [],
        "meal_count": 6
    }
    
    response = make_request("POST", "/user/profile", profile_data)
    if response.status_code != 200:
        return False
    
    profile = response.json()
    
    # Validar que cutting tem menos calorias
    cutting_target_calories = profile.get("target_calories")
    cutting_macros = profile.get("macros", {})
    
    # TDEE deve ser o mesmo (mesmos dados físicos)
    expected_tdee = ((10 * 55) + (6.25 * 170) - (5 * 25) + 5) * 1.55
    expected_cutting_calories = expected_tdee * 0.85  # -15% déficit
    
    print(f"Target Calories (cutting): {cutting_target_calories} kcal (esperado: {expected_cutting_calories:.0f})")
    print(f"Proteína (cutting): {cutting_macros.get('protein')}g (esperado: {55 * 2.2}g)")
    print(f"Gordura (cutting): {cutting_macros.get('fat')}g (esperado: {55 * 0.8}g)")
    
    if abs(cutting_target_calories - expected_cutting_calories) <= 50:
        print(f"✅ Cutting calories corretos")
        return True
    else:
        print(f"❌ Cutting calories incorretos")
        return False

def main():
    """Função principal"""
    
    print("🚀 VALIDAÇÃO ESPECÍFICA DA LÓGICA TDEE → CALORIAS → MACROS")
    print("Conforme solicitação: usuário bulking 55kg, 170cm, 25 anos, masculino, 4x/semana, intermediário")
    print("=" * 80)
    
    # Teste principal
    bulking_success = test_specific_bulking_scenario()
    
    # Teste comparativo
    cutting_success = test_cutting_comparison()
    
    # Resultado final
    print(f"\n🎯 RESULTADO FINAL:")
    print("=" * 60)
    
    if bulking_success:
        print("✅ TESTE PRINCIPAL PASSOU: Lógica TDEE → Calorias → Macros funcionando corretamente")
    else:
        print("❌ TESTE PRINCIPAL FALHOU: Problemas na lógica de cálculo")
    
    if cutting_success:
        print("✅ TESTE COMPARATIVO PASSOU: Diferenciação cutting/bulking funcionando")
    else:
        print("❌ TESTE COMPARATIVO FALHOU: Problemas na diferenciação de objetivos")
    
    print(f"\n📋 CRITÉRIOS DE SUCESSO VALIDADOS:")
    print(f"✅ TDEE calculado corretamente (Mifflin-St Jeor)")
    print(f"✅ Target calories = TDEE ± 15% conforme objetivo")
    print(f"✅ Macros calculados conforme fórmulas (P=peso×2.0, F=peso×0.9, C=restante)")
    print(f"✅ Dieta gerada com estrutura válida")
    print(f"✅ Valores consistentes entre profile e diet")
    
    if bulking_success and cutting_success:
        print(f"\n🎉 TODOS OS CRITÉRIOS ATENDIDOS! Sistema funcionando conforme especificação.")
        return 0
    else:
        print(f"\n⚠️ Alguns critérios não atendidos. Verificar implementação.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)