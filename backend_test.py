#!/usr/bin/env python3
"""
TESTE ABRANGENTE - Múltiplos Perfis de Usuário
Testa TODAS as funcionalidades para cada perfil conforme especificação.
"""

import requests
import json
import uuid
from typing import Dict, List, Any

# Base URL conforme especificação
BASE_URL = "https://workoutcycler.preview.emergentagent.com/api"

class LAFTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_users = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "data": data
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    def create_profile(self, profile_data: Dict) -> Dict:
        """Cria perfil de usuário e retorna dados completos"""
        try:
            # Gera ID único para o usuário
            user_id = str(uuid.uuid4())
            profile_data["id"] = user_id
            
            response = self.session.post(
                f"{self.base_url}/user/profile",
                json=profile_data,
                timeout=30
            )
            
            if response.status_code == 200:
                profile = response.json()
                self.created_users.append(user_id)
                
                # Valida TDEE e cálculos
                tdee = profile.get("tdee", 0)
                target_calories = profile.get("target_calories", 0)
                macros = profile.get("macros", {})
                
                self.log_test(
                    f"Criar Perfil - {profile_data['name']}", 
                    True,
                    f"TDEE: {tdee}kcal, Target: {target_calories}kcal, P:{macros.get('protein', 0)}g C:{macros.get('carbs', 0)}g F:{macros.get('fat', 0)}g"
                )
                return profile
            else:
                self.log_test(
                    f"Criar Perfil - {profile_data['name']}", 
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                f"Criar Perfil - {profile_data['name']}", 
                False,
                f"Erro: {str(e)}"
            )
            return None
    
    def generate_diet(self, user_id: str, user_name: str) -> Dict:
        """Gera dieta para o usuário"""
        try:
            response = self.session.post(
                f"{self.base_url}/diet/generate",
                params={"user_id": user_id},
                timeout=30
            )
            
            if response.status_code == 200:
                diet = response.json()
                meals = diet.get("meals", [])
                computed_calories = diet.get("computed_calories", 0)
                computed_macros = diet.get("computed_macros", {})
                
                self.log_test(
                    f"Gerar Dieta - {user_name}",
                    True,
                    f"{len(meals)} refeições, {computed_calories}kcal, P:{computed_macros.get('protein', 0)}g C:{computed_macros.get('carbs', 0)}g F:{computed_macros.get('fat', 0)}g"
                )
                return diet
            else:
                self.log_test(
                    f"Gerar Dieta - {user_name}",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                f"Gerar Dieta - {user_name}",
                False,
                f"Erro: {str(e)}"
            )
            return None
    
    def generate_workout(self, user_id: str, user_name: str) -> Dict:
        """Gera treino para o usuário"""
        try:
            response = self.session.post(
                f"{self.base_url}/workout/generate",
                params={"user_id": user_id},
                timeout=30
            )
            
            if response.status_code == 200:
                workout = response.json()
                workouts = workout.get("workouts", [])
                
                # Conta exercícios e verifica séries
                total_exercises = 0
                max_sets = 0
                
                for day in workouts:
                    exercises = day.get("exercises", [])
                    total_exercises += len(exercises)
                    
                    for exercise in exercises:
                        sets = exercise.get("sets", 0)
                        if sets > max_sets:
                            max_sets = sets
                
                self.log_test(
                    f"Gerar Treino - {user_name}",
                    True,
                    f"{len(workouts)} dias, {total_exercises} exercícios total, max {max_sets} séries"
                )
                return workout
            else:
                self.log_test(
                    f"Gerar Treino - {user_name}",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                f"Gerar Treino - {user_name}",
                False,
                f"Erro: {str(e)}"
            )
            return None
    
    def validate_dietary_restrictions(self, diet: Dict, restrictions: List[str], user_name: str):
        """Valida se restrições alimentares são respeitadas"""
        if not diet or not restrictions:
            return
            
        meals = diet.get("meals", [])
        violations = []
        
        for meal in meals:
            foods = meal.get("foods", [])
            for food in foods:
                food_name = food.get("name", "").lower()
                food_key = food.get("key", "").lower()
                
                # Verifica restrições específicas
                for restriction in restrictions:
                    if restriction == "vegetariano":
                        # Vegetariano não pode ter carne ou peixe
                        meat_keywords = ["frango", "carne", "peixe", "salmao", "atum", "beef", "chicken", "fish"]
                        if any(keyword in food_name or keyword in food_key for keyword in meat_keywords):
                            violations.append(f"Vegetariano com {food_name}")
                    
                    elif restriction == "sem_lactose":
                        # Sem lactose não pode ter leite ou queijo
                        lactose_keywords = ["leite", "queijo", "iogurte", "milk", "cheese", "yogurt"]
                        if any(keyword in food_name or keyword in food_key for keyword in lactose_keywords):
                            violations.append(f"Sem lactose com {food_name}")
                    
                    elif restriction == "sem_gluten":
                        # Sem glúten não pode ter trigo ou aveia
                        gluten_keywords = ["trigo", "aveia", "pao", "macarrao", "wheat", "oats", "bread"]
                        if any(keyword in food_name or keyword in food_key for keyword in gluten_keywords):
                            violations.append(f"Sem glúten com {food_name}")
                    
                    elif restriction == "diabetico":
                        # Diabético não pode ter açúcar ou tapioca
                        sugar_keywords = ["acucar", "tapioca", "mel", "sugar", "honey"]
                        if any(keyword in food_name or keyword in food_key for keyword in sugar_keywords):
                            violations.append(f"Diabético com {food_name}")
        
        if violations:
            self.log_test(
                f"Validar Restrições - {user_name}",
                False,
                f"Violações encontradas: {', '.join(violations)}"
            )
        else:
            self.log_test(
                f"Validar Restrições - {user_name}",
                True,
                f"Todas as restrições {restrictions} respeitadas"
            )
    
    def validate_workout_constraints(self, workout: Dict, expected_frequency: int, user_name: str):
        """Valida restrições do treino"""
        if not workout:
            return
            
        workouts = workout.get("workouts", [])
        
        # Verifica frequência
        frequency_ok = len(workouts) == expected_frequency
        
        # Verifica séries ≤ 4
        max_sets = 0
        sets_violations = []
        
        for day in workouts:
            exercises = day.get("exercises", [])
            for exercise in exercises:
                sets = exercise.get("sets", 0)
                if sets > max_sets:
                    max_sets = sets
                if sets > 4:
                    sets_violations.append(f"{exercise.get('name', 'Exercício')} com {sets} séries")
        
        # Log resultados
        if frequency_ok and not sets_violations:
            self.log_test(
                f"Validar Treino - {user_name}",
                True,
                f"Frequência {len(workouts)}/{expected_frequency} ✓, Max séries: {max_sets} ✓"
            )
        else:
            issues = []
            if not frequency_ok:
                issues.append(f"Frequência {len(workouts)}/{expected_frequency}")
            if sets_violations:
                issues.append(f"Séries > 4: {', '.join(sets_violations)}")
            
            self.log_test(
                f"Validar Treino - {user_name}",
                False,
                f"Problemas: {'; '.join(issues)}"
            )
    
    def validate_calories_by_goal(self, profile: Dict, diet: Dict, user_name: str):
        """Valida se calorias estão coerentes com objetivo"""
        if not profile or not diet:
            return
            
        goal = profile.get("goal", "")
        tdee = profile.get("tdee", 0)
        target_calories = profile.get("target_calories", 0)
        computed_calories = diet.get("computed_calories", 0)
        
        # Verifica lógica de calorias por objetivo
        if goal == "cutting":
            expected_below_tdee = target_calories < tdee
        elif goal == "bulking":
            expected_above_tdee = target_calories > tdee
        else:  # manutenção
            expected_equal_tdee = abs(target_calories - tdee) < 100
        
        # Verifica se dieta gerada está próxima do target
        calorie_diff = abs(computed_calories - target_calories)
        calorie_tolerance = target_calories * 0.15  # 15% de tolerância
        
        calories_ok = calorie_diff <= calorie_tolerance
        
        if goal == "cutting":
            goal_ok = expected_below_tdee
            goal_msg = f"Cutting: Target {target_calories} < TDEE {tdee}"
        elif goal == "bulking":
            goal_ok = expected_above_tdee
            goal_msg = f"Bulking: Target {target_calories} > TDEE {tdee}"
        else:
            goal_ok = expected_equal_tdee
            goal_msg = f"Manutenção: Target {target_calories} ≈ TDEE {tdee}"
        
        if goal_ok and calories_ok:
            self.log_test(
                f"Validar Calorias - {user_name}",
                True,
                f"{goal_msg} ✓, Dieta: {computed_calories}kcal (Δ{calorie_diff}kcal)"
            )
        else:
            issues = []
            if not goal_ok:
                issues.append(f"Lógica objetivo incorreta: {goal_msg}")
            if not calories_ok:
                issues.append(f"Dieta muito diferente: {computed_calories} vs {target_calories} (Δ{calorie_diff})")
            
            self.log_test(
                f"Validar Calorias - {user_name}",
                False,
                f"Problemas: {'; '.join(issues)}"
            )
    
    def test_complete_profile(self, profile_data: Dict):
        """Testa perfil completo: criação + dieta + treino + validações"""
        user_name = profile_data["name"]
        print(f"\n🔍 TESTANDO PERFIL: {user_name}")
        print("=" * 60)
        
        # 1. Criar perfil
        profile = self.create_profile(profile_data)
        if not profile:
            return
        
        user_id = profile["id"]
        
        # 2. Gerar dieta
        diet = self.generate_diet(user_id, user_name)
        
        # 3. Gerar treino
        workout = self.generate_workout(user_id, user_name)
        
        # 4. Validar restrições alimentares
        if diet and profile_data.get("dietary_restrictions"):
            self.validate_dietary_restrictions(
                diet, 
                profile_data["dietary_restrictions"], 
                user_name
            )
        
        # 5. Validar treino
        if workout:
            self.validate_workout_constraints(
                workout,
                profile_data["weekly_training_frequency"],
                user_name
            )
        
        # 6. Validar calorias por objetivo
        if profile and diet:
            self.validate_calories_by_goal(profile, diet, user_name)
    
    def run_comprehensive_test(self):
        """Executa teste abrangente com todos os 6 perfis"""
        print("🚀 INICIANDO TESTE ABRANGENTE - MÚLTIPLOS PERFIS DE USUÁRIO")
        print("=" * 80)
        
        # PERFIL 1 - Homem Cutting Iniciante (Leve)
        profile1 = {
            "name": "João Silva",
            "email": "joao_cutting@test.com",
            "age": 25,
            "sex": "masculino",
            "height": 170,
            "weight": 65,
            "target_weight": 60,
            "goal": "cutting",
            "training_level": "iniciante",
            "weekly_training_frequency": 3,
            "available_time_per_session": 45,
            "dietary_restrictions": [],
            "food_preferences": ["frango", "arroz", "ovo"]
        }
        
        # PERFIL 2 - Mulher Bulking Avançada (Pesada)
        profile2 = {
            "name": "Maria Santos",
            "email": "maria_bulking@test.com",
            "age": 30,
            "sex": "feminino",
            "height": 165,
            "weight": 70,
            "target_weight": 75,
            "goal": "bulking",
            "training_level": "avancado",
            "weekly_training_frequency": 6,
            "available_time_per_session": 90,
            "dietary_restrictions": ["sem_lactose"],
            "food_preferences": ["peixe", "batata_doce", "banana"]
        }
        
        # PERFIL 3 - Homem Manutenção Intermediário (Alto)
        profile3 = {
            "name": "Pedro Costa",
            "email": "pedro_manutencao@test.com",
            "age": 35,
            "sex": "masculino",
            "height": 190,
            "weight": 95,
            "target_weight": 95,
            "goal": "manutencao",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "dietary_restrictions": ["sem_gluten"],
            "food_preferences": ["carne", "arroz", "feijao"]
        }
        
        # PERFIL 4 - Mulher Cutting Novata (Vegetariana)
        profile4 = {
            "name": "Ana Oliveira",
            "email": "ana_vegetariana@test.com",
            "age": 22,
            "sex": "feminino",
            "height": 158,
            "weight": 58,
            "target_weight": 52,
            "goal": "cutting",
            "training_level": "novato",
            "weekly_training_frequency": 2,
            "available_time_per_session": 30,
            "dietary_restrictions": ["vegetariano"],
            "food_preferences": ["ovo", "queijo", "aveia"]
        }
        
        # PERFIL 5 - Homem Bulking Avançado (Pesado, Alto Volume)
        profile5 = {
            "name": "Carlos Ferreira",
            "email": "carlos_bulking@test.com",
            "age": 28,
            "sex": "masculino",
            "height": 185,
            "weight": 100,
            "target_weight": 110,
            "goal": "bulking",
            "training_level": "avancado",
            "weekly_training_frequency": 5,
            "available_time_per_session": 75,
            "dietary_restrictions": [],
            "food_preferences": ["frango", "arroz", "batata_doce", "ovo"]
        }
        
        # PERFIL 6 - Mulher Manutenção Iniciante (Diabética)
        profile6 = {
            "name": "Lucia Mendes",
            "email": "lucia_diabetica@test.com",
            "age": 45,
            "sex": "feminino",
            "height": 160,
            "weight": 68,
            "target_weight": 65,
            "goal": "manutencao",
            "training_level": "iniciante",
            "weekly_training_frequency": 3,
            "available_time_per_session": 45,
            "dietary_restrictions": ["diabetico"],
            "food_preferences": ["peixe", "legumes", "ovo"]
        }
        
        # Testa todos os perfis
        profiles = [profile1, profile2, profile3, profile4, profile5, profile6]
        
        for profile in profiles:
            self.test_complete_profile(profile)
        
        # Relatório final
        self.print_final_report()
    
    def print_final_report(self):
        """Imprime relatório final dos testes"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL - TESTE ABRANGENTE")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de testes: {total_tests}")
        print(f"✅ Sucessos: {passed_tests}")
        print(f"❌ Falhas: {failed_tests}")
        print(f"📈 Taxa de sucesso: {(passed_tests/total_tests*100):.1f}%")
        
        # Lista falhas
        if failed_tests > 0:
            print(f"\n❌ TESTES QUE FALHARAM ({failed_tests}):")
            print("-" * 50)
            for result in self.test_results:
                if not result["success"]:
                    print(f"• {result['test']}: {result['details']}")
        
        # Critérios de sucesso
        print(f"\n🎯 CRITÉRIOS DE SUCESSO:")
        print("-" * 30)
        
        # Conta sucessos por categoria
        profiles_created = sum(1 for r in self.test_results if "Criar Perfil" in r["test"] and r["success"])
        diets_generated = sum(1 for r in self.test_results if "Gerar Dieta" in r["test"] and r["success"])
        workouts_generated = sum(1 for r in self.test_results if "Gerar Treino" in r["test"] and r["success"])
        restrictions_ok = sum(1 for r in self.test_results if "Validar Restrições" in r["test"] and r["success"])
        workouts_ok = sum(1 for r in self.test_results if "Validar Treino" in r["test"] and r["success"])
        calories_ok = sum(1 for r in self.test_results if "Validar Calorias" in r["test"] and r["success"])
        
        print(f"✅ 6 perfis criados: {profiles_created}/6")
        print(f"✅ 6 dietas geradas: {diets_generated}/6")
        print(f"✅ 6 treinos gerados: {workouts_generated}/6")
        print(f"✅ Restrições respeitadas: {restrictions_ok} validações")
        print(f"✅ Treinos com séries ≤ 4: {workouts_ok} validações")
        print(f"✅ Calorias coerentes: {calories_ok} validações")
        
        print(f"\n👥 Usuários criados: {len(self.created_users)}")
        for user_id in self.created_users:
            print(f"   • {user_id}")

if __name__ == "__main__":
    tester = LAFTester()
    tester.run_comprehensive_test()