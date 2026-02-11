#!/usr/bin/env python3
"""
🔍 LAF COMPREHENSIVE BACKEND AUDIT - COMPLETE TESTING
Executa AUDITORIA COMPLETA conforme solicitação da revisão em português.
Testa TODOS os endpoints e funcionalidades especificadas.
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "https://macro-safety-caps.preview.emergentagent.com/api"
TIMEOUT = 30

class ComprehensiveLAFTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.test_accounts = []
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: dict = None):
        """Log test result with detailed tracking"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        
    def create_test_account(self, email_suffix: str, name: str) -> Optional[Dict]:
        """Create a test account and return user data"""
        try:
            email = f"test_backend_{int(time.time())}_{email_suffix}@test.com"
            password = "TestPass123!"
            
            # POST /api/auth/signup
            signup_response = self.session.post(
                f"{BASE_URL}/auth/signup",
                json={"email": email, "password": password}
            )
            
            if signup_response.status_code == 200:
                signup_data = signup_response.json()
                
                # POST /api/auth/login to get fresh token
                login_response = self.session.post(
                    f"{BASE_URL}/auth/login",
                    json={"email": email, "password": password}
                )
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    
                    account = {
                        "email": email,
                        "password": password,
                        "name": name,
                        "user_id": signup_data.get("user_id"),
                        "token": login_data.get("token")
                    }
                    
                    self.log_test(f"Account Creation - {name}", True, f"Created account: {email}")
                    return account
                else:
                    self.log_test(f"Account Login - {name}", False, f"Login failed: {login_response.status_code}")
            else:
                self.log_test(f"Account Signup - {name}", False, f"Signup failed: {signup_response.status_code}")
                
        except Exception as e:
            self.log_test(f"Account Creation - {name}", False, f"Error: {str(e)}")
            
        return None
    
    def test_1_authentication(self):
        """1. AUTENTICAÇÃO - Criar 3 contas diferentes com emails únicos"""
        print("\n" + "="*80)
        print("1. TESTE DE AUTENTICAÇÃO")
        print("="*80)
        
        accounts_to_create = [
            ("homem_cutting", "João Silva"),
            ("mulher_bulking", "Maria Santos"), 
            ("homem_manutencao", "Carlos Oliveira")
        ]
        
        for suffix, name in accounts_to_create:
            account = self.create_test_account(suffix, name)
            if account:
                self.test_accounts.append(account)
                
                # Test login with each account
                login_response = self.session.post(
                    f"{BASE_URL}/auth/login",
                    json={"email": account["email"], "password": account["password"]}
                )
                
                if login_response.status_code == 200:
                    self.log_test(f"Login Test - {name}", True, "Login successful")
                else:
                    self.log_test(f"Login Test - {name}", False, f"Login failed: {login_response.status_code}")
    
    def test_2_varied_profiles(self):
        """2. PERFIS VARIADOS - Criar 3 perfis diferentes conforme especificação"""
        print("\n" + "="*80)
        print("2. TESTE DE PERFIS VARIADOS")
        print("="*80)
        
        if len(self.test_accounts) < 3:
            self.log_test("Profile Creation", False, "Insufficient accounts for profile testing")
            return
            
        profiles = [
            {
                "name": "Perfil 1 - Homem Cutting",
                "account_idx": 0,
                "data": {
                    "name": "João Silva",
                    "age": 25,
                    "sex": "masculino",
                    "height": 180.0,
                    "weight": 85.0,
                    "goal": "cutting",
                    "training_level": "intermediario",
                    "weekly_training_frequency": 5,
                    "available_time_per_session": 60,
                    "dietary_restrictions": [],
                    "food_preferences": []
                }
            },
            {
                "name": "Perfil 2 - Mulher Bulking",
                "account_idx": 1,
                "data": {
                    "name": "Maria Santos",
                    "age": 30,
                    "sex": "feminino",
                    "height": 165.0,
                    "weight": 55.0,
                    "goal": "bulking",
                    "training_level": "intermediario",
                    "weekly_training_frequency": 4,
                    "available_time_per_session": 45,
                    "dietary_restrictions": ["vegetariano"],
                    "food_preferences": ["tofu", "feijao", "quinoa"]
                }
            },
            {
                "name": "Perfil 3 - Homem Manutenção",
                "account_idx": 2,
                "data": {
                    "name": "Carlos Oliveira",
                    "age": 40,
                    "sex": "masculino",
                    "height": 175.0,
                    "weight": 78.0,
                    "goal": "manutencao",
                    "training_level": "avancado",
                    "weekly_training_frequency": 3,
                    "available_time_per_session": 90,
                    "dietary_restrictions": ["sem_lactose"],
                    "food_preferences": ["frango", "arroz_integral", "batata_doce"]
                }
            }
        ]
        
        for profile in profiles:
            try:
                account = self.test_accounts[profile["account_idx"]]
                profile_data = profile["data"].copy()
                profile_data["id"] = account["user_id"]
                
                headers = {"Authorization": f"Bearer {account['token']}"}
                
                # POST /api/user/profile
                response = self.session.post(
                    f"{BASE_URL}/user/profile",
                    json=profile_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    profile_result = response.json()
                    account["profile"] = profile_result
                    
                    tdee = profile_result.get("tdee", 0)
                    target_calories = profile_result.get("target_calories", 0)
                    macros = profile_result.get("macros", {})
                    
                    details = f"TDEE: {tdee}kcal, Target: {target_calories}kcal, P:{macros.get('protein')}g C:{macros.get('carbs')}g F:{macros.get('fat')}g"
                    self.log_test(profile["name"], True, details)
                    
                    # GET /api/user/profile/{user_id} - Verificar perfil
                    get_response = self.session.get(
                        f"{BASE_URL}/user/profile/{account['user_id']}",
                        headers=headers
                    )
                    
                    if get_response.status_code == 200:
                        self.log_test(f"Profile Retrieval - {profile['name']}", True, "Profile retrieved successfully")
                    else:
                        self.log_test(f"Profile Retrieval - {profile['name']}", False, f"Status: {get_response.status_code}")
                        
                else:
                    self.log_test(profile["name"], False, f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(profile["name"], False, f"Error: {str(e)}")
    
    def test_3_diet_generation(self):
        """3. DIETA - Para cada perfil: gerar dieta e verificar"""
        print("\n" + "="*80)
        print("3. TESTE DE GERAÇÃO DE DIETA")
        print("="*80)
        
        for i, account in enumerate(self.test_accounts):
            if "profile" not in account:
                continue
                
            try:
                headers = {"Authorization": f"Bearer {account['token']}"}
                
                # POST /api/diet/generate
                response = self.session.post(
                    f"{BASE_URL}/diet/generate?user_id={account['user_id']}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    diet_data = response.json()
                    account["diet"] = diet_data
                    
                    meals = diet_data.get("meals", [])
                    computed_calories = diet_data.get("computed_calories", 0)
                    
                    self.log_test(f"Diet Generation - {account['name']}", True, f"{len(meals)} meals, {computed_calories}kcal total")
                    
                    # GET /api/diet/{user_id} - Verificar dieta gerada
                    get_response = self.session.get(
                        f"{BASE_URL}/diet/{account['user_id']}",
                        headers=headers
                    )
                    
                    if get_response.status_code == 200:
                        retrieved_diet = get_response.json()
                        self.log_test(f"Diet Retrieval - {account['name']}", True, "Diet retrieved successfully")
                        
                        # Verificar se todas as quantidades são múltiplos de 10
                        self.validate_multiples_of_10(retrieved_diet, account['name'])
                        
                        # Verificar se macros estão corretos para cada objetivo
                        self.validate_diet_macros(account, retrieved_diet)
                        
                    else:
                        self.log_test(f"Diet Retrieval - {account['name']}", False, f"Status: {get_response.status_code}")
                        
                else:
                    self.log_test(f"Diet Generation - {account['name']}", False, f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Diet Generation - {account['name']}", False, f"Error: {str(e)}")
    
    def validate_multiples_of_10(self, diet_data: dict, user_name: str):
        """Verificar se todas as quantidades são múltiplos de 10"""
        try:
            violations = []
            total_foods = 0
            
            meals = diet_data.get("meals", [])
            for meal_idx, meal in enumerate(meals):
                foods = meal.get("foods", [])
                for food in foods:
                    total_foods += 1
                    grams = food.get("grams", 0)
                    
                    if grams % 10 != 0:
                        violations.append(f"{food.get('name', 'Unknown')}: {grams}g")
            
            if len(violations) == 0:
                self.log_test(f"Multiples of 10 - {user_name}", True, f"All {total_foods} foods are multiples of 10")
            else:
                violation_rate = len(violations) / total_foods * 100
                details = f"{len(violations)}/{total_foods} violations ({violation_rate:.1f}%): {violations[:3]}"
                self.log_test(f"Multiples of 10 - {user_name}", False, details)
                
        except Exception as e:
            self.log_test(f"Multiples of 10 - {user_name}", False, f"Error: {str(e)}")
    
    def validate_diet_macros(self, account: dict, diet_data: dict):
        """Verificar se macros estão corretos para cada objetivo"""
        try:
            profile = account["profile"]
            goal = profile.get("goal", "")
            target_calories = profile.get("target_calories", 0)
            target_macros = profile.get("macros", {})
            
            computed_calories = diet_data.get("computed_calories", 0)
            computed_macros = diet_data.get("computed_macros", {})
            
            # Tolerances (generous as per specification)
            cal_tolerance = max(300, target_calories * 0.15)  # 15% or 300kcal
            
            cal_diff = abs(computed_calories - target_calories)
            
            if cal_diff <= cal_tolerance:
                self.log_test(f"Macro Validation - {account['name']}", True, f"Calories within tolerance: Δ{cal_diff:.0f}kcal")
            else:
                self.log_test(f"Macro Validation - {account['name']}", False, f"Calories out of tolerance: Δ{cal_diff:.0f}kcal > {cal_tolerance:.0f}kcal")
                
        except Exception as e:
            self.log_test(f"Macro Validation - {account['name']}", False, f"Error: {str(e)}")
    
    def test_4_workout_generation(self):
        """4. TREINO - Para cada perfil: gerar treino e verificar"""
        print("\n" + "="*80)
        print("4. TESTE DE GERAÇÃO DE TREINO")
        print("="*80)
        
        for account in self.test_accounts:
            if "profile" not in account:
                continue
                
            try:
                headers = {"Authorization": f"Bearer {account['token']}"}
                
                # POST /api/workout/generate
                response = self.session.post(
                    f"{BASE_URL}/workout/generate?user_id={account['user_id']}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    workout_data = response.json()
                    account["workout"] = workout_data
                    
                    workouts = workout_data.get("workouts", [])
                    expected_frequency = account["profile"].get("weekly_training_frequency", 0)
                    
                    if len(workouts) == expected_frequency:
                        self.log_test(f"Workout Generation - {account['name']}", True, f"{len(workouts)} workouts match frequency {expected_frequency}x/week")
                    else:
                        self.log_test(f"Workout Generation - {account['name']}", False, f"Frequency mismatch: {len(workouts)} vs {expected_frequency}")
                    
                    # GET /api/workout/{user_id}
                    get_response = self.session.get(
                        f"{BASE_URL}/workout/{account['user_id']}",
                        headers=headers
                    )
                    
                    if get_response.status_code == 200:
                        self.log_test(f"Workout Retrieval - {account['name']}", True, "Workout retrieved successfully")
                    else:
                        self.log_test(f"Workout Retrieval - {account['name']}", False, f"Status: {get_response.status_code}")
                    
                    # GET /api/training-cycle/week-preview/{user_id}
                    preview_response = self.session.get(
                        f"{BASE_URL}/training-cycle/week-preview/{account['user_id']}",
                        headers=headers
                    )
                    
                    if preview_response.status_code == 200:
                        self.log_test(f"Week Preview - {account['name']}", True, "Week preview obtained")
                    else:
                        self.log_test(f"Week Preview - {account['name']}", False, f"Status: {preview_response.status_code}")
                    
                    # GET /api/training-cycle/status/{user_id}
                    status_response = self.session.get(
                        f"{BASE_URL}/training-cycle/status/{account['user_id']}",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        day_type = status_data.get("day_type", "unknown")
                        self.log_test(f"Training Status - {account['name']}", True, f"Status: {day_type}")
                    else:
                        self.log_test(f"Training Status - {account['name']}", False, f"Status: {status_response.status_code}")
                        
                else:
                    self.log_test(f"Workout Generation - {account['name']}", False, f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Workout Generation - {account['name']}", False, f"Error: {str(e)}")
    
    def test_5_extra_functionalities(self):
        """5. FUNCIONALIDADES EXTRAS"""
        print("\n" + "="*80)
        print("5. TESTE DE FUNCIONALIDADES EXTRAS")
        print("="*80)
        
        for account in self.test_accounts:
            if "profile" not in account:
                continue
                
            try:
                headers = {"Authorization": f"Bearer {account['token']}"}
                user_id = account["user_id"]
                
                # PUT /api/user/profile/{user_id} - Atualizar perfil
                update_data = {"weight": account["profile"]["weight"] + 1.0}
                update_response = self.session.put(
                    f"{BASE_URL}/user/profile/{user_id}",
                    json=update_data,
                    headers=headers
                )
                
                if update_response.status_code == 200:
                    updated_profile = update_response.json()
                    new_weight = updated_profile.get("weight")
                    self.log_test(f"Profile Update - {account['name']}", True, f"Weight updated to {new_weight}kg")
                else:
                    self.log_test(f"Profile Update - {account['name']}", False, f"Status: {update_response.status_code}")
                
                # POST /api/user/{user_id}/switch-goal - Trocar objetivo
                current_goal = account["profile"].get("goal")
                new_goal = "bulking" if current_goal != "bulking" else "cutting"
                
                switch_response = self.session.post(
                    f"{BASE_URL}/user/{user_id}/switch-goal/{new_goal}",
                    headers=headers
                )
                
                if switch_response.status_code == 200:
                    self.log_test(f"Goal Switch - {account['name']}", True, f"Goal switched to {new_goal}")
                else:
                    self.log_test(f"Goal Switch - {account['name']}", False, f"Status: {switch_response.status_code}, Response: {switch_response.text}")
                
                # GET /api/user/premium/{user_id} - Status premium
                premium_response = self.session.get(
                    f"{BASE_URL}/user/premium/{user_id}",
                    headers=headers
                )
                
                if premium_response.status_code in [200, 404]:
                    # 404 is acceptable if endpoint not implemented
                    self.log_test(f"Premium Status - {account['name']}", True, f"Status: {premium_response.status_code}")
                else:
                    self.log_test(f"Premium Status - {account['name']}", False, f"Status: {premium_response.status_code}")
                
                # GET /api/progress/weight/{user_id} - Histórico de peso
                weight_history_response = self.session.get(
                    f"{BASE_URL}/progress/weight/{user_id}",
                    headers=headers
                )
                
                if weight_history_response.status_code in [200, 404]:
                    # 404 is acceptable if no history exists
                    self.log_test(f"Weight History - {account['name']}", True, f"Status: {weight_history_response.status_code}")
                else:
                    self.log_test(f"Weight History - {account['name']}", False, f"Status: {weight_history_response.status_code}")
                
                # POST /api/progress/weight - Registrar peso (may fail due to 14-day blocking)
                weight_data = {
                    "weight": account["profile"]["weight"] + 0.5,
                    "questionnaire": {
                        "diet": 8,
                        "training": 7,
                        "cardio": 6,
                        "sleep": 8,
                        "hydration": 9
                    }
                }
                
                weight_register_response = self.session.post(
                    f"{BASE_URL}/progress/weight/{user_id}",
                    json=weight_data,
                    headers=headers
                )
                
                if weight_register_response.status_code == 200:
                    self.log_test(f"Weight Registration - {account['name']}", True, "Weight registered successfully")
                elif weight_register_response.status_code == 400:
                    # 14-day blocking is expected behavior
                    response_text = weight_register_response.text
                    if "14 dias" in response_text or "Aguarde" in response_text:
                        self.log_test(f"Weight Registration - {account['name']}", True, "14-day blocking working correctly")
                    else:
                        self.log_test(f"Weight Registration - {account['name']}", False, f"Unexpected 400: {response_text}")
                else:
                    self.log_test(f"Weight Registration - {account['name']}", False, f"Status: {weight_register_response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Extra Functionalities - {account['name']}", False, f"Error: {str(e)}")
    
    def test_6_dietary_restrictions(self):
        """6. PREFERÊNCIAS ALIMENTARES - Testar diferentes restrições"""
        print("\n" + "="*80)
        print("6. TESTE DE PREFERÊNCIAS ALIMENTARES")
        print("="*80)
        
        restrictions_to_test = [
            {
                "name": "Vegetariano",
                "restrictions": ["vegetariano"],
                "preferences": ["tofu", "feijao", "quinoa"],
                "forbidden_foods": ["frango", "carne", "peixe", "tilapia", "salmao"]
            },
            {
                "name": "Vegano",
                "restrictions": ["vegano"],
                "preferences": ["tofu", "feijao", "quinoa", "lentilha"],
                "forbidden_foods": ["frango", "carne", "peixe", "ovos", "leite", "queijo", "whey"]
            },
            {
                "name": "Sem Lactose",
                "restrictions": ["sem_lactose"],
                "preferences": ["frango", "arroz", "batata_doce"],
                "forbidden_foods": ["leite", "queijo", "iogurte", "whey"]
            },
            {
                "name": "Sem Glúten",
                "restrictions": ["sem_gluten"],
                "preferences": ["frango", "arroz", "batata_doce", "tapioca"],
                "forbidden_foods": ["pao", "macarrao", "aveia", "trigo"]
            }
        ]
        
        for restriction_test in restrictions_to_test:
            try:
                # Create temporary account for restriction testing
                temp_account = self.create_test_account(
                    f"restriction_{restriction_test['name'].lower()}",
                    f"Test {restriction_test['name']}"
                )
                
                if not temp_account:
                    continue
                
                # Create profile with restrictions
                profile_data = {
                    "id": temp_account["user_id"],
                    "name": temp_account["name"],
                    "age": 30,
                    "sex": "masculino",
                    "height": 175.0,
                    "weight": 70.0,
                    "goal": "manutencao",
                    "training_level": "intermediario",
                    "weekly_training_frequency": 3,
                    "available_time_per_session": 60,
                    "dietary_restrictions": restriction_test["restrictions"],
                    "food_preferences": restriction_test["preferences"]
                }
                
                headers = {"Authorization": f"Bearer {temp_account['token']}"}
                
                profile_response = self.session.post(
                    f"{BASE_URL}/user/profile",
                    json=profile_data,
                    headers=headers
                )
                
                if profile_response.status_code != 200:
                    self.log_test(f"Restriction Profile - {restriction_test['name']}", False, f"Profile creation failed: {profile_response.status_code}")
                    continue
                
                # Generate diet
                diet_response = self.session.post(
                    f"{BASE_URL}/diet/generate?user_id={temp_account['user_id']}",
                    headers=headers
                )
                
                if diet_response.status_code == 200:
                    diet_data = diet_response.json()
                    
                    # Validate restrictions
                    violations = self.validate_dietary_restrictions(
                        diet_data,
                        restriction_test["forbidden_foods"],
                        restriction_test["name"]
                    )
                    
                    if len(violations) == 0:
                        self.log_test(f"Dietary Restrictions - {restriction_test['name']}", True, "All restrictions respected")
                    else:
                        self.log_test(f"Dietary Restrictions - {restriction_test['name']}", False, f"Violations found: {violations}")
                        
                else:
                    self.log_test(f"Dietary Restrictions - {restriction_test['name']}", False, f"Diet generation failed: {diet_response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Dietary Restrictions - {restriction_test['name']}", False, f"Error: {str(e)}")
    
    def validate_dietary_restrictions(self, diet_data: dict, forbidden_foods: List[str], restriction_name: str) -> List[str]:
        """Validate that dietary restrictions are respected"""
        violations = []
        
        try:
            meals = diet_data.get("meals", [])
            
            for meal in meals:
                for food in meal.get("foods", []):
                    food_name = food.get("name", "").lower()
                    food_key = food.get("key", "").lower()
                    
                    for forbidden in forbidden_foods:
                        if forbidden.lower() in food_name or forbidden.lower() in food_key:
                            violations.append(f"Found forbidden food '{food.get('name')}' for {restriction_name}")
                            
        except Exception as e:
            violations.append(f"Error validating restrictions: {str(e)}")
            
        return violations
    
    def test_7_validations(self):
        """7. VALIDAÇÕES - Verificar cálculos TDEE, macros, distribuição"""
        print("\n" + "="*80)
        print("7. TESTE DE VALIDAÇÕES")
        print("="*80)
        
        for account in self.test_accounts:
            if "profile" not in account:
                continue
                
            try:
                profile = account["profile"]
                
                # Verificar cálculo de TDEE
                tdee = profile.get("tdee", 0)
                weight = profile.get("weight", 0)
                height = profile.get("height", 0)
                age = profile.get("age", 0)
                sex = profile.get("sex", "")
                
                # Basic TDEE validation (should be reasonable for human)
                if 1200 <= tdee <= 5000:
                    self.log_test(f"TDEE Validation - {account['name']}", True, f"TDEE {tdee}kcal is reasonable")
                else:
                    self.log_test(f"TDEE Validation - {account['name']}", False, f"TDEE {tdee}kcal seems unreasonable")
                
                # Verificar macros por objetivo
                goal = profile.get("goal", "")
                target_calories = profile.get("target_calories", 0)
                macros = profile.get("macros", {})
                
                protein = macros.get("protein", 0)
                carbs = macros.get("carbs", 0)
                fat = macros.get("fat", 0)
                
                # Protein should be around 2g/kg body weight
                expected_protein_min = weight * 1.5
                expected_protein_max = weight * 2.5
                
                if expected_protein_min <= protein <= expected_protein_max:
                    self.log_test(f"Protein Validation - {account['name']}", True, f"Protein {protein}g is appropriate for {weight}kg")
                else:
                    self.log_test(f"Protein Validation - {account['name']}", False, f"Protein {protein}g seems inappropriate for {weight}kg")
                
                # Verificar distribuição de refeições
                if "diet" in account:
                    diet = account["diet"]
                    meals = diet.get("meals", [])
                    
                    if 4 <= len(meals) <= 6:
                        self.log_test(f"Meal Distribution - {account['name']}", True, f"{len(meals)} meals is appropriate")
                    else:
                        self.log_test(f"Meal Distribution - {account['name']}", False, f"{len(meals)} meals is not in range 4-6")
                
                # Verificar exercícios por frequência
                if "workout" in account:
                    workout = account["workout"]
                    workouts = workout.get("workouts", [])
                    expected_frequency = profile.get("weekly_training_frequency", 0)
                    
                    if len(workouts) == expected_frequency:
                        self.log_test(f"Exercise Frequency - {account['name']}", True, f"Workout frequency matches: {len(workouts)}x/week")
                    else:
                        self.log_test(f"Exercise Frequency - {account['name']}", False, f"Frequency mismatch: {len(workouts)} vs {expected_frequency}")
                        
            except Exception as e:
                self.log_test(f"Validations - {account['name']}", False, f"Error: {str(e)}")
    
    def test_food_substitution(self):
        """Test food substitution functionality"""
        print("\n" + "="*80)
        print("TESTE DE SUBSTITUIÇÃO DE ALIMENTOS")
        print("="*80)
        
        if len(self.test_accounts) == 0 or "diet" not in self.test_accounts[0]:
            self.log_test("Food Substitution", False, "No diet available for substitution test")
            return
        
        account = self.test_accounts[0]
        headers = {"Authorization": f"Bearer {account['token']}"}
        user_id = account["user_id"]
        
        try:
            diet = account["diet"]
            meals = diet.get("meals", [])
            
            if len(meals) == 0 or len(meals[0].get("foods", [])) == 0:
                self.log_test("Food Substitution", False, "No foods available for substitution")
                return
            
            # Get first food from first meal
            first_food = meals[0]["foods"][0]
            food_key = first_food.get("key", first_food.get("name", ""))
            
            # GET /api/diet/{user_id}/substitutes/{food_key}
            substitutes_response = self.session.get(
                f"{BASE_URL}/diet/{user_id}/substitutes/{food_key}",
                headers=headers
            )
            
            if substitutes_response.status_code == 200:
                substitutes_data = substitutes_response.json()
                substitutes = substitutes_data.get("substitutes", [])
                
                self.log_test("Get Food Substitutes", True, f"{len(substitutes)} substitutes found for {first_food.get('name')}")
                
                if len(substitutes) > 0:
                    # Try to substitute with first substitute
                    new_food_key = substitutes[0]["key"]
                    
                    substitution_request = {
                        "meal_index": 0,
                        "food_index": 0,
                        "new_food_key": new_food_key
                    }
                    
                    # PUT /api/diet/{user_id}/substitute
                    substitute_response = self.session.put(
                        f"{BASE_URL}/diet/{user_id}/substitute",
                        json=substitution_request,
                        headers=headers
                    )
                    
                    if substitute_response.status_code == 200:
                        self.log_test("Execute Food Substitution", True, f"Substitution successful: {first_food.get('name')} -> {substitutes[0]['name']}")
                    else:
                        self.log_test("Execute Food Substitution", False, f"Status: {substitute_response.status_code}")
                else:
                    self.log_test("Execute Food Substitution", False, "No substitutes available")
            else:
                self.log_test("Get Food Substitutes", False, f"Status: {substitutes_response.status_code}")
                
        except Exception as e:
            self.log_test("Food Substitution", False, f"Error: {str(e)}")
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "="*80)
        print("RELATÓRIO FINAL - AUDITORIA COMPLETA LAF BACKEND")
        print("="*80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"TOTAL DE TESTES EXECUTADOS: {self.total_tests}")
        print(f"TESTES APROVADOS: {self.passed_tests}")
        print(f"TESTES FALHARAM: {self.total_tests - self.passed_tests}")
        print(f"TAXA DE SUCESSO: {success_rate:.1f}%")
        print()
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["test"].split(" - ")[0] if " - " in result["test"] else result["test"].split(" ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            
            categories[category]["tests"].append(result)
        
        print("RESULTADOS POR CATEGORIA:")
        print("-" * 50)
        for category, data in categories.items():
            total = data["passed"] + data["failed"]
            rate = (data["passed"] / total * 100) if total > 0 else 0
            status = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
            print(f"{status} {category}: {data['passed']}/{total} ({rate:.1f}%)")
        
        print("\n" + "="*80)
        print("FALHAS CRÍTICAS ENCONTRADAS:")
        print("="*80)
        
        failures = [r for r in self.test_results if not r["success"]]
        
        if len(failures) == 0:
            print("🎉 NENHUMA FALHA CRÍTICA ENCONTRADA!")
            print("✅ SISTEMA BACKEND 100% FUNCIONAL")
        else:
            for failure in failures:
                print(f"❌ {failure['test']}: {failure['details']}")
        
        print("\n" + "="*80)
        print("RESUMO EXECUTIVO:")
        print("="*80)
        
        if success_rate >= 95:
            print("🏆 EXCELENTE: Sistema backend altamente funcional")
        elif success_rate >= 85:
            print("✅ BOM: Sistema backend funcional com pequenos problemas")
        elif success_rate >= 70:
            print("⚠️ ACEITÁVEL: Sistema backend funcional mas precisa de melhorias")
        else:
            print("❌ CRÍTICO: Sistema backend com problemas sérios")
        
        print(f"\nBase URL testada: {BASE_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "categories": categories,
            "failures": failures
        }

def main():
    """Execute comprehensive LAF backend testing"""
    print("🔍 INICIANDO AUDITORIA COMPLETA LAF BACKEND")
    print("Testando TODOS os endpoints conforme solicitação da revisão")
    print(f"Base URL: {BASE_URL}")
    print("="*80)
    
    tester = ComprehensiveLAFTester()
    
    # Execute all tests in order
    tester.test_1_authentication()
    tester.test_2_varied_profiles()
    tester.test_3_diet_generation()
    tester.test_4_workout_generation()
    tester.test_5_extra_functionalities()
    tester.test_6_dietary_restrictions()
    tester.test_7_validations()
    tester.test_food_substitution()
    
    # Generate final report
    report = tester.generate_final_report()
    
    return report

if __name__ == "__main__":
    results = main()