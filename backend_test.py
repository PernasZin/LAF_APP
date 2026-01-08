#!/usr/bin/env python3
"""
Teste do Endpoint de Geração de Dieta - Validação das Novas Regras por Refeição
==============================================================================

OBJETIVO: Testar POST /api/diet/generate para verificar se as novas regras por refeição estão funcionando corretamente.

REGRAS QUE DEVEM SER VALIDADAS:

1. **Café da Manhã (07:00)**:
   - DEVE conter: ovos/claras/iogurte/cottage + aveia/pão/tapioca + frutas
   - NÃO PODE conter: carnes (frango, carne, peixe), arroz, batata, azeite

2. **Lanche Manhã (10:00)**:
   - DEVE conter: frutas + oleaginosas (castanhas/amêndoas)
   - NÃO PODE conter: carnes, arroz, batata, azeite

3. **Almoço (12:30)**:
   - DEVE conter: EXATAMENTE 1 proteína (carne/frango/peixe) + 1 carboidrato (arroz/batata) + legumes + azeite
   - NÃO PODE ter mais de 1 proteína ou mais de 1 carboidrato principal

4. **Lanche Tarde (16:00)**:
   - DEVE conter: frutas + iogurte/cottage
   - NÃO PODE conter: carnes, arroz, batata, azeite

5. **Jantar (19:30)**:
   - DEVE conter: EXATAMENTE 1 proteína + 1 carboidrato + legumes + azeite
   - NÃO PODE ter mais de 1 proteína ou mais de 1 carboidrato principal

6. **Ceia (21:30)** - NOVA REFEIÇÃO:
   - DEVE conter: proteína leve (ovos/iogurte/cottage) + frutas
   - NÃO PODE conter: carnes, carboidratos complexos, gorduras adicionadas

TESTE:
1. Criar usuário com perfil completo
2. Gerar dieta
3. Validar cada refeição contra as regras acima
4. Verificar que existem 6 refeições no total
5. Verificar que a Ceia existe e tem os alimentos corretos
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Set

# Configuração da URL do backend
BACKEND_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://athlete-phase.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{Colors.END}")

# Definições das regras por refeição
MEAL_RULES = {
    "Café da Manhã": {
        "time": "07:00",
        "allowed_proteins": {"ovos", "claras", "iogurte_grego", "cottage"},
        "allowed_carbs": {"aveia", "pao", "pao_integral", "tapioca"},
        "forbidden_proteins": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", "tilapia", "atum", "salmao", "camarao", "sardinha", "peru"},
        "forbidden_carbs": {"arroz_branco", "arroz_integral", "batata_doce", "batata"},
        "forbidden_fats": {"azeite"},
        "must_have_fruits": True,
        "description": "Proteínas leves + carboidratos leves + frutas"
    },
    "Lanche Manhã": {
        "time": "10:00", 
        "allowed_fats": {"castanhas", "amendoas", "nozes", "pasta_amendoim"},
        "forbidden_proteins": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", "tilapia", "atum", "salmao", "camarao", "sardinha", "peru"},
        "forbidden_carbs": {"arroz_branco", "arroz_integral", "batata_doce", "batata"},
        "forbidden_fats": {"azeite"},
        "must_have_fruits": True,
        "description": "Frutas + oleaginosas"
    },
    "Almoço": {
        "time": "12:30",
        "allowed_proteins": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", "tilapia", "atum", "salmao", "camarao", "sardinha", "peru", "ovos", "claras", "tofu"},
        "allowed_carbs": {"arroz_branco", "arroz_integral", "batata_doce", "batata", "macarrao", "quinoa", "cuscuz", "milho", "feijao", "lentilha", "grao_de_bico"},
        "allowed_fats": {"azeite"},
        "max_proteins": 1,
        "max_carbs": 1,
        "must_have_vegetables": True,
        "description": "EXATAMENTE 1 proteína + 1 carboidrato + legumes + azeite"
    },
    "Lanche Tarde": {
        "time": "16:00",
        "allowed_proteins": {"iogurte_grego", "cottage"},
        "forbidden_proteins": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", "tilapia", "atum", "salmao", "camarao", "sardinha", "peru"},
        "forbidden_carbs": {"arroz_branco", "arroz_integral", "batata_doce", "batata"},
        "forbidden_fats": {"azeite"},
        "must_have_fruits": True,
        "description": "Frutas + iogurte/cottage"
    },
    "Jantar": {
        "time": "19:30",
        "allowed_proteins": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", "tilapia", "atum", "salmao", "camarao", "sardinha", "peru", "ovos", "claras", "tofu"},
        "allowed_carbs": {"arroz_branco", "arroz_integral", "batata_doce", "batata", "macarrao", "quinoa", "cuscuz", "milho", "feijao", "lentilha", "grao_de_bico"},
        "allowed_fats": {"azeite"},
        "max_proteins": 1,
        "max_carbs": 1,
        "must_have_vegetables": True,
        "description": "EXATAMENTE 1 proteína + 1 carboidrato + legumes + azeite"
    },
    "Ceia": {
        "time": "21:30",
        "allowed_proteins": {"ovos", "iogurte_grego", "cottage"},
        "forbidden_proteins": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", "tilapia", "atum", "salmao", "camarao", "sardinha", "peru"},
        "forbidden_carbs": {"arroz_branco", "arroz_integral", "batata_doce", "batata", "macarrao", "quinoa", "cuscuz", "milho", "feijao", "lentilha", "grao_de_bico"},
        "forbidden_fats": {"azeite", "castanhas", "amendoas", "nozes", "pasta_amendoim"},
        "must_have_fruits": True,
        "description": "Proteína leve + frutas (SEM carbs complexos, SEM gorduras adicionadas)"
    }
}

# Categorias de alimentos
FOOD_CATEGORIES = {
    # Proteínas
    "frango": "protein", "coxa_frango": "protein", "patinho": "protein", "carne_moida": "protein", 
    "suino": "protein", "ovos": "protein", "claras": "protein", "tilapia": "protein", 
    "atum": "protein", "salmao": "protein", "camarao": "protein", "sardinha": "protein", 
    "peru": "protein", "cottage": "protein", "iogurte_grego": "protein", "tofu": "protein",
    
    # Carboidratos
    "arroz_branco": "carb", "arroz_integral": "carb", "batata_doce": "carb", "batata": "carb",
    "aveia": "carb", "macarrao": "carb", "pao": "carb", "pao_integral": "carb", 
    "quinoa": "carb", "cuscuz": "carb", "tapioca": "carb", "milho": "carb", 
    "feijao": "carb", "lentilha": "carb", "grao_de_bico": "carb",
    
    # Gorduras
    "azeite": "fat", "pasta_amendoim": "fat", "pasta_amendoa": "fat", "oleo_coco": "fat",
    "manteiga": "fat", "castanhas": "fat", "amendoas": "fat", "nozes": "fat", 
    "chia": "fat", "linhaca": "fat", "queijo": "fat", "cream_cheese": "fat",
    
    # Frutas
    "banana": "fruit", "maca": "fruit", "laranja": "fruit", "morango": "fruit",
    "mamao": "fruit", "manga": "fruit", "melancia": "fruit", "abacate": "fruit",
    "uva": "fruit", "abacaxi": "fruit", "melao": "fruit", "kiwi": "fruit",
    "pera": "fruit", "pessego": "fruit", "mirtilo": "fruit", "acai": "fruit",
    
    # Vegetais
    "salada": "vegetable", "brocolis": "vegetable"
}

def create_test_user() -> Dict:
    """Cria um usuário de teste com perfil completo"""
    print_info("Criando usuário de teste...")
    
    # Dados do usuário para teste
    user_data = {
        "id": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "name": "João Silva",
        "age": 30,
        "sex": "masculino",
        "height": 175.0,
        "weight": 80.0,
        "target_weight": 75.0,
        "body_fat_percentage": 15.0,
        "training_level": "intermediario",
        "weekly_training_frequency": 4,
        "available_time_per_session": 60,
        "goal": "cutting",
        "dietary_restrictions": [],
        "food_preferences": [
            # Proteínas
            "frango", "ovos", "iogurte_grego", "cottage", "tilapia", "atum",
            # Carboidratos
            "arroz_branco", "arroz_integral", "batata_doce", "aveia", "pao_integral", "tapioca",
            # Gorduras
            "azeite", "castanhas", "amendoas",
            # Frutas
            "banana", "maca", "laranja", "morango", "mamao",
            # Vegetais
            "salada", "brocolis"
        ],
        "injury_history": []
    }
    
    try:
        response = requests.post(f"{API_BASE}/user/profile", json=user_data, timeout=30)
        
        if response.status_code == 200:
            profile = response.json()
            print_success(f"Usuário criado: {profile['id']}")
            print_info(f"TDEE: {profile['tdee']}kcal, Target: {profile['target_calories']}kcal")
            print_info(f"Macros: P{profile['macros']['protein']}g C{profile['macros']['carbs']}g F{profile['macros']['fat']}g")
            return profile
        else:
            print_error(f"Erro ao criar usuário: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Erro na requisição: {e}")
        return None

def generate_diet(user_id: str) -> Dict:
    """Gera dieta para o usuário"""
    print_info(f"Gerando dieta para usuário {user_id}...")
    
    try:
        response = requests.post(f"{API_BASE}/diet/generate", json={"user_id": user_id}, timeout=60)
        
        if response.status_code == 200:
            diet = response.json()
            print_success("Dieta gerada com sucesso!")
            print_info(f"Total de refeições: {len(diet['meals'])}")
            print_info(f"Calorias computadas: {diet['computed_calories']}kcal")
            print_info(f"Macros computados: P{diet['computed_macros']['protein']}g C{diet['computed_macros']['carbs']}g F{diet['computed_macros']['fat']}g")
            return diet
        else:
            print_error(f"Erro ao gerar dieta: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Erro na requisição: {e}")
        return None

def get_food_category(food_key: str) -> str:
    """Retorna a categoria de um alimento"""
    return FOOD_CATEGORIES.get(food_key, "unknown")

def validate_meal_rules(meal: Dict, meal_name: str) -> List[str]:
    """Valida se uma refeição segue as regras definidas"""
    errors = []
    
    if meal_name not in MEAL_RULES:
        errors.append(f"Refeição '{meal_name}' não reconhecida")
        return errors
    
    rules = MEAL_RULES[meal_name]
    foods = meal.get("foods", [])
    
    # Contadores por categoria
    proteins = []
    carbs = []
    fats = []
    fruits = []
    vegetables = []
    
    # Classifica alimentos por categoria
    for food in foods:
        food_key = food.get("key", "")
        category = get_food_category(food_key)
        
        if category == "protein":
            proteins.append(food_key)
        elif category == "carb":
            carbs.append(food_key)
        elif category == "fat":
            fats.append(food_key)
        elif category == "fruit":
            fruits.append(food_key)
        elif category == "vegetable":
            vegetables.append(food_key)
    
    # Valida proteínas permitidas
    if "allowed_proteins" in rules:
        for protein in proteins:
            if protein not in rules["allowed_proteins"]:
                errors.append(f"Proteína '{protein}' não permitida em {meal_name}")
    
    # Valida proteínas proibidas
    if "forbidden_proteins" in rules:
        for protein in proteins:
            if protein in rules["forbidden_proteins"]:
                errors.append(f"Proteína '{protein}' PROIBIDA em {meal_name}")
    
    # Valida carboidratos permitidos
    if "allowed_carbs" in rules:
        for carb in carbs:
            if carb not in rules["allowed_carbs"]:
                errors.append(f"Carboidrato '{carb}' não permitido em {meal_name}")
    
    # Valida carboidratos proibidos
    if "forbidden_carbs" in rules:
        for carb in carbs:
            if carb in rules["forbidden_carbs"]:
                errors.append(f"Carboidrato '{carb}' PROIBIDO em {meal_name}")
    
    # Valida gorduras permitidas
    if "allowed_fats" in rules:
        for fat in fats:
            if fat not in rules["allowed_fats"]:
                errors.append(f"Gordura '{fat}' não permitida em {meal_name}")
    
    # Valida gorduras proibidas
    if "forbidden_fats" in rules:
        for fat in fats:
            if fat in rules["forbidden_fats"]:
                errors.append(f"Gordura '{fat}' PROIBIDA em {meal_name}")
    
    # Valida máximo de proteínas
    if "max_proteins" in rules:
        if len(proteins) > rules["max_proteins"]:
            errors.append(f"{meal_name} deve ter EXATAMENTE {rules['max_proteins']} proteína(s), encontradas: {len(proteins)} ({', '.join(proteins)})")
    
    # Valida máximo de carboidratos
    if "max_carbs" in rules:
        if len(carbs) > rules["max_carbs"]:
            errors.append(f"{meal_name} deve ter EXATAMENTE {rules['max_carbs']} carboidrato(s), encontrados: {len(carbs)} ({', '.join(carbs)})")
    
    # Valida presença obrigatória de frutas
    if rules.get("must_have_fruits", False):
        if len(fruits) == 0:
            errors.append(f"{meal_name} DEVE conter frutas")
    
    # Valida presença obrigatória de vegetais
    if rules.get("must_have_vegetables", False):
        if len(vegetables) == 0:
            errors.append(f"{meal_name} DEVE conter legumes/vegetais")
    
    return errors

def validate_diet_structure(diet: Dict) -> List[str]:
    """Valida a estrutura geral da dieta"""
    errors = []
    
    # Verifica se tem 6 refeições
    meals = diet.get("meals", [])
    if len(meals) != 6:
        errors.append(f"Dieta deve ter EXATAMENTE 6 refeições, encontradas: {len(meals)}")
    
    # Verifica se a Ceia existe
    meal_names = [meal.get("name", "") for meal in meals]
    if "Ceia" not in meal_names:
        errors.append("NOVA REFEIÇÃO 'Ceia' não encontrada na dieta")
    
    # Verifica horários esperados
    expected_times = ["07:00", "10:00", "12:30", "16:00", "19:30", "21:30"]
    actual_times = [meal.get("time", "") for meal in meals]
    
    for i, expected_time in enumerate(expected_times):
        if i < len(actual_times):
            if actual_times[i] != expected_time:
                errors.append(f"Refeição {i+1} deveria ser às {expected_time}, mas é às {actual_times[i]}")
        else:
            errors.append(f"Refeição {i+1} faltando (deveria ser às {expected_time})")
    
    return errors

def print_meal_details(meal: Dict, meal_index: int):
    """Imprime detalhes de uma refeição"""
    meal_name = meal.get("name", f"Refeição {meal_index + 1}")
    meal_time = meal.get("time", "??:??")
    foods = meal.get("foods", [])
    
    print(f"\n{Colors.BOLD}{meal_index + 1}. {meal_name} ({meal_time}){Colors.END}")
    
    if not foods:
        print_error("  Refeição VAZIA!")
        return
    
    for food in foods:
        name = food.get("name", "Alimento desconhecido")
        quantity = food.get("quantity", "0g")
        key = food.get("key", "")
        category = get_food_category(key)
        
        # Cor por categoria
        if category == "protein":
            color = Colors.RED
        elif category == "carb":
            color = Colors.YELLOW
        elif category == "fat":
            color = Colors.BLUE
        elif category == "fruit":
            color = Colors.GREEN
        else:
            color = ""
        
        print(f"  {color}• {name} - {quantity} [{category}]{Colors.END}")
    
    # Totais da refeição
    total_cal = meal.get("total_calories", 0)
    macros = meal.get("macros", {})
    p = macros.get("protein", 0)
    c = macros.get("carbs", 0)
    f = macros.get("fat", 0)
    
    print(f"  📊 Total: {total_cal}kcal | P{p}g C{c}g F{f}g")

def run_diet_validation_test():
    """Executa o teste completo de validação da dieta"""
    print_header("TESTE DE VALIDAÇÃO DAS REGRAS POR REFEIÇÃO")
    print_info("Testando POST /api/diet/generate")
    print_info(f"Backend URL: {BACKEND_URL}")
    
    # 1. Criar usuário de teste
    print_header("1. CRIAÇÃO DO USUÁRIO DE TESTE")
    user_profile = create_test_user()
    if not user_profile:
        print_error("Falha ao criar usuário. Abortando teste.")
        return False
    
    # 2. Gerar dieta
    print_header("2. GERAÇÃO DA DIETA")
    diet = generate_diet(user_profile["id"])
    if not diet:
        print_error("Falha ao gerar dieta. Abortando teste.")
        return False
    
    # 3. Validar estrutura geral
    print_header("3. VALIDAÇÃO DA ESTRUTURA GERAL")
    structure_errors = validate_diet_structure(diet)
    
    if structure_errors:
        print_error("Erros na estrutura da dieta:")
        for error in structure_errors:
            print_error(f"  • {error}")
    else:
        print_success("Estrutura da dieta está correta!")
    
    # 4. Mostrar detalhes das refeições
    print_header("4. DETALHES DAS REFEIÇÕES GERADAS")
    meals = diet.get("meals", [])
    
    for i, meal in enumerate(meals):
        print_meal_details(meal, i)
    
    # 5. Validar regras por refeição
    print_header("5. VALIDAÇÃO DAS REGRAS POR REFEIÇÃO")
    
    total_errors = 0
    
    for i, meal in enumerate(meals):
        meal_name = meal.get("name", f"Refeição {i + 1}")
        print(f"\n{Colors.BOLD}Validando {meal_name}:{Colors.END}")
        
        meal_errors = validate_meal_rules(meal, meal_name)
        
        if meal_errors:
            total_errors += len(meal_errors)
            print_error(f"  {len(meal_errors)} erro(s) encontrado(s):")
            for error in meal_errors:
                print_error(f"    • {error}")
        else:
            print_success(f"  {meal_name} está conforme as regras!")
    
    # 6. Resumo final
    print_header("6. RESUMO FINAL")
    
    structure_ok = len(structure_errors) == 0
    rules_ok = total_errors == 0
    
    print(f"📊 Estrutura da dieta: {'✅ OK' if structure_ok else '❌ ERRO'}")
    print(f"📋 Regras por refeição: {'✅ OK' if rules_ok else f'❌ {total_errors} ERRO(S)'}")
    print(f"🍽️  Total de refeições: {len(meals)}")
    print(f"⏰ Ceia (21:30) presente: {'✅ SIM' if any(m.get('name') == 'Ceia' for m in meals) else '❌ NÃO'}")
    
    # Totais da dieta
    target_cal = diet.get("target_calories", 0)
    computed_cal = diet.get("computed_calories", 0)
    target_macros = diet.get("target_macros", {})
    computed_macros = diet.get("computed_macros", {})
    
    print(f"\n📈 MACROS:")
    print(f"   Target:   {target_cal}kcal | P{target_macros.get('protein', 0)}g C{target_macros.get('carbs', 0)}g F{target_macros.get('fat', 0)}g")
    print(f"   Computed: {computed_cal}kcal | P{computed_macros.get('protein', 0)}g C{computed_macros.get('carbs', 0)}g F{computed_macros.get('fat', 0)}g")
    
    cal_diff = abs(computed_cal - target_cal)
    p_diff = abs(computed_macros.get('protein', 0) - target_macros.get('protein', 0))
    c_diff = abs(computed_macros.get('carbs', 0) - target_macros.get('carbs', 0))
    f_diff = abs(computed_macros.get('fat', 0) - target_macros.get('fat', 0))
    
    print(f"   Diferenças: Δ{cal_diff}kcal | ΔP{p_diff}g ΔC{c_diff}g ΔF{f_diff}g")
    
    # Resultado final
    all_ok = structure_ok and rules_ok
    
    if all_ok:
        print_success("\n🎉 TESTE PASSOU! Todas as regras por refeição estão funcionando corretamente.")
    else:
        print_error(f"\n💥 TESTE FALHOU! {len(structure_errors) + total_errors} erro(s) encontrado(s).")
    
    return all_ok

if __name__ == "__main__":
    print(f"{Colors.BOLD}Teste de Validação das Regras por Refeição - LAF Diet System{Colors.END}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = run_diet_validation_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\nTeste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)