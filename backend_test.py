#!/usr/bin/env python3
"""
TESTE DE VALIDAÇÃO DA LÓGICA TDEE → CALORIAS → MACROS
Conforme solicitação específica do usuário para validar cálculos de dieta.
"""

import requests
import json
import sys
from datetime import datetime

# URL base do backend
BASE_URL = "https://nutrition-flow-1.preview.emergentagent.com/api"

class TestResults:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []
    
    def run_test(self, test_name, test_func):
        self.tests_run += 1
        try:
            print(f"\n🧪 TESTE: {test_name}")
            test_func()
            self.tests_passed += 1
            print(f"✅ PASSOU: {test_name}")
        except Exception as e:
            self.failures.append(f"{test_name}: {str(e)}")
            print(f"❌ FALHOU: {test_name} - {str(e)}")
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"RESUMO DOS TESTES")
        print(f"{'='*60}")
        print(f"Total de testes: {self.tests_run}")
        print(f"Testes aprovados: {self.tests_passed}")
        print(f"Testes falharam: {len(self.failures)}")
        print(f"Taxa de sucesso: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failures:
            print(f"\n❌ FALHAS ENCONTRADAS:")
            for failure in self.failures:
                print(f"  - {failure}")

def make_request(method, endpoint, data=None, headers=None):
    """Helper para fazer requisições HTTP"""
    url = f"{BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, json=data, headers=headers)
        else:
            raise ValueError(f"Método HTTP não suportado: {method}")
        
        print(f"📡 {method} {endpoint} → Status: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
        return response
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        raise

def test_user_signup_and_profile_creation():
    """TESTE 1: Criar usuário de teste e perfil com dados específicos"""
    
    # Dados do usuário de teste conforme especificação
    test_email = f"teste_tdee_{datetime.now().strftime('%H%M%S')}@laf.com"
    test_password = "Teste123!"
    
    # 1. Criar usuário
    signup_data = {
        "email": test_email,
        "password": test_password
    }
    
    response = make_request("POST", "/auth/signup", signup_data)
    assert response.status_code == 200, f"Signup falhou: {response.text}"
    
    signup_result = response.json()
    user_id = signup_result["user_id"]
    token = signup_result["token"]
    
    print(f"✅ Usuário criado: {user_id}")
    
    # 2. Criar perfil com dados específicos do teste
    profile_data = {
        "id": user_id,
        "name": "Usuário Teste TDEE",
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
    assert response.status_code == 200, f"Profile creation falhou: {response.text}"
    
    profile_result = response.json()
    
    # Validar cálculos conforme especificação
    print(f"\n📊 VALIDAÇÃO DOS CÁLCULOS:")
    
    # BMR esperado: (10 × 55) + (6.25 × 170) - (5 × 25) + 5 = 1492.5
    expected_bmr = (10 * 55) + (6.25 * 170) - (5 * 25) + 5
    print(f"BMR esperado: {expected_bmr} kcal")
    
    # TDEE esperado: BMR × 1.55 (intermediário 4x/semana)
    expected_tdee = expected_bmr * 1.55
    print(f"TDEE esperado: {expected_tdee:.0f} kcal")
    
    # Target calories esperado: TDEE × 1.15 (bulking +15%)
    expected_target_calories = expected_tdee * 1.15
    print(f"Target Calories esperado: {expected_target_calories:.0f} kcal")
    
    # Macros esperados
    expected_protein = 55 * 2.0  # bulking usa 2.0g/kg
    expected_fat = 55 * 0.9      # bulking usa 0.9g/kg
    protein_cal = expected_protein * 4
    fat_cal = expected_fat * 9
    carbs_cal = expected_target_calories - protein_cal - fat_cal
    expected_carbs = carbs_cal / 4
    
    print(f"Macros esperados: P={expected_protein}g, C={expected_carbs:.0f}g, F={expected_fat}g")
    
    # Validar resultados
    actual_tdee = profile_result.get("tdee")
    actual_target_calories = profile_result.get("target_calories")
    actual_macros = profile_result.get("macros", {})
    
    print(f"\n📈 RESULTADOS OBTIDOS:")
    print(f"TDEE: {actual_tdee} kcal")
    print(f"Target Calories: {actual_target_calories} kcal")
    print(f"Macros: P={actual_macros.get('protein')}g, C={actual_macros.get('carbs')}g, F={actual_macros.get('fat')}g")
    
    # Tolerâncias para validação (±5% para TDEE/calorias, ±10% para macros)
    tdee_tolerance = expected_tdee * 0.05
    cal_tolerance = expected_target_calories * 0.05
    macro_tolerance = 0.10
    
    assert abs(actual_tdee - expected_tdee) <= tdee_tolerance, \
        f"TDEE fora da tolerância: esperado {expected_tdee:.0f}±{tdee_tolerance:.0f}, obtido {actual_tdee}"
    
    assert abs(actual_target_calories - expected_target_calories) <= cal_tolerance, \
        f"Target calories fora da tolerância: esperado {expected_target_calories:.0f}±{cal_tolerance:.0f}, obtido {actual_target_calories}"
    
    assert abs(actual_macros.get('protein', 0) - expected_protein) <= expected_protein * macro_tolerance, \
        f"Proteína fora da tolerância: esperado {expected_protein}g±{expected_protein*macro_tolerance:.1f}g, obtido {actual_macros.get('protein')}g"
    
    assert abs(actual_macros.get('fat', 0) - expected_fat) <= expected_fat * macro_tolerance, \
        f"Gordura fora da tolerância: esperado {expected_fat}g±{expected_fat*macro_tolerance:.1f}g, obtido {actual_macros.get('fat')}g"
    
    assert abs(actual_macros.get('carbs', 0) - expected_carbs) <= expected_carbs * macro_tolerance, \
        f"Carboidratos fora da tolerância: esperado {expected_carbs:.0f}g±{expected_carbs*macro_tolerance:.1f}g, obtido {actual_macros.get('carbs')}g"
    
    print(f"✅ TODOS OS CÁLCULOS VALIDADOS COM SUCESSO!")
    
    return user_id, token, profile_result

def test_cutting_scenario():
    """TESTE 2: Validar cenário de cutting para comparação"""
    
    # Criar usuário para cutting
    test_email = f"teste_cutting_{datetime.now().strftime('%H%M%S')}@laf.com"
    test_password = "Teste123!"
    
    signup_data = {
        "email": test_email,
        "password": test_password
    }
    
    response = make_request("POST", "/auth/signup", signup_data)
    assert response.status_code == 200, f"Signup falhou: {response.text}"
    
    signup_result = response.json()
    user_id = signup_result["user_id"]
    
    # Perfil para cutting (mesmos dados físicos, objetivo diferente)
    profile_data = {
        "id": user_id,
        "name": "Usuário Teste Cutting",
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
    assert response.status_code == 200, f"Profile creation falhou: {response.text}"
    
    profile_result = response.json()
    
    # Validar cálculos para cutting
    print(f"\n📊 VALIDAÇÃO CUTTING:")
    
    # TDEE deve ser o mesmo (mesmos dados físicos)
    expected_tdee = ((10 * 55) + (6.25 * 170) - (5 * 25) + 5) * 1.55
    
    # Target calories para cutting: TDEE × 0.85 (déficit 15%)
    expected_target_calories = expected_tdee * 0.85
    
    # Macros para cutting
    expected_protein = 55 * 2.2  # cutting usa 2.2g/kg (maior para preservar massa)
    expected_fat = 55 * 0.8      # cutting usa 0.8g/kg (menor)
    
    actual_target_calories = profile_result.get("target_calories")
    actual_macros = profile_result.get("macros", {})
    
    print(f"Target Calories (cutting): {actual_target_calories} kcal (esperado: {expected_target_calories:.0f})")
    print(f"Proteína (cutting): {actual_macros.get('protein')}g (esperado: {expected_protein}g)")
    print(f"Gordura (cutting): {actual_macros.get('fat')}g (esperado: {expected_fat}g)")
    
    # Validar que cutting tem menos calorias que bulking
    assert actual_target_calories < expected_tdee, \
        f"Cutting deveria ter menos calorias que TDEE: {actual_target_calories} < {expected_tdee}"
    
    # Validar déficit de 15%
    cal_tolerance = expected_target_calories * 0.05
    assert abs(actual_target_calories - expected_target_calories) <= cal_tolerance, \
        f"Déficit de cutting incorreto: esperado {expected_target_calories:.0f}±{cal_tolerance:.0f}, obtido {actual_target_calories}"
    
    print(f"✅ CENÁRIO CUTTING VALIDADO!")
    
    return user_id, profile_result

def test_diet_generation_consistency(user_id, profile_data):
    """TESTE 3: Validar que a dieta gerada corresponde aos targets do perfil"""
    
    print(f"\n🍽️ TESTANDO GERAÇÃO DE DIETA PARA USER: {user_id}")
    
    # Gerar dieta
    response = make_request("POST", f"/diet/generate?user_id={user_id}")
    assert response.status_code == 200, f"Diet generation falhou: {response.text}"
    
    diet_result = response.json()
    
    # Extrair valores computados da dieta
    computed_calories = diet_result.get("computed_calories", 0)
    computed_macros = diet_result.get("computed_macros", {})
    
    # Extrair targets do perfil
    target_calories = profile_data.get("target_calories", 0)
    target_macros = profile_data.get("macros", {})
    
    print(f"\n📊 COMPARAÇÃO DIETA vs PERFIL:")
    print(f"Calorias - Target: {target_calories}, Computed: {computed_calories}")
    print(f"Proteína - Target: {target_macros.get('protein')}g, Computed: {computed_macros.get('protein')}g")
    print(f"Carbs - Target: {target_macros.get('carbs')}g, Computed: {computed_macros.get('carbs')}g")
    print(f"Gordura - Target: {target_macros.get('fat')}g, Computed: {computed_macros.get('fat')}g")
    
    # Tolerâncias para dieta (±15% conforme especificação do sistema)
    cal_tolerance = target_calories * 0.15
    macro_tolerance = 0.20  # ±20% para macros
    
    # Validar que dieta está dentro das tolerâncias
    cal_diff = abs(computed_calories - target_calories)
    assert cal_diff <= cal_tolerance, \
        f"Calorias da dieta fora da tolerância: diferença {cal_diff:.0f}kcal > {cal_tolerance:.0f}kcal"
    
    protein_diff = abs(computed_macros.get('protein', 0) - target_macros.get('protein', 0))
    protein_tolerance = target_macros.get('protein', 0) * macro_tolerance
    assert protein_diff <= protein_tolerance, \
        f"Proteína da dieta fora da tolerância: diferença {protein_diff:.1f}g > {protein_tolerance:.1f}g"
    
    carbs_diff = abs(computed_macros.get('carbs', 0) - target_macros.get('carbs', 0))
    carbs_tolerance = target_macros.get('carbs', 0) * macro_tolerance
    assert carbs_diff <= carbs_tolerance, \
        f"Carboidratos da dieta fora da tolerância: diferença {carbs_diff:.1f}g > {carbs_tolerance:.1f}g"
    
    fat_diff = abs(computed_macros.get('fat', 0) - target_macros.get('fat', 0))
    fat_tolerance = target_macros.get('fat', 0) * macro_tolerance
    assert fat_diff <= fat_tolerance, \
        f"Gordura da dieta fora da tolerância: diferença {fat_diff:.1f}g > {fat_tolerance:.1f}g"
    
    # Validar estrutura da dieta
    meals = diet_result.get("meals", [])
    assert len(meals) > 0, "Dieta deve ter pelo menos uma refeição"
    
    # Validar que cada refeição tem alimentos
    for i, meal in enumerate(meals):
        foods = meal.get("foods", [])
        assert len(foods) > 0, f"Refeição {i} ({meal.get('name')}) não tem alimentos"
        
        # Validar que cada alimento tem macros
        for food in foods:
            assert food.get("protein", 0) >= 0, f"Alimento {food.get('name')} tem proteína inválida"
            assert food.get("carbs", 0) >= 0, f"Alimento {food.get('name')} tem carboidratos inválidos"
            assert food.get("fat", 0) >= 0, f"Alimento {food.get('name')} tem gordura inválida"
            assert food.get("calories", 0) > 0, f"Alimento {food.get('name')} tem calorias inválidas"
    
    print(f"✅ DIETA GERADA DENTRO DAS TOLERÂNCIAS!")
    print(f"   Diferenças: Cal={cal_diff:.0f}kcal, P={protein_diff:.1f}g, C={carbs_diff:.1f}g, F={fat_diff:.1f}g")
    
    return diet_result

def test_profile_retrieval(user_id):
    """TESTE 4: Validar recuperação de perfil"""
    
    response = make_request("GET", f"/user/profile/{user_id}")
    assert response.status_code == 200, f"Profile retrieval falhou: {response.text}"
    
    profile = response.json()
    
    # Validar campos obrigatórios
    required_fields = ["id", "name", "age", "sex", "height", "weight", "goal", "tdee", "target_calories", "macros"]
    for field in required_fields:
        assert field in profile, f"Campo obrigatório '{field}' ausente no perfil"
    
    # Validar tipos de dados
    assert isinstance(profile["tdee"], (int, float)), "TDEE deve ser numérico"
    assert isinstance(profile["target_calories"], (int, float)), "Target calories deve ser numérico"
    assert isinstance(profile["macros"], dict), "Macros deve ser um dicionário"
    
    print(f"✅ PERFIL RECUPERADO CORRETAMENTE!")
    
    return profile

def main():
    """Função principal que executa todos os testes"""
    
    print("🚀 INICIANDO VALIDAÇÃO DA LÓGICA TDEE → CALORIAS → MACROS")
    print("=" * 60)
    
    results = TestResults()
    
    # Variáveis para compartilhar entre testes
    bulking_user_id = None
    bulking_profile = None
    cutting_user_id = None
    cutting_profile = None
    
    # TESTE 1: Cenário principal - Bulking
    def test_1():
        nonlocal bulking_user_id, bulking_profile
        bulking_user_id, token, bulking_profile = test_user_signup_and_profile_creation()
    
    results.run_test("Criação de usuário BULKING e validação de cálculos", test_1)
    
    # TESTE 2: Cenário de comparação - Cutting
    def test_2():
        nonlocal cutting_user_id, cutting_profile
        cutting_user_id, cutting_profile = test_cutting_scenario()
    
    results.run_test("Criação de usuário CUTTING e validação de déficit", test_2)
    
    # TESTE 3: Geração de dieta para bulking
    if bulking_user_id and bulking_profile:
        def test_3():
            test_diet_generation_consistency(bulking_user_id, bulking_profile)
        
        results.run_test("Geração de dieta BULKING e validação de consistência", test_3)
    
    # TESTE 4: Geração de dieta para cutting
    if cutting_user_id and cutting_profile:
        def test_4():
            test_diet_generation_consistency(cutting_user_id, cutting_profile)
        
        results.run_test("Geração de dieta CUTTING e validação de consistência", test_4)
    
    # TESTE 5: Recuperação de perfil
    if bulking_user_id:
        def test_5():
            test_profile_retrieval(bulking_user_id)
        
        results.run_test("Recuperação de perfil via GET", test_5)
    
    # Imprimir resumo final
    results.print_summary()
    
    # Critérios de sucesso conforme especificação
    print(f"\n🎯 CRITÉRIOS DE SUCESSO:")
    print(f"✅ TDEE calculado corretamente")
    print(f"✅ Target calories = TDEE ± ajuste conforme objetivo")
    print(f"✅ Macros calculados conforme fórmulas especificadas")
    print(f"✅ Dieta gerada dentro das tolerâncias")
    print(f"✅ Valores consistentes entre profile e diet")
    
    if results.tests_passed == results.tests_run:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! Sistema funcionando conforme especificação.")
        return 0
    else:
        print(f"\n❌ {len(results.failures)} TESTE(S) FALHARAM. Verificar implementação.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)