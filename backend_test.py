#!/usr/bin/env python3
"""
Backend Testing Suite - Dietary Restrictions Validation
Testing dietary restrictions compliance for LAF app
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Base URL from environment
BASE_URL = "https://workoutcycler.preview.emergentagent.com/api"

class DietaryRestrictionsTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def create_profile(self, profile_data: Dict) -> Dict:
        """Create user profile"""
        try:
            response = self.session.post(
                f"{self.base_url}/user/profile",
                json=profile_data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Profile creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating profile: {e}")
            return None
    
    def generate_diet(self, user_id: str) -> Dict:
        """Generate diet for user"""
        try:
            response = self.session.post(
                f"{self.base_url}/diet/generate?user_id={user_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Diet generation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating diet: {e}")
            return None
    
    def get_diet(self, user_id: str) -> Dict:
        """Get user diet"""
        try:
            response = self.session.get(
                f"{self.base_url}/diet/{user_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Diet retrieval failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error retrieving diet: {e}")
            return None
    
    def extract_all_foods(self, diet: Dict) -> List[str]:
        """Extract all food names from diet"""
        foods = []
        if not diet or "meals" not in diet:
            return foods
            
        for meal in diet["meals"]:
            if "foods" in meal:
                for food in meal["foods"]:
                    food_name = food.get("name", "").lower()
                    food_key = food.get("key", "").lower()
                    foods.append(f"{food_name} ({food_key})")
        
        return foods
    
    def check_gluten_free(self, foods: List[str]) -> Dict:
        """Check if diet is gluten-free"""
        forbidden_foods = [
            "pão", "pao", "bread", "pao_integral", "pao_forma",
            "aveia", "oat", "oats",
            "macarrão", "macarrao", "macarrao_integral", "pasta",
            "seitan", "trigo", "wheat", "cevada", "centeio"
        ]
        
        violations = []
        for food in foods:
            for forbidden in forbidden_foods:
                if forbidden in food.lower():
                    violations.append(food)
                    break
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "forbidden_items": forbidden_foods
        }
    
    def check_vegetarian(self, foods: List[str]) -> Dict:
        """Check if diet is vegetarian"""
        forbidden_foods = [
            "frango", "chicken", "carne", "beef", "peixe", "fish",
            "atum", "tuna", "tilapia", "peru", "turkey", "porco", "pork",
            "salmão", "salmon", "bacalhau", "cod", "camarão", "shrimp"
        ]
        
        violations = []
        for food in foods:
            for forbidden in forbidden_foods:
                if forbidden in food.lower():
                    violations.append(food)
                    break
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "forbidden_items": forbidden_foods
        }
    
    def check_lactose_free(self, foods: List[str]) -> Dict:
        """Check if diet is lactose-free"""
        forbidden_foods = [
            "leite", "milk", "queijo", "cheese", "cottage",
            "iogurte", "yogurt", "whey", "manteiga", "butter",
            "creme", "cream", "requeijão"
        ]
        
        violations = []
        for food in foods:
            for forbidden in forbidden_foods:
                if forbidden in food.lower():
                    violations.append(food)
                    break
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "forbidden_items": forbidden_foods
        }
    
    def test_gluten_free_profile(self):
        """Test gluten-free dietary restriction"""
        print("\n🧪 TESTE 1 - SEM GLÚTEN")
        print("=" * 50)
        
        profile_data = {
            "id": "fix-test-sem-gluten",
            "user_id": "fix-test-sem-gluten",
            "name": "Fix Sem Gluten",
            "email": "fix_gluten@test.com",
            "age": 30,
            "sex": "masculino",
            "height": 180,
            "weight": 80,
            "target_weight": 85,
            "goal": "bulking",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "training_days": [1, 3, 5, 6],
            "dietary_restrictions": ["sem_gluten"],
            "food_preferences": ["arroz", "frango", "ovo"],
            "meal_count": 5
        }
        
        # Create profile
        profile = self.create_profile(profile_data)
        if not profile:
            self.log_result("Gluten-Free Profile Creation", False, "Failed to create profile")
            return
        
        self.log_result("Gluten-Free Profile Creation", True, f"Profile created with ID: {profile.get('id')}")
        
        # Generate diet
        diet = self.generate_diet(profile_data["id"])
        if not diet:
            self.log_result("Gluten-Free Diet Generation", False, "Failed to generate diet")
            return
        
        self.log_result("Gluten-Free Diet Generation", True, "Diet generated successfully")
        
        # Get diet
        diet_data = self.get_diet(profile_data["id"])
        if not diet_data:
            self.log_result("Gluten-Free Diet Retrieval", False, "Failed to retrieve diet")
            return
        
        # Extract foods and check compliance
        foods = self.extract_all_foods(diet_data)
        compliance = self.check_gluten_free(foods)
        
        print(f"\n📋 ALIMENTOS NA DIETA ({len(foods)} itens):")
        for food in foods:
            print(f"  - {food}")
        
        if compliance["compliant"]:
            self.log_result("Gluten-Free Compliance", True, "✅ ZERO alimentos com glúten encontrados")
        else:
            self.log_result(
                "Gluten-Free Compliance", 
                False, 
                f"❌ VIOLAÇÃO CRÍTICA: {len(compliance['violations'])} alimentos com glúten encontrados",
                {"violations": compliance["violations"]}
            )
        
        # Check for required foods
        has_rice = any("arroz" in food.lower() or "rice" in food.lower() for food in foods)
        has_tapioca = any("tapioca" in food.lower() for food in foods)
        
        if has_rice:
            self.log_result("Gluten-Free Rice Check", True, "✅ Arroz encontrado como carboidrato principal")
        else:
            self.log_result("Gluten-Free Rice Check", False, "❌ Arroz não encontrado na dieta")
        
        if has_tapioca:
            print("✅ Tapioca pode aparecer no café da manhã")
    
    def test_vegetarian_profile(self):
        """Test vegetarian dietary restriction"""
        print("\n🧪 TESTE 2 - VEGETARIANO")
        print("=" * 50)
        
        profile_data = {
            "id": "fix-test-vegetariano",
            "user_id": "fix-test-vegetariano",
            "name": "Fix Vegetariano",
            "email": "fix_veg@test.com",
            "age": 28,
            "sex": "feminino",
            "height": 165,
            "weight": 60,
            "target_weight": 60,
            "goal": "manutencao",
            "training_level": "iniciante",
            "weekly_training_frequency": 3,
            "training_days": [1, 3, 5],
            "dietary_restrictions": ["vegetariano"],
            "preferred_foods": ["ovo", "queijo", "arroz", "feijao"],
            "meal_count": 5
        }
        
        # Create profile
        profile = self.create_profile(profile_data)
        if not profile:
            self.log_result("Vegetarian Profile Creation", False, "Failed to create profile")
            return
        
        self.log_result("Vegetarian Profile Creation", True, f"Profile created with ID: {profile.get('id')}")
        
        # Generate diet
        diet = self.generate_diet(profile_data["id"])
        if not diet:
            self.log_result("Vegetarian Diet Generation", False, "Failed to generate diet")
            return
        
        self.log_result("Vegetarian Diet Generation", True, "Diet generated successfully")
        
        # Get diet
        diet_data = self.get_diet(profile_data["id"])
        if not diet_data:
            self.log_result("Vegetarian Diet Retrieval", False, "Failed to retrieve diet")
            return
        
        # Extract foods and check compliance
        foods = self.extract_all_foods(diet_data)
        compliance = self.check_vegetarian(foods)
        
        print(f"\n📋 ALIMENTOS NA DIETA ({len(foods)} itens):")
        for food in foods:
            print(f"  - {food}")
        
        if compliance["compliant"]:
            self.log_result("Vegetarian Compliance", True, "✅ ZERO carnes/peixes encontrados")
        else:
            self.log_result(
                "Vegetarian Compliance", 
                False, 
                f"❌ VIOLAÇÃO CRÍTICA: {len(compliance['violations'])} produtos de origem animal encontrados",
                {"violations": compliance["violations"]}
            )
        
        # Check for required foods
        has_eggs = any("ovo" in food.lower() or "egg" in food.lower() for food in foods)
        has_cheese = any("queijo" in food.lower() or "cottage" in food.lower() or "cheese" in food.lower() for food in foods)
        has_beans = any("feijão" in food.lower() or "feijao" in food.lower() or "bean" in food.lower() for food in foods)
        
        if has_eggs:
            self.log_result("Vegetarian Eggs Check", True, "✅ Ovos encontrados como proteína")
        
        if has_cheese:
            self.log_result("Vegetarian Cheese Check", True, "✅ Queijo/Cottage encontrado")
        
        if has_beans:
            self.log_result("Vegetarian Beans Check", True, "✅ Feijão encontrado como proteína vegetal")
    
    def test_lactose_free_profile(self):
        """Test lactose-free dietary restriction"""
        print("\n🧪 TESTE 3 - SEM LACTOSE")
        print("=" * 50)
        
        profile_data = {
            "id": "fix-test-sem-lactose",
            "user_id": "fix-test-sem-lactose",
            "name": "Fix Sem Lactose",
            "email": "fix_lactose@test.com",
            "age": 35,
            "sex": "feminino",
            "height": 170,
            "weight": 65,
            "target_weight": 60,
            "goal": "cutting",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "training_days": [0, 2, 4, 6],
            "dietary_restrictions": ["sem_lactose"],
            "preferred_foods": ["frango", "arroz", "banana"],
            "meal_count": 5
        }
        
        # Create profile
        profile = self.create_profile(profile_data)
        if not profile:
            self.log_result("Lactose-Free Profile Creation", False, "Failed to create profile")
            return
        
        self.log_result("Lactose-Free Profile Creation", True, f"Profile created with ID: {profile.get('id')}")
        
        # Generate diet
        diet = self.generate_diet(profile_data["id"])
        if not diet:
            self.log_result("Lactose-Free Diet Generation", False, "Failed to generate diet")
            return
        
        self.log_result("Lactose-Free Diet Generation", True, "Diet generated successfully")
        
        # Get diet
        diet_data = self.get_diet(profile_data["id"])
        if not diet_data:
            self.log_result("Lactose-Free Diet Retrieval", False, "Failed to retrieve diet")
            return
        
        # Extract foods and check compliance
        foods = self.extract_all_foods(diet_data)
        compliance = self.check_lactose_free(foods)
        
        print(f"\n📋 ALIMENTOS NA DIETA ({len(foods)} itens):")
        for food in foods:
            print(f"  - {food}")
        
        if compliance["compliant"]:
            self.log_result("Lactose-Free Compliance", True, "✅ ZERO laticínios encontrados")
        else:
            self.log_result(
                "Lactose-Free Compliance", 
                False, 
                f"❌ VIOLAÇÃO CRÍTICA: {len(compliance['violations'])} produtos com lactose encontrados",
                {"violations": compliance["violations"]}
            )
        
        # Check for required foods
        has_chicken = any("frango" in food.lower() or "chicken" in food.lower() for food in foods)
        has_rice = any("arroz" in food.lower() or "rice" in food.lower() for food in foods)
        
        if has_chicken:
            self.log_result("Lactose-Free Chicken Check", True, "✅ Frango encontrado como proteína")
        
        if has_rice:
            self.log_result("Lactose-Free Rice Check", True, "✅ Arroz encontrado como carboidrato")
    
    def run_all_tests(self):
        """Run all dietary restriction tests"""
        print("🔍 VERIFICAÇÃO DE CORREÇÕES - Restrições Alimentares")
        print("=" * 60)
        print(f"BASE URL: {self.base_url}")
        print()
        
        # Test each dietary restriction
        self.test_gluten_free_profile()
        self.test_vegetarian_profile()
        self.test_lactose_free_profile()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de testes: {total_tests}")
        print(f"✅ Aprovados: {passed_tests}")
        print(f"❌ Falharam: {failed_tests}")
        print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical failures
        critical_failures = [r for r in self.test_results if not r["success"] and "Compliance" in r["test"]]
        
        if critical_failures:
            print(f"\n🚨 FALHAS CRÍTICAS ENCONTRADAS ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"  ❌ {failure['test']}: {failure['message']}")
                if failure.get("details", {}).get("violations"):
                    for violation in failure["details"]["violations"]:
                        print(f"     - {violation}")
        else:
            print("\n✅ NENHUMA FALHA CRÍTICA - Todas as restrições alimentares foram respeitadas!")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = DietaryRestrictionsTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("\n💥 ALGUNS TESTES FALHARAM!")
        sys.exit(1)

if __name__ == "__main__":
    main()