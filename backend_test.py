#!/usr/bin/env python3
"""
LAF App - Teste de Integração do Modelo de Domínio de Atleta
Testa validação, criação de perfis em diferentes fases, geração de dieta e comparações.
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from environment
BACKEND_URL = "https://fit-buddy-81.preview.emergentagent.com/api"

class AthleteModelTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.created_profiles = []  # Track for cleanup
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        print()

    def test_athlete_validation_missing_phase(self):
        """Test 1a: Atleta sem competition_phase → DEVE retornar 400"""
        payload = {
            "name": "Atleta Falha",
            "age": 28,
            "sex": "masculino",
            "height": 180,
            "weight": 85,
            "training_level": "avancado",
            "weekly_training_frequency": 6,
            "available_time_per_session": 90,
            "goal": "atleta"
            # Missing competition_phase
        }
        
        try:
            response = requests.post(f"{self.base_url}/user/profile", json=payload)
            
            if response.status_code == 400:
                error_msg = response.json().get("detail", "")
                if "competition_phase" in error_msg:
                    self.log_test("Validação: Atleta sem competition_phase", True, 
                                f"Retornou 400 corretamente: {error_msg}")
                else:
                    self.log_test("Validação: Atleta sem competition_phase", False,
                                f"Erro 400 mas mensagem incorreta: {error_msg}")
            else:
                self.log_test("Validação: Atleta sem competition_phase", False,
                            f"Deveria retornar 400, mas retornou {response.status_code}")
                
        except Exception as e:
            self.log_test("Validação: Atleta sem competition_phase", False, f"Erro de conexão: {e}")

    def test_athlete_validation_missing_weeks(self):
        """Test 1b: Atleta sem weeks_to_competition → DEVE retornar 400"""
        payload = {
            "name": "Atleta Falha",
            "age": 28,
            "sex": "masculino", 
            "height": 180,
            "weight": 85,
            "training_level": "avancado",
            "weekly_training_frequency": 6,
            "available_time_per_session": 90,
            "goal": "atleta",
            "competition_phase": "prep"
            # Missing weeks_to_competition
        }
        
        try:
            response = requests.post(f"{self.base_url}/user/profile", json=payload)
            
            if response.status_code == 400:
                error_msg = response.json().get("detail", "")
                if "weeks_to_competition" in error_msg:
                    self.log_test("Validação: Atleta sem weeks_to_competition", True,
                                f"Retornou 400 corretamente: {error_msg}")
                else:
                    self.log_test("Validação: Atleta sem weeks_to_competition", False,
                                f"Erro 400 mas mensagem incorreta: {error_msg}")
            else:
                self.log_test("Validação: Atleta sem weeks_to_competition", False,
                            f"Deveria retornar 400, mas retornou {response.status_code}")
                
        except Exception as e:
            self.log_test("Validação: Atleta sem weeks_to_competition", False, f"Erro de conexão: {e}")

    def test_athlete_validation_invalid_phase(self):
        """Test 1c: Atleta com fase inválida → DEVE retornar 400"""
        payload = {
            "name": "Atleta Falha",
            "age": 28,
            "sex": "masculino",
            "height": 180,
            "weight": 85,
            "training_level": "avancado",
            "weekly_training_frequency": 6,
            "available_time_per_session": 90,
            "goal": "atleta",
            "competition_phase": "invalid_phase",
            "weeks_to_competition": 10
        }
        
        try:
            response = requests.post(f"{self.base_url}/user/profile", json=payload)
            
            if response.status_code == 400:
                error_msg = response.json().get("detail", "")
                if "Fase inválida" in error_msg or "invalid" in error_msg.lower():
                    self.log_test("Validação: Atleta com fase inválida", True,
                                f"Retornou 400 corretamente: {error_msg}")
                else:
                    self.log_test("Validação: Atleta com fase inválida", False,
                                f"Erro 400 mas mensagem incorreta: {error_msg}")
            else:
                self.log_test("Validação: Atleta com fase inválida", False,
                            f"Deveria retornar 400, mas retornou {response.status_code}")
                
        except Exception as e:
            self.log_test("Validação: Atleta com fase inválida", False, f"Erro de conexão: {e}")

    def create_athlete_profile(self, phase: str, weeks: int, test_name: str) -> Dict[str, Any]:
        """Helper para criar perfil de atleta e validar cálculos"""
        # Dados base: peso=80kg, height=175, age=28, sex=masculino
        payload = {
            "name": f"Atleta {phase.title()}",
            "age": 28,
            "sex": "masculino",
            "height": 175,
            "weight": 80,
            "training_level": "avancado",
            "weekly_training_frequency": 6,
            "available_time_per_session": 90,
            "goal": "atleta",
            "competition_phase": phase,
            "weeks_to_competition": weeks
        }
        
        try:
            response = requests.post(f"{self.base_url}/user/profile", json=payload)
            
            if response.status_code == 200:
                profile = response.json()
                self.created_profiles.append(profile["id"])
                return profile
            else:
                self.log_test(test_name, False, 
                            f"Falha ao criar perfil: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test(test_name, False, f"Erro de conexão: {e}")
            return None

    def test_athlete_off_season(self):
        """Test 2a: off_season (weeks=25) - superávit +7.5%, P=2.0g/kg, F=0.9g/kg"""
        profile = self.create_athlete_profile("off_season", 25, "Criação: Atleta Off-Season")
        
        if not profile:
            return
            
        # Validações esperadas para peso=80kg, height=175, age=28, masculino, avançado, 6x/semana
        # BMR = (10*80) + (6.25*175) - (5*28) + 5 = 800 + 1093.75 - 140 + 5 = 1758.75
        # TDEE = BMR * 1.9 (avançado, 6x/semana) = 1758.75 * 1.9 = 3341.625
        # Target = TDEE * 1.075 (off_season +7.5%) = 3341.625 * 1.075 = 3592.25 ≈ 3592
        expected_calories_min = 3580  # Tolerância
        expected_calories_max = 3605
        
        # Macros esperados: P=2.0g/kg=160g, F=0.9g/kg=72g
        expected_protein = 160.0
        expected_fat = 72.0
        
        success = True
        details = []
        
        # Verifica calorias
        actual_calories = profile.get("target_calories")
        if not (expected_calories_min <= actual_calories <= expected_calories_max):
            success = False
            details.append(f"Calorias incorretas: esperado ~3592, obtido {actual_calories}")
        else:
            details.append(f"Calorias OK: {actual_calories} (esperado ~3592)")
            
        # Verifica macros
        macros = profile.get("macros", {})
        actual_protein = macros.get("protein", 0)
        actual_fat = macros.get("fat", 0)
        
        if abs(actual_protein - expected_protein) > 1:
            success = False
            details.append(f"Proteína incorreta: esperado {expected_protein}g, obtido {actual_protein}g")
        else:
            details.append(f"Proteína OK: {actual_protein}g")
            
        if abs(actual_fat - expected_fat) > 1:
            success = False
            details.append(f"Gordura incorreta: esperado {expected_fat}g, obtido {actual_fat}g")
        else:
            details.append(f"Gordura OK: {actual_fat}g")
            
        # Verifica campos obrigatórios
        if not profile.get("weeks_to_competition"):
            success = False
            details.append("weeks_to_competition não persistido")
        else:
            details.append(f"weeks_to_competition: {profile.get('weeks_to_competition')}")
            
        if not profile.get("phase_start_date"):
            success = False
            details.append("phase_start_date não criado")
        else:
            details.append("phase_start_date criado")
            
        self.log_test("Criação: Atleta Off-Season", success, " | ".join(details))
        return profile

    def test_athlete_pre_prep(self):
        """Test 2b: pre_prep (weeks=18) - leve déficit -5%, P=2.2g/kg, F=0.8g/kg"""
        profile = self.create_athlete_profile("pre_prep", 18, "Criação: Atleta Pre-Prep")
        
        if not profile:
            return
            
        # Target = TDEE * 0.95 (pre_prep -5%) = 3341.625 * 0.95 = 3174.54 ≈ 3175
        expected_calories_min = 3165
        expected_calories_max = 3185
        
        # Macros esperados: P=2.2g/kg=176g, F=0.8g/kg=64g
        expected_protein = 176.0
        expected_fat = 64.0
        
        success = True
        details = []
        
        actual_calories = profile.get("target_calories")
        if not (expected_calories_min <= actual_calories <= expected_calories_max):
            success = False
            details.append(f"Calorias incorretas: esperado ~3175, obtido {actual_calories}")
        else:
            details.append(f"Calorias OK: {actual_calories}")
            
        macros = profile.get("macros", {})
        actual_protein = macros.get("protein", 0)
        actual_fat = macros.get("fat", 0)
        
        if abs(actual_protein - expected_protein) > 1:
            success = False
            details.append(f"Proteína incorreta: esperado {expected_protein}g, obtido {actual_protein}g")
        else:
            details.append(f"Proteína OK: {actual_protein}g")
            
        if abs(actual_fat - expected_fat) > 1:
            success = False
            details.append(f"Gordura incorreta: esperado {expected_fat}g, obtido {actual_fat}g")
        else:
            details.append(f"Gordura OK: {actual_fat}g")
            
        self.log_test("Criação: Atleta Pre-Prep", success, " | ".join(details))
        return profile

    def test_athlete_prep(self):
        """Test 2c: prep (weeks=12) - déficit agressivo -22.5%, P=2.6g/kg, F=0.7g/kg"""
        profile = self.create_athlete_profile("prep", 12, "Criação: Atleta Prep")
        
        if not profile:
            return
            
        # Target = TDEE * 0.775 (prep -22.5%) = 3341.625 * 0.775 = 2589.76 ≈ 2590
        expected_calories_min = 2580
        expected_calories_max = 2600
        
        # Macros esperados: P=2.6g/kg=208g, F=0.7g/kg=56g
        expected_protein = 208.0
        expected_fat = 56.0
        
        success = True
        details = []
        
        actual_calories = profile.get("target_calories")
        if not (expected_calories_min <= actual_calories <= expected_calories_max):
            success = False
            details.append(f"Calorias incorretas: esperado ~2590, obtido {actual_calories}")
        else:
            details.append(f"Calorias OK: {actual_calories}")
            
        macros = profile.get("macros", {})
        actual_protein = macros.get("protein", 0)
        actual_fat = macros.get("fat", 0)
        
        if abs(actual_protein - expected_protein) > 1:
            success = False
            details.append(f"Proteína incorreta: esperado {expected_protein}g, obtido {actual_protein}g")
        else:
            details.append(f"Proteína OK: {actual_protein}g")
            
        if abs(actual_fat - expected_fat) > 1:
            success = False
            details.append(f"Gordura incorreta: esperado {expected_fat}g, obtido {actual_fat}g")
        else:
            details.append(f"Gordura OK: {actual_fat}g")
            
        self.log_test("Criação: Atleta Prep", success, " | ".join(details))
        return profile

    def test_athlete_peak_week(self):
        """Test 2d: peak_week (weeks=1) - déficit máximo -25%, P=2.8g/kg, F=0.5g/kg"""
        profile = self.create_athlete_profile("peak_week", 1, "Criação: Atleta Peak Week")
        
        if not profile:
            return
            
        # Target = TDEE * 0.75 (peak_week -25%) = 3341.625 * 0.75 = 2506.22 ≈ 2506
        expected_calories_min = 2495
        expected_calories_max = 2515
        
        # Macros esperados: P=2.8g/kg=224g, F=0.5g/kg=40g
        expected_protein = 224.0
        expected_fat = 40.0
        
        success = True
        details = []
        
        actual_calories = profile.get("target_calories")
        if not (expected_calories_min <= actual_calories <= expected_calories_max):
            success = False
            details.append(f"Calorias incorretas: esperado ~2506, obtido {actual_calories}")
        else:
            details.append(f"Calorias OK: {actual_calories}")
            
        macros = profile.get("macros", {})
        actual_protein = macros.get("protein", 0)
        actual_fat = macros.get("fat", 0)
        
        if abs(actual_protein - expected_protein) > 1:
            success = False
            details.append(f"Proteína incorreta: esperado {expected_protein}g, obtido {actual_protein}g")
        else:
            details.append(f"Proteína OK: {actual_protein}g")
            
        if abs(actual_fat - expected_fat) > 1:
            success = False
            details.append(f"Gordura incorreta: esperado {expected_fat}g, obtido {actual_fat}g")
        else:
            details.append(f"Gordura OK: {actual_fat}g")
            
        self.log_test("Criação: Atleta Peak Week", success, " | ".join(details))
        return profile

    def test_diet_generation_for_athlete(self, athlete_profile):
        """Test 3: Geração de dieta para atleta em fase prep"""
        if not athlete_profile:
            self.log_test("Geração de Dieta: Atleta Prep", False, "Perfil de atleta não disponível")
            return
            
        user_id = athlete_profile["id"]
        
        try:
            response = requests.post(f"{self.base_url}/diet/generate?user_id={user_id}")
            
            if response.status_code == 200:
                diet = response.json()
                
                # Verifica estrutura da resposta
                success = True
                details = []
                
                if "meals" not in diet:
                    success = False
                    details.append("Campo 'meals' ausente")
                elif len(diet["meals"]) != 5:
                    success = False
                    details.append(f"Esperado 5 refeições, obtido {len(diet['meals'])}")
                else:
                    details.append("5 refeições criadas")
                
                # Verifica tolerâncias dos macros
                target_macros = athlete_profile.get("macros", {})
                computed_macros = diet.get("computed_macros", {})
                
                if target_macros and computed_macros:
                    p_diff = abs(computed_macros.get("protein", 0) - target_macros.get("protein", 0))
                    c_diff = abs(computed_macros.get("carbs", 0) - target_macros.get("carbs", 0))
                    f_diff = abs(computed_macros.get("fat", 0) - target_macros.get("fat", 0))
                    
                    if p_diff <= 3:
                        details.append(f"Proteína OK: Δ{p_diff:.1f}g")
                    else:
                        success = False
                        details.append(f"Proteína fora da tolerância: Δ{p_diff:.1f}g (máx 3g)")
                        
                    if c_diff <= 3:
                        details.append(f"Carboidratos OK: Δ{c_diff:.1f}g")
                    else:
                        success = False
                        details.append(f"Carboidratos fora da tolerância: Δ{c_diff:.1f}g (máx 3g)")
                        
                    if f_diff <= 2:
                        details.append(f"Gordura OK: Δ{f_diff:.1f}g")
                    else:
                        success = False
                        details.append(f"Gordura fora da tolerância: Δ{f_diff:.1f}g (máx 2g)")
                
                self.log_test("Geração de Dieta: Atleta Prep", success, " | ".join(details))
                
            else:
                self.log_test("Geração de Dieta: Atleta Prep", False,
                            f"Falha na geração: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_test("Geração de Dieta: Atleta Prep", False, f"Erro de conexão: {e}")

    def test_comparison_with_non_athlete(self, athlete_prep_profile):
        """Test 4: Comparação com não-atleta (cutting)"""
        if not athlete_prep_profile:
            self.log_test("Comparação: Atleta vs Cutting", False, "Perfil de atleta prep não disponível")
            return
            
        # Cria perfil cutting com mesmo peso/altura
        cutting_payload = {
            "name": "Cutting Normal",
            "age": 28,
            "sex": "masculino",
            "height": 175,
            "weight": 80,
            "training_level": "avancado",
            "weekly_training_frequency": 6,
            "available_time_per_session": 90,
            "goal": "cutting"
        }
        
        try:
            response = requests.post(f"{self.base_url}/user/profile", json=cutting_payload)
            
            if response.status_code == 200:
                cutting_profile = response.json()
                self.created_profiles.append(cutting_profile["id"])
                
                athlete_calories = athlete_prep_profile.get("target_calories")
                cutting_calories = cutting_profile.get("target_calories")
                
                # Atleta em prep deve ter menos calorias que cutting normal
                if athlete_calories < cutting_calories:
                    difference = cutting_calories - athlete_calories
                    self.log_test("Comparação: Atleta vs Cutting", True,
                                f"Atleta prep ({athlete_calories}kcal) < Cutting ({cutting_calories}kcal) - Diferença: {difference}kcal")
                else:
                    self.log_test("Comparação: Atleta vs Cutting", False,
                                f"Atleta prep ({athlete_calories}kcal) >= Cutting ({cutting_calories}kcal)")
                    
            else:
                self.log_test("Comparação: Atleta vs Cutting", False,
                            f"Falha ao criar perfil cutting: {response.status_code}")
                
        except Exception as e:
            self.log_test("Comparação: Atleta vs Cutting", False, f"Erro de conexão: {e}")

    def run_all_tests(self):
        """Executa todos os testes do modelo de atleta"""
        print("🏃‍♂️ INICIANDO TESTES DO MODELO DE DOMÍNIO DE ATLETA")
        print("=" * 60)
        print()
        
        # Teste 1: Validações
        print("📋 TESTE 1: VALIDAÇÃO DE ATLETA")
        print("-" * 40)
        self.test_athlete_validation_missing_phase()
        self.test_athlete_validation_missing_weeks()
        self.test_athlete_validation_invalid_phase()
        
        # Teste 2: Criação em diferentes fases
        print("🏗️ TESTE 2: CRIAÇÃO DE ATLETAS EM DIFERENTES FASES")
        print("-" * 50)
        off_season_profile = self.test_athlete_off_season()
        pre_prep_profile = self.test_athlete_pre_prep()
        prep_profile = self.test_athlete_prep()
        peak_week_profile = self.test_athlete_peak_week()
        
        # Teste 3: Geração de dieta
        print("🍽️ TESTE 3: GERAÇÃO DE DIETA PARA ATLETAS")
        print("-" * 40)
        self.test_diet_generation_for_athlete(prep_profile)
        
        # Teste 4: Comparação
        print("⚖️ TESTE 4: COMPARAÇÃO COM NÃO-ATLETA")
        print("-" * 35)
        self.test_comparison_with_non_athlete(prep_profile)
        
        # Resumo
        print("📊 RESUMO DOS TESTES")
        print("=" * 20)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print(f"✅ Testes aprovados: {passed}/{total}")
        print(f"❌ Testes falharam: {total - passed}/{total}")
        print(f"📈 Taxa de sucesso: {(passed/total)*100:.1f}%")
        print()
        
        if total - passed > 0:
            print("❌ TESTES QUE FALHARAM:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        return passed == total

def main():
    """Função principal"""
    tester = AthleteModelTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("🎉 TODOS OS TESTES PASSARAM! Modelo de atleta funcionando corretamente.")
            sys.exit(0)
        else:
            print("⚠️ ALGUNS TESTES FALHARAM. Verifique os detalhes acima.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Testes interrompidos pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()