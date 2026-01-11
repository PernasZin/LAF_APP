#!/usr/bin/env python3
"""
LAF Backend Comprehensive Audit Test Suite
==========================================

This test suite performs a complete audit of the LAF diet application backend
as requested in the review. It specifically validates:

1. Health check endpoint
2. User profile creation for all 3 objectives (cutting, bulking, manutencao)
3. Diet generation with correct calorie calculations
4. Weight registration with 14-day blocking
5. Water tracker functionality
6. Verification that NO athlete mode references exist

CRITICAL: The athlete mode has been COMPLETELY REMOVED according to the review request.
Any references to "athlete", "peak_week", or "competition_date" should be flagged as errors.
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://healthappfix.preview.emergentagent.com/api"

class LAFBackendAuditor:
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        
    def log_result(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test result with details"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if not success:
            self.errors.append(f"{test_name}: {details}")
            
    def log_warning(self, message: str):
        """Log warning message"""
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")
        
    def check_athlete_references(self, data: Any, context: str) -> List[str]:
        """Check for any athlete mode references that should not exist"""
        athlete_terms = ["athlete", "peak_week", "competition_date", "competition_phase", "weeks_to_competition"]
        found_terms = []
        
        def search_dict(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if any(term in key.lower() for term in athlete_terms):
                        found_terms.append(f"{context} -> {current_path}: {key}")
                    search_dict(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    search_dict(item, f"{path}[{i}]")
            elif isinstance(obj, str):
                for term in athlete_terms:
                    if term in obj.lower():
                        found_terms.append(f"{context} -> {path}: contains '{term}'")
        
        search_dict(data)
        return found_terms
        
    def test_health_check(self):
        """Test 1: Health Check"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Check", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
            
    def test_user_creation_cutting(self):
        """Test 2: User Creation - Cutting Objective"""
        profile_data = {
            "id": "test_audit_cutting_001",
            "name": "Test Cutting",
            "age": 30,
            "sex": "masculino",
            "weight": 85,
            "height": 175,
            "goal": "cutting",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "dietary_restrictions": [],
            "food_preferences": [],
            "injury_history": []
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/user/profile",
                json=profile_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for athlete references
                athlete_refs = self.check_athlete_references(data, "User Creation (Cutting)")
                if athlete_refs:
                    self.log_result("User Creation - Cutting", False, f"ATHLETE REFERENCES FOUND: {athlete_refs}")
                    return False
                
                # Validate TDEE calculation for cutting
                expected_deficit = 0.82  # 18% deficit
                tdee = data.get("tdee", 0)
                target_calories = data.get("target_calories", 0)
                
                if tdee > 0 and target_calories > 0:
                    actual_ratio = target_calories / tdee
                    if abs(actual_ratio - expected_deficit) < 0.05:  # 5% tolerance
                        self.log_result("User Creation - Cutting", True, 
                                      f"TDEE: {tdee}kcal, Target: {target_calories}kcal (deficit: {(1-actual_ratio)*100:.1f}%)")
                    else:
                        self.log_result("User Creation - Cutting", False, 
                                      f"Incorrect deficit calculation. Expected ~18%, got {(1-actual_ratio)*100:.1f}%")
                else:
                    self.log_result("User Creation - Cutting", False, "Missing TDEE or target_calories in response")
                
                return True
            else:
                self.log_result("User Creation - Cutting", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Creation - Cutting", False, f"Error: {str(e)}")
            return False
            
    def test_user_creation_bulking(self):
        """Test 3: User Creation - Bulking Objective"""
        profile_data = {
            "id": "test_audit_bulking_002",
            "name": "Test Bulking",
            "age": 25,
            "sex": "masculino",
            "weight": 70,
            "height": 180,
            "goal": "bulking",
            "training_level": "avancado",
            "weekly_training_frequency": 5,
            "available_time_per_session": 90,
            "dietary_restrictions": [],
            "food_preferences": [],
            "injury_history": []
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/user/profile",
                json=profile_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for athlete references
                athlete_refs = self.check_athlete_references(data, "User Creation (Bulking)")
                if athlete_refs:
                    self.log_result("User Creation - Bulking", False, f"ATHLETE REFERENCES FOUND: {athlete_refs}")
                    return False
                
                # Validate TDEE calculation for bulking
                expected_surplus = 1.12  # 12% surplus
                tdee = data.get("tdee", 0)
                target_calories = data.get("target_calories", 0)
                
                if tdee > 0 and target_calories > 0:
                    actual_ratio = target_calories / tdee
                    if abs(actual_ratio - expected_surplus) < 0.05:  # 5% tolerance
                        self.log_result("User Creation - Bulking", True, 
                                      f"TDEE: {tdee}kcal, Target: {target_calories}kcal (surplus: {(actual_ratio-1)*100:.1f}%)")
                    else:
                        self.log_result("User Creation - Bulking", False, 
                                      f"Incorrect surplus calculation. Expected ~12%, got {(actual_ratio-1)*100:.1f}%")
                else:
                    self.log_result("User Creation - Bulking", False, "Missing TDEE or target_calories in response")
                
                return True
            else:
                self.log_result("User Creation - Bulking", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Creation - Bulking", False, f"Error: {str(e)}")
            return False
            
    def test_user_creation_manutencao(self):
        """Test 4: User Creation - Maintenance Objective"""
        profile_data = {
            "id": "test_audit_manutencao_003",
            "name": "Test Manutencao",
            "age": 35,
            "sex": "feminino",
            "weight": 75,
            "height": 170,
            "goal": "manutencao",
            "training_level": "iniciante",
            "weekly_training_frequency": 3,
            "available_time_per_session": 45,
            "dietary_restrictions": [],
            "food_preferences": [],
            "injury_history": []
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/user/profile",
                json=profile_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for athlete references
                athlete_refs = self.check_athlete_references(data, "User Creation (Manutencao)")
                if athlete_refs:
                    self.log_result("User Creation - Manutencao", False, f"ATHLETE REFERENCES FOUND: {athlete_refs}")
                    return False
                
                # Validate TDEE calculation for maintenance
                tdee = data.get("tdee", 0)
                target_calories = data.get("target_calories", 0)
                
                if tdee > 0 and target_calories > 0:
                    # For maintenance, target should equal TDEE
                    if abs(target_calories - tdee) < 50:  # 50 kcal tolerance
                        self.log_result("User Creation - Manutencao", True, 
                                      f"TDEE: {tdee}kcal, Target: {target_calories}kcal (maintenance)")
                    else:
                        self.log_result("User Creation - Manutencao", False, 
                                      f"Maintenance calories incorrect. TDEE: {tdee}, Target: {target_calories}")
                else:
                    self.log_result("User Creation - Manutencao", False, "Missing TDEE or target_calories in response")
                
                return True
            else:
                self.log_result("User Creation - Manutencao", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Creation - Manutencao", False, f"Error: {str(e)}")
            return False
            
    def test_diet_generation_cutting(self):
        """Test 5: Diet Generation - Cutting"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/diet/generate?user_id=test_audit_cutting_001",
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for athlete references
                athlete_refs = self.check_athlete_references(data, "Diet Generation (Cutting)")
                if athlete_refs:
                    self.log_result("Diet Generation - Cutting", False, f"ATHLETE REFERENCES FOUND: {athlete_refs}")
                    return False
                
                # Validate diet structure and calorie deficit
                meals = data.get("meals", [])
                computed_calories = data.get("computed_calories", 0)
                target_calories = data.get("target_calories", 0)
                
                if len(meals) > 0 and computed_calories > 0:
                    # Check if calories are within reasonable range for cutting
                    if 1200 <= computed_calories <= 2500:  # Reasonable cutting range
                        self.log_result("Diet Generation - Cutting", True, 
                                      f"Generated {len(meals)} meals, {computed_calories}kcal (cutting diet)")
                    else:
                        self.log_result("Diet Generation - Cutting", False, 
                                      f"Calories outside cutting range: {computed_calories}kcal")
                else:
                    self.log_result("Diet Generation - Cutting", False, "Invalid diet structure or missing calories")
                
                return True
            else:
                self.log_result("Diet Generation - Cutting", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Diet Generation - Cutting", False, f"Error: {str(e)}")
            return False
            
    def test_diet_generation_bulking(self):
        """Test 6: Diet Generation - Bulking"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/diet/generate?user_id=test_audit_bulking_002",
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for athlete references
                athlete_refs = self.check_athlete_references(data, "Diet Generation (Bulking)")
                if athlete_refs:
                    self.log_result("Diet Generation - Bulking", False, f"ATHLETE REFERENCES FOUND: {athlete_refs}")
                    return False
                
                # Validate diet structure and calorie surplus
                meals = data.get("meals", [])
                computed_calories = data.get("computed_calories", 0)
                
                if len(meals) > 0 and computed_calories > 0:
                    # Check if calories are within reasonable range for bulking
                    if 2500 <= computed_calories <= 4500:  # Reasonable bulking range
                        self.log_result("Diet Generation - Bulking", True, 
                                      f"Generated {len(meals)} meals, {computed_calories}kcal (bulking diet)")
                    else:
                        self.log_result("Diet Generation - Bulking", False, 
                                      f"Calories outside bulking range: {computed_calories}kcal")
                else:
                    self.log_result("Diet Generation - Bulking", False, "Invalid diet structure or missing calories")
                
                return True
            else:
                self.log_result("Diet Generation - Bulking", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Diet Generation - Bulking", False, f"Error: {str(e)}")
            return False
            
    def test_weight_registration(self):
        """Test 7: Weight Registration"""
        weight_data = {
            "weight": 84.5,
            "notes": "Test weight registration",
            "questionnaire": {
                "diet": 8,
                "training": 7,
                "cardio": 6,
                "sleep": 8,
                "hydration": 9
            }
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/progress/weight/test_audit_cutting_001",
                json=weight_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for athlete references
                athlete_refs = self.check_athlete_references(data, "Weight Registration")
                if athlete_refs:
                    self.log_result("Weight Registration", False, f"ATHLETE REFERENCES FOUND: {athlete_refs}")
                    return False
                
                record = data.get("record", {})
                if record.get("weight") == 84.5:
                    self.log_result("Weight Registration", True, 
                                  f"Weight registered: {record.get('weight')}kg")
                else:
                    self.log_result("Weight Registration", False, "Weight not properly recorded")
                
                return True
            else:
                self.log_result("Weight Registration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Weight Registration", False, f"Error: {str(e)}")
            return False
            
    def test_14_day_weight_block(self):
        """Test 8: 14-Day Weight Registration Block"""
        weight_data = {
            "weight": 84.0,
            "notes": "Should be blocked",
            "questionnaire": {
                "diet": 7,
                "training": 6,
                "cardio": 5,
                "sleep": 7,
                "hydration": 8
            }
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/progress/weight/test_audit_cutting_001",
                json=weight_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Should return 400 error for blocked registration
            if response.status_code == 400:
                error_message = response.text
                if "14" in error_message or "dias" in error_message.lower():
                    self.log_result("14-Day Weight Block", True, 
                                  "Correctly blocked weight registration within 14 days")
                else:
                    self.log_result("14-Day Weight Block", False, 
                                  f"Blocked but wrong message: {error_message}")
                return True
            else:
                self.log_result("14-Day Weight Block", False, 
                              f"Should be blocked but got HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("14-Day Weight Block", False, f"Error: {str(e)}")
            return False
            
    def test_profile_retrieval(self):
        """Test 9: Profile Retrieval - No Athlete Fields"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/user/profile/test_audit_cutting_001",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for athlete references - THIS IS CRITICAL
                athlete_refs = self.check_athlete_references(data, "Profile Retrieval")
                if athlete_refs:
                    self.log_result("Profile Retrieval - No Athlete Fields", False, 
                                  f"CRITICAL: ATHLETE REFERENCES FOUND: {athlete_refs}")
                    return False
                
                # Verify profile data
                if data.get("name") and data.get("goal"):
                    self.log_result("Profile Retrieval - No Athlete Fields", True, 
                                  f"Profile retrieved successfully, goal: {data.get('goal')}")
                else:
                    self.log_result("Profile Retrieval - No Athlete Fields", False, 
                                  "Profile missing essential fields")
                
                return True
            else:
                self.log_result("Profile Retrieval - No Athlete Fields", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Profile Retrieval - No Athlete Fields", False, f"Error: {str(e)}")
            return False
            
    def test_weight_history(self):
        """Test 10: Weight History Retrieval"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/progress/weight/test_audit_cutting_001",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for athlete references
                athlete_refs = self.check_athlete_references(data, "Weight History")
                if athlete_refs:
                    self.log_result("Weight History", False, f"ATHLETE REFERENCES FOUND: {athlete_refs}")
                    return False
                
                history = data.get("history", [])
                if len(history) > 0:
                    self.log_result("Weight History", True, 
                                  f"Retrieved {len(history)} weight records")
                else:
                    self.log_result("Weight History", True, "No weight history (expected for new user)")
                
                return True
            else:
                self.log_result("Weight History", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Weight History", False, f"Error: {str(e)}")
            return False
            
    def test_water_tracker(self):
        """Test 11: Water Tracker"""
        water_data = {
            "water_ml": 500,
            "notes": "Test water intake"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/tracker/water-sodium/test_audit_cutting_001",
                json=water_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for athlete references
                athlete_refs = self.check_athlete_references(data, "Water Tracker")
                if athlete_refs:
                    self.log_result("Water Tracker", False, f"ATHLETE REFERENCES FOUND: {athlete_refs}")
                    return False
                
                if data.get("success") and data.get("water_ml") >= 500:
                    self.log_result("Water Tracker", True, 
                                  f"Water tracked: {data.get('water_ml')}ml")
                else:
                    self.log_result("Water Tracker", False, "Water tracking failed")
                
                return True
            else:
                self.log_result("Water Tracker", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Water Tracker", False, f"Error: {str(e)}")
            return False
            
    def run_comprehensive_audit(self):
        """Run all audit tests"""
        print("=" * 80)
        print("LAF BACKEND COMPREHENSIVE AUDIT")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Run all tests
        tests = [
            self.test_health_check,
            self.test_user_creation_cutting,
            self.test_user_creation_bulking,
            self.test_user_creation_manutencao,
            self.test_diet_generation_cutting,
            self.test_diet_generation_bulking,
            self.test_weight_registration,
            self.test_14_day_weight_block,
            self.test_profile_retrieval,
            self.test_weight_history,
            self.test_water_tracker
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                self.log_result(test.__name__, False, f"Test execution error: {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if self.errors:
            print(f"\n❌ CRITICAL ISSUES ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Check for athlete mode violations
        athlete_violations = [error for error in self.errors if "ATHLETE REFERENCES" in error]
        if athlete_violations:
            print(f"\n🚨 ATHLETE MODE VIOLATIONS ({len(athlete_violations)}):")
            print("   The review request states athlete mode was COMPLETELY REMOVED!")
            for violation in athlete_violations:
                print(f"  • {violation}")
        
        print("\n" + "=" * 80)
        
        return passed == total

if __name__ == "__main__":
    auditor = LAFBackendAuditor()
    success = auditor.run_comprehensive_audit()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)