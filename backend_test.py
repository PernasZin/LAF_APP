#!/usr/bin/env python3
"""
AUDITORIA COMPLETA - Múltiplos Perfis com Foco em DIETA
Teste abrangente de 6 perfis diferentes com restrições alimentares e preferências
Base URL: https://workoutcycler.preview.emergentagent.com/api
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Configuração
BASE_URL = "https://workoutcycler.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class DietAuditTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.test_results = []
        self.profiles_created = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def calculate_expected_calories(self, profile: Dict) -> Dict:
        """Calculate expected TDEE and target calories"""
        # BMR calculation (Mifflin-St Jeor)
        weight = profile["weight"]
        height = profile["height"] 
        age = profile["age"]
        sex = profile["sex"]
        
        if sex == "masculino":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
            
        # Activity factor based on frequency
        freq = profile["weekly_training_frequency"]
        if freq <= 1:
            factor = 1.3
        elif freq <= 3:
            factor = 1.45
        elif freq <= 5:
            factor = 1.6
        else:
            factor = 1.75
            
        # TDEE base
        tdee_base = bmr * factor
        
        # Add cardio calories based on goal
        goal = profile["goal"]
        if goal == "cutting":
            cardio_weekly = 1270
        elif goal == "bulking":
            cardio_weekly = 420
        else:  # manutencao
            cardio_weekly = 656
            
        cardio_daily = cardio_weekly / 7
        tdee = tdee_base + cardio_daily
        
        # Target calories based on goal
        if goal == "cutting":
            target_calories = tdee * 0.80  # -20%
        elif goal == "bulking":
            target_calories = tdee * 1.12  # +12%
        else:  # manutencao
            target_calories = tdee
            
        # Expected protein (2.0 g/kg for all goals)
        expected_protein = weight * 2.0
        
        return {
            "bmr": bmr,
            "tdee": tdee,
            "target_calories": target_calories,
            "expected_protein": expected_protein
        }
        
    def create_profile(self, profile_data: Dict) -> bool:
        """Create user profile"""
        try:
            response = requests.post(
                f"{self.base_url}/user/profile",
                headers=self.headers,
                json=profile_data,
                timeout=30
            )
            
            if response.status_code == 200:
                profile_response = response.json()
                self.profiles_created.append(profile_data["id"])
                
                # Validate calculations
                expected = self.calculate_expected_calories(profile_data)
                actual_tdee = profile_response.get("tdee", 0)
                actual_target = profile_response.get("target_calories", 0)
                actual_protein = profile_response.get("macros", {}).get("protein", 0)
                
                # Check TDEE (±50 kcal tolerance)
                tdee_diff = abs(actual_tdee - expected["tdee"])
                tdee_ok = tdee_diff <= 50
                
                # Check target calories (±50 kcal tolerance)
                cal_diff = abs(actual_target - expected["target_calories"])
                cal_ok = cal_diff <= 50
                
                # Check protein (±10g tolerance)
                protein_diff = abs(actual_protein - expected["expected_protein"])
                protein_ok = protein_diff <= 10
                
                details = f"TDEE: {actual_tdee}kcal (expected {expected['tdee']:.0f}, Δ{tdee_diff:.0f}), Target: {actual_target}kcal (expected {expected['target_calories']:.0f}, Δ{cal_diff:.0f}), Protein: {actual_protein}g (expected {expected['expected_protein']:.0f}, Δ{protein_diff:.0f})"
                
                if tdee_ok and cal_ok and protein_ok:
                    self.log_test(f"Profile Creation - {profile_data['name']}", True, details)
                    return True
                else:
                    self.log_test(f"Profile Creation - {profile_data['name']}", False, f"Calculation errors: {details}")
                    return False
            else:
                self.log_test(f"Profile Creation - {profile_data['name']}", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"Profile Creation - {profile_data['name']}", False, f"Exception: {str(e)}")
            return False
            
    def generate_diet(self, user_id: str, profile_name: str) -> Dict:
        """Generate diet for user"""
        try:
            # Use query parameter format
            response = requests.post(
                f"{self.base_url}/diet/generate?user_id={user_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                diet = response.json()
                self.log_test(f"Diet Generation - {profile_name}", True, f"Generated {len(diet.get('meals', []))} meals")
                return diet
            else:
                self.log_test(f"Diet Generation - {profile_name}", False, f"HTTP {response.status_code}: {response.text}")
                return {}
                
        except Exception as e:
            self.log_test(f"Diet Generation - {profile_name}", False, f"Exception: {str(e)}")
            return {}
            
    def validate_diet_preferences(self, diet: Dict, preferred_foods: List[str], profile_name: str) -> bool:
        """Validate that preferred foods appear in diet"""
        if not diet or not diet.get("meals"):
            return False
            
        # Get all food names from diet
        all_foods = []
        for meal in diet.get("meals", []):
            for food in meal.get("foods", []):
                food_name = food.get("name", "").lower()
                food_key = food.get("key", "").lower()
                all_foods.extend([food_name, food_key])
                
        # Check each preferred food
        found_preferences = []
        for pref in preferred_foods:
            pref_lower = pref.lower()
            # Map preferences to common food names
            food_mappings = {
                "arroz": ["arroz", "rice"],
                "frango": ["frango", "chicken", "peito"],
                "ovo": ["ovo", "egg"],
                "banana": ["banana"],
                "batata_doce": ["batata", "potato", "doce"],
                "peixe": ["peixe", "fish", "tilapia", "salmao"],
                "abacate": ["abacate", "avocado"],
                "aveia": ["aveia", "oat"],
                "queijo": ["queijo", "cheese"],
                "feijao": ["feijao", "bean"],
                "castanhas": ["castanha", "nut", "amendoa", "noz"],
                "legumes": ["legume", "vegetal", "brocoli", "couve"]
            }
            
            search_terms = food_mappings.get(pref_lower, [pref_lower])
            found = any(term in food_text for food_text in all_foods for term in search_terms)
            
            if found:
                found_preferences.append(pref)
                
        success = len(found_preferences) >= len(preferred_foods) * 0.7  # At least 70% of preferences
        details = f"Found {len(found_preferences)}/{len(preferred_foods)} preferences: {found_preferences}"
        
        self.log_test(f"Diet Preferences - {profile_name}", success, details)
        return success
        
    def validate_diet_restrictions(self, diet: Dict, restrictions: List[str], profile_name: str) -> bool:
        """Validate that restricted foods DO NOT appear in diet - CRITICAL"""
        if not diet or not diet.get("meals"):
            return False
            
        # Get all food names from diet
        all_foods = []
        for meal in diet.get("meals", []):
            for food in meal.get("foods", []):
                food_name = food.get("name", "").lower()
                food_key = food.get("key", "").lower()
                all_foods.extend([food_name, food_key])
                
        # Check each restriction
        violations = []
        for restriction in restrictions:
            restriction_lower = restriction.lower()
            
            # Define forbidden foods for each restriction
            forbidden_mappings = {
                "vegetariano": ["frango", "chicken", "carne", "beef", "peixe", "fish", "tilapia", "salmao", "bacon", "presunto"],
                "sem_lactose": ["leite", "milk", "queijo", "cheese", "iogurte", "yogurt", "whey", "requeijao"],
                "sem_gluten": ["pao", "bread", "macarrao", "pasta", "aveia", "oat", "trigo", "wheat"],
                "diabetico": ["acucar", "sugar", "tapioca", "mel", "honey", "doce", "sweet"]
            }
            
            forbidden_foods = forbidden_mappings.get(restriction_lower, [])
            
            for forbidden in forbidden_foods:
                found_violations = [food for food in all_foods if forbidden in food]
                if found_violations:
                    violations.extend([(restriction, forbidden, found_violations)])
                    
        success = len(violations) == 0
        if violations:
            details = f"CRITICAL VIOLATIONS: {violations}"
        else:
            details = f"All restrictions respected: {restrictions}"
            
        self.log_test(f"Diet Restrictions - {profile_name}", success, details)
        return success
        
    def validate_diet_calories(self, diet: Dict, expected_calories: float, profile_name: str) -> bool:
        """Validate diet calories match target"""
        if not diet:
            return False
            
        computed_calories = diet.get("computed_calories", 0)
        calorie_diff = abs(computed_calories - expected_calories)
        calorie_diff_pct = (calorie_diff / expected_calories) * 100 if expected_calories > 0 else 100
        
        # Allow 15% tolerance as per system specification
        success = calorie_diff_pct <= 15
        details = f"Computed: {computed_calories}kcal, Expected: {expected_calories:.0f}kcal, Diff: {calorie_diff:.0f}kcal ({calorie_diff_pct:.1f}%)"
        
        self.log_test(f"Diet Calories - {profile_name}", success, details)
        return success
        
    def validate_meal_count(self, diet: Dict, expected_count: int, profile_name: str) -> bool:
        """Validate number of meals"""
        if not diet:
            return False
            
        actual_count = len(diet.get("meals", []))
        success = actual_count == expected_count
        details = f"Meals: {actual_count} (expected {expected_count})"
        
        self.log_test(f"Meal Count - {profile_name}", success, details)
        return success
        
    def run_profile_test(self, profile_data: Dict, expected_validations: Dict) -> bool:
        """Run complete test for a profile"""
        print(f"\n🔍 TESTING PROFILE: {profile_data['name']}")
        print("=" * 60)
        
        # Step 1: Create profile
        if not self.create_profile(profile_data):
            return False
            
        # Step 2: Generate diet
        diet = self.generate_diet(profile_data["id"], profile_data["name"])
        if not diet:
            return False
            
        # Step 3: Validate preferences
        prefs_ok = self.validate_diet_preferences(
            diet, 
            profile_data.get("preferred_foods", []), 
            profile_data["name"]
        )
        
        # Step 4: Validate restrictions (CRITICAL)
        restrictions_ok = self.validate_diet_restrictions(
            diet,
            profile_data.get("dietary_restrictions", []),
            profile_data["name"]
        )
        
        # Step 5: Validate calories
        expected = self.calculate_expected_calories(profile_data)
        calories_ok = self.validate_diet_calories(
            diet,
            expected["target_calories"],
            profile_data["name"]
        )
        
        # Step 6: Validate meal count
        meal_count_ok = self.validate_meal_count(
            diet,
            profile_data.get("meal_count", 6),
            profile_data["name"]
        )
        
        # Overall success
        overall_success = prefs_ok and restrictions_ok and calories_ok and meal_count_ok
        
        if overall_success:
            print(f"✅ PROFILE {profile_data['name']} - ALL TESTS PASSED")
        else:
            print(f"❌ PROFILE {profile_data['name']} - SOME TESTS FAILED")
            
        return overall_success
        
    def run_comprehensive_audit(self):
        """Run the complete audit with all 6 profiles"""
        print("🎯 AUDITORIA COMPLETA - MÚLTIPLOS PERFIS COM FOCO EM DIETA")
        print("=" * 80)
        
        # PERFIL 1 - Homem Cutting com preferência por ARROZ e FRANGO
        profile1 = {
            "id": "audit-1-cutting-arroz",
            "user_id": "audit-1-cutting-arroz",
            "name": "João Cutting Arroz",
            "email": "joao_arroz@audit.com",
            "age": 28,
            "sex": "masculino",
            "height": 180,
            "weight": 90,
            "target_weight": 80,
            "goal": "cutting",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "dietary_restrictions": [],
            "preferred_foods": ["arroz", "frango", "ovo", "banana"],
            "meal_count": 5
        }
        
        # PERFIL 2 - Mulher Bulking com preferência por BATATA DOCE e PEIXE
        profile2 = {
            "id": "audit-2-bulking-batata",
            "user_id": "audit-2-bulking-batata", 
            "name": "Maria Bulking Batata",
            "email": "maria_batata@audit.com",
            "age": 25,
            "sex": "feminino",
            "height": 165,
            "weight": 55,
            "target_weight": 62,
            "goal": "bulking",
            "training_level": "avancado",
            "weekly_training_frequency": 5,
            "available_time_per_session": 60,
            "dietary_restrictions": [],
            "preferred_foods": ["batata_doce", "peixe", "abacate", "aveia"],
            "meal_count": 6
        }
        
        # PERFIL 3 - Homem Manutenção VEGETARIANO
        profile3 = {
            "id": "audit-3-vegetariano",
            "user_id": "audit-3-vegetariano",
            "name": "Pedro Vegetariano", 
            "email": "pedro_veg@audit.com",
            "age": 32,
            "sex": "masculino",
            "height": 175,
            "weight": 75,
            "target_weight": 75,
            "goal": "manutencao",
            "training_level": "iniciante",
            "weekly_training_frequency": 3,
            "available_time_per_session": 60,
            "dietary_restrictions": ["vegetariano"],
            "preferred_foods": ["ovo", "queijo", "feijao", "arroz"],
            "meal_count": 5
        }
        
        # PERFIL 4 - Mulher Cutting SEM LACTOSE
        profile4 = {
            "id": "audit-4-sem-lactose",
            "user_id": "audit-4-sem-lactose",
            "name": "Ana Sem Lactose",
            "email": "ana_lactose@audit.com", 
            "age": 30,
            "sex": "feminino",
            "height": 160,
            "weight": 70,
            "target_weight": 60,
            "goal": "cutting",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "dietary_restrictions": ["sem_lactose"],
            "preferred_foods": ["frango", "arroz", "banana", "castanhas"],
            "meal_count": 5
        }
        
        # PERFIL 5 - Homem Bulking SEM GLÚTEN com MACARRÃO (contradição!)
        profile5 = {
            "id": "audit-5-sem-gluten",
            "user_id": "audit-5-sem-gluten",
            "name": "Carlos Sem Gluten",
            "email": "carlos_gluten@audit.com",
            "age": 27,
            "sex": "masculino", 
            "height": 185,
            "weight": 80,
            "target_weight": 90,
            "goal": "bulking",
            "training_level": "avancado",
            "weekly_training_frequency": 6,
            "available_time_per_session": 60,
            "dietary_restrictions": ["sem_gluten"],
            "preferred_foods": ["macarrao", "frango", "arroz", "ovo"],  # macarrao should NOT appear due to restriction
            "meal_count": 6
        }
        
        # PERFIL 6 - Mulher DIABÉTICA com preferências específicas
        profile6 = {
            "id": "audit-6-diabetica",
            "user_id": "audit-6-diabetica",
            "name": "Lucia Diabetica",
            "email": "lucia_diab@audit.com",
            "age": 45,
            "sex": "feminino",
            "height": 158,
            "weight": 65,
            "target_weight": 58,
            "goal": "cutting",
            "training_level": "novato",
            "weekly_training_frequency": 2,
            "available_time_per_session": 60,
            "dietary_restrictions": ["diabetico"],
            "preferred_foods": ["peixe", "ovo", "legumes", "castanhas"],
            "meal_count": 4
        }
        
        # Run tests for all profiles
        profiles = [profile1, profile2, profile3, profile4, profile5, profile6]
        successful_profiles = 0
        
        for profile in profiles:
            if self.run_profile_test(profile, {}):
                successful_profiles += 1
                
        # Final summary
        print("\n" + "=" * 80)
        print("🏆 AUDITORIA FINAL - RESULTADOS")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        
        print(f"📊 ESTATÍSTICAS GERAIS:")
        print(f"   • Perfis testados: {len(profiles)}")
        print(f"   • Perfis aprovados: {successful_profiles}/{len(profiles)}")
        print(f"   • Testes individuais: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
        
        # Show critical failures
        critical_failures = [r for r in self.test_results if not r["success"] and "Restrictions" in r["test"]]
        if critical_failures:
            print(f"\n❌ FALHAS CRÍTICAS (Restrições Alimentares):")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['details']}")
                
        # Show preference failures  
        pref_failures = [r for r in self.test_results if not r["success"] and "Preferences" in r["test"]]
        if pref_failures:
            print(f"\n⚠️  FALHAS DE PREFERÊNCIAS:")
            for failure in pref_failures:
                print(f"   • {failure['test']}: {failure['details']}")
                
        return successful_profiles == len(profiles)

def main():
    """Main test execution"""
    tester = DietAuditTester()
    
    try:
        success = tester.run_comprehensive_audit()
        
        if success:
            print(f"\n🎉 AUDITORIA COMPLETA - 100% SUCESSO!")
            print("Todos os perfis passaram em todos os testes.")
            sys.exit(0)
        else:
            print(f"\n⚠️  AUDITORIA COMPLETA - PROBLEMAS ENCONTRADOS!")
            print("Alguns perfis falharam nos testes. Verifique os detalhes acima.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERRO INESPERADO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()