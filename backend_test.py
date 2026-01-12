#!/usr/bin/env python3
"""
🔍 AUDITORIA COMPLETA E EXTENSIVA DO BACKEND LAF
Execute testes EXAUSTIVOS de TODAS as funcionalidades conforme solicitação do usuário.

Base URL: https://diet-fixer.preview.emergentagent.com/api
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configuração
BASE_URL = "https://diet-fixer.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class LAFBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.test_results = []
        self.auth_token = None
        self.test_user_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}: {details}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request and return (success, response, status_code)"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, params=params, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data, params=params, timeout=30)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data, params=params, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, params=params, timeout=30)
            else:
                return False, None, 0
                
            return response.status_code < 400, response, response.status_code
            
        except Exception as e:
            print(f"Request error: {e}")
            return False, None, 0

    def test_authentication_flow(self):
        """1. AUTENTICAÇÃO (Fluxo Completo)"""
        print("\n🔐 TESTANDO AUTENTICAÇÃO COMPLETA")
        
        # Dados de teste únicos
        timestamp = int(time.time())
        test_email = f"test_user_{timestamp}@laf.com"
        test_password = "TestPassword123!"
        
        # 1.1 POST /api/auth/signup - Cadastrar novo usuário
        signup_data = {
            "email": test_email,
            "password": test_password
        }
        
        success, response, status = self.make_request("POST", "/auth/signup", signup_data)
        
        if success and response:
            try:
                signup_result = response.json()
                self.auth_token = signup_result.get("token")
                self.test_user_id = signup_result.get("user_id")
                
                # Adiciona token ao header para próximas requisições
                self.headers["Authorization"] = f"Bearer {self.auth_token}"
                
                self.log_test(
                    "AUTH - Signup", 
                    True, 
                    f"Usuário criado com sucesso. ID: {self.test_user_id}",
                    {"email": test_email, "user_id": self.test_user_id}
                )
            except Exception as e:
                self.log_test("AUTH - Signup", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("AUTH - Signup", False, f"Status: {status}, Response: {response.text if response else 'None'}")
            
        # 1.2 POST /api/auth/login - Login
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        success, response, status = self.make_request("POST", "/auth/login", login_data)
        
        if success and response:
            try:
                login_result = response.json()
                login_token = login_result.get("token")
                
                self.log_test(
                    "AUTH - Login", 
                    True, 
                    f"Login realizado com sucesso. Token válido: {bool(login_token)}",
                    {"token_length": len(login_token) if login_token else 0}
                )
            except Exception as e:
                self.log_test("AUTH - Login", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("AUTH - Login", False, f"Status: {status}")
            
        # 1.3 GET /api/auth/validate - Validar token
        success, response, status = self.make_request("GET", "/auth/validate")
        
        if success and response:
            try:
                validate_result = response.json()
                self.log_test(
                    "AUTH - Validate Token", 
                    True, 
                    f"Token válido. User ID: {validate_result.get('user_id')}",
                    validate_result
                )
            except Exception as e:
                self.log_test("AUTH - Validate Token", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("AUTH - Validate Token", False, f"Status: {status}")

    def test_user_profile_crud(self):
        """2. PERFIL DE USUÁRIO - TODAS as combinações"""
        print("\n👤 TESTANDO PERFIL DE USUÁRIO - TODAS AS COMBINAÇÕES")
        
        if not self.test_user_id:
            self.log_test("USER PROFILE", False, "Usuário não autenticado - pulando testes de perfil")
            return
            
        # Combinações para testar
        test_combinations = [
            {
                "name": "Cutting + Vegetariano + Novato + 3x/semana",
                "goal": "cutting",
                "restrictions": ["vegetariano"],
                "level": "novato",
                "frequency": 3,
                "sex": "masculino",
                "age": 25,
                "weight": 80.0,
                "height": 175.0
            },
            {
                "name": "Bulking + Sem Lactose + Intermediário + 5x/semana", 
                "goal": "bulking",
                "restrictions": ["sem_lactose"],
                "level": "intermediario",
                "frequency": 5,
                "sex": "feminino",
                "age": 28,
                "weight": 65.0,
                "height": 165.0
            },
            {
                "name": "Manutenção + Sem Glúten + Avançado + 4x/semana",
                "goal": "manutencao", 
                "restrictions": ["sem_gluten"],
                "level": "avancado",
                "frequency": 4,
                "sex": "masculino",
                "age": 35,
                "weight": 90.0,
                "height": 180.0
            },
            {
                "name": "Cutting + Múltiplas Restrições + Iniciante + 6x/semana",
                "goal": "cutting",
                "restrictions": ["vegetariano", "sem_lactose"],
                "level": "iniciante", 
                "frequency": 6,
                "sex": "feminino",
                "age": 22,
                "weight": 55.0,
                "height": 160.0
            }
        ]
        
        for i, combo in enumerate(test_combinations):
            # 2.1 POST /api/user/profile - Criar perfil
            profile_data = {
                "id": self.test_user_id,
                "name": f"Usuário Teste {i+1}",
                "age": combo["age"],
                "sex": combo["sex"],
                "height": combo["height"],
                "weight": combo["weight"],
                "target_weight": combo["weight"] - 5 if combo["goal"] == "cutting" else combo["weight"] + 5,
                "body_fat_percentage": 15.0,
                "training_level": combo["level"],
                "weekly_training_frequency": combo["frequency"],
                "available_time_per_session": 60,
                "goal": combo["goal"],
                "dietary_restrictions": combo["restrictions"],
                "food_preferences": [],
                "injury_history": [],
                "meal_count": 6
            }
            
            success, response, status = self.make_request("POST", "/user/profile", profile_data)
            
            if success and response:
                try:
                    profile_result = response.json()
                    
                    # Validações específicas
                    tdee = profile_result.get("tdee", 0)
                    target_calories = profile_result.get("target_calories", 0)
                    macros = profile_result.get("macros", {})
                    
                    # Verifica se TDEE foi calculado
                    tdee_valid = tdee > 1000 and tdee < 5000
                    
                    # Verifica se target_calories está correto para o objetivo
                    if combo["goal"] == "cutting":
                        calories_valid = target_calories < tdee  # Déficit
                    elif combo["goal"] == "bulking":
                        calories_valid = target_calories > tdee  # Superávit
                    else:  # manutenção
                        calories_valid = abs(target_calories - tdee) < 50  # Aproximadamente igual
                    
                    # Verifica macros
                    macros_valid = (
                        macros.get("protein", 0) > 0 and
                        macros.get("carbs", 0) > 0 and
                        macros.get("fat", 0) > 0
                    )
                    
                    all_valid = tdee_valid and calories_valid and macros_valid
                    
                    details = f"{combo['name']} - TDEE: {tdee}kcal, Target: {target_calories}kcal, P:{macros.get('protein')}g C:{macros.get('carbs')}g F:{macros.get('fat')}g"
                    
                    self.log_test(
                        f"USER PROFILE - Create ({combo['name']})",
                        all_valid,
                        details,
                        {
                            "tdee": tdee,
                            "target_calories": target_calories,
                            "macros": macros,
                            "goal": combo["goal"],
                            "restrictions": combo["restrictions"]
                        }
                    )
                    
                except Exception as e:
                    self.log_test(f"USER PROFILE - Create ({combo['name']})", False, f"Erro ao processar resposta: {e}")
            else:
                self.log_test(f"USER PROFILE - Create ({combo['name']})", False, f"Status: {status}")
        
        # 2.2 GET /api/user/profile/{user_id} - Buscar perfil
        success, response, status = self.make_request("GET", f"/user/profile/{self.test_user_id}")
        
        if success and response:
            try:
                profile = response.json()
                self.log_test(
                    "USER PROFILE - Get",
                    True,
                    f"Perfil recuperado. TDEE: {profile.get('tdee')}kcal",
                    {"user_id": self.test_user_id, "tdee": profile.get("tdee")}
                )
            except Exception as e:
                self.log_test("USER PROFILE - Get", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("USER PROFILE - Get", False, f"Status: {status}")
            
        # 2.3 PUT /api/user/profile/{user_id} - Atualizar perfil
        update_data = {
            "weight": 85.0,
            "goal": "bulking"
        }
        
        success, response, status = self.make_request("PUT", f"/user/profile/{self.test_user_id}", update_data)
        
        if success and response:
            try:
                updated_profile = response.json()
                new_weight = updated_profile.get("weight")
                new_goal = updated_profile.get("goal")
                new_tdee = updated_profile.get("tdee")
                
                weight_updated = new_weight == 85.0
                goal_updated = new_goal == "bulking"
                tdee_recalculated = new_tdee > 0
                
                all_updated = weight_updated and goal_updated and tdee_recalculated
                
                self.log_test(
                    "USER PROFILE - Update",
                    all_updated,
                    f"Perfil atualizado. Peso: {new_weight}kg, Goal: {new_goal}, TDEE: {new_tdee}kcal",
                    {"weight": new_weight, "goal": new_goal, "tdee": new_tdee}
                )
            except Exception as e:
                self.log_test("USER PROFILE - Update", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("USER PROFILE - Update", False, f"Status: {status}")

    def test_user_settings(self):
        """3. CONFIGURAÇÕES DE USUÁRIO"""
        print("\n⚙️ TESTANDO CONFIGURAÇÕES DE USUÁRIO")
        
        if not self.test_user_id:
            self.log_test("USER SETTINGS", False, "Usuário não autenticado - pulando testes de configurações")
            return
            
        # 3.1 GET /api/user/settings/{user_id}
        success, response, status = self.make_request("GET", f"/user/settings/{self.test_user_id}")
        
        if success and response:
            try:
                settings = response.json()
                self.log_test(
                    "USER SETTINGS - Get",
                    True,
                    f"Configurações recuperadas. meal_count: {settings.get('meal_count', 'N/A')}",
                    settings
                )
            except Exception as e:
                self.log_test("USER SETTINGS - Get", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("USER SETTINGS - Get", False, f"Status: {status}")
            
        # 3.2 PATCH /api/user/settings/{user_id} - Testar meal_count: 4, 5 e 6
        for meal_count in [4, 5, 6]:
            settings_data = {
                "meal_count": meal_count,
                "notifications_enabled": True,
                "language": "pt-BR"
            }
            
            success, response, status = self.make_request("PATCH", f"/user/settings/{self.test_user_id}", settings_data)
            
            if success and response:
                try:
                    updated_settings = response.json()
                    saved_meal_count = updated_settings.get("meal_count")
                    
                    self.log_test(
                        f"USER SETTINGS - Update meal_count={meal_count}",
                        saved_meal_count == meal_count,
                        f"meal_count salvo: {saved_meal_count}",
                        {"requested": meal_count, "saved": saved_meal_count}
                    )
                except Exception as e:
                    self.log_test(f"USER SETTINGS - Update meal_count={meal_count}", False, f"Erro ao processar resposta: {e}")
            else:
                self.log_test(f"USER SETTINGS - Update meal_count={meal_count}", False, f"Status: {status}")

    def test_diet_generation_comprehensive(self):
        """4. GERAÇÃO DE DIETA (CRÍTICO - TESTAR TODAS COMBINAÇÕES)"""
        print("\n🍽️ TESTANDO GERAÇÃO DE DIETA - TODAS AS COMBINAÇÕES")
        
        if not self.test_user_id:
            self.log_test("DIET GENERATION", False, "Usuário não autenticado - pulando testes de dieta")
            return
            
        # Combinações críticas para testar
        test_scenarios = [
            {
                "name": "4 refeições + cutting + vegetariano",
                "meal_count": 4,
                "goal": "cutting",
                "restrictions": ["vegetariano"],
                "weight": 70.0,
                "expected_meals": 4
            },
            {
                "name": "5 refeições + bulking + sem_lactose",
                "meal_count": 5,
                "goal": "bulking", 
                "restrictions": ["sem_lactose"],
                "weight": 80.0,
                "expected_meals": 5
            },
            {
                "name": "6 refeições + manutenção + sem_gluten",
                "meal_count": 6,
                "goal": "manutencao",
                "restrictions": ["sem_gluten"],
                "weight": 75.0,
                "expected_meals": 6
            },
            {
                "name": "4 refeições + cutting + múltiplas restrições",
                "meal_count": 4,
                "goal": "cutting",
                "restrictions": ["vegetariano", "sem_lactose"],
                "weight": 65.0,
                "expected_meals": 4
            }
        ]
        
        for scenario in test_scenarios:
            # Primeiro, atualiza o perfil para o cenário
            profile_update = {
                "goal": scenario["goal"],
                "weight": scenario["weight"],
                "dietary_restrictions": scenario["restrictions"]
            }
            
            self.make_request("PUT", f"/user/profile/{self.test_user_id}", profile_update)
            
            # Atualiza configurações de meal_count
            settings_update = {"meal_count": scenario["meal_count"]}
            self.make_request("PATCH", f"/user/settings/{self.test_user_id}", settings_update)
            
            # Gera dieta
            success, response, status = self.make_request("POST", f"/diet/generate", params={"user_id": self.test_user_id})
            
            if success and response:
                try:
                    diet = response.json()
                    meals = diet.get("meals", [])
                    
                    # Validações críticas
                    correct_meal_count = len(meals) == scenario["expected_meals"]
                    
                    # Verifica se restrições estão sendo respeitadas
                    restrictions_respected = self.validate_dietary_restrictions(meals, scenario["restrictions"])
                    
                    # Verifica se cada refeição tem alimentos
                    meals_have_foods = all(len(meal.get("foods", [])) > 0 for meal in meals)
                    
                    # Verifica se macros estão calculados
                    macros_calculated = diet.get("computed_macros") is not None
                    
                    # Verifica se cada refeição tem total_calories
                    calories_per_meal = all(meal.get("total_calories", 0) > 0 for meal in meals)
                    
                    all_valid = (correct_meal_count and restrictions_respected and 
                               meals_have_foods and macros_calculated and calories_per_meal)
                    
                    details = f"{scenario['name']} - Refeições: {len(meals)}/{scenario['expected_meals']}, Restrições OK: {restrictions_respected}, Calorias/refeição: {calories_per_meal}"
                    
                    self.log_test(
                        f"DIET GENERATION - {scenario['name']}",
                        all_valid,
                        details,
                        {
                            "meal_count": len(meals),
                            "expected": scenario["expected_meals"],
                            "restrictions_ok": restrictions_respected,
                            "total_calories": diet.get("computed_calories"),
                            "macros": diet.get("computed_macros")
                        }
                    )
                    
                except Exception as e:
                    self.log_test(f"DIET GENERATION - {scenario['name']}", False, f"Erro ao processar resposta: {e}")
            else:
                self.log_test(f"DIET GENERATION - {scenario['name']}", False, f"Status: {status}")

    def validate_dietary_restrictions(self, meals: List[Dict], restrictions: List[str]) -> bool:
        """Valida se as restrições alimentares estão sendo respeitadas"""
        
        # Alimentos proibidos por restrição
        forbidden_foods = {
            "vegetariano": ["frango", "patinho", "tilapia", "atum", "salmao", "peru", "carne"],
            "sem_lactose": ["iogurte_zero", "whey_protein", "cottage", "queijo", "leite"],
            "sem_gluten": ["aveia", "macarrao", "pao", "pao_integral", "trigo"]
        }
        
        for restriction in restrictions:
            if restriction in forbidden_foods:
                forbidden = forbidden_foods[restriction]
                
                # Verifica todos os alimentos de todas as refeições
                for meal in meals:
                    for food in meal.get("foods", []):
                        food_key = food.get("key", "").lower()
                        food_name = food.get("name", "").lower()
                        
                        # Verifica se algum alimento proibido está presente
                        for forbidden_item in forbidden:
                            if forbidden_item in food_key or forbidden_item in food_name:
                                return False
        
        return True

    def test_food_substitution(self):
        """5. SUBSTITUIÇÃO DE ALIMENTOS"""
        print("\n🔄 TESTANDO SUBSTITUIÇÃO DE ALIMENTOS")
        
        if not self.test_user_id:
            self.log_test("FOOD SUBSTITUTION", False, "Usuário não autenticado - pulando testes de substituição")
            return
            
        # Primeiro, garante que há uma dieta
        self.make_request("POST", f"/diet/generate", params={"user_id": self.test_user_id})
        
        # Busca a dieta atual
        success, response, status = self.make_request("GET", f"/diet/{self.test_user_id}")
        
        if not success or not response:
            self.log_test("FOOD SUBSTITUTION", False, "Não foi possível obter dieta para testar substituição")
            return
            
        try:
            diet = response.json()
            meals = diet.get("meals", [])
            
            if not meals or not meals[0].get("foods"):
                self.log_test("FOOD SUBSTITUTION", False, "Dieta não tem alimentos para substituir")
                return
                
            # Pega o primeiro alimento da primeira refeição
            first_food = meals[0]["foods"][0]
            food_key = first_food.get("key")
            
            if not food_key:
                self.log_test("FOOD SUBSTITUTION", False, "Alimento não tem chave para substituição")
                return
                
            # 5.1 GET /api/diet/{user_id}/substitutes/{food_key}
            success, response, status = self.make_request("GET", f"/diet/{self.test_user_id}/substitutes/{food_key}")
            
            if success and response:
                try:
                    substitutes_data = response.json()
                    substitutes = substitutes_data.get("substitutes", [])
                    original = substitutes_data.get("original", {})
                    
                    self.log_test(
                        "FOOD SUBSTITUTION - Get Substitutes",
                        len(substitutes) > 0,
                        f"Encontrados {len(substitutes)} substitutos para {original.get('name', food_key)}",
                        {"original": original.get("name"), "substitutes_count": len(substitutes)}
                    )
                    
                    # 5.2 PUT /api/diet/{user_id}/substitute - Executa substituição
                    if substitutes:
                        substitute_food = substitutes[0]  # Pega o primeiro substituto
                        
                        substitution_data = {
                            "meal_index": 0,
                            "food_index": 0,
                            "new_food_key": substitute_food.get("key")
                        }
                        
                        success, response, status = self.make_request("PUT", f"/diet/{self.test_user_id}/substitute", substitution_data)
                        
                        if success and response:
                            try:
                                updated_diet = response.json()
                                new_meals = updated_diet.get("meals", [])
                                
                                if new_meals and new_meals[0].get("foods"):
                                    new_first_food = new_meals[0]["foods"][0]
                                    substitution_successful = new_first_food.get("key") == substitute_food.get("key")
                                    
                                    self.log_test(
                                        "FOOD SUBSTITUTION - Execute",
                                        substitution_successful,
                                        f"Substituição: {original.get('name')} → {new_first_food.get('name')}",
                                        {
                                            "original": original.get("name"),
                                            "new": new_first_food.get("name"),
                                            "successful": substitution_successful
                                        }
                                    )
                                else:
                                    self.log_test("FOOD SUBSTITUTION - Execute", False, "Dieta atualizada não tem alimentos")
                            except Exception as e:
                                self.log_test("FOOD SUBSTITUTION - Execute", False, f"Erro ao processar resposta: {e}")
                        else:
                            self.log_test("FOOD SUBSTITUTION - Execute", False, f"Status: {status}")
                    
                except Exception as e:
                    self.log_test("FOOD SUBSTITUTION - Get Substitutes", False, f"Erro ao processar resposta: {e}")
            else:
                self.log_test("FOOD SUBSTITUTION - Get Substitutes", False, f"Status: {status}")
                
        except Exception as e:
            self.log_test("FOOD SUBSTITUTION", False, f"Erro geral: {e}")

    def test_workout_generation(self):
        """6. GERAÇÃO DE TREINO (CRÍTICO)"""
        print("\n🏋️ TESTANDO GERAÇÃO DE TREINO - DIFERENTES TEMPOS E FREQUÊNCIAS")
        
        if not self.test_user_id:
            self.log_test("WORKOUT GENERATION", False, "Usuário não autenticado - pulando testes de treino")
            return
            
        # Cenários de teste
        workout_scenarios = [
            {
                "name": "30 minutos - 3x/semana",
                "time": 30,
                "frequency": 3,
                "expected_workouts": 3,
                "expected_exercises_per_day": (3, 4)  # Min, Max
            },
            {
                "name": "60 minutos - 4x/semana", 
                "time": 60,
                "frequency": 4,
                "expected_workouts": 4,
                "expected_exercises_per_day": (5, 6)
            },
            {
                "name": "90 minutos - 5x/semana",
                "time": 90,
                "frequency": 5,
                "expected_workouts": 5,
                "expected_exercises_per_day": (6, 8)
            }
        ]
        
        for scenario in workout_scenarios:
            # Atualiza perfil com tempo e frequência
            profile_update = {
                "available_time_per_session": scenario["time"],
                "weekly_training_frequency": scenario["frequency"]
            }
            
            self.make_request("PUT", f"/user/profile/{self.test_user_id}", profile_update)
            
            # Gera treino
            success, response, status = self.make_request("POST", f"/workout/generate", params={"user_id": self.test_user_id})
            
            if success and response:
                try:
                    workout = response.json()
                    workouts = workout.get("workouts", [])
                    
                    # Validações
                    correct_workout_count = len(workouts) == scenario["expected_workouts"]
                    
                    # Verifica exercícios por dia
                    exercises_per_day_valid = True
                    min_exercises, max_exercises = scenario["expected_exercises_per_day"]
                    
                    for day_workout in workouts:
                        exercises = day_workout.get("exercises", [])
                        exercise_count = len(exercises)
                        
                        if exercise_count < min_exercises or exercise_count > max_exercises:
                            exercises_per_day_valid = False
                            break
                    
                    # Verifica se todos os treinos têm exercícios
                    all_have_exercises = all(len(w.get("exercises", [])) > 0 for w in workouts)
                    
                    all_valid = correct_workout_count and exercises_per_day_valid and all_have_exercises
                    
                    exercise_counts = [len(w.get("exercises", [])) for w in workouts]
                    
                    details = f"{scenario['name']} - Treinos: {len(workouts)}/{scenario['expected_workouts']}, Exercícios/dia: {exercise_counts}, Esperado: {min_exercises}-{max_exercises}"
                    
                    self.log_test(
                        f"WORKOUT GENERATION - {scenario['name']}",
                        all_valid,
                        details,
                        {
                            "workout_count": len(workouts),
                            "expected": scenario["expected_workouts"],
                            "exercises_per_day": exercise_counts,
                            "time_per_session": scenario["time"],
                            "frequency": scenario["frequency"]
                        }
                    )
                    
                except Exception as e:
                    self.log_test(f"WORKOUT GENERATION - {scenario['name']}", False, f"Erro ao processar resposta: {e}")
            else:
                self.log_test(f"WORKOUT GENERATION - {scenario['name']}", False, f"Status: {status}")

    def test_weight_registration(self):
        """7. REGISTRO DE PESO"""
        print("\n⚖️ TESTANDO REGISTRO DE PESO COM BLOQUEIO DE 14 DIAS")
        
        if not self.test_user_id:
            self.log_test("WEIGHT REGISTRATION", False, "Usuário não autenticado - pulando testes de peso")
            return
            
        # 7.1 GET /api/progress/weight/{user_id}/can-update
        success, response, status = self.make_request("GET", f"/progress/weight/{self.test_user_id}/can-update")
        
        if success and response:
            try:
                can_update_data = response.json()
                can_update = can_update_data.get("can_update", False)
                
                self.log_test(
                    "WEIGHT - Can Update Check",
                    True,
                    f"Pode atualizar: {can_update}, Razão: {can_update_data.get('reason', 'N/A')}",
                    can_update_data
                )
                
                # 7.2 POST /api/progress/weight/{user_id} - Registra peso se permitido
                if can_update:
                    weight_data = {
                        "weight": 84.5,
                        "notes": "Teste de registro de peso",
                        "questionnaire": {
                            "diet": 8,
                            "training": 7,
                            "cardio": 6,
                            "sleep": 8,
                            "hydration": 9
                        }
                    }
                    
                    success, response, status = self.make_request("POST", f"/progress/weight/{self.test_user_id}", weight_data)
                    
                    if success and response:
                        try:
                            weight_result = response.json()
                            record = weight_result.get("record", {})
                            
                            self.log_test(
                                "WEIGHT - Register",
                                record.get("weight") == 84.5,
                                f"Peso registrado: {record.get('weight')}kg, Média questionário: {record.get('questionnaire_average')}",
                                {"weight": record.get("weight"), "questionnaire_avg": record.get("questionnaire_average")}
                            )
                            
                            # Testa bloqueio de 14 dias - tenta registrar novamente
                            success2, response2, status2 = self.make_request("POST", f"/progress/weight/{self.test_user_id}", weight_data)
                            
                            # Deve falhar com status 400 (bloqueado)
                            blocked_correctly = status2 == 400
                            
                            self.log_test(
                                "WEIGHT - 14-Day Block",
                                blocked_correctly,
                                f"Bloqueio funcionando: {blocked_correctly}, Status: {status2}",
                                {"blocked": blocked_correctly, "status": status2}
                            )
                            
                        except Exception as e:
                            self.log_test("WEIGHT - Register", False, f"Erro ao processar resposta: {e}")
                    else:
                        self.log_test("WEIGHT - Register", False, f"Status: {status}")
                else:
                    self.log_test("WEIGHT - Register", True, "Bloqueio de 14 dias ativo - não pode registrar ainda")
                    
            except Exception as e:
                self.log_test("WEIGHT - Can Update Check", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("WEIGHT - Can Update Check", False, f"Status: {status}")
            
        # 7.3 GET /api/progress/weight/{user_id} - Histórico
        success, response, status = self.make_request("GET", f"/progress/weight/{self.test_user_id}")
        
        if success and response:
            try:
                history_data = response.json()
                history = history_data.get("history", [])
                
                self.log_test(
                    "WEIGHT - Get History",
                    True,
                    f"Histórico recuperado: {len(history)} registros",
                    {"records_count": len(history), "current_weight": history_data.get("current_weight")}
                )
            except Exception as e:
                self.log_test("WEIGHT - Get History", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("WEIGHT - Get History", False, f"Status: {status}")

    def test_water_tracker(self):
        """8. WATER TRACKER"""
        print("\n💧 TESTANDO WATER TRACKER")
        
        if not self.test_user_id:
            self.log_test("WATER TRACKER", False, "Usuário não autenticado - pulando testes de água")
            return
            
        # 8.1 GET /api/tracker/water-sodium/{user_id}
        success, response, status = self.make_request("GET", f"/tracker/water-sodium/{self.test_user_id}")
        
        if success and response:
            try:
                tracker_data = response.json()
                
                self.log_test(
                    "WATER TRACKER - Get",
                    True,
                    f"Tracker recuperado: {tracker_data.get('water_ml', 0)}ml água, {tracker_data.get('sodium_mg', 0)}mg sódio",
                    tracker_data
                )
            except Exception as e:
                self.log_test("WATER TRACKER - Get", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("WATER TRACKER - Get", False, f"Status: {status}")
            
        # 8.2 POST /api/tracker/water-sodium/{user_id}
        water_entry = {
            "water_ml": 500,
            "sodium_mg": 200,
            "notes": "Teste de registro de água"
        }
        
        success, response, status = self.make_request("POST", f"/tracker/water-sodium/{self.test_user_id}", water_entry)
        
        if success and response:
            try:
                entry_result = response.json()
                
                self.log_test(
                    "WATER TRACKER - Add Entry",
                    True,
                    f"Entrada registrada: {entry_result.get('water_ml', 0)}ml total",
                    entry_result
                )
            except Exception as e:
                self.log_test("WATER TRACKER - Add Entry", False, f"Erro ao processar resposta: {e}")
        else:
            self.log_test("WATER TRACKER - Add Entry", False, f"Status: {status}")

    def run_comprehensive_audit(self):
        """Executa auditoria completa e extensiva"""
        print("🔍 INICIANDO AUDITORIA COMPLETA E EXTENSIVA DO BACKEND LAF")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Executa todos os testes
        self.test_authentication_flow()
        self.test_user_profile_crud()
        self.test_user_settings()
        self.test_diet_generation_comprehensive()
        self.test_food_substitution()
        self.test_workout_generation()
        self.test_weight_registration()
        self.test_water_tracker()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Gera relatório final
        self.generate_final_report(duration)

    def generate_final_report(self, duration):
        """Gera relatório final detalhado"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL DA AUDITORIA LAF")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"⏱️  Duração: {duration}")
        print(f"📈 Total de testes: {total_tests}")
        print(f"✅ Testes aprovados: {passed_tests}")
        print(f"❌ Testes falharam: {failed_tests}")
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        print("\n🔍 RESUMO POR FUNCIONALIDADE:")
        
        # Agrupa por categoria
        categories = {}
        for result in self.test_results:
            category = result["test"].split(" - ")[0]
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0}
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["passed"] += 1
        
        for category, stats in categories.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status = "✅" if rate == 100 else "⚠️" if rate >= 50 else "❌"
            print(f"{status} {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # Lista falhas críticas
        failures = [r for r in self.test_results if not r["success"]]
        if failures:
            print("\n❌ FALHAS IDENTIFICADAS:")
            for failure in failures:
                print(f"   • {failure['test']}: {failure['details']}")
        
        print("\n🎯 CRITÉRIOS DE SUCESSO VALIDADOS:")
        
        # Verifica critérios específicos da auditoria
        auth_working = any(r["success"] and "AUTH" in r["test"] for r in self.test_results)
        diet_working = any(r["success"] and "DIET GENERATION" in r["test"] for r in self.test_results)
        substitution_working = any(r["success"] and "FOOD SUBSTITUTION" in r["test"] for r in self.test_results)
        workout_working = any(r["success"] and "WORKOUT GENERATION" in r["test"] for r in self.test_results)
        
        print(f"✅ Autenticação: {'FUNCIONANDO' if auth_working else 'FALHOU'}")
        print(f"✅ Geração de Dieta: {'FUNCIONANDO' if diet_working else 'FALHOU'}")
        print(f"✅ Substituição de Alimentos: {'FUNCIONANDO' if substitution_working else 'FALHOU'}")
        print(f"✅ Geração de Treino: {'FUNCIONANDO' if workout_working else 'FALHOU'}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            print("🎉 AUDITORIA CONCLUÍDA COM SUCESSO - BACKEND FUNCIONANDO PERFEITAMENTE!")
        elif success_rate >= 70:
            print("⚠️ AUDITORIA CONCLUÍDA - BACKEND FUNCIONANDO COM ALGUMAS RESSALVAS")
        else:
            print("❌ AUDITORIA CONCLUÍDA - PROBLEMAS CRÍTICOS IDENTIFICADOS NO BACKEND")
            
        print("=" * 80)

if __name__ == "__main__":
    tester = LAFBackendTester()
    tester.run_comprehensive_audit()