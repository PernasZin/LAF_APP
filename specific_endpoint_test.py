#!/usr/bin/env python3
"""
LAF Backend API Testing - Specific Endpoints as Requested
Tests the exact endpoints mentioned in the review request.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Base URL from frontend .env
BASE_URL = "https://prelaunch-diet.preview.emergentagent.com/api"

class LAFSpecificTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        
        # Default headers
        default_headers = {"Content-Type": "application/json"}
        if self.auth_token:
            default_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        if headers:
            default_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=default_headers, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=default_headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=default_headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            raise
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints as requested"""
        print("\n=== 1. AUTENTICAÇÃO ===")
        
        # Generate unique email with timestamp
        timestamp = int(time.time())
        test_email = f"test_backend_{timestamp}@test.com"
        test_password = "TestPassword123!"
        
        # 1. POST /api/auth/signup - Criar nova conta com email único
        signup_data = {
            "email": test_email,
            "password": test_password
        }
        
        try:
            response = self.make_request("POST", "/auth/signup", signup_data)
            if response.status_code == 200:
                signup_result = response.json()
                self.auth_token = signup_result.get("access_token")
                self.user_id = signup_result.get("user_id")
                self.log_test("POST /api/auth/signup", True, 
                            f"Conta criada com email único: {test_email}")
            else:
                self.log_test("POST /api/auth/signup", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("POST /api/auth/signup", False, f"Exception: {str(e)}")
            return False
            
        # 2. POST /api/auth/login - Login com credenciais válidas
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        try:
            response = self.make_request("POST", "/auth/login", login_data)
            if response.status_code == 200:
                login_result = response.json()
                self.auth_token = login_result.get("token")  # Update token
                self.log_test("POST /api/auth/login", True, 
                            f"Login realizado com credenciais válidas")
            else:
                self.log_test("POST /api/auth/login", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("POST /api/auth/login", False, f"Exception: {str(e)}")
            return False
            
        return True
    
    def test_user_profile_endpoints(self):
        """Test user profile endpoints as requested"""
        print("\n=== 2. PERFIL DO USUÁRIO ===")
        
        if not self.user_id or not self.auth_token:
            self.log_test("User Profile Tests", False, "Usuário não autenticado")
            return False
            
        # Create profile first
        profile_data = {
            "id": self.user_id,
            "name": "Test User Specific",
            "age": 28,
            "sex": "masculino",
            "height": 175.0,
            "weight": 80.0,
            "target_weight": 75.0,
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "goal": "cutting",
            "dietary_restrictions": [],
            "food_preferences": ["frango", "arroz_integral"],
            "meal_count": 6
        }
        
        # Create profile
        try:
            response = self.make_request("POST", "/user/profile", profile_data)
            if response.status_code != 200:
                self.log_test("Profile Creation", False, f"Failed to create profile: {response.text}")
                return False
        except Exception as e:
            self.log_test("Profile Creation", False, f"Exception: {str(e)}")
            return False
            
        # 1. GET /api/user/profile/{user_id} - Obter perfil
        try:
            response = self.make_request("GET", f"/user/profile/{self.user_id}")
            if response.status_code == 200:
                profile_result = response.json()
                tdee = profile_result.get("tdee")
                target_calories = profile_result.get("target_calories")
                self.log_test("GET /api/user/profile/{user_id}", True, 
                            f"Perfil obtido - TDEE: {tdee}kcal, Target: {target_calories}kcal")
            else:
                self.log_test("GET /api/user/profile/{user_id}", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /api/user/profile/{user_id}", False, f"Exception: {str(e)}")
            return False
            
        # 2. PUT /api/user/profile/{user_id} - Atualizar perfil
        update_data = {
            "weight": 78.5,
            "goal": "bulking"
        }
        
        try:
            response = self.make_request("PUT", f"/user/profile/{self.user_id}", update_data)
            if response.status_code == 200:
                updated_profile = response.json()
                new_weight = updated_profile.get("weight")
                new_goal = updated_profile.get("goal")
                new_target_calories = updated_profile.get("target_calories")
                self.log_test("PUT /api/user/profile/{user_id}", True, 
                            f"Perfil atualizado - Peso: {new_weight}kg, Objetivo: {new_goal}, Calorias: {new_target_calories}kcal")
            else:
                self.log_test("PUT /api/user/profile/{user_id}", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("PUT /api/user/profile/{user_id}", False, f"Exception: {str(e)}")
            return False
            
        return True
    
    def test_diet_endpoints(self):
        """Test diet endpoints as requested"""
        print("\n=== 3. DIETA ===")
        
        if not self.user_id:
            self.log_test("Diet Tests", False, "Usuário não disponível")
            return False
            
        # 1. POST /api/diet/generate?user_id={user_id} - Gerar dieta
        try:
            response = self.make_request("POST", f"/diet/generate?user_id={self.user_id}")
            if response.status_code == 200:
                diet_result = response.json()
                meals = diet_result.get("meals", [])
                computed_calories = diet_result.get("computed_calories")
                computed_macros = diet_result.get("computed_macros", {})
                self.log_test("POST /api/diet/generate", True, 
                            f"Dieta gerada - {len(meals)} refeições, {computed_calories}kcal, P:{computed_macros.get('protein')}g C:{computed_macros.get('carbs')}g F:{computed_macros.get('fat')}g")
            else:
                self.log_test("POST /api/diet/generate", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("POST /api/diet/generate", False, f"Exception: {str(e)}")
            return False
            
        # 2. GET /api/diet/{user_id} - Obter dieta do usuário
        try:
            response = self.make_request("GET", f"/diet/{self.user_id}")
            if response.status_code == 200:
                diet_result = response.json()
                meals = diet_result.get("meals", [])
                
                # Check if each meal has calorie info
                meals_with_calories = 0
                total_meal_calories = 0
                for meal in meals:
                    meal_cal = meal.get("total_calories") or meal.get("calories", 0)
                    if meal_cal > 0:
                        meals_with_calories += 1
                        total_meal_calories += meal_cal
                
                self.log_test("GET /api/diet/{user_id}", True, 
                            f"Dieta obtida - {len(meals)} refeições, {meals_with_calories} com calorias, Total: {total_meal_calories}kcal")
            else:
                self.log_test("GET /api/diet/{user_id}", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /api/diet/{user_id}", False, f"Exception: {str(e)}")
            return False
            
        return True
    
    def test_workout_endpoints(self):
        """Test workout endpoints as requested"""
        print("\n=== 4. TREINO ===")
        
        if not self.user_id:
            self.log_test("Workout Tests", False, "Usuário não disponível")
            return False
            
        # 1. POST /api/workout/generate?user_id={user_id} - Gerar treino
        try:
            response = self.make_request("POST", f"/workout/generate?user_id={self.user_id}")
            if response.status_code == 200:
                workout_result = response.json()
                workouts = workout_result.get("workouts", [])
                self.log_test("POST /api/workout/generate", True, 
                            f"Treino gerado - {len(workouts)} dias de treino")
            else:
                self.log_test("POST /api/workout/generate", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("POST /api/workout/generate", False, f"Exception: {str(e)}")
            return False
            
        # 2. GET /api/workout/{user_id} - Obter treino do usuário
        try:
            response = self.make_request("GET", f"/workout/{self.user_id}")
            if response.status_code == 200:
                workout_result = response.json()
                workouts = workout_result.get("workouts", [])
                self.log_test("GET /api/workout/{user_id}", True, 
                            f"Treino obtido - {len(workouts)} dias de treino")
            else:
                self.log_test("GET /api/workout/{user_id}", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /api/workout/{user_id}", False, f"Exception: {str(e)}")
            return False
            
        # 3. GET /api/training-cycle/week-preview/{user_id} - Preview da semana
        try:
            response = self.make_request("GET", f"/training-cycle/week-preview/{self.user_id}")
            if response.status_code == 200:
                preview_result = response.json()
                days = preview_result.get("days", [])
                self.log_test("GET /api/training-cycle/week-preview/{user_id}", True, 
                            f"Preview da semana obtido - {len(days)} dias")
            else:
                self.log_test("GET /api/training-cycle/week-preview/{user_id}", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /api/training-cycle/week-preview/{user_id}", False, f"Exception: {str(e)}")
            return False
            
        return True
    
    def test_stripe_endpoints(self):
        """Test Stripe/Payment endpoints as requested"""
        print("\n=== 5. STRIPE/PAGAMENTOS ===")
        
        if not self.user_id:
            self.log_test("Stripe Tests", False, "Usuário não disponível")
            return False
            
        # 1. POST /api/stripe/create-checkout-session - Criar sessão de checkout
        checkout_data = {
            "user_id": self.user_id,
            "price_id": "price_1SsY8nJnbIltYEtzUvMf9vd9",  # Monthly price from .env
            "success_url": "https://prelaunch-diet.preview.emergentagent.com/success",
            "cancel_url": "https://prelaunch-diet.preview.emergentagent.com/cancel"
        }
        
        try:
            response = self.make_request("POST", "/stripe/create-checkout-session", checkout_data)
            if response.status_code == 200:
                checkout_result = response.json()
                session_url = checkout_result.get("url")
                session_id = checkout_result.get("session_id")
                self.log_test("POST /api/stripe/create-checkout-session", True, 
                            f"Sessão de checkout criada - URL: {'Sim' if session_url else 'Não'}, ID: {'Sim' if session_id else 'Não'}")
            else:
                self.log_test("POST /api/stripe/create-checkout-session", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("POST /api/stripe/create-checkout-session", False, f"Exception: {str(e)}")
            
        # 2. GET /api/user/premium/{user_id} - Status premium
        try:
            response = self.make_request("GET", f"/user/premium/{self.user_id}")
            if response.status_code == 200:
                premium_result = response.json()
                is_premium = premium_result.get("is_premium", False)
                subscription_status = premium_result.get("subscription_status", "N/A")
                self.log_test("GET /api/user/premium/{user_id}", True, 
                            f"Status premium obtido - Premium: {is_premium}, Status: {subscription_status}")
            else:
                self.log_test("GET /api/user/premium/{user_id}", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("GET /api/user/premium/{user_id}", False, f"Exception: {str(e)}")
            
        return True
    
    def run_specific_tests(self):
        """Run all specific endpoint tests as requested"""
        print("🚀 TESTE DOS ENDPOINTS PRINCIPAIS - LAF BACKEND")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        # Run test suites in order
        auth_success = self.test_authentication_endpoints()
        
        if auth_success:
            profile_success = self.test_user_profile_endpoints()
            diet_success = self.test_diet_endpoints()
            workout_success = self.test_workout_endpoints()
            stripe_success = self.test_stripe_endpoints()
        else:
            print("❌ Autenticação falhou - pulando outros testes")
            
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de Testes: {total_tests}")
        print(f"✅ Aprovados: {passed_tests}")
        print(f"❌ Falharam: {failed_tests}")
        print(f"Taxa de Sucesso: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 TESTES QUE FALHARAM:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n📋 TODOS OS RESULTADOS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")

if __name__ == "__main__":
    tester = LAFSpecificTester()
    tester.run_specific_tests()