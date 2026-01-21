#!/usr/bin/env python3
"""
TESTE DE PREFERÊNCIAS ALIMENTARES - LAF Backend Testing
Testa se os alimentos PREFERIDOS realmente aparecem na dieta gerada.

Base URL: https://workoutcycler.preview.emergentagent.com/api
"""

import requests
import json
import time
from typing import Dict, List, Any

# Configuração
BASE_URL = "https://workoutcycler.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class FoodPreferencesTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name: str, success: bool, details: str):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}: {details}")
        else:
            print(f"❌ {test_name}: {details}")
        
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def create_profile(self, profile_data: Dict) -> bool:
        """Create user profile"""
        try:
            response = requests.post(f"{BASE_URL}/user/profile", json=profile_data, headers=HEADERS)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Erro ao criar perfil {profile_data['id']}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Exceção ao criar perfil {profile_data['id']}: {e}")
            return False
    
    def generate_diet(self, user_id: str) -> Dict:
        """Generate diet for user"""
        try:
            response = requests.post(f"{BASE_URL}/diet/generate?user_id={user_id}", headers=HEADERS)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao gerar dieta para {user_id}: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"❌ Exceção ao gerar dieta para {user_id}: {e}")
            return {}
    
    def extract_foods_from_diet(self, diet_plan: Dict) -> List[str]:
        """Extract all food names/keys from diet plan"""
        foods = []
        for meal in diet_plan.get("meals", []):
            for food in meal.get("foods", []):
                food_key = food.get("key", "").lower()
                food_name = food.get("name", "").lower()
                foods.append(food_key)
                foods.append(food_name)
        return foods
    
    def check_food_preferences(self, user_id: str, preferred_foods: List[str], diet_plan: Dict) -> Dict:
        """Check if preferred foods appear in diet"""
        diet_foods = self.extract_foods_from_diet(diet_plan)
        diet_foods_str = " ".join(diet_foods).lower()
        
        results = {}
        found_preferences = []
        
        # Mapeamento de preferências para possíveis variações nos alimentos
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
        
        for pref in preferred_foods:
            pref_lower = pref.lower()
            variations = food_mappings.get(pref_lower, [pref_lower])
            
            found = False
            for variation in variations:
                if variation in diet_foods_str:
                    found = True
                    found_preferences.append(pref)
                    break
            
            results[pref] = found
        
        return {
            "results": results,
            "found_count": len(found_preferences),
            "total_preferences": len(preferred_foods),
            "found_preferences": found_preferences,
            "diet_foods": diet_foods[:10]  # Primeiros 10 alimentos para debug
        }
    
    def test_profile_1_batata_tilapia(self):
        """PERFIL 1 - Preferência: BATATA DOCE + TILÁPIA + ABACATE + MORANGO"""
        print("\n🧪 TESTANDO PERFIL 1 - BATATA DOCE + TILÁPIA + ABACATE + MORANGO")
        
        profile_data = {
            "id": "pref-test-1",
            "user_id": "pref-test-1",
            "name": "Teste Batata Tilapia",
            "email": "pref1@test.com",
            "age": 28,
            "sex": "masculino",
            "height": 180,
            "weight": 80,
            "target_weight": 75,
            "goal": "cutting",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "dietary_restrictions": [],
            "food_preferences": ["batata_doce", "tilapia", "abacate", "morango"],
            "meal_count": 5
        }
        
        # Criar perfil
        if not self.create_profile(profile_data):
            self.log_result("PERFIL 1 - Criação", False, "Falha ao criar perfil")
            return
        
        self.log_result("PERFIL 1 - Criação", True, "Perfil criado com sucesso")
        
        # Gerar dieta
        diet_plan = self.generate_diet("pref-test-1")
        if not diet_plan:
            self.log_result("PERFIL 1 - Geração Dieta", False, "Falha ao gerar dieta")
            return
        
        self.log_result("PERFIL 1 - Geração Dieta", True, f"Dieta gerada com {len(diet_plan.get('meals', []))} refeições")
        
        # Verificar preferências
        pref_results = self.check_food_preferences("pref-test-1", ["batata_doce", "tilapia", "abacate", "morango"], diet_plan)
        
        # Validações específicas
        results = pref_results["results"]
        
        # BATATA DOCE deve aparecer (não arroz como carboidrato principal)
        batata_found = results.get("batata_doce", False)
        self.log_result("PERFIL 1 - BATATA DOCE", batata_found, 
                       "BATATA DOCE encontrada na dieta" if batata_found else "BATATA DOCE NÃO encontrada - pode ter arroz como principal")
        
        # TILÁPIA deve aparecer (não frango como proteína principal)
        tilapia_found = results.get("tilapia", False)
        self.log_result("PERFIL 1 - TILÁPIA", tilapia_found,
                       "TILÁPIA encontrada na dieta" if tilapia_found else "TILÁPIA NÃO encontrada - pode ter frango como principal")
        
        # ABACATE deve aparecer
        abacate_found = results.get("abacate", False)
        self.log_result("PERFIL 1 - ABACATE", abacate_found,
                       "ABACATE encontrado na dieta" if abacate_found else "ABACATE NÃO encontrado")
        
        # MORANGO deve aparecer
        morango_found = results.get("morango", False)
        self.log_result("PERFIL 1 - MORANGO", morango_found,
                       "MORANGO encontrado na dieta" if morango_found else "MORANGO NÃO encontrado")
        
        # Verificar número de refeições
        meal_count = len(diet_plan.get("meals", []))
        expected_meals = 5
        meals_correct = meal_count == expected_meals
        self.log_result("PERFIL 1 - MEAL COUNT", meals_correct,
                       f"Correto: {meal_count} refeições" if meals_correct else f"Incorreto: {meal_count} refeições (esperado {expected_meals})")
        
        print(f"📊 PERFIL 1 RESUMO: {pref_results['found_count']}/{pref_results['total_preferences']} preferências encontradas")
        print(f"🍽️ Alimentos encontrados: {pref_results['found_preferences']}")
    
    def test_profile_2_macarrao_carne(self):
        """PERFIL 2 - Preferência: MACARRÃO + CARNE MOÍDA + BANANA + CASTANHAS"""
        print("\n🧪 TESTANDO PERFIL 2 - MACARRÃO + CARNE MOÍDA + BANANA + CASTANHAS")
        
        profile_data = {
            "id": "pref-test-2",
            "user_id": "pref-test-2",
            "name": "Teste Macarrao Carne",
            "email": "pref2@test.com",
            "age": 30,
            "sex": "feminino",
            "height": 165,
            "weight": 60,
            "target_weight": 65,
            "goal": "bulking",
            "training_level": "avancado",
            "weekly_training_frequency": 5,
            "available_time_per_session": 90,
            "dietary_restrictions": [],
            "food_preferences": ["macarrao", "carne_moida", "banana", "castanhas"],
            "meal_count": 5
        }
        
        # Criar perfil
        if not self.create_profile(profile_data):
            self.log_result("PERFIL 2 - Criação", False, "Falha ao criar perfil")
            return
        
        self.log_result("PERFIL 2 - Criação", True, "Perfil criado com sucesso")
        
        # Gerar dieta
        diet_plan = self.generate_diet("pref-test-2")
        if not diet_plan:
            self.log_result("PERFIL 2 - Geração Dieta", False, "Falha ao gerar dieta")
            return
        
        self.log_result("PERFIL 2 - Geração Dieta", True, f"Dieta gerada com {len(diet_plan.get('meals', []))} refeições")
        
        # Verificar preferências
        pref_results = self.check_food_preferences("pref-test-2", ["macarrao", "carne_moida", "banana", "castanhas"], diet_plan)
        
        # Validações específicas
        results = pref_results["results"]
        
        # MACARRÃO deve aparecer (não arroz)
        macarrao_found = results.get("macarrao", False)
        self.log_result("PERFIL 2 - MACARRÃO", macarrao_found,
                       "MACARRÃO encontrado na dieta" if macarrao_found else "MACARRÃO NÃO encontrado - pode ter arroz")
        
        # CARNE MOÍDA deve aparecer (não frango)
        carne_found = results.get("carne_moida", False)
        self.log_result("PERFIL 2 - CARNE MOÍDA", carne_found,
                       "CARNE MOÍDA encontrada na dieta" if carne_found else "CARNE MOÍDA NÃO encontrada - pode ter frango")
        
        # BANANA deve aparecer
        banana_found = results.get("banana", False)
        self.log_result("PERFIL 2 - BANANA", banana_found,
                       "BANANA encontrada na dieta" if banana_found else "BANANA NÃO encontrada")
        
        # CASTANHAS devem aparecer
        castanhas_found = results.get("castanhas", False)
        self.log_result("PERFIL 2 - CASTANHAS", castanhas_found,
                       "CASTANHAS encontradas na dieta" if castanhas_found else "CASTANHAS NÃO encontradas")
        
        print(f"📊 PERFIL 2 RESUMO: {pref_results['found_count']}/{pref_results['total_preferences']} preferências encontradas")
        print(f"🍽️ Alimentos encontrados: {pref_results['found_preferences']}")
    
    def test_profile_3_aveia_salmao(self):
        """PERFIL 3 - Preferência: AVEIA + SALMÃO + MAMÃO + AMENDOIM"""
        print("\n🧪 TESTANDO PERFIL 3 - AVEIA + SALMÃO + MAMÃO + AMENDOIM")
        
        profile_data = {
            "id": "pref-test-3",
            "user_id": "pref-test-3",
            "name": "Teste Aveia Salmao",
            "email": "pref3@test.com",
            "age": 35,
            "sex": "masculino",
            "height": 175,
            "weight": 85,
            "target_weight": 85,
            "goal": "manutencao",
            "training_level": "iniciante",
            "weekly_training_frequency": 3,
            "available_time_per_session": 45,
            "dietary_restrictions": [],
            "food_preferences": ["aveia", "salmao", "mamao", "amendoim"],
            "meal_count": 5
        }
        
        # Criar perfil
        if not self.create_profile(profile_data):
            self.log_result("PERFIL 3 - Criação", False, "Falha ao criar perfil")
            return
        
        self.log_result("PERFIL 3 - Criação", True, "Perfil criado com sucesso")
        
        # Gerar dieta
        diet_plan = self.generate_diet("pref-test-3")
        if not diet_plan:
            self.log_result("PERFIL 3 - Geração Dieta", False, "Falha ao gerar dieta")
            return
        
        self.log_result("PERFIL 3 - Geração Dieta", True, f"Dieta gerada com {len(diet_plan.get('meals', []))} refeições")
        
        # Verificar preferências
        pref_results = self.check_food_preferences("pref-test-3", ["aveia", "salmao", "mamao", "amendoim"], diet_plan)
        
        # Validações específicas
        results = pref_results["results"]
        
        # AVEIA deve aparecer no café da manhã
        aveia_found = results.get("aveia", False)
        self.log_result("PERFIL 3 - AVEIA", aveia_found,
                       "AVEIA encontrada na dieta" if aveia_found else "AVEIA NÃO encontrada no café da manhã")
        
        # SALMÃO deve aparecer (não frango ou tilápia)
        salmao_found = results.get("salmao", False)
        self.log_result("PERFIL 3 - SALMÃO", salmao_found,
                       "SALMÃO encontrado na dieta" if salmao_found else "SALMÃO NÃO encontrado - pode ter frango/tilápia")
        
        # MAMÃO deve aparecer
        mamao_found = results.get("mamao", False)
        self.log_result("PERFIL 3 - MAMÃO", mamao_found,
                       "MAMÃO encontrado na dieta" if mamao_found else "MAMÃO NÃO encontrado")
        
        # AMENDOIM deve aparecer
        amendoim_found = results.get("amendoim", False)
        self.log_result("PERFIL 3 - AMENDOIM", amendoim_found,
                       "AMENDOIM encontrado na dieta" if amendoim_found else "AMENDOIM NÃO encontrado")
        
        print(f"📊 PERFIL 3 RESUMO: {pref_results['found_count']}/{pref_results['total_preferences']} preferências encontradas")
        print(f"🍽️ Alimentos encontrados: {pref_results['found_preferences']}")
    
    def test_profile_4_arroz_atum(self):
        """PERFIL 4 - Preferência: ARROZ INTEGRAL + ATUM + LARANJA + AZEITE"""
        print("\n🧪 TESTANDO PERFIL 4 - ARROZ INTEGRAL + ATUM + LARANJA + AZEITE")
        
        profile_data = {
            "id": "pref-test-4",
            "user_id": "pref-test-4",
            "name": "Teste Arroz Atum",
            "email": "pref4@test.com",
            "age": 25,
            "sex": "feminino",
            "height": 160,
            "weight": 55,
            "target_weight": 52,
            "goal": "cutting",
            "training_level": "iniciante",
            "weekly_training_frequency": 2,
            "available_time_per_session": 30,
            "dietary_restrictions": [],
            "food_preferences": ["arroz_integral", "atum", "laranja", "azeite"],
            "meal_count": 4
        }
        
        # Criar perfil
        if not self.create_profile(profile_data):
            self.log_result("PERFIL 4 - Criação", False, "Falha ao criar perfil")
            return
        
        self.log_result("PERFIL 4 - Criação", True, "Perfil criado com sucesso")
        
        # Gerar dieta
        diet_plan = self.generate_diet("pref-test-4")
        if not diet_plan:
            self.log_result("PERFIL 4 - Geração Dieta", False, "Falha ao gerar dieta")
            return
        
        self.log_result("PERFIL 4 - Geração Dieta", True, f"Dieta gerada com {len(diet_plan.get('meals', []))} refeições")
        
        # Verificar preferências
        pref_results = self.check_food_preferences("pref-test-4", ["arroz_integral", "atum", "laranja", "azeite"], diet_plan)
        
        # Validações específicas
        results = pref_results["results"]
        
        # ARROZ INTEGRAL deve aparecer (não arroz branco)
        arroz_found = results.get("arroz_integral", False)
        self.log_result("PERFIL 4 - ARROZ INTEGRAL", arroz_found,
                       "ARROZ INTEGRAL encontrado na dieta" if arroz_found else "ARROZ INTEGRAL NÃO encontrado - pode ter arroz branco")
        
        # ATUM deve aparecer (não frango)
        atum_found = results.get("atum", False)
        self.log_result("PERFIL 4 - ATUM", atum_found,
                       "ATUM encontrado na dieta" if atum_found else "ATUM NÃO encontrado - pode ter frango")
        
        # LARANJA deve aparecer
        laranja_found = results.get("laranja", False)
        self.log_result("PERFIL 4 - LARANJA", laranja_found,
                       "LARANJA encontrada na dieta" if laranja_found else "LARANJA NÃO encontrada")
        
        # AZEITE deve aparecer
        azeite_found = results.get("azeite", False)
        self.log_result("PERFIL 4 - AZEITE", azeite_found,
                       "AZEITE encontrado na dieta" if azeite_found else "AZEITE NÃO encontrado")
        
        # Verificar número de refeições (4)
        meal_count = len(diet_plan.get("meals", []))
        expected_meals = 4
        meals_correct = meal_count == expected_meals
        self.log_result("PERFIL 4 - MEAL COUNT", meals_correct,
                       f"Correto: {meal_count} refeições" if meals_correct else f"Incorreto: {meal_count} refeições (esperado {expected_meals})")
        
        print(f"📊 PERFIL 4 RESUMO: {pref_results['found_count']}/{pref_results['total_preferences']} preferências encontradas")
        print(f"🍽️ Alimentos encontrados: {pref_results['found_preferences']}")
    
    def test_profile_5_feijao_whey(self):
        """PERFIL 5 - Preferência: FEIJÃO + WHEY + MAÇÃ + COTTAGE"""
        print("\n🧪 TESTANDO PERFIL 5 - FEIJÃO + WHEY + MAÇÃ + COTTAGE")
        
        profile_data = {
            "id": "pref-test-5",
            "user_id": "pref-test-5",
            "name": "Teste Feijao Whey",
            "email": "pref5@test.com",
            "age": 40,
            "sex": "masculino",
            "height": 170,
            "weight": 90,
            "target_weight": 80,
            "goal": "cutting",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "dietary_restrictions": [],
            "food_preferences": ["feijao", "whey_protein", "maca", "cottage"],
            "meal_count": 6
        }
        
        # Criar perfil
        if not self.create_profile(profile_data):
            self.log_result("PERFIL 5 - Criação", False, "Falha ao criar perfil")
            return
        
        self.log_result("PERFIL 5 - Criação", True, "Perfil criado com sucesso")
        
        # Gerar dieta
        diet_plan = self.generate_diet("pref-test-5")
        if not diet_plan:
            self.log_result("PERFIL 5 - Geração Dieta", False, "Falha ao gerar dieta")
            return
        
        self.log_result("PERFIL 5 - Geração Dieta", True, f"Dieta gerada com {len(diet_plan.get('meals', []))} refeições")
        
        # Verificar preferências
        pref_results = self.check_food_preferences("pref-test-5", ["feijao", "whey_protein", "maca", "cottage"], diet_plan)
        
        # Validações específicas
        results = pref_results["results"]
        
        # FEIJÃO deve aparecer
        feijao_found = results.get("feijao", False)
        self.log_result("PERFIL 5 - FEIJÃO", feijao_found,
                       "FEIJÃO encontrado na dieta" if feijao_found else "FEIJÃO NÃO encontrado")
        
        # WHEY PROTEIN deve aparecer nos lanches
        whey_found = results.get("whey_protein", False)
        self.log_result("PERFIL 5 - WHEY PROTEIN", whey_found,
                       "WHEY PROTEIN encontrado na dieta" if whey_found else "WHEY PROTEIN NÃO encontrado nos lanches")
        
        # MAÇÃ deve aparecer
        maca_found = results.get("maca", False)
        self.log_result("PERFIL 5 - MAÇÃ", maca_found,
                       "MAÇÃ encontrada na dieta" if maca_found else "MAÇÃ NÃO encontrada")
        
        # COTTAGE deve aparecer
        cottage_found = results.get("cottage", False)
        self.log_result("PERFIL 5 - COTTAGE", cottage_found,
                       "COTTAGE encontrado na dieta" if cottage_found else "COTTAGE NÃO encontrado")
        
        # Verificar número de refeições (6)
        meal_count = len(diet_plan.get("meals", []))
        expected_meals = 6
        meals_correct = meal_count == expected_meals
        self.log_result("PERFIL 5 - MEAL COUNT", meals_correct,
                       f"Correto: {meal_count} refeições" if meals_correct else f"Incorreto: {meal_count} refeições (esperado {expected_meals})")
        
        print(f"📊 PERFIL 5 RESUMO: {pref_results['found_count']}/{pref_results['total_preferences']} preferências encontradas")
        print(f"🍽️ Alimentos encontrados: {pref_results['found_preferences']}")
    
    def test_profile_6_tapioca_peru(self):
        """PERFIL 6 - Preferência: TAPIOCA + PERU + MELANCIA + GRANOLA"""
        print("\n🧪 TESTANDO PERFIL 6 - TAPIOCA + PERU + MELANCIA + GRANOLA")
        
        profile_data = {
            "id": "pref-test-6",
            "user_id": "pref-test-6",
            "name": "Teste Tapioca Peru",
            "email": "pref6@test.com",
            "age": 22,
            "sex": "feminino",
            "height": 168,
            "weight": 58,
            "target_weight": 62,
            "goal": "bulking",
            "training_level": "avancado",
            "weekly_training_frequency": 6,
            "available_time_per_session": 75,
            "dietary_restrictions": [],
            "food_preferences": ["tapioca", "peru", "melancia", "granola"],
            "meal_count": 6
        }
        
        # Criar perfil
        if not self.create_profile(profile_data):
            self.log_result("PERFIL 6 - Criação", False, "Falha ao criar perfil")
            return
        
        self.log_result("PERFIL 6 - Criação", True, "Perfil criado com sucesso")
        
        # Gerar dieta
        diet_plan = self.generate_diet("pref-test-6")
        if not diet_plan:
            self.log_result("PERFIL 6 - Geração Dieta", False, "Falha ao gerar dieta")
            return
        
        self.log_result("PERFIL 6 - Geração Dieta", True, f"Dieta gerada com {len(diet_plan.get('meals', []))} refeições")
        
        # Verificar preferências
        pref_results = self.check_food_preferences("pref-test-6", ["tapioca", "peru", "melancia", "granola"], diet_plan)
        
        # Validações específicas
        results = pref_results["results"]
        
        # TAPIOCA deve aparecer no café da manhã
        tapioca_found = results.get("tapioca", False)
        self.log_result("PERFIL 6 - TAPIOCA", tapioca_found,
                       "TAPIOCA encontrada na dieta" if tapioca_found else "TAPIOCA NÃO encontrada no café da manhã")
        
        # PERU deve aparecer (não frango)
        peru_found = results.get("peru", False)
        self.log_result("PERFIL 6 - PERU", peru_found,
                       "PERU encontrado na dieta" if peru_found else "PERU NÃO encontrado - pode ter frango")
        
        # MELANCIA deve aparecer
        melancia_found = results.get("melancia", False)
        self.log_result("PERFIL 6 - MELANCIA", melancia_found,
                       "MELANCIA encontrada na dieta" if melancia_found else "MELANCIA NÃO encontrada")
        
        # GRANOLA deve aparecer
        granola_found = results.get("granola", False)
        self.log_result("PERFIL 6 - GRANOLA", granola_found,
                       "GRANOLA encontrada na dieta" if granola_found else "GRANOLA NÃO encontrada")
        
        # Verificar número de refeições (6)
        meal_count = len(diet_plan.get("meals", []))
        expected_meals = 6
        meals_correct = meal_count == expected_meals
        self.log_result("PERFIL 6 - MEAL COUNT", meals_correct,
                       f"Correto: {meal_count} refeições" if meals_correct else f"Incorreto: {meal_count} refeições (esperado {expected_meals})")
        
        print(f"📊 PERFIL 6 RESUMO: {pref_results['found_count']}/{pref_results['total_preferences']} preferências encontradas")
        print(f"🍽️ Alimentos encontrados: {pref_results['found_preferences']}")
    
    def run_all_tests(self):
        """Run all food preference tests"""
        print("🚀 INICIANDO TESTE DE PREFERÊNCIAS ALIMENTARES - LAF")
        print("=" * 80)
        
        # Test all profiles
        self.test_profile_1_batata_tilapia()
        self.test_profile_2_macarrao_carne()
        self.test_profile_3_aveia_salmao()
        self.test_profile_4_arroz_atum()
        self.test_profile_5_feijao_whey()
        self.test_profile_6_tapioca_peru()
        
        # Final summary
        print("\n" + "=" * 80)
        print("📊 RESUMO FINAL DOS TESTES DE PREFERÊNCIAS ALIMENTARES")
        print("=" * 80)
        print(f"✅ Testes Passaram: {self.passed_tests}")
        print(f"❌ Testes Falharam: {self.total_tests - self.passed_tests}")
        print(f"📈 Taxa de Sucesso: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        # Detailed results
        print("\n🔍 DETALHES DOS RESULTADOS:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return self.passed_tests, self.total_tests

def main():
    """Main test function"""
    tester = FoodPreferencesTester()
    passed, total = tester.run_all_tests()
    
    if passed == total:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! ({passed}/{total})")
        exit(0)
    else:
        print(f"\n⚠️ ALGUNS TESTES FALHARAM ({total-passed}/{total})")
        exit(1)

if __name__ == "__main__":
    main()