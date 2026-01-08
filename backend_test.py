#!/usr/bin/env python3
"""
Teste Rigoroso do Endpoint POST /api/diet/generate
=================================================

OBJETIVO: Validar REGRAS RÍGIDAS por tipo de refeição conforme especificação.

REGRA DE FALHA CRÍTICA:
Se arroz, frango, peixe ou azeite aparecerem em lanches ou café, a saída é INVÁLIDA!

VALIDAÇÕES OBRIGATÓRIAS:

☀️ CAFÉ DA MANHÃ (índice 0):
- DEVE conter APENAS: Ovos OU Cottage OU Iogurte Grego
- DEVE conter: Aveia OU Pão Integral
- PODE conter: Frutas
- NÃO PODE conter: Arroz, Feijão, Frango, Peixe, Carne, Peru, Azeite

🍎 LANCHE MANHÃ (índice 1):
- DEVE conter: Frutas
- PODE conter: Castanhas, Amêndoas
- NÃO PODE conter: Arroz, Aveia, Pão, Batatas, Frango, Peixe, Carne, Peru, OVOS, Azeite, Pasta de Amendoim, Queijo

🍽️ ALMOÇO (índice 2):
- DEVE conter: EXATAMENTE 1 proteína (Frango, Patinho, Peixe, Peru)
- DEVE conter: EXATAMENTE 1 carboidrato (Arroz, Batata, Macarrão, Feijão, Lentilha)
- PODE conter: Azeite, Legumes

🍎 LANCHE TARDE (índice 3):
- DEVE conter: Frutas
- PODE conter: Iogurte Grego OU Cottage, Castanhas, Amêndoas
- NÃO PODE conter: Arroz, Aveia, Pão, Batatas, Frango, Peixe, Carne, Peru, OVOS, Azeite, Pasta de Amendoim

🍽️ JANTAR (índice 4):
- DEVE conter: EXATAMENTE 1 proteína
- DEVE conter: EXATAMENTE 1 carboidrato
- PODE conter: Azeite, Legumes

🌙 CEIA (índice 5):
- DEVE conter: Cottage OU Iogurte Grego OU Ovos
- PODE conter: Frutas
- NÃO PODE conter: Arroz, Batatas, Massas, Frango, Peixe, Carne, Azeite
"""

import requests
import json
import sys
from typing import Dict, List, Any, Set

# Configuração da API
BASE_URL = "https://athlete-phase.preview.emergentagent.com/api"

# Mapeamento de alimentos para categorias e validação
FOOD_CATEGORIES = {
    # PROTEÍNAS PRINCIPAIS (permitidas em almoço/jantar)
    "frango": "main_protein",
    "patinho": "main_protein", 
    "tilapia": "main_protein",
    "atum": "main_protein",
    "salmao": "main_protein",
    "peru": "main_protein",
    "carne_moida": "main_protein",
    
    # PROTEÍNAS LEVES (permitidas em café/ceia/lanches)
    "ovos": "light_protein",
    "cottage": "light_protein",
    "iogurte_grego": "light_protein",
    
    # CARBOIDRATOS PRINCIPAIS (permitidos em almoço/jantar)
    "arroz_branco": "main_carb",
    "arroz_integral": "main_carb",
    "batata_doce": "main_carb",
    "batata": "main_carb",
    "macarrao": "main_carb",
    "feijao": "main_carb",
    "lentilha": "main_carb",
    
    # CARBOIDRATOS LEVES (permitidos apenas no café)
    "aveia": "light_carb",
    "pao_integral": "light_carb",
    
    # GORDURAS
    "azeite": "fat",
    "pasta_amendoim": "fat",
    "castanhas": "fat",
    "amendoas": "fat",
    "queijo": "fat",
    
    # FRUTAS
    "banana": "fruit",
    "maca": "fruit",
    "laranja": "fruit",
    "morango": "fruit",
    "mamao": "fruit",
    "melancia": "fruit",
    
    # VEGETAIS
    "salada": "vegetable",
    "brocolis": "vegetable"
}

# Alimentos PROIBIDOS por tipo de refeição
FORBIDDEN_FOODS = {
    "cafe_da_manha": {
        "arroz_branco", "arroz_integral", "feijao", "lentilha", "macarrao",
        "frango", "patinho", "tilapia", "atum", "salmao", "peru", "carne_moida",
        "azeite", "batata_doce", "batata"
    },
    "lanche_manha": {
        "arroz_branco", "arroz_integral", "aveia", "pao_integral", "batata_doce", "batata",
        "frango", "patinho", "tilapia", "atum", "salmao", "peru", "carne_moida",
        "ovos", "azeite", "pasta_amendoim", "queijo", "feijao", "lentilha", "macarrao"
    },
    "lanche_tarde": {
        "arroz_branco", "arroz_integral", "aveia", "pao_integral", "batata_doce", "batata",
        "frango", "patinho", "tilapia", "atum", "salmao", "peru", "carne_moida",
        "ovos", "azeite", "pasta_amendoim", "feijao", "lentilha", "macarrao"
    },
    "ceia": {
        "arroz_branco", "arroz_integral", "batata_doce", "batata", "macarrao",
        "frango", "patinho", "tilapia", "atum", "salmao", "peru", "carne_moida",
        "azeite", "feijao", "lentilha"
    }
}

# Alimentos OBRIGATÓRIOS por tipo de refeição
REQUIRED_FOODS = {
    "cafe_da_manha": {
        "proteins": {"ovos", "cottage", "iogurte_grego"},  # APENAS UM destes
        "carbs": {"aveia", "pao_integral"}  # APENAS UM destes
    },
    "lanche_manha": {
        "fruits": True  # DEVE ter frutas
    },
    "almoco": {
        "main_proteins": 1,  # EXATAMENTE 1 proteína principal
        "main_carbs": 1      # EXATAMENTE 1 carboidrato principal
    },
    "lanche_tarde": {
        "fruits": True  # DEVE ter frutas
    },
    "jantar": {
        "main_proteins": 1,  # EXATAMENTE 1 proteína principal
        "main_carbs": 1      # EXATAMENTE 1 carboidrato principal
    },
    "ceia": {
        "proteins": {"ovos", "cottage", "iogurte_grego"}  # APENAS UM destes
    }
}

def normalize_food_name(food_name: str) -> str:
    """Normaliza nome do alimento para chave padrão"""
    # Remove acentos e converte para minúsculo
    name = food_name.lower().strip()
    
    # Mapeamentos comuns
    mappings = {
        "peito de frango": "frango",
        "frango grelhado": "frango",
        "patinho (carne magra)": "patinho",
        "carne magra": "patinho",
        "ovos inteiros": "ovos",
        "queijo cottage": "cottage",
        "iogurte grego": "iogurte_grego",
        "arroz branco": "arroz_branco",
        "arroz integral": "arroz_integral",
        "batata doce": "batata_doce",
        "batata inglesa": "batata",
        "pão integral": "pao_integral",
        "azeite de oliva": "azeite",
        "pasta de amendoim": "pasta_amendoim",
        "salada verde": "salada",
        "brócolis": "brocolis",
        "maçã": "maca"
    }
    
    return mappings.get(name, name.replace(" ", "_").replace("ã", "a").replace("ç", "c"))

def create_test_user() -> str:
    """Cria usuário de teste com perfil completo"""
    print("🔧 Criando usuário de teste...")
    
    # Dados realistas para teste
    user_data = {
        "id": "test_diet_rules_user_001",
        "name": "Carlos Silva",
        "age": 28,
        "sex": "masculino",
        "height": 175.0,
        "weight": 80.0,
        "target_weight": 75.0,
        "body_fat_percentage": 15.0,
        "training_level": "intermediario",
        "weekly_training_frequency": 5,
        "available_time_per_session": 60,
        "goal": "cutting",
        "dietary_restrictions": [],
        "food_preferences": [
            "frango", "patinho", "tilapia", "ovos", "cottage", "iogurte_grego",
            "arroz_branco", "arroz_integral", "batata_doce", "aveia", "pao_integral",
            "azeite", "castanhas", "amendoas", "banana", "maca", "laranja", "morango"
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/profile", json=user_data, timeout=30)
        if response.status_code == 200:
            print(f"✅ Usuário criado: {user_data['id']}")
            return user_data['id']
        else:
            print(f"❌ Erro ao criar usuário: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro de conexão ao criar usuário: {e}")
        return None

def generate_diet(user_id: str) -> Dict:
    """Gera dieta para o usuário"""
    print(f"🍽️ Gerando dieta para usuário {user_id}...")
    
    try:
        response = requests.post(f"{BASE_URL}/diet/generate", params={"user_id": user_id}, timeout=60)
        if response.status_code == 200:
            diet_data = response.json()
            print(f"✅ Dieta gerada com sucesso")
            return diet_data
        else:
            print(f"❌ Erro ao gerar dieta: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro de conexão ao gerar dieta: {e}")
        return None

def validate_meal_structure(diet_data: Dict) -> List[str]:
    """Valida estrutura básica da dieta"""
    errors = []
    
    # Verifica se tem campo meals
    if "meals" not in diet_data:
        errors.append("❌ CRÍTICO: Campo 'meals' não encontrado na resposta")
        return errors
    
    meals = diet_data["meals"]
    
    # Verifica se tem exatamente 6 refeições
    if len(meals) != 6:
        errors.append(f"❌ CRÍTICO: Esperado 6 refeições, encontrado {len(meals)}")
        return errors
    
    # Verifica estrutura de cada refeição
    expected_meal_names = [
        "Café da Manhã", "Lanche Manhã", "Almoço", 
        "Lanche Tarde", "Jantar", "Ceia"
    ]
    
    for i, meal in enumerate(meals):
        if "name" not in meal:
            errors.append(f"❌ Refeição {i}: Campo 'name' ausente")
        elif meal["name"] not in expected_meal_names:
            errors.append(f"⚠️ Refeição {i}: Nome inesperado '{meal['name']}'")
        
        if "foods" not in meal:
            errors.append(f"❌ CRÍTICO: Refeição {i} ({meal.get('name', 'N/A')}): Campo 'foods' ausente")
        elif len(meal["foods"]) == 0:
            errors.append(f"❌ CRÍTICO: Refeição {i} ({meal.get('name', 'N/A')}): Lista de alimentos vazia")
    
    return errors

def validate_forbidden_foods(meals: List[Dict]) -> List[str]:
    """Valida REGRA CRÍTICA: alimentos proibidos por tipo de refeição"""
    errors = []
    
    meal_types = ["cafe_da_manha", "lanche_manha", "almoco", "lanche_tarde", "jantar", "ceia"]
    
    for i, meal in enumerate(meals):
        if i >= len(meal_types):
            continue
            
        meal_type = meal_types[i]
        meal_name = meal.get("name", f"Refeição {i}")
        foods = meal.get("foods", [])
        
        forbidden = FORBIDDEN_FOODS.get(meal_type, set())
        
        for food in foods:
            food_name = food.get("name", "")
            food_key = normalize_food_name(food_name)
            
            if food_key in forbidden:
                errors.append(f"❌ CRÍTICO: {meal_name} contém alimento PROIBIDO: {food_name} ({food_key})")
        
        # REGRA ESPECIAL: Arroz, Frango, Peixe, Azeite em lanches ou café = INVÁLIDO
        critical_forbidden = {"arroz_branco", "arroz_integral", "frango", "tilapia", "atum", "salmao", "azeite"}
        
        if meal_type in ["cafe_da_manha", "lanche_manha", "lanche_tarde"]:
            for food in foods:
                food_key = normalize_food_name(food.get("name", ""))
                if food_key in critical_forbidden:
                    errors.append(f"🚨 FALHA CRÍTICA: {meal_name} contém {food.get('name')} - SAÍDA INVÁLIDA!")
    
    return errors

def validate_required_foods(meals: List[Dict]) -> List[str]:
    """Valida alimentos obrigatórios por tipo de refeição"""
    errors = []
    
    meal_types = ["cafe_da_manha", "lanche_manha", "almoco", "lanche_tarde", "jantar", "ceia"]
    
    for i, meal in enumerate(meals):
        if i >= len(meal_types):
            continue
            
        meal_type = meal_types[i]
        meal_name = meal.get("name", f"Refeição {i}")
        foods = meal.get("foods", [])
        
        # Extrai chaves dos alimentos presentes
        present_foods = set()
        main_proteins = 0
        main_carbs = 0
        has_fruits = False
        
        for food in foods:
            food_key = normalize_food_name(food.get("name", ""))
            present_foods.add(food_key)
            
            # Conta proteínas e carboidratos principais
            if food_key in FOOD_CATEGORIES:
                category = FOOD_CATEGORIES[food_key]
                if category == "main_protein":
                    main_proteins += 1
                elif category == "main_carb":
                    main_carbs += 1
                elif category == "fruit":
                    has_fruits = True
        
        # Valida requisitos específicos por refeição
        requirements = REQUIRED_FOODS.get(meal_type, {})
        
        if meal_type == "cafe_da_manha":
            # DEVE ter proteína leve (ovos, cottage, iogurte)
            required_proteins = requirements.get("proteins", set())
            has_required_protein = any(p in present_foods for p in required_proteins)
            if not has_required_protein:
                errors.append(f"❌ {meal_name}: DEVE conter uma proteína leve: {', '.join(required_proteins)}")
            
            # DEVE ter carboidrato leve (aveia, pão integral)
            required_carbs = requirements.get("carbs", set())
            has_required_carb = any(c in present_foods for c in required_carbs)
            if not has_required_carb:
                errors.append(f"❌ {meal_name}: DEVE conter carboidrato leve: {', '.join(required_carbs)}")
        
        elif meal_type in ["lanche_manha", "lanche_tarde"]:
            # DEVE ter frutas
            if not has_fruits:
                errors.append(f"❌ {meal_name}: DEVE conter frutas")
        
        elif meal_type in ["almoco", "jantar"]:
            # DEVE ter EXATAMENTE 1 proteína principal
            if main_proteins != 1:
                errors.append(f"❌ {meal_name}: DEVE conter EXATAMENTE 1 proteína principal (encontrado: {main_proteins})")
            
            # DEVE ter EXATAMENTE 1 carboidrato principal
            if main_carbs != 1:
                errors.append(f"❌ {meal_name}: DEVE conter EXATAMENTE 1 carboidrato principal (encontrado: {main_carbs})")
        
        elif meal_type == "ceia":
            # DEVE ter proteína leve (ovos, cottage, iogurte)
            required_proteins = requirements.get("proteins", set())
            has_required_protein = any(p in present_foods for p in required_proteins)
            if not has_required_protein:
                errors.append(f"❌ {meal_name}: DEVE conter uma proteína leve: {', '.join(required_proteins)}")
    
    return errors

def print_diet_summary(diet_data: Dict):
    """Imprime resumo da dieta gerada"""
    print("\n" + "="*60)
    print("📋 RESUMO DA DIETA GERADA")
    print("="*60)
    
    meals = diet_data.get("meals", [])
    
    for i, meal in enumerate(meals):
        print(f"\n{i}. {meal.get('name', 'N/A')} ({meal.get('time', 'N/A')})")
        foods = meal.get("foods", [])
        
        for food in foods:
            name = food.get("name", "N/A")
            quantity = food.get("quantity", "N/A")
            calories = food.get("calories", 0)
            protein = food.get("protein", 0)
            carbs = food.get("carbs", 0)
            fat = food.get("fat", 0)
            
            print(f"   • {name} - {quantity} ({calories}kcal, P:{protein}g, C:{carbs}g, G:{fat}g)")
    
    # Totais
    computed_calories = diet_data.get("computed_calories", 0)
    computed_macros = diet_data.get("computed_macros", {})
    target_calories = diet_data.get("target_calories", 0)
    target_macros = diet_data.get("target_macros", {})
    
    print(f"\n📊 TOTAIS COMPUTADOS:")
    print(f"   Calorias: {computed_calories}kcal (Target: {target_calories}kcal)")
    print(f"   Proteína: {computed_macros.get('protein', 0)}g (Target: {target_macros.get('protein', 0)}g)")
    print(f"   Carboidratos: {computed_macros.get('carbs', 0)}g (Target: {target_macros.get('carbs', 0)}g)")
    print(f"   Gordura: {computed_macros.get('fat', 0)}g (Target: {target_macros.get('fat', 0)}g)")

def run_comprehensive_test():
    """Executa teste completo das regras de refeição"""
    print("🧪 INICIANDO TESTE RIGOROSO DO ENDPOINT /api/diet/generate")
    print("="*70)
    
    # 1. Criar usuário de teste
    user_id = create_test_user()
    if not user_id:
        print("❌ TESTE FALHOU: Não foi possível criar usuário")
        return False
    
    # 2. Gerar dieta
    diet_data = generate_diet(user_id)
    if not diet_data:
        print("❌ TESTE FALHOU: Não foi possível gerar dieta")
        return False
    
    # 3. Imprimir resumo da dieta
    print_diet_summary(diet_data)
    
    # 4. Validar estrutura
    print("\n🔍 VALIDANDO ESTRUTURA DA DIETA...")
    structure_errors = validate_meal_structure(diet_data)
    
    if structure_errors:
        print("❌ ERROS DE ESTRUTURA:")
        for error in structure_errors:
            print(f"   {error}")
        return False
    else:
        print("✅ Estrutura da dieta válida (6 refeições)")
    
    # 5. Validar alimentos proibidos (REGRA CRÍTICA)
    print("\n🚫 VALIDANDO ALIMENTOS PROIBIDOS...")
    forbidden_errors = validate_forbidden_foods(diet_data["meals"])
    
    if forbidden_errors:
        print("❌ VIOLAÇÕES DE REGRAS CRÍTICAS:")
        for error in forbidden_errors:
            print(f"   {error}")
        return False
    else:
        print("✅ Nenhum alimento proibido encontrado")
    
    # 6. Validar alimentos obrigatórios
    print("\n✅ VALIDANDO ALIMENTOS OBRIGATÓRIOS...")
    required_errors = validate_required_foods(diet_data["meals"])
    
    if required_errors:
        print("❌ ALIMENTOS OBRIGATÓRIOS AUSENTES:")
        for error in required_errors:
            print(f"   {error}")
        return False
    else:
        print("✅ Todos os alimentos obrigatórios presentes")
    
    # 7. Resultado final
    print("\n" + "="*70)
    print("🎉 TESTE COMPLETO: TODAS AS REGRAS VALIDADAS COM SUCESSO!")
    print("✅ Endpoint POST /api/diet/generate está funcionando corretamente")
    print("✅ Regras rígidas por tipo de refeição respeitadas")
    print("✅ Nenhuma violação crítica encontrada")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)