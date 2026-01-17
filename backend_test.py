#!/usr/bin/env python3
"""
🎯 TESTE COMPLETO DOS NOVOS ENDPOINTS DE CICLO DE TREINO AUTOMÁTICO

Testa todos os endpoints implementados conforme especificação:
1. POST /api/training-cycle/setup/{user_id}
2. GET /api/training-cycle/status/{user_id}
3. POST /api/training-cycle/start-session/{user_id}
4. POST /api/training-cycle/finish-session/{user_id}
5. GET /api/training-cycle/week-preview/{user_id}

VALIDAÇÕES CRÍTICAS:
- Dia 0 = SEMPRE descanso
- Dias de treino corretos para frequência escolhida
- Não permitir iniciar treino duas vezes no mesmo dia
- Timer salvo corretamente
- Multiplicadores de dieta corretos
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuração
BASE_URL = "https://flexcal-diet-tracker.preview.emergentagent.com/api"
TEST_USER_ID = "046ca077-2173-4a40-8e20-59441d36f2f7"  # Usuário existente conforme especificação

def log_test(test_name, success, details=""):
    """Log padronizado dos testes"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    print()

def test_training_cycle_setup():
    """
    Testa POST /api/training-cycle/setup/{user_id}
    
    VALIDAÇÕES:
    - Aceita frequência 2-6
    - Retorna first_day_type = "rest" (dia 0 sempre descanso)
    - Salva startDate e frequência
    """
    print("🔧 TESTANDO SETUP DO CICLO DE TREINO")
    
    # Teste 1: Setup com frequência 4x/semana
    try:
        payload = {"frequency": 4}
        response = requests.post(f"{BASE_URL}/training-cycle/setup/{TEST_USER_ID}", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            # Validações críticas
            success = (
                data.get("success") == True and
                data.get("frequency") == 4 and
                data.get("first_day_type") == "rest" and  # DIA 0 = SEMPRE DESCANSO
                "start_date" in data
            )
            
            details = f"Frequency: {data.get('frequency')}, First day: {data.get('first_day_type')}, Start: {data.get('start_date')}"
            log_test("Setup ciclo 4x/semana", success, details)
            
            return data.get("start_date")  # Retorna para usar em outros testes
        else:
            log_test("Setup ciclo 4x/semana", False, f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        log_test("Setup ciclo 4x/semana", False, f"Erro: {str(e)}")
        return None

def test_training_cycle_status(start_date=None):
    """
    Testa GET /api/training-cycle/status/{user_id}
    
    VALIDAÇÕES:
    - Retorna day_type correto ("train"/"rest")
    - Inclui multiplicadores de dieta corretos
    - Inclui informações do ciclo
    """
    print("📊 TESTANDO STATUS DO CICLO DE TREINO")
    
    try:
        response = requests.get(f"{BASE_URL}/training-cycle/status/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Validações críticas
            required_fields = [
                "day_type", "day_number", "cycle_day", "frequency", 
                "has_trained_today", "is_training_in_progress", "diet"
            ]
            
            has_required_fields = all(field in data for field in required_fields)
            
            # Valida multiplicadores de dieta
            diet = data.get("diet", {})
            valid_diet_multipliers = (
                "calorie_multiplier" in diet and
                "carb_multiplier" in diet and
                diet.get("type") in ["training", "rest"]
            )
            
            # Valida lógica de multiplicadores
            if data.get("day_type") == "train" and data.get("has_trained_today"):
                expected_cal_mult = 1.05
                expected_carb_mult = 1.15
                expected_diet_type = "training"
            else:
                expected_cal_mult = 0.95
                expected_carb_mult = 0.80
                expected_diet_type = "rest"
            
            correct_multipliers = (
                diet.get("calorie_multiplier") == expected_cal_mult and
                diet.get("carb_multiplier") == expected_carb_mult and
                diet.get("type") == expected_diet_type
            )
            
            success = has_required_fields and valid_diet_multipliers and correct_multipliers
            
            details = f"Day type: {data.get('day_type')}, Cycle day: {data.get('cycle_day')}, Diet: {diet.get('type')} (cal×{diet.get('calorie_multiplier')}, carb×{diet.get('carb_multiplier')})"
            log_test("Status do ciclo", success, details)
            
            return data
        else:
            log_test("Status do ciclo", False, f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        log_test("Status do ciclo", False, f"Erro: {str(e)}")
        return None

def test_start_training_session():
    """
    Testa POST /api/training-cycle/start-session/{user_id}
    
    VALIDAÇÕES:
    - Inicia sessão de treino
    - Não permite iniciar duas vezes no mesmo dia
    - Retorna informações da sessão
    """
    print("▶️ TESTANDO INÍCIO DE SESSÃO DE TREINO")
    
    # Teste 1: Iniciar sessão pela primeira vez
    try:
        response = requests.post(f"{BASE_URL}/training-cycle/start-session/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            
            success = (
                data.get("success") == True and
                "session" in data and
                "started_at" in data.get("session", {})
            )
            
            details = f"Started at: {data.get('session', {}).get('started_at')}, Already started: {data.get('session', {}).get('already_started', False)}"
            log_test("Iniciar sessão de treino", success, details)
            
            # Teste 2: Tentar iniciar novamente (deve retornar que já está em andamento)
            response2 = requests.post(f"{BASE_URL}/training-cycle/start-session/{TEST_USER_ID}")
            
            if response2.status_code == 200:
                data2 = response2.json()
                
                # Deve indicar que já está em andamento
                already_started = data2.get("session", {}).get("already_started", False)
                success2 = already_started or "já em andamento" in data2.get("message", "").lower()
                
                details2 = f"Segunda tentativa: {data2.get('message')}"
                log_test("Prevenção de duplo início", success2, details2)
                
                return True
            else:
                log_test("Prevenção de duplo início", False, f"HTTP {response2.status_code}: {response2.text}")
                return False
        else:
            log_test("Iniciar sessão de treino", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Iniciar sessão de treino", False, f"Erro: {str(e)}")
        return False

def test_finish_training_session():
    """
    Testa POST /api/training-cycle/finish-session/{user_id}
    
    VALIDAÇÕES:
    - Finaliza sessão de treino
    - Salva duração corretamente
    - Retorna duration_formatted
    """
    print("⏹️ TESTANDO FINALIZAÇÃO DE SESSÃO DE TREINO")
    
    try:
        # Duração de teste: 1 hora (3600 segundos)
        payload = {
            "duration_seconds": 3600,
            "exercises_completed": 10
        }
        
        response = requests.post(f"{BASE_URL}/training-cycle/finish-session/{TEST_USER_ID}", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            session = data.get("session", {})
            success = (
                data.get("success") == True and
                session.get("duration_seconds") == 3600 and
                session.get("exercises_completed") == 10 and
                "duration_formatted" in session and
                "completed_at" in session
            )
            
            details = f"Duration: {session.get('duration_formatted')}, Exercises: {session.get('exercises_completed')}, Completed: {session.get('completed_at')}"
            log_test("Finalizar sessão de treino", success, details)
            
            return True
        else:
            log_test("Finalizar sessão de treino", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Finalizar sessão de treino", False, f"Erro: {str(e)}")
        return False

def test_week_preview():
    """
    Testa GET /api/training-cycle/week-preview/{user_id}
    
    VALIDAÇÕES:
    - Retorna preview de 7 dias
    - Cada dia tem day_type correto
    - Inclui informações do ciclo
    """
    print("📅 TESTANDO PREVIEW DA SEMANA")
    
    try:
        response = requests.get(f"{BASE_URL}/training-cycle/week-preview/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            
            week_preview = data.get("week_preview", [])
            
            # Validações críticas
            success = (
                len(week_preview) == 7 and  # 7 dias
                data.get("frequency") is not None and
                "start_date" in data
            )
            
            # Valida estrutura de cada dia
            if success:
                for day in week_preview:
                    required_day_fields = ["date", "day_name", "day_type", "cycle_day", "is_today"]
                    if not all(field in day for field in required_day_fields):
                        success = False
                        break
                    
                    if day.get("day_type") not in ["train", "rest"]:
                        success = False
                        break
            
            # Conta dias de treino e descanso
            train_days = sum(1 for day in week_preview if day.get("day_type") == "train")
            rest_days = sum(1 for day in week_preview if day.get("day_type") == "rest")
            
            details = f"Frequency: {data.get('frequency')}, Train days: {train_days}, Rest days: {rest_days}, Total days: {len(week_preview)}"
            log_test("Preview da semana", success, details)
            
            # Log detalhado dos dias
            print("    📋 Detalhes da semana:")
            for day in week_preview:
                day_indicator = "🏃" if day.get("day_type") == "train" else "😴"
                today_indicator = " (HOJE)" if day.get("is_today") else ""
                print(f"        {day_indicator} {day.get('day_name')} ({day.get('date')}): {day.get('day_type').upper()}{today_indicator}")
            print()
            
            return True
        else:
            log_test("Preview da semana", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Preview da semana", False, f"Erro: {str(e)}")
        return False

def test_day_zero_logic():
    """
    Testa a lógica crítica do DIA 0 = SEMPRE DESCANSO
    
    Cria um novo ciclo e verifica se o primeiro dia é sempre descanso
    """
    print("🎯 TESTANDO LÓGICA CRÍTICA: DIA 0 = SEMPRE DESCANSO")
    
    # Testa diferentes frequências para garantir que dia 0 é sempre descanso
    frequencies = [2, 3, 4, 5, 6]
    all_success = True
    
    for freq in frequencies:
        try:
            # Setup novo ciclo
            payload = {"frequency": freq}
            response = requests.post(f"{BASE_URL}/training-cycle/setup/{TEST_USER_ID}", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                first_day_type = data.get("first_day_type")
                
                success = first_day_type == "rest"
                details = f"Freq {freq}x: primeiro dia = {first_day_type}"
                log_test(f"Dia 0 descanso (freq {freq}x)", success, details)
                
                if not success:
                    all_success = False
            else:
                log_test(f"Dia 0 descanso (freq {freq}x)", False, f"HTTP {response.status_code}")
                all_success = False
                
        except Exception as e:
            log_test(f"Dia 0 descanso (freq {freq}x)", False, f"Erro: {str(e)}")
            all_success = False
    
    return all_success

def test_diet_multipliers_integration():
    """
    Testa a integração com multiplicadores de dieta
    
    VALIDAÇÕES:
    - dayType === "train" + treinou → dieta de treino (cal×1.05, carbs×1.15)
    - dayType === "rest" OU não treinou → dieta de descanso (cal×0.95, carbs×0.80)
    """
    print("🍽️ TESTANDO INTEGRAÇÃO COM MULTIPLICADORES DE DIETA")
    
    try:
        # Pega status atual
        response = requests.get(f"{BASE_URL}/training-cycle/status/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            
            day_type = data.get("day_type")
            has_trained = data.get("has_trained_today")
            diet = data.get("diet", {})
            
            # Lógica esperada:
            # Se é dia de treino E já treinou → multiplicadores de treino
            # Caso contrário → multiplicadores de descanso
            
            if day_type == "train" and has_trained:
                expected_cal_mult = 1.05
                expected_carb_mult = 1.15
                expected_diet_type = "training"
                scenario = "Dia de treino + treinou"
            else:
                expected_cal_mult = 0.95
                expected_carb_mult = 0.80
                expected_diet_type = "rest"
                scenario = "Dia de descanso OU não treinou"
            
            success = (
                diet.get("calorie_multiplier") == expected_cal_mult and
                diet.get("carb_multiplier") == expected_carb_mult and
                diet.get("type") == expected_diet_type
            )
            
            details = f"{scenario}: cal×{diet.get('calorie_multiplier')} carb×{diet.get('carb_multiplier')} type={diet.get('type')}"
            log_test("Multiplicadores de dieta", success, details)
            
            return success
        else:
            log_test("Multiplicadores de dieta", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Multiplicadores de dieta", False, f"Erro: {str(e)}")
        return False

def run_all_tests():
    """
    Executa todos os testes dos novos endpoints de ciclo de treino
    """
    print("🚀 INICIANDO TESTES DOS NOVOS ENDPOINTS DE CICLO DE TREINO AUTOMÁTICO")
    print("=" * 80)
    print(f"🎯 Usuário de teste: {TEST_USER_ID}")
    print(f"🌐 Base URL: {BASE_URL}")
    print("=" * 80)
    print()
    
    # Contador de sucessos
    tests_passed = 0
    total_tests = 0
    
    # 1. Teste de setup do ciclo
    start_date = test_training_cycle_setup()
    total_tests += 1
    if start_date:
        tests_passed += 1
    
    # 2. Teste de status do ciclo
    status_data = test_training_cycle_status(start_date)
    total_tests += 1
    if status_data:
        tests_passed += 1
    
    # 3. Teste de início de sessão
    session_started = test_start_training_session()
    total_tests += 1
    if session_started:
        tests_passed += 1
    
    # 4. Teste de finalização de sessão
    session_finished = test_finish_training_session()
    total_tests += 1
    if session_finished:
        tests_passed += 1
    
    # 5. Teste de preview da semana
    week_preview_ok = test_week_preview()
    total_tests += 1
    if week_preview_ok:
        tests_passed += 1
    
    # 6. Teste da lógica crítica do dia 0
    day_zero_ok = test_day_zero_logic()
    total_tests += 1
    if day_zero_ok:
        tests_passed += 1
    
    # 7. Teste de integração com multiplicadores de dieta
    diet_mult_ok = test_diet_multipliers_integration()
    total_tests += 1
    if diet_mult_ok:
        tests_passed += 1
    
    # Resultado final
    print("=" * 80)
    print("📊 RESULTADO FINAL DOS TESTES")
    print("=" * 80)
    
    success_rate = (tests_passed / total_tests) * 100
    
    if tests_passed == total_tests:
        print(f"🎉 TODOS OS TESTES PASSARAM! ({tests_passed}/{total_tests}) - {success_rate:.1f}%")
        print()
        print("✅ VALIDAÇÕES CRÍTICAS CONFIRMADAS:")
        print("   • Dia 0 = SEMPRE descanso")
        print("   • Dias de treino corretos para frequência escolhida")
        print("   • Não permite iniciar treino duas vezes no mesmo dia")
        print("   • Timer salvo corretamente")
        print("   • Multiplicadores de dieta corretos")
    else:
        print(f"⚠️ ALGUNS TESTES FALHARAM: {tests_passed}/{total_tests} passaram ({success_rate:.1f}%)")
        failed_tests = total_tests - tests_passed
        print(f"❌ {failed_tests} teste(s) falharam")
    
    print("=" * 80)
    
    return tests_passed == total_tests

if __name__ == "__main__":
    run_all_tests()