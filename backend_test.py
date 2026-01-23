#!/usr/bin/env python3
"""
🧪 LAF BACKEND TESTING SUITE - COMPREHENSIVE PROGRESS SYSTEM TEST
Focus: PROGRESS SYSTEM (Critical for recurring revenue)

Test Account:
- Email: apple-reviewer@laf.com
- Password: AppleReview2025!
- User ID: 14017240-2fff-4123-9d26-fa240255ea21
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# BASE URL from frontend .env
BASE_URL = "https://appdeployer.preview.emergentagent.com/api"

# Test credentials from review request
TEST_EMAIL = "apple-reviewer@laf.com"
TEST_PASSWORD = "AppleReview2025!"
TEST_USER_ID = "14017240-2fff-4123-9d26-fa240255ea21"

class LAFTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None
        self.user_id = TEST_USER_ID
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.log(f"{status} {test_name}")
        if details:
            self.log(f"   {details}")
        if response_data and not success:
            self.log(f"   Response: {response_data}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data, params=params)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, json=data)
            else:
                return False, f"Unsupported method: {method}"
            
            return True, response
        except Exception as e:
            return False, str(e)
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        self.log("🔐 TESTING AUTHENTICATION")
        
        # Test login with provided credentials
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        success, response = self.make_request("POST", "/auth/login", login_data)
        
        if success and response.status_code == 200:
            data = response.json()
            if "token" in data:
                self.token = data["token"]
                self.user_id = data.get("user_id", TEST_USER_ID)
                self.log_test("Authentication Login", True, f"Token received, User ID: {self.user_id}")
            else:
                self.log_test("Authentication Login", False, "No token in response", data)
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Authentication Login", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
        
        # Test token validation
        if self.token:
            success, response = self.make_request("GET", "/auth/validate")
            if success and response.status_code == 200:
                self.log_test("Token Validation", True, "Token is valid")
            else:
                error_msg = response.text if success else str(response)
                self.log_test("Token Validation", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
    
    def test_progress_system_comprehensive(self):
        """Test the CRITICAL PROGRESS system extensively"""
        self.log("📊 TESTING PROGRESS SYSTEM (CRITICAL FOR RECURRING REVENUE)")
        
        if not self.user_id:
            self.log_test("Progress System - No User ID", False, "Cannot test without user ID")
            return
        
        # 1. Test weight registration - POST /api/progress/weight
        self.log("1️⃣ Testing Weight Registration")
        
        # First check if can update
        success, response = self.make_request("GET", f"/progress/weight/{self.user_id}/can-update")
        
        if success and response.status_code == 200:
            can_update_data = response.json()
            can_update = can_update_data.get("can_update", False)
            reason = can_update_data.get("reason", "Unknown")
            self.log_test("Weight Update Check", True, f"Can update: {can_update}, Reason: {reason}")
            
            # Try to register weight (even if blocked, to test the blocking mechanism)
            weight_data = {
                "weight": 75.5,
                "notes": "Teste LAF - Sistema de Progresso",
                "questionnaire": {
                    "diet": 8,
                    "training": 7,
                    "cardio": 6,
                    "sleep": 8,
                    "hydration": 9
                }
            }
            
            success, response = self.make_request("POST", f"/progress/weight/{self.user_id}", weight_data)
            
            if success:
                if response.status_code == 200:
                    weight_response = response.json()
                    recorded_weight = weight_response.get('record', {}).get('weight')
                    self.log_test("Weight Registration", True, f"Weight registered: {recorded_weight}kg")
                elif response.status_code == 400 and "Aguarde" in response.text:
                    self.log_test("Weight Registration Blocking", True, "14-day blocking working correctly")
                else:
                    self.log_test("Weight Registration", False, f"Unexpected status: {response.status_code}", response.text)
            else:
                self.log_test("Weight Registration", False, "Request failed", str(response))
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Weight Update Check", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
        
        # 2. Test weight history - GET /api/progress/weight/{user_id}
        self.log("2️⃣ Testing Weight History")
        
        success, response = self.make_request("GET", f"/progress/weight/{self.user_id}")
        
        if success and response.status_code == 200:
            history_data = response.json()
            records_count = len(history_data) if isinstance(history_data, list) else 0
            self.log_test("Weight History", True, f"Retrieved {records_count} weight records")
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Weight History", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
        
        # 3. Test progress evaluation - GET /api/progress/evaluation/{user_id}
        self.log("3️⃣ Testing Progress Evaluation")
        
        success, response = self.make_request("GET", f"/progress/evaluation/{self.user_id}")
        
        if success and response.status_code == 200:
            evaluation_data = response.json()
            self.log_test("Progress Evaluation", True, f"Evaluation retrieved successfully")
        else:
            # This endpoint might not exist in current implementation
            self.log_test("Progress Evaluation", False, f"Endpoint not implemented or failed - Status: {response.status_code if success else 'Request failed'}")
        
        # 4. Test evaluate and adjust - POST /api/progress/evaluate (simulate 2 weeks scenario)
        self.log("4️⃣ Testing Evaluate and Adjust (2 weeks simulation)")
        
        # Test different scenarios
        scenarios = [
            {"goal": "cutting", "weight_change": -1.2, "description": "CUTTING - Lost 1.2kg in 2 weeks"},
            {"goal": "bulking", "weight_change": 0.8, "description": "BULKING - Gained 0.8kg in 2 weeks"},
            {"goal": "manutencao", "weight_change": 0.1, "description": "MAINTENANCE - Maintained weight"}
        ]
        
        for scenario in scenarios:
            evaluate_data = {
                "user_id": self.user_id,
                "simulate_weeks": 2,
                "goal": scenario["goal"],
                "weight_change": scenario["weight_change"]
            }
            
            success, response = self.make_request("POST", "/progress/evaluate", evaluate_data)
            
            if success and response.status_code == 200:
                adjust_data = response.json()
                adjustment = adjust_data.get('adjustment', 'None')
                self.log_test(f"Progress Evaluate & Adjust - {scenario['goal'].upper()}", True, 
                            f"{scenario['description']} -> Adjustment: {adjustment}")
            else:
                # This endpoint might not exist in current implementation
                self.log_test(f"Progress Evaluate & Adjust - {scenario['goal'].upper()}", False, 
                            f"Endpoint not implemented - Status: {response.status_code if success else 'Request failed'}")
    
    def test_diet_system_comprehensive(self):
        """Test diet generation with TACO table validation"""
        self.log("🍽️ TESTING DIET SYSTEM WITH TACO VALIDATION")
        
        if not self.user_id:
            self.log_test("Diet System - No User ID", False, "Cannot test without user ID")
            return
        
        # 5. Test diet generation - POST /api/diet/generate?user_id={user_id}
        self.log("5️⃣ Testing Diet Generation")
        
        success, response = self.make_request("POST", f"/diet/generate?user_id={self.user_id}")
        
        if success and response.status_code == 200:
            diet_data = response.json()
            meals_count = len(diet_data.get("meals", []))
            total_calories = diet_data.get("computed_calories", 0)
            target_calories = diet_data.get("target_calories", 0)
            
            self.log_test("Diet Generation", True, f"Generated {meals_count} meals, {total_calories} kcal (target: {target_calories})")
            
            # Validate TACO table values (Brazilian food composition)
            self.validate_taco_values(diet_data)
            
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Diet Generation", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
        
        # 6. Test diet retrieval - GET /api/diet/{user_id}
        self.log("6️⃣ Testing Diet Retrieval")
        
        success, response = self.make_request("GET", f"/diet/{self.user_id}")
        
        if success and response.status_code == 200:
            retrieved_diet = response.json()
            retrieved_calories = retrieved_diet.get("computed_calories", 0)
            diet_type = retrieved_diet.get("diet_type", "unknown")
            self.log_test("Diet Retrieval", True, f"Retrieved diet: {retrieved_calories} kcal, type: {diet_type}")
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Diet Retrieval", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
    
    def validate_taco_values(self, diet_data: Dict):
        """Validate TACO table nutritional values"""
        self.log("🔍 Validating TACO Table Values")
        
        meals = diet_data.get("meals", [])
        total_foods = 0
        valid_foods = 0
        
        for meal in meals:
            for food in meal.get("foods", []):
                total_foods += 1
                food_name = food.get("name", "")
                calories = food.get("calories", 0)
                protein = food.get("protein", 0)
                carbs = food.get("carbs", 0)
                fat = food.get("fat", 0)
                grams = food.get("grams", 0)
                
                # Basic validation - values should be reasonable
                if (calories > 0 and protein >= 0 and carbs >= 0 and fat >= 0 and grams > 0):
                    # Check if calorie calculation is approximately correct
                    calculated_calories = (protein * 4) + (carbs * 4) + (fat * 9)
                    calorie_diff = abs(calories - calculated_calories)
                    
                    if calorie_diff <= calories * 0.1:  # Allow 10% difference
                        valid_foods += 1
                    else:
                        self.log(f"⚠️ Calorie mismatch in {food_name}: {calories} vs calculated {calculated_calories:.1f}")
                else:
                    self.log(f"❌ Invalid values in {food_name}: cal={calories}, p={protein}, c={carbs}, f={fat}, g={grams}")
        
        validation_rate = (valid_foods / total_foods * 100) if total_foods > 0 else 0
        self.log_test("TACO Table Values Validation", validation_rate >= 90, 
                     f"Validated {valid_foods}/{total_foods} foods ({validation_rate:.1f}%)")
    
    def test_workout_system(self):
        """Test workout generation"""
        self.log("💪 TESTING WORKOUT SYSTEM")
        
        if not self.user_id:
            self.log_test("Workout System - No User ID", False, "Cannot test without user ID")
            return
        
        # 7. Test workout generation - POST /api/workout/generate?user_id={user_id}
        success, response = self.make_request("POST", f"/workout/generate?user_id={self.user_id}")
        
        if success and response.status_code == 200:
            workout_data = response.json()
            workouts = workout_data.get("workouts", [])
            workouts_count = len(workouts)
            self.log_test("Workout Generation", True, f"Generated {workouts_count} workouts")
            
            # 8. Test workout retrieval - GET /api/workout/{user_id}
            success, response = self.make_request("GET", f"/workout/{self.user_id}")
            
            if success and response.status_code == 200:
                retrieved_workout = response.json()
                self.log_test("Workout Retrieval", True, "Workout retrieved successfully")
            else:
                error_msg = response.text if success else str(response)
                self.log_test("Workout Retrieval", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Workout Generation", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
    
    def test_training_cycle(self):
        """Test training cycle system"""
        self.log("🔄 TESTING TRAINING CYCLE")
        
        if not self.user_id:
            self.log_test("Training Cycle - No User ID", False, "Cannot test without user ID")
            return
        
        # 9. Test training cycle status - GET /api/training-cycle/status/{user_id}
        success, response = self.make_request("GET", f"/training-cycle/status/{self.user_id}")
        
        if success and response.status_code == 200:
            cycle_data = response.json()
            day_type = cycle_data.get("day_type", "unknown")
            calorie_multiplier = cycle_data.get("calorie_multiplier", 1.0)
            self.log_test("Training Cycle Status", True, f"Day type: {day_type}, calorie multiplier: {calorie_multiplier}")
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Training Cycle Status", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
    
    def test_profile_diet_regeneration(self):
        """Test profile update with automatic diet regeneration"""
        self.log("👤 TESTING PROFILE WITH DIET REGENERATION")
        
        if not self.user_id:
            self.log_test("Profile Diet Regeneration - No User ID", False, "Cannot test without user ID")
            return
        
        # 10. Test profile update with goal change - PUT /api/user/profile/{user_id}
        goals_to_test = ["cutting", "bulking", "manutencao"]
        
        for goal in goals_to_test:
            update_data = {"goal": goal}
            success, response = self.make_request("PUT", f"/user/profile/{self.user_id}", update_data)
            
            if success and response.status_code == 200:
                updated_profile = response.json()
                new_goal = updated_profile.get("goal")
                new_calories = updated_profile.get("target_calories")
                self.log_test(f"Profile Update - Goal to {goal.upper()}", True, 
                            f"Goal updated to: {new_goal}, calories: {new_calories}")
                
                # Verify diet was regenerated by checking if it exists
                time.sleep(1)  # Give time for diet regeneration
                success, response = self.make_request("GET", f"/diet/{self.user_id}")
                if success and response.status_code == 200:
                    diet = response.json()
                    diet_calories = diet.get("computed_calories", 0)
                    self.log_test(f"Diet Regeneration - {goal.upper()}", True, 
                                f"Diet regenerated with {diet_calories} kcal")
                else:
                    self.log_test(f"Diet Regeneration - {goal.upper()}", False, "Diet not found after profile update")
            else:
                error_msg = response.text if success else str(response)
                self.log_test(f"Profile Update - Goal to {goal.upper()}", False, 
                            f"Status: {response.status_code if success else 'Request failed'}", error_msg)
    
    def test_premium_system(self):
        """Test premium system"""
        self.log("💎 TESTING PREMIUM SYSTEM")
        
        if not self.user_id:
            self.log_test("Premium System - No User ID", False, "Cannot test without user ID")
            return
        
        # 11. Test premium status - GET /api/user/premium/{user_id}
        success, response = self.make_request("GET", f"/user/premium/{self.user_id}")
        
        if success and response.status_code == 200:
            premium_data = response.json()
            is_premium = premium_data.get("is_premium", False)
            self.log_test("Premium Status", True, f"Premium status: {is_premium}")
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Premium Status", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
    
    def test_account_deletion(self):
        """Test account deletion (create test account first)"""
        self.log("🗑️ TESTING ACCOUNT DELETION")
        
        # Create a test account for deletion
        test_email = f"delete-test-{int(time.time())}@laf.com"
        test_password = "DeleteTest123!"
        
        # 1. Create account
        signup_data = {
            "email": test_email,
            "password": test_password
        }
        
        success, response = self.make_request("POST", "/auth/signup", signup_data)
        
        if success and response.status_code == 200:
            signup_response = response.json()
            test_user_id = signup_response.get("user_id")
            self.log_test("Create Test Account for Deletion", True, f"Test account created: {test_user_id}")
            
            # 2. Delete the account
            if test_user_id:
                delete_data = {
                    "user_id": test_user_id,
                    "password": test_password
                }
                
                success, response = self.make_request("DELETE", "/auth/delete-account", delete_data)
                
                if success and response.status_code == 200:
                    delete_response = response.json()
                    deleted_data = delete_response.get("deleted_data", {})
                    self.log_test("Account Deletion", True, f"Account deleted successfully: {deleted_data}")
                else:
                    error_msg = response.text if success else str(response)
                    self.log_test("Account Deletion", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
        else:
            error_msg = response.text if success else str(response)
            self.log_test("Create Test Account for Deletion", False, f"Status: {response.status_code if success else 'Request failed'}", error_msg)
    
    def run_comprehensive_test(self):
        """Run comprehensive test with all 8 profiles"""
        
        # 8 PERFIS ESPECÍFICOS CONFORME SOLICITAÇÃO
        profiles = [
            {
                "name": "João Silva",
                "age": 25,
                "sex": "masculino",
                "height": 175,
                "weight": 85,
                "training_level": "iniciante",
                "weekly_training_frequency": 3,
                "available_time_per_session": 45,
                "goal": "cutting",
                "dietary_restrictions": [],
                "food_preferences": ["frango", "arroz_branco", "batata_doce", "banana"],
                "meal_count": 4
            },
            {
                "name": "Maria Santos",
                "age": 28,
                "sex": "feminino",
                "height": 165,
                "weight": 60,
                "training_level": "avancado",
                "weekly_training_frequency": 6,
                "available_time_per_session": 90,
                "goal": "bulking",
                "dietary_restrictions": ["sem_lactose"],
                "food_preferences": ["tilapia", "arroz_integral", "aveia", "morango"],
                "meal_count": 6
            },
            {
                "name": "Pedro Costa",
                "age": 35,
                "sex": "masculino",
                "height": 180,
                "weight": 78,
                "training_level": "intermediario",
                "weekly_training_frequency": 4,
                "available_time_per_session": 60,
                "goal": "manutencao",
                "dietary_restrictions": ["vegetariano"],
                "food_preferences": ["tofu", "arroz_branco", "feijao", "maca"],
                "meal_count": 5
            },
            {
                "name": "Ana Oliveira",
                "age": 45,
                "sex": "feminino",
                "height": 160,
                "weight": 70,
                "training_level": "iniciante",
                "weekly_training_frequency": 2,
                "available_time_per_session": 30,
                "goal": "cutting",
                "dietary_restrictions": ["diabetico"],
                "food_preferences": ["frango", "arroz_integral", "brocolis", "maca"],
                "meal_count": 4
            },
            {
                "name": "Carlos Ferreira",
                "age": 30,
                "sex": "masculino",
                "height": 185,
                "weight": 90,
                "training_level": "avancado",
                "weekly_training_frequency": 5,
                "available_time_per_session": 75,
                "goal": "bulking",
                "dietary_restrictions": ["sem_gluten"],
                "food_preferences": ["patinho", "arroz_branco", "batata_doce", "banana"],
                "meal_count": 5
            },
            {
                "name": "Lucia Mendes",
                "age": 32,
                "sex": "feminino",
                "height": 168,
                "weight": 65,
                "training_level": "intermediario",
                "weekly_training_frequency": 4,
                "available_time_per_session": 50,
                "goal": "manutencao",
                "dietary_restrictions": ["sem_lactose"],
                "food_preferences": ["salmao", "arroz_integral", "abacate", "laranja"],
                "meal_count": 6
            },
            {
                "name": "Roberto Lima",
                "age": 40,
                "sex": "masculino",
                "height": 170,
                "weight": 110,
                "training_level": "iniciante",
                "weekly_training_frequency": 3,
                "available_time_per_session": 40,
                "goal": "cutting",
                "dietary_restrictions": [],
                "food_preferences": ["frango", "arroz_branco", "brocolis", "maca"],
                "meal_count": 4
            },
            {
                "name": "Fernanda Souza",
                "age": 22,
                "sex": "feminino",
                "height": 170,
                "weight": 52,
                "training_level": "intermediario",
                "weekly_training_frequency": 5,
                "available_time_per_session": 60,
                "goal": "bulking",
                "dietary_restrictions": [],
                "food_preferences": ["frango", "macarrao", "pasta_amendoim", "banana"],
                "meal_count": 6
            }
        ]
        
        self.log("🚀 INICIANDO TESTE EXTENSIVO - 8 PERFIS DIFERENTES")
        self.log("=" * 80)
        
        total_tests = 0
        successful_tests = 0
        
        for i, profile_data in enumerate(profiles, 1):
            self.log(f"\n📋 TESTANDO PERFIL {i}/8: {profile_data['name']}")
            self.log("-" * 60)
            
            # 1. CREATE PROFILE
            user_id = self.create_profile(profile_data)
            if not user_id:
                continue
            
            self.test_results["profiles_tested"] += 1
            
            # 2. GENERATE DIET
            diet = self.generate_diet(user_id, profile_data['name'])
            if not diet:
                continue
            
            self.test_results["diets_generated"] += 1
            
            # Count foods
            food_count = sum(len(meal.get("foods", [])) for meal in diet.get("meals", []))
            self.test_results["foods_verified"] += food_count
            
            # 3. VALIDATE MULTIPLE OF 10 (CRÍTICO!)
            multiple_violations = self.validate_multiple_of_10(diet, profile_data['name'])
            self.test_results["multiple_10_violations"].extend(multiple_violations)
            
            # 4. VALIDATE DIETARY RESTRICTIONS
            restriction_violations = self.validate_dietary_restrictions(
                diet, profile_data.get("dietary_restrictions", []), profile_data['name']
            )
            self.test_results["restriction_violations"].extend(restriction_violations)
            
            # 5. VALIDATE MEAL COUNT
            meal_count_violations = self.validate_meal_count(
                diet, profile_data.get("meal_count", 6), profile_data['name']
            )
            self.test_results["meal_count_violations"].extend(meal_count_violations)
            
            # 6. VALIDATE CALORIE COHERENCE
            calorie_coherent = self.validate_calorie_coherence(diet, profile_data, profile_data['name'])
            
            # 7. TEST SWITCH GOAL
            goal_switch_success = self.test_switch_goal(user_id, profile_data['name'], profile_data['goal'])
            
            # 8. TEST FOOD SUBSTITUTION
            substitution_success = self.test_food_substitution(user_id, profile_data['name'])
            
            # Calculate success for this profile
            profile_success = (
                len(multiple_violations) == 0 and
                len(restriction_violations) == 0 and
                len(meal_count_violations) == 0 and
                calorie_coherent and
                goal_switch_success and
                substitution_success
            )
            
            if profile_success:
                successful_tests += 1
                self.log(f"✅ PERFIL {profile_data['name']} - TODOS OS TESTES PASSARAM")
            else:
                self.log(f"❌ PERFIL {profile_data['name']} - ALGUNS TESTES FALHARAM")
            
            total_tests += 1
            
            # Store detailed results
            self.test_results["detailed_results"].append({
                "profile": profile_data['name'],
                "success": profile_success,
                "multiple_10_violations": len(multiple_violations),
                "restriction_violations": len(restriction_violations),
                "meal_count_violations": len(meal_count_violations),
                "calorie_coherent": calorie_coherent,
                "goal_switch_success": goal_switch_success,
                "substitution_success": substitution_success
            })
            
            # Small delay between profiles
            time.sleep(1)
        
        # Calculate overall success rate
        if total_tests > 0:
            self.test_results["success_rate"] = (successful_tests / total_tests) * 100
        
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        self.log("\n" + "=" * 80)
        self.log("📊 RELATÓRIO FINAL - TESTE EXTENSIVO LAF")
        self.log("=" * 80)
        
        # Summary statistics
        self.log(f"📋 Total de perfis testados: {self.test_results['profiles_tested']}")
        self.log(f"🍽️ Total de dietas geradas: {self.test_results['diets_generated']}")
        self.log(f"🥗 Total de alimentos verificados: {self.test_results['foods_verified']}")
        self.log(f"📈 Taxa de sucesso geral: {self.test_results['success_rate']:.1f}%")
        
        # Critical violations
        self.log(f"\n🚨 VIOLAÇÕES CRÍTICAS ENCONTRADAS:")
        self.log(f"❌ Violações de múltiplos de 10: {len(self.test_results['multiple_10_violations'])}")
        self.log(f"❌ Violações de restrições alimentares: {len(self.test_results['restriction_violations'])}")
        self.log(f"❌ Violações de meal_count: {len(self.test_results['meal_count_violations'])}")
        
        # Detailed violations
        if self.test_results['multiple_10_violations']:
            self.log(f"\n🔍 DETALHES - VIOLAÇÕES MÚLTIPLOS DE 10:")
            for violation in self.test_results['multiple_10_violations'][:10]:  # Show first 10
                self.log(f"  • {violation}")
            if len(self.test_results['multiple_10_violations']) > 10:
                self.log(f"  ... e mais {len(self.test_results['multiple_10_violations']) - 10} violações")
        
        if self.test_results['restriction_violations']:
            self.log(f"\n🔍 DETALHES - VIOLAÇÕES RESTRIÇÕES ALIMENTARES:")
            for violation in self.test_results['restriction_violations']:
                self.log(f"  • {violation}")
        
        if self.test_results['meal_count_violations']:
            self.log(f"\n🔍 DETALHES - VIOLAÇÕES MEAL_COUNT:")
            for violation in self.test_results['meal_count_violations']:
                self.log(f"  • {violation}")
        
        # Per-profile results
        self.log(f"\n📋 RESULTADOS POR PERFIL:")
        for result in self.test_results['detailed_results']:
            status = "✅ PASSOU" if result['success'] else "❌ FALHOU"
            self.log(f"  {result['profile']}: {status}")
        
        # Final approval criteria
        self.log(f"\n🎯 CRITÉRIO DE APROVAÇÃO:")
        multiple_10_ok = len(self.test_results['multiple_10_violations']) == 0
        restrictions_ok = len(self.test_results['restriction_violations']) == 0
        
        self.log(f"  • 100% múltiplos de 10: {'✅ APROVADO' if multiple_10_ok else '❌ REPROVADO'}")
        self.log(f"  • 100% restrições respeitadas: {'✅ APROVADO' if restrictions_ok else '❌ REPROVADO'}")
        
        overall_approved = multiple_10_ok and restrictions_ok
        self.log(f"\n🏆 RESULTADO FINAL: {'✅ APROVADO' if overall_approved else '❌ REPROVADO'}")
        
        if not overall_approved:
            self.log("⚠️  SISTEMA PRECISA DE CORREÇÕES ANTES DA APROVAÇÃO")
        
        return self.test_results

if __name__ == "__main__":
    tester = LAFTester()
    results = tester.run_comprehensive_test()