#!/usr/bin/env python3
"""
Teste completo das correções de dieta - LAF Backend Testing
Cenários específicos: Vegetariano, Normal, Vegano
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuração
BASE_URL = "https://fitfood-debug.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class DietTestRunner:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
        
        print(result)
        self.results.append({"test": test_name, "passed": passed, "details": details})
        
    def create_user_and_profile(self, name, email, dietary_restrictions, food_preferences, goal="bulking", weight=70):
        """Cria usuário e perfil completo"""
        try:
            # 1. Signup
            signup_data = {
                "email": email,
                "password": "TestPass123!"
            }
            
            signup_response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, headers=HEADERS)
            if signup_response.status_code != 200:
                return None, f"Signup failed: {signup_response.text}"
            
            user_data = signup_response.json()
            user_id = user_data.get("user_id")
            
            # 2. Create Profile
            profile_data = {
                "id": user_id,
                "name": name,
                "age": 30,
                "sex": "masculino",
                "height": 175.0,
                "weight": float(weight),
                "goal": goal,
                "training_level": "intermediario",
                "weekly_training_frequency": 4,
                "available_time_per_session": 60,
                "dietary_restrictions": dietary_restrictions,
                "food_preferences": food_preferences,
                "meal_count": 6
            }
            
            profile_response = requests.post(f"{BASE_URL}/user/profile", json=profile_data, headers=HEADERS)
            if profile_response.status_code != 200:
                return None, f"Profile creation failed: {profile_response.text}"
            
            return user_id, "Success"
            
        except Exception as e:
            return None, f"Exception: {str(e)}"
    
    def generate_diet(self, user_id):
        """Gera dieta para o usuário"""
        try:
            response = requests.post(f"{BASE_URL}/diet/generate?user_id={user_id}", headers=HEADERS)
            if response.status_code != 200:
                return None, f"Diet generation failed: {response.text}"
            
            return response.json(), "Success"
            
        except Exception as e:
            return None, f"Exception: {str(e)}"
    
    def analyze_diet_foods(self, diet_data):
        """Analisa os alimentos da dieta"""
        foods_by_meal = {}
        total_protein = 0
        total_carbs = 0
        total_calories = 0
        
        all_foods = []
        
        for meal in diet_data.get("meals", []):
            meal_name = meal.get("name", "Unknown")
            meal_foods = []
            
            for food in meal.get("foods", []):
                food_info = {
                    "name": food.get("name", ""),
                    "key": food.get("key", ""),
                    "grams": food.get("grams", 0),
                    "protein": food.get("protein", 0),
                    "carbs": food.get("carbs", 0),
                    "calories": food.get("calories", 0)
                }
                meal_foods.append(food_info)
                all_foods.append(food_info)
                
                total_protein += food_info["protein"]
                total_carbs += food_info["carbs"] 
                total_calories += food_info["calories"]
            
            foods_by_meal[meal_name] = meal_foods
        
        return {
            "foods_by_meal": foods_by_meal,
            "all_foods": all_foods,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_calories": total_calories
        }
    
    def check_vegetarian_restrictions(self, analysis):
        """Verifica restrições vegetarianas"""
        violations = []
        
        # Lista de carnes proibidas para vegetarianos
        meat_keywords = [
            "frango", "chicken", "patinho", "beef", "carne", "meat",
            "tilapia", "fish", "peixe", "salmao", "salmon", "atum", "tuna",
            "peru", "turkey", "porco", "pork", "bacon"
        ]
        
        for food in analysis["all_foods"]:
            food_name = food["name"].lower()
            food_key = food["key"].lower()
            
            for meat in meat_keywords:
                if meat in food_name or meat in food_key:
                    violations.append(f"Carne encontrada: {food['name']} ({food['grams']}g)")
        
        return violations
    
    def check_vegan_restrictions(self, analysis):
        """Verifica restrições veganas"""
        violations = []
        
        # Lista de produtos proibidos para veganos
        forbidden_keywords = [
            "frango", "chicken", "patinho", "beef", "carne", "meat",
            "tilapia", "fish", "peixe", "salmao", "salmon", "atum", "tuna",
            "peru", "turkey", "porco", "pork", "bacon",
            "ovos", "eggs", "ovo", "egg",
            "leite", "milk", "queijo", "cheese", "iogurte", "yogurt",
            "whey", "cottage", "ricotta"
        ]
        
        for food in analysis["all_foods"]:
            food_name = food["name"].lower()
            food_key = food["key"].lower()
            
            for forbidden in forbidden_keywords:
                if forbidden in food_name or forbidden in food_key:
                    violations.append(f"Produto animal encontrado: {food['name']} ({food['grams']}g)")
        
        return violations
    
    def check_protein_sources(self, analysis, diet_type):
        """Verifica fontes de proteína adequadas"""
        protein_sources = []
        
        for meal_name, foods in analysis["foods_by_meal"].items():
            for food in foods:
                if food["protein"] > 10:  # Considera alimento com >10g proteína como fonte proteica
                    protein_sources.append({
                        "meal": meal_name,
                        "food": food["name"],
                        "protein": food["protein"],
                        "grams": food["grams"]
                    })
        
        return protein_sources
    
    def check_eggs_placement(self, analysis):
        """Verifica se ovos estão apenas no café da manhã"""
        violations = []
        
        for meal_name, foods in analysis["foods_by_meal"].items():
            for food in foods:
                food_name = food["name"].lower()
                food_key = food["key"].lower()
                
                if "ovo" in food_name or "egg" in food_name or "ovo" in food_key:
                    if "café" not in meal_name.lower() and "breakfast" not in meal_name.lower():
                        violations.append(f"Ovos fora do café da manhã: {food['name']} em {meal_name}")
        
        return violations
    
    def check_tofu_presence(self, analysis):
        """Verifica presença de tofu no almoço/jantar"""
        tofu_meals = []
        
        for meal_name, foods in analysis["foods_by_meal"].items():
            for food in foods:
                food_name = food["name"].lower()
                food_key = food["key"].lower()
                
                if "tofu" in food_name or "tofu" in food_key:
                    tofu_meals.append(f"Tofu em {meal_name}: {food['name']} ({food['grams']}g)")
        
        return tofu_meals
    
    def check_beans_quantity(self, analysis):
        """Verifica se feijão não excede 300g total"""
        total_beans = 0
        bean_foods = []
        
        for food in analysis["all_foods"]:
            food_name = food["name"].lower()
            food_key = food["key"].lower()
            
            if "feijao" in food_name or "bean" in food_name or "feijao" in food_key:
                total_beans += food["grams"]
                bean_foods.append(f"{food['name']} ({food['grams']}g)")
        
        return total_beans, bean_foods
    
    def check_rice_vs_beans(self, analysis):
        """Verifica se arroz > feijão em quantidade"""
        total_rice = 0
        total_beans = 0
        
        for food in analysis["all_foods"]:
            food_name = food["name"].lower()
            food_key = food["key"].lower()
            
            if "arroz" in food_name or "rice" in food_name or "arroz" in food_key:
                total_rice += food["grams"]
            elif "feijao" in food_name or "bean" in food_name or "feijao" in food_key:
                total_beans += food["grams"]
        
        return total_rice, total_beans
    
    def test_scenario_1_vegetarian(self):
        """Cenário 1: Dieta Vegetariana"""
        print("\n🥬 CENÁRIO 1: DIETA VEGETARIANA")
        print("=" * 50)
        
        # Criar usuário vegetariano
        user_id, error = self.create_user_and_profile(
            name="Test Vegetariano",
            email=f"vegetariano_{int(time.time())}@test.com",
            dietary_restrictions=["vegetariano"],
            food_preferences=["ovos", "arroz_branco", "feijao", "banana", "castanhas", "azeite"],
            weight=70
        )
        
        if not user_id:
            self.log_result("Vegetariano - Criação de usuário", False, error)
            return
        
        self.log_result("Vegetariano - Criação de usuário", True, f"User ID: {user_id}")
        
        # Gerar dieta
        diet_data, error = self.generate_diet(user_id)
        if not diet_data:
            self.log_result("Vegetariano - Geração de dieta", False, error)
            return
        
        self.log_result("Vegetariano - Geração de dieta", True, "Dieta gerada com sucesso")
        
        # Analisar dieta
        analysis = self.analyze_diet_foods(diet_data)
        
        # Teste 1: NÃO deve ter carnes
        meat_violations = self.check_vegetarian_restrictions(analysis)
        if meat_violations:
            self.log_result("Vegetariano - Sem carnes", False, f"Violações: {'; '.join(meat_violations)}")
        else:
            self.log_result("Vegetariano - Sem carnes", True, "Nenhuma carne encontrada")
        
        # Teste 2: DEVE ter tofu no almoço/jantar
        tofu_meals = self.check_tofu_presence(analysis)
        if tofu_meals:
            self.log_result("Vegetariano - Tofu presente", True, f"Encontrado: {'; '.join(tofu_meals)}")
        else:
            self.log_result("Vegetariano - Tofu presente", False, "Tofu não encontrado no almoço/jantar")
        
        # Teste 3: Ovos APENAS no café da manhã
        egg_violations = self.check_eggs_placement(analysis)
        if egg_violations:
            self.log_result("Vegetariano - Ovos só no café", False, f"Violações: {'; '.join(egg_violations)}")
        else:
            self.log_result("Vegetariano - Ovos só no café", True, "Ovos apenas no café da manhã")
        
        # Teste 4: Proteína total adequada (>100g para 70kg)
        total_protein = analysis["total_protein"]
        if total_protein >= 100:
            self.log_result("Vegetariano - Proteína adequada", True, f"Proteína total: {total_protein:.1f}g")
        else:
            self.log_result("Vegetariano - Proteína adequada", False, f"Proteína insuficiente: {total_protein:.1f}g (mínimo 100g)")
        
        return user_id, analysis
    
    def test_scenario_2_normal(self):
        """Cenário 2: Dieta Normal (sem restrições)"""
        print("\n🍗 CENÁRIO 2: DIETA NORMAL")
        print("=" * 50)
        
        # Criar usuário normal
        user_id, error = self.create_user_and_profile(
            name="Test Normal",
            email=f"normal_{int(time.time())}@test.com",
            dietary_restrictions=[],
            food_preferences=["frango", "arroz", "feijao"],
            weight=70
        )
        
        if not user_id:
            self.log_result("Normal - Criação de usuário", False, error)
            return
        
        self.log_result("Normal - Criação de usuário", True, f"User ID: {user_id}")
        
        # Gerar dieta
        diet_data, error = self.generate_diet(user_id)
        if not diet_data:
            self.log_result("Normal - Geração de dieta", False, error)
            return
        
        self.log_result("Normal - Geração de dieta", True, "Dieta gerada com sucesso")
        
        # Analisar dieta
        analysis = self.analyze_diet_foods(diet_data)
        
        # Teste 1: Feijão não deve exceder 300g total
        total_beans, bean_foods = self.check_beans_quantity(analysis)
        if total_beans <= 300:
            self.log_result("Normal - Feijão ≤300g", True, f"Feijão total: {total_beans}g")
        else:
            self.log_result("Normal - Feijão ≤300g", False, f"Feijão excessivo: {total_beans}g (máximo 300g)")
        
        # Teste 2: Arroz deve ser > feijão
        total_rice, total_beans = self.check_rice_vs_beans(analysis)
        if total_rice > total_beans:
            self.log_result("Normal - Arroz > Feijão", True, f"Arroz: {total_rice}g, Feijão: {total_beans}g")
        else:
            self.log_result("Normal - Arroz > Feijão", False, f"Proporção inadequada - Arroz: {total_rice}g, Feijão: {total_beans}g")
        
        # Teste 3: Proteína adequada com frango
        protein_sources = self.check_protein_sources(analysis, "normal")
        chicken_found = any("frango" in p["food"].lower() or "chicken" in p["food"].lower() for p in protein_sources)
        total_protein = analysis["total_protein"]
        
        if chicken_found and total_protein >= 100:
            self.log_result("Normal - Proteína com frango", True, f"Frango presente, proteína: {total_protein:.1f}g")
        else:
            details = f"Frango: {'Sim' if chicken_found else 'Não'}, Proteína: {total_protein:.1f}g"
            self.log_result("Normal - Proteína com frango", False, details)
        
        return user_id, analysis
    
    def test_scenario_3_vegan(self):
        """Cenário 3: Dieta Vegana"""
        print("\n🌱 CENÁRIO 3: DIETA VEGANA")
        print("=" * 50)
        
        # Criar usuário vegano
        user_id, error = self.create_user_and_profile(
            name="Test Vegano",
            email=f"vegano_{int(time.time())}@test.com",
            dietary_restrictions=["vegano"],
            food_preferences=["tofu", "arroz", "feijao", "banana"],
            weight=70
        )
        
        if not user_id:
            self.log_result("Vegano - Criação de usuário", False, error)
            return
        
        self.log_result("Vegano - Criação de usuário", True, f"User ID: {user_id}")
        
        # Gerar dieta
        diet_data, error = self.generate_diet(user_id)
        if not diet_data:
            self.log_result("Vegano - Geração de dieta", False, error)
            return
        
        self.log_result("Vegano - Geração de dieta", True, "Dieta gerada com sucesso")
        
        # Analisar dieta
        analysis = self.analyze_diet_foods(diet_data)
        
        # Teste 1: NÃO deve ter carnes, ovos, laticínios
        vegan_violations = self.check_vegan_restrictions(analysis)
        if vegan_violations:
            self.log_result("Vegano - Sem produtos animais", False, f"Violações: {'; '.join(vegan_violations)}")
        else:
            self.log_result("Vegano - Sem produtos animais", True, "Nenhum produto animal encontrado")
        
        # Teste 2: DEVE ter tofu ou tempeh como proteína
        protein_sources = self.check_protein_sources(analysis, "vegan")
        vegan_proteins = [p for p in protein_sources if "tofu" in p["food"].lower() or "tempeh" in p["food"].lower()]
        
        if vegan_proteins:
            protein_list = [f"{p['food']} ({p['protein']}g)" for p in vegan_proteins]
            self.log_result("Vegano - Proteína vegana", True, f"Encontrado: {'; '.join(protein_list)}")
        else:
            self.log_result("Vegano - Proteína vegana", False, "Tofu/tempeh não encontrado como fonte proteica")
        
        # Teste 3: Proteína total adequada (>80g)
        total_protein = analysis["total_protein"]
        if total_protein >= 80:
            self.log_result("Vegano - Proteína adequada", True, f"Proteína total: {total_protein:.1f}g")
        else:
            self.log_result("Vegano - Proteína adequada", False, f"Proteína insuficiente: {total_protein:.1f}g (mínimo 80g)")
        
        return user_id, analysis
    
    def run_all_tests(self):
        """Executa todos os cenários de teste"""
        print("🧪 TESTE COMPLETO DAS CORREÇÕES DE DIETA - LAF")
        print("=" * 60)
        print(f"URL Base: {BASE_URL}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Executar cenários
        scenario1_result = self.test_scenario_1_vegetarian()
        scenario2_result = self.test_scenario_2_normal()
        scenario3_result = self.test_scenario_3_vegan()
        
        # Resumo final
        print("\n📊 RESUMO DOS TESTES")
        print("=" * 50)
        print(f"Total de testes: {self.total_tests}")
        print(f"Testes aprovados: {self.passed_tests}")
        print(f"Testes falharam: {self.total_tests - self.passed_tests}")
        print(f"Taxa de sucesso: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        # Detalhes dos falhas
        failed_tests = [r for r in self.results if not r["passed"]]
        if failed_tests:
            print(f"\n❌ TESTES FALHARAM ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": self.passed_tests/self.total_tests*100 if self.total_tests > 0 else 0,
            "failed_tests": failed_tests
        }

if __name__ == "__main__":
    runner = DietTestRunner()
    results = runner.run_all_tests()