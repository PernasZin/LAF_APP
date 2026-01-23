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
        self.test_results = {
            "profiles_tested": 0,
            "diets_generated": 0,
            "foods_verified": 0,
            "multiple_10_violations": [],
            "restriction_violations": [],
            "meal_count_violations": [],
            "success_rate": 0.0,
            "detailed_results": []
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def create_profile(self, profile_data: Dict) -> Optional[str]:
        """Create user profile and return user_id"""
        try:
            # First create auth user
            auth_data = {
                "email": f"{profile_data['name'].lower().replace(' ', '.')}@laf.com",
                "password": "Teste123!"
            }
            
            # Try signup (might fail if user exists)
            signup_response = self.session.post(f"{self.base_url}/auth/signup", json=auth_data)
            if signup_response.status_code == 200:
                signup_data = signup_response.json()
                user_id = signup_data.get("user_id")
                self.log(f"✅ Created auth user: {user_id}")
            else:
                # Try login instead
                login_response = self.session.post(f"{self.base_url}/auth/login", json=auth_data)
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    user_id = login_data.get("user_id")
                    self.log(f"✅ Logged in existing user: {user_id}")
                else:
                    self.log(f"❌ Failed to create/login user: {login_response.text}", "ERROR")
                    return None
            
            # Create profile with the user_id
            profile_data["id"] = user_id
            
            response = self.session.post(f"{self.base_url}/user/profile", json=profile_data)
            
            if response.status_code == 200:
                profile = response.json()
                self.log(f"✅ Profile created: {profile['name']} (TDEE: {profile.get('tdee', 'N/A')}kcal)")
                return user_id
            else:
                self.log(f"❌ Failed to create profile: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Exception creating profile: {e}", "ERROR")
            return None
    
    def generate_diet(self, user_id: str, profile_name: str) -> Optional[Dict]:
        """Generate diet for user"""
        try:
            response = self.session.post(f"{self.base_url}/diet/generate?user_id={user_id}")
            
            if response.status_code == 200:
                diet = response.json()
                self.log(f"✅ Diet generated for {profile_name}: {len(diet.get('meals', []))} meals")
                return diet
            else:
                self.log(f"❌ Failed to generate diet for {profile_name}: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Exception generating diet: {e}", "ERROR")
            return None
    
    def validate_multiple_of_10(self, diet: Dict, profile_name: str) -> List[str]:
        """Validate that ALL quantities are multiples of 10"""
        violations = []
        
        for meal_idx, meal in enumerate(diet.get("meals", [])):
            meal_name = meal.get("name", f"Meal {meal_idx + 1}")
            
            for food_idx, food in enumerate(meal.get("foods", [])):
                grams = food.get("grams", 0)
                food_name = food.get("name", f"Food {food_idx + 1}")
                
                if grams % 10 != 0:
                    violation = f"{profile_name} - {meal_name} - {food_name}: {grams}g (NOT multiple of 10)"
                    violations.append(violation)
                    self.log(f"🚨 MULTIPLE OF 10 VIOLATION: {violation}", "ERROR")
        
        return violations
    
    def validate_dietary_restrictions(self, diet: Dict, restrictions: List[str], profile_name: str) -> List[str]:
        """Validate dietary restrictions compliance"""
        violations = []
        
        # Define forbidden foods for each restriction
        forbidden_foods = {
            "vegetariano": ["frango", "chicken", "carne", "beef", "peixe", "fish", "atum", "tuna", "salmao", "salmon", "patinho", "peru", "turkey"],
            "diabetico": ["mel", "honey", "banana", "tapioca", "pao", "bread", "acucar", "sugar"],
            "sem_gluten": ["pao", "bread", "aveia", "oat", "macarrao", "pasta", "trigo", "wheat", "pao_integral"],
            "sem_lactose": ["cottage", "queijo", "cheese", "iogurte", "yogurt", "whey", "leite", "milk"]
        }
        
        for restriction in restrictions:
            if restriction in forbidden_foods:
                forbidden = forbidden_foods[restriction]
                
                for meal_idx, meal in enumerate(diet.get("meals", [])):
                    meal_name = meal.get("name", f"Meal {meal_idx + 1}")
                    
                    for food in meal.get("foods", []):
                        food_key = food.get("key", "").lower()
                        food_name = food.get("name", "").lower()
                        
                        for forbidden_item in forbidden:
                            if forbidden_item in food_key or forbidden_item in food_name:
                                violation = f"{profile_name} ({restriction}) - {meal_name} - {food.get('name', 'Unknown')}: FORBIDDEN FOOD"
                                violations.append(violation)
                                self.log(f"🚨 DIETARY RESTRICTION VIOLATION: {violation}", "ERROR")
        
        return violations
    
    def validate_meal_count(self, diet: Dict, expected_count: int, profile_name: str) -> List[str]:
        """Validate meal count"""
        violations = []
        actual_count = len(diet.get("meals", []))
        
        if actual_count != expected_count:
            violation = f"{profile_name}: Expected {expected_count} meals, got {actual_count}"
            violations.append(violation)
            self.log(f"❌ MEAL COUNT VIOLATION: {violation}", "ERROR")
        
        return violations
    
    def validate_calorie_coherence(self, diet: Dict, profile_data: Dict, profile_name: str) -> bool:
        """Validate calorie coherence with goal"""
        try:
            computed_calories = diet.get("computed_calories", 0)
            goal = profile_data.get("goal", "")
            
            # Get user profile to check TDEE
            user_id = profile_data.get("id")
            if user_id:
                profile_response = self.session.get(f"{self.base_url}/user/profile/{user_id}")
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    tdee = profile.get("tdee", 0)
                    target_calories = profile.get("target_calories", 0)
                    
                    self.log(f"📊 {profile_name} - Goal: {goal}, TDEE: {tdee}kcal, Target: {target_calories}kcal, Diet: {computed_calories}kcal")
                    
                    # Validate goal coherence
                    if goal == "cutting" and computed_calories >= tdee:
                        self.log(f"❌ CALORIE INCOHERENCE: {profile_name} cutting should have calories < TDEE", "ERROR")
                        return False
                    elif goal == "bulking" and computed_calories <= tdee:
                        self.log(f"❌ CALORIE INCOHERENCE: {profile_name} bulking should have calories > TDEE", "ERROR")
                        return False
                    elif goal == "manutencao" and abs(computed_calories - tdee) > tdee * 0.1:
                        self.log(f"❌ CALORIE INCOHERENCE: {profile_name} maintenance should have calories ≈ TDEE", "ERROR")
                        return False
                    
                    self.log(f"✅ Calorie coherence validated for {profile_name}")
                    return True
            
            return False
            
        except Exception as e:
            self.log(f"❌ Exception validating calories: {e}", "ERROR")
            return False
    
    def test_switch_goal(self, user_id: str, profile_name: str, current_goal: str) -> bool:
        """Test goal switching functionality"""
        try:
            # Define goal transitions
            transitions = {
                "cutting": "bulking",
                "bulking": "manutencao", 
                "manutencao": "cutting"
            }
            
            new_goal = transitions.get(current_goal, "bulking")
            
            response = self.session.post(f"{self.base_url}/user/{user_id}/switch-goal/{new_goal}")
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ Goal switch successful for {profile_name}: {current_goal} → {new_goal}")
                return True
            else:
                self.log(f"❌ Goal switch failed for {profile_name}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception switching goal: {e}", "ERROR")
            return False
    
    def test_food_substitution(self, user_id: str, profile_name: str) -> bool:
        """Test food substitution functionality"""
        try:
            # Get current diet
            diet_response = self.session.get(f"{self.base_url}/diet/{user_id}")
            if diet_response.status_code != 200:
                self.log(f"❌ Failed to get diet for substitution test: {diet_response.text}", "ERROR")
                return False
            
            diet = diet_response.json()
            
            # Find first food to substitute
            if not diet.get("meals") or not diet["meals"][0].get("foods"):
                self.log(f"❌ No foods found for substitution test", "ERROR")
                return False
            
            first_food = diet["meals"][0]["foods"][0]
            food_key = first_food.get("key")
            
            if not food_key:
                self.log(f"❌ No food key found for substitution test", "ERROR")
                return False
            
            # Get substitutes
            substitutes_response = self.session.get(f"{self.base_url}/diet/{user_id}/substitutes/{food_key}")
            
            if substitutes_response.status_code == 200:
                substitutes = substitutes_response.json()
                substitute_count = len(substitutes.get("substitutes", []))
                self.log(f"✅ Food substitution working for {profile_name}: {substitute_count} substitutes found")
                return True
            else:
                self.log(f"❌ Food substitution failed for {profile_name}: {substitutes_response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception testing food substitution: {e}", "ERROR")
            return False
    
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