#!/usr/bin/env python3
"""
LAF Backend Testing - User Profile API Tests
Tests the user profile system with TDEE and macros calculation
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://train-eat-laf.preview.emergentagent.com/api"

class LAFBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.created_profiles = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def test_health_check(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Health Check", True, f"Status: {response.json()}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def create_test_profile(self, profile_data: Dict[str, Any]) -> str:
        """Create a test profile and return the ID"""
        try:
            response = requests.post(
                f"{self.base_url}/user/profile",
                json=profile_data,
                timeout=10
            )
            
            if response.status_code == 200:
                profile = response.json()
                profile_id = profile["id"]
                self.created_profiles.append(profile_id)
                return profile_id
            else:
                print(f"Failed to create test profile: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating test profile: {str(e)}")
            return None
    
    def test_get_profile(self):
        """Test GET /api/user/profile/{user_id}"""
        # First create a profile to test with
        test_profile = {
            "name": "João Silva",
            "age": 28,
            "sex": "masculino",
            "height": 178.0,
            "weight": 82.0,
            "target_weight": 78.0,
            "body_fat_percentage": 15.0,
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "goal": "cutting",
            "dietary_restrictions": ["lactose"],
            "food_preferences": ["frango", "arroz"],
            "injury_history": []
        }
        
        profile_id = self.create_test_profile(test_profile)
        if not profile_id:
            self.log_test("GET Profile - Setup", False, "Could not create test profile")
            return False
        
        try:
            # Test getting the profile
            response = requests.get(f"{self.base_url}/user/profile/{profile_id}", timeout=10)
            
            if response.status_code == 200:
                profile = response.json()
                
                # Verify basic data
                if (profile["name"] == test_profile["name"] and 
                    profile["age"] == test_profile["age"] and
                    profile["weight"] == test_profile["weight"]):
                    
                    # Verify calculations exist
                    if "tdee" in profile and "target_calories" in profile and "macros" in profile:
                        # Verify TDEE calculation (should be around 2786 for this profile)
                        expected_tdee = 2786  # From review request
                        actual_tdee = profile["tdee"]
                        tdee_diff = abs(actual_tdee - expected_tdee)
                        
                        if tdee_diff < 50:  # Allow 50 calorie tolerance
                            self.log_test("GET Profile", True, 
                                        f"Profile retrieved successfully. TDEE: {actual_tdee} (expected ~{expected_tdee})")
                            return True
                        else:
                            self.log_test("GET Profile", False, 
                                        f"TDEE calculation incorrect: {actual_tdee} (expected ~{expected_tdee})")
                            return False
                    else:
                        self.log_test("GET Profile", False, "Missing calculated fields (tdee, target_calories, macros)")
                        return False
                else:
                    self.log_test("GET Profile", False, "Basic profile data doesn't match")
                    return False
            elif response.status_code == 404:
                self.log_test("GET Profile", False, "Profile not found (404)")
                return False
            else:
                self.log_test("GET Profile", False, f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GET Profile", False, f"Request error: {str(e)}")
            return False
    
    def test_get_nonexistent_profile(self):
        """Test GET with non-existent profile ID"""
        try:
            fake_id = "non-existent-id-12345"
            response = requests.get(f"{self.base_url}/user/profile/{fake_id}", timeout=10)
            
            if response.status_code == 404:
                self.log_test("GET Non-existent Profile", True, "Correctly returned 404")
                return True
            else:
                self.log_test("GET Non-existent Profile", False, 
                            f"Expected 404, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET Non-existent Profile", False, f"Request error: {str(e)}")
            return False
    
    def test_update_profile_weight(self):
        """Test PUT /api/user/profile/{user_id} - Update weight"""
        # Create test profile
        test_profile = {
            "name": "Maria Santos",
            "age": 25,
            "sex": "feminino",
            "height": 165.0,
            "weight": 60.0,
            "training_level": "intermediario",
            "weekly_training_frequency": 3,
            "available_time_per_session": 45,
            "goal": "bulking"
        }
        
        profile_id = self.create_test_profile(test_profile)
        if not profile_id:
            self.log_test("UPDATE Profile Weight - Setup", False, "Could not create test profile")
            return False
        
        try:
            # Get original profile
            original_response = requests.get(f"{self.base_url}/user/profile/{profile_id}", timeout=10)
            original_profile = original_response.json()
            original_tdee = original_profile["tdee"]
            
            # Update weight
            update_data = {"weight": 65.0}  # +5kg
            response = requests.put(
                f"{self.base_url}/user/profile/{profile_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                updated_profile = response.json()
                
                # Verify weight was updated
                if updated_profile["weight"] == 65.0:
                    # Verify TDEE was recalculated (should be higher with more weight)
                    new_tdee = updated_profile["tdee"]
                    if new_tdee > original_tdee:
                        self.log_test("UPDATE Profile Weight", True, 
                                    f"Weight updated and TDEE recalculated: {original_tdee} → {new_tdee}")
                        return True
                    else:
                        self.log_test("UPDATE Profile Weight", False, 
                                    f"TDEE not recalculated properly: {original_tdee} → {new_tdee}")
                        return False
                else:
                    self.log_test("UPDATE Profile Weight", False, "Weight not updated")
                    return False
            else:
                self.log_test("UPDATE Profile Weight", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("UPDATE Profile Weight", False, f"Request error: {str(e)}")
            return False
    
    def test_update_profile_goal(self):
        """Test PUT /api/user/profile/{user_id} - Update goal"""
        # Create test profile with cutting goal
        test_profile = {
            "name": "Carlos Oliveira",
            "age": 30,
            "sex": "masculino",
            "height": 180.0,
            "weight": 85.0,
            "training_level": "avancado",
            "weekly_training_frequency": 5,
            "available_time_per_session": 90,
            "goal": "cutting"
        }
        
        profile_id = self.create_test_profile(test_profile)
        if not profile_id:
            self.log_test("UPDATE Profile Goal - Setup", False, "Could not create test profile")
            return False
        
        try:
            # Get original profile
            original_response = requests.get(f"{self.base_url}/user/profile/{profile_id}", timeout=10)
            original_profile = original_response.json()
            original_calories = original_profile["target_calories"]
            
            # Update goal from cutting to bulking
            update_data = {"goal": "bulking"}
            response = requests.put(
                f"{self.base_url}/user/profile/{profile_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                updated_profile = response.json()
                
                # Verify goal was updated
                if updated_profile["goal"] == "bulking":
                    # Verify target calories increased (cutting -> bulking)
                    new_calories = updated_profile["target_calories"]
                    if new_calories > original_calories:
                        self.log_test("UPDATE Profile Goal", True, 
                                    f"Goal updated and calories recalculated: {original_calories} → {new_calories}")
                        return True
                    else:
                        self.log_test("UPDATE Profile Goal", False, 
                                    f"Calories not recalculated properly: {original_calories} → {new_calories}")
                        return False
                else:
                    self.log_test("UPDATE Profile Goal", False, "Goal not updated")
                    return False
            else:
                self.log_test("UPDATE Profile Goal", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("UPDATE Profile Goal", False, f"Request error: {str(e)}")
            return False
    
    def test_edge_case_female_profile(self):
        """Test profile creation with female user (different BMR formula)"""
        test_profile = {
            "name": "Ana Costa",
            "age": 26,
            "sex": "feminino",
            "height": 160.0,
            "weight": 55.0,
            "training_level": "iniciante",
            "weekly_training_frequency": 2,
            "available_time_per_session": 30,
            "goal": "manutencao"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/user/profile",
                json=test_profile,
                timeout=10
            )
            
            if response.status_code == 200:
                profile = response.json()
                self.created_profiles.append(profile["id"])
                
                # Verify calculations exist and are reasonable for female
                tdee = profile["tdee"]
                target_calories = profile["target_calories"]
                
                # For maintenance goal, target_calories should equal TDEE
                if abs(tdee - target_calories) < 5:  # Small tolerance
                    # Female BMR should be lower than male equivalent
                    if 1200 < tdee < 2200:  # Reasonable range for this profile
                        self.log_test("Edge Case - Female Profile", True, 
                                    f"Female profile created successfully. TDEE: {tdee}")
                        return True
                    else:
                        self.log_test("Edge Case - Female Profile", False, 
                                    f"TDEE seems unreasonable for female: {tdee}")
                        return False
                else:
                    self.log_test("Edge Case - Female Profile", False, 
                                f"Maintenance goal error: TDEE {tdee} != Target {target_calories}")
                    return False
            else:
                self.log_test("Edge Case - Female Profile", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Edge Case - Female Profile", False, f"Request error: {str(e)}")
            return False
    
    def test_edge_case_athlete_goal(self):
        """Test profile with athlete goal"""
        test_profile = {
            "name": "Pedro Atleta",
            "age": 24,
            "sex": "masculino",
            "height": 185.0,
            "weight": 78.0,
            "training_level": "avancado",
            "weekly_training_frequency": 6,
            "available_time_per_session": 120,
            "goal": "atleta"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/user/profile",
                json=test_profile,
                timeout=10
            )
            
            if response.status_code == 200:
                profile = response.json()
                self.created_profiles.append(profile["id"])
                
                tdee = profile["tdee"]
                target_calories = profile["target_calories"]
                
                # Athlete goal should have moderate surplus (8%)
                expected_surplus = tdee * 0.08
                actual_surplus = target_calories - tdee
                
                if abs(actual_surplus - expected_surplus) < 50:  # 50 calorie tolerance
                    self.log_test("Edge Case - Athlete Goal", True, 
                                f"Athlete profile created. TDEE: {tdee}, Target: {target_calories} (+{actual_surplus:.0f})")
                    return True
                else:
                    self.log_test("Edge Case - Athlete Goal", False, 
                                f"Athlete surplus incorrect: expected +{expected_surplus:.0f}, got +{actual_surplus:.0f}")
                    return False
            else:
                self.log_test("Edge Case - Athlete Goal", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Edge Case - Athlete Goal", False, f"Request error: {str(e)}")
            return False
    
    def test_minimal_profile(self):
        """Test profile creation with minimal required data"""
        test_profile = {
            "name": "Usuário Mínimo",
            "age": 25,
            "sex": "masculino",
            "height": 175.0,
            "weight": 70.0,
            "training_level": "iniciante",
            "weekly_training_frequency": 1,
            "available_time_per_session": 30,
            "goal": "manutencao"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/user/profile",
                json=test_profile,
                timeout=10
            )
            
            if response.status_code == 200:
                profile = response.json()
                self.created_profiles.append(profile["id"])
                
                # Verify all required calculations are present
                required_fields = ["tdee", "target_calories", "macros"]
                missing_fields = [field for field in required_fields if field not in profile or profile[field] is None]
                
                if not missing_fields:
                    self.log_test("Edge Case - Minimal Profile", True, 
                                f"Minimal profile created successfully with all calculations")
                    return True
                else:
                    self.log_test("Edge Case - Minimal Profile", False, 
                                f"Missing calculated fields: {missing_fields}")
                    return False
            else:
                self.log_test("Edge Case - Minimal Profile", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Edge Case - Minimal Profile", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("LAF BACKEND API TESTING")
        print("=" * 60)
        print(f"Testing backend at: {self.base_url}")
        print()
        
        # Test connectivity first
        if not self.test_health_check():
            print("\n❌ Backend is not accessible. Stopping tests.")
            return False
        
        print()
        
        # Run all tests
        tests = [
            self.test_get_profile,
            self.test_get_nonexistent_profile,
            self.test_update_profile_weight,
            self.test_update_profile_goal,
            self.test_edge_case_female_profile,
            self.test_edge_case_athlete_goal,
            self.test_minimal_profile
        ]
        
        for test in tests:
            test()
            print()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print("❌ Some tests failed:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
            return False

if __name__ == "__main__":
    tester = LAFBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)