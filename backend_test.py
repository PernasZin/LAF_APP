#!/usr/bin/env python3
"""
Backend Testing Suite for LAF Workout Generation Bug Fixes
==========================================================

Testing the following critical bug fixes:
1. LIMITE DE 4 SÉRIES: All exercises must have ≤ 4 sets
2. NÍVEL AVANÇADO DIFERENCIADO: Advanced level reps="10-12" (vs intermediate "8-12")
3. Workout plans should be different between levels

Base URL: https://workoutcycler.preview.emergentagent.com/api
"""

import requests
import json
import sys
from typing import Dict, List, Any
from datetime import datetime

# Configuration
BASE_URL = "https://workoutcycler.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class WorkoutTestSuite:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f"\n    Details: {details}"
        
        self.test_results.append(result)
        print(result)
        
    def create_test_user_and_profile(self, training_level: str, name_suffix: str) -> Dict[str, Any]:
        """Create a test user with authentication and profile for workout generation"""
        email = f"{training_level}_test@test.com"
        password = "TestPassword123!"
        
        # Step 1: Create authenticated user
        try:
            signup_data = {
                "email": email,
                "password": password
            }
            
            response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, headers=HEADERS)
            
            if response.status_code == 200:
                auth_result = response.json()
                user_id = auth_result.get("user_id")
                self.log_test(f"Create {training_level.upper()} auth user", True, f"User ID: {user_id}")
            else:
                # User might already exist, try login
                response = requests.post(f"{BASE_URL}/auth/login", json=signup_data, headers=HEADERS)
                if response.status_code == 200:
                    auth_result = response.json()
                    user_id = auth_result.get("user_id")
                    self.log_test(f"Login {training_level.upper()} user", True, f"User ID: {user_id}")
                else:
                    self.log_test(f"Create/Login {training_level.upper()} user", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            self.log_test(f"Create {training_level.upper()} user", False, f"Exception: {str(e)}")
            return None
        
        # Step 2: Create profile with the authenticated user ID
        profile_data = {
            "id": user_id,  # Required field
            "name": f"Teste {name_suffix}",
            "email": email,
            "age": 30 if training_level == "avancado" else 25,
            "sex": "masculino",
            "height": 180 if training_level == "avancado" else 175,
            "weight": 85 if training_level == "avancado" else 70,
            "target_weight": 90 if training_level == "avancado" else 75,
            "goal": "bulking",
            "training_level": training_level,
            "weekly_training_frequency": 4,
            "available_time_per_session": 60
        }
        
        try:
            response = requests.post(f"{BASE_URL}/user/profile", json=profile_data, headers=HEADERS)
            
            if response.status_code == 200:
                profile = response.json()
                self.log_test(f"Create {training_level.upper()} profile", True, 
                            f"TDEE: {profile.get('tdee')}kcal, Target: {profile.get('target_calories')}kcal")
                return {"user_id": user_id, "profile": profile}
            else:
                self.log_test(f"Create {training_level.upper()} profile", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test(f"Create {training_level.upper()} profile", False, f"Exception: {str(e)}")
            return None
    
    def generate_workout(self, user_id: str, training_level: str) -> Dict[str, Any]:
        """Generate workout for user"""
        try:
            response = requests.post(f"{BASE_URL}/workout/generate?user_id={user_id}", headers=HEADERS)
            
            if response.status_code == 200:
                workout = response.json()
                workouts_count = len(workout.get("workouts", []))
                self.log_test(f"Generate {training_level.upper()} workout", True, 
                            f"Generated {workouts_count} workout days")
                return workout
            else:
                self.log_test(f"Generate {training_level.upper()} workout", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test(f"Generate {training_level.upper()} workout", False, f"Exception: {str(e)}")
            return None
    
    def validate_sets_limit(self, workout: Dict[str, Any], training_level: str) -> bool:
        """Validate that ALL exercises have ≤ 4 sets"""
        try:
            workouts = workout.get("workouts", [])
            if not workouts:
                self.log_test(f"{training_level.upper()} - Sets ≤ 4 validation", False, "No workouts found")
                return False
            
            violations = []
            total_exercises = 0
            
            for day_idx, day in enumerate(workouts):
                exercises = day.get("exercises", [])
                for ex_idx, exercise in enumerate(exercises):
                    total_exercises += 1
                    sets = exercise.get("sets", 0)
                    
                    if sets > 4:
                        violations.append(f"Day {day_idx+1}, Exercise {ex_idx+1} ({exercise.get('name', 'Unknown')}): {sets} sets")
            
            if violations:
                details = f"Found {len(violations)} violations out of {total_exercises} exercises:\n" + "\n".join(violations[:5])
                if len(violations) > 5:
                    details += f"\n... and {len(violations) - 5} more violations"
                self.log_test(f"{training_level.upper()} - Sets ≤ 4 validation", False, details)
                return False
            else:
                self.log_test(f"{training_level.upper()} - Sets ≤ 4 validation", True, 
                            f"All {total_exercises} exercises have ≤ 4 sets")
                return True
                
        except Exception as e:
            self.log_test(f"{training_level.upper()} - Sets ≤ 4 validation", False, f"Exception: {str(e)}")
            return False
    
    def validate_reps_format(self, workout: Dict[str, Any], training_level: str, expected_reps: str) -> bool:
        """Validate that exercises have the expected reps format"""
        try:
            workouts = workout.get("workouts", [])
            if not workouts:
                self.log_test(f"{training_level.upper()} - Reps validation", False, "No workouts found")
                return False
            
            violations = []
            total_exercises = 0
            correct_reps = 0
            
            for day_idx, day in enumerate(workouts):
                exercises = day.get("exercises", [])
                for ex_idx, exercise in enumerate(exercises):
                    total_exercises += 1
                    reps = exercise.get("reps", "")
                    
                    if reps == expected_reps:
                        correct_reps += 1
                    else:
                        violations.append(f"Day {day_idx+1}, Exercise {ex_idx+1} ({exercise.get('name', 'Unknown')}): got '{reps}', expected '{expected_reps}'")
            
            if violations:
                details = f"Found {len(violations)} violations out of {total_exercises} exercises (only {correct_reps} correct):\n" + "\n".join(violations[:5])
                if len(violations) > 5:
                    details += f"\n... and {len(violations) - 5} more violations"
                self.log_test(f"{training_level.upper()} - Reps '{expected_reps}' validation", False, details)
                return False
            else:
                self.log_test(f"{training_level.upper()} - Reps '{expected_reps}' validation", True, 
                            f"All {total_exercises} exercises have reps='{expected_reps}'")
                return True
                
        except Exception as e:
            self.log_test(f"{training_level.upper()} - Reps validation", False, f"Exception: {str(e)}")
            return False
    
    def compare_workout_plans(self, advanced_workout: Dict[str, Any], beginner_workout: Dict[str, Any]) -> bool:
        """Compare advanced vs beginner workout plans to ensure they're different"""
        try:
            adv_workouts = advanced_workout.get("workouts", [])
            beg_workouts = beginner_workout.get("workouts", [])
            
            if not adv_workouts or not beg_workouts:
                self.log_test("Advanced vs Beginner comparison", False, "Missing workout data")
                return False
            
            # Count total exercises per level
            adv_total_exercises = sum(len(day.get("exercises", [])) for day in adv_workouts)
            beg_total_exercises = sum(len(day.get("exercises", [])) for day in beg_workouts)
            
            # Get exercise names for comparison
            adv_exercises = []
            beg_exercises = []
            
            for day in adv_workouts:
                for exercise in day.get("exercises", []):
                    adv_exercises.append(exercise.get("name", ""))
            
            for day in beg_workouts:
                for exercise in day.get("exercises", []):
                    beg_exercises.append(exercise.get("name", ""))
            
            # Calculate differences
            exercise_diff = abs(adv_total_exercises - beg_total_exercises)
            common_exercises = len(set(adv_exercises) & set(beg_exercises))
            total_unique_exercises = len(set(adv_exercises) | set(beg_exercises))
            
            # Plans should be different if:
            # 1. Different number of exercises, OR
            # 2. Less than 80% overlap in exercise selection
            overlap_percentage = (common_exercises / total_unique_exercises * 100) if total_unique_exercises > 0 else 100
            
            is_different = exercise_diff > 0 or overlap_percentage < 80
            
            details = f"Advanced: {adv_total_exercises} exercises, Beginner: {beg_total_exercises} exercises, " \
                     f"Exercise overlap: {overlap_percentage:.1f}% ({common_exercises}/{total_unique_exercises})"
            
            self.log_test("Advanced vs Beginner comparison", is_different, details)
            return is_different
            
        except Exception as e:
            self.log_test("Advanced vs Beginner comparison", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete test suite for workout generation bug fixes"""
        print("=" * 80)
        print("🏋️ LAF WORKOUT GENERATION BUG FIXES VALIDATION")
        print("=" * 80)
        print(f"Testing against: {BASE_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test 1 & 2: Create profiles
        print("📋 STEP 1: Creating test profiles...")
        advanced_data = self.create_test_profile("avancado", "Avancado")
        beginner_data = self.create_test_profile("iniciante", "Iniciante")
        
        if not advanced_data or not beginner_data:
            print("❌ CRITICAL: Failed to create test profiles. Aborting tests.")
            return False
        
        print()
        
        # Test 3 & 4: Generate workouts
        print("🏋️ STEP 2: Generating workouts...")
        advanced_workout = self.generate_workout(advanced_data["user_id"], "avancado")
        beginner_workout = self.generate_workout(beginner_data["user_id"], "iniciante")
        
        if not advanced_workout or not beginner_workout:
            print("❌ CRITICAL: Failed to generate workouts. Aborting validation tests.")
            return False
        
        print()
        
        # Test 5-8: Validation tests
        print("🔍 STEP 3: Validating bug fixes...")
        
        # Validate sets limit (≤ 4 sets for all exercises)
        advanced_sets_ok = self.validate_sets_limit(advanced_workout, "avancado")
        beginner_sets_ok = self.validate_sets_limit(beginner_workout, "iniciante")
        
        # Validate reps format
        advanced_reps_ok = self.validate_reps_format(advanced_workout, "avancado", "10-12")
        beginner_reps_ok = self.validate_reps_format(beginner_workout, "iniciante", "10-12")
        
        # Compare workout plans
        plans_different = self.compare_workout_plans(advanced_workout, beginner_workout)
        
        print()
        
        # Summary
        print("=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        for result in self.test_results:
            print(result)
        
        print()
        print(f"🎯 OVERALL RESULTS: {self.passed_tests}/{self.total_tests} tests passed ({self.passed_tests/self.total_tests*100:.1f}%)")
        
        # Critical success criteria
        critical_tests_passed = (
            advanced_sets_ok and beginner_sets_ok and  # Sets ≤ 4
            advanced_reps_ok and beginner_reps_ok and  # Correct reps
            plans_different  # Plans are different
        )
        
        if critical_tests_passed:
            print("🎉 SUCCESS: All critical bug fixes validated!")
            return True
        else:
            print("❌ FAILURE: Some critical bug fixes are not working properly.")
            return False

def main():
    """Main test execution"""
    test_suite = WorkoutTestSuite()
    success = test_suite.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()