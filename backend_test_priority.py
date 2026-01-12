#!/usr/bin/env python3
"""
LAF Backend Testing - Priority Tests
Testing workout generation with variable time and diet generation with meal count
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BASE_URL = "https://workoutgenerator.preview.emergentagent.com/api"

class LAFBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_users = []
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def create_test_user(self, email_suffix=""):
        """Create a test user for testing"""
        timestamp = int(time.time())
        email = f"teste_treino{email_suffix}_{timestamp}@test.com"
        password = "teste123456"
        
        self.log(f"Creating test user: {email}")
        
        # Signup
        signup_data = {
            "email": email,
            "password": password
        }
        
        response = self.session.post(f"{self.base_url}/auth/signup", json=signup_data)
        if response.status_code != 200:
            self.log(f"❌ Signup failed: {response.status_code} - {response.text}")
            return None
            
        signup_result = response.json()
        user_id = signup_result.get("user_id")
        token = signup_result.get("access_token")  # Changed from "token" to "access_token"
        
        if not user_id or not token:
            self.log(f"❌ Signup response missing user_id or access_token: {signup_result}")
            return None
            
        self.log(f"✅ User created: {user_id}")
        
        # Set auth header
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        user_data = {
            "user_id": user_id,
            "email": email,
            "token": token
        }
        self.test_users.append(user_data)
        
        return user_data
        
    def create_user_profile(self, user_id, available_time_per_session=30, goal="bulking"):
        """Create user profile with specific training time"""
        self.log(f"Creating profile for user {user_id} with {available_time_per_session}min sessions")
        
        profile_data = {
            "id": user_id,
            "name": "Teste Treino",
            "age": 30,
            "sex": "masculino",
            "height": 175,
            "weight": 80,
            "training_level": "avancado",
            "weekly_training_frequency": 5,
            "available_time_per_session": available_time_per_session,
            "goal": goal
        }
        
        response = self.session.post(f"{self.base_url}/user/profile", json=profile_data)
        if response.status_code != 200:
            self.log(f"❌ Profile creation failed: {response.status_code} - {response.text}")
            return None
            
        profile = response.json()
        self.log(f"✅ Profile created with TDEE: {profile.get('tdee')}kcal, Target: {profile.get('target_calories')}kcal")
        return profile
        
    def test_workout_generation_time_variation(self):
        """Test workout generation with different time durations"""
        self.log("\n🏋️ TESTING WORKOUT GENERATION WITH TIME VARIATION")
        
        test_scenarios = [
            {"time": 30, "expected_exercises": (3, 4), "expected_sets": (3, 4)},
            {"time": 60, "expected_exercises": (5, 6), "expected_sets": (3, 4)},
            {"time": 90, "expected_exercises": (6, 8), "expected_sets": (3, 4)}
        ]
        
        results = []
        
        for i, scenario in enumerate(test_scenarios):
            self.log(f"\n--- Scenario {i+1}: {scenario['time']} minutes ---")
            
            # Create user for this scenario
            user = self.create_test_user(f"_time_{scenario['time']}")
            if not user:
                results.append({"scenario": scenario, "success": False, "error": "User creation failed"})
                continue
                
            # Create profile with specific time
            profile = self.create_user_profile(user["user_id"], scenario["time"])
            if not profile:
                results.append({"scenario": scenario, "success": False, "error": "Profile creation failed"})
                continue
                
            # Generate workout
            self.log(f"Generating workout for {scenario['time']}min sessions...")
            response = self.session.post(f"{self.base_url}/workout/generate?user_id={user['user_id']}")
            
            if response.status_code != 200:
                self.log(f"❌ Workout generation failed: {response.status_code} - {response.text}")
                results.append({"scenario": scenario, "success": False, "error": f"API error: {response.status_code}"})
                continue
                
            workout = response.json()
            
            # Analyze workout - Check exercises PER DAY, not total
            workout_days = workout.get("workout_days", [])
            
            # For time variation test, we should check the average exercises per day
            # or check if any day exceeds the expected range
            exercises_per_day = []
            sets_per_day = []
            
            for day in workout_days:
                exercises = day.get("exercises", [])
                day_exercises = len(exercises)
                day_sets = 0
                
                for exercise in exercises:
                    sets_count = exercise.get("sets", 0)
                    day_sets += sets_count
                
                exercises_per_day.append(day_exercises)
                sets_per_day.append(day_sets)
            
            # Check if the workout structure respects time constraints
            # Use the maximum exercises per day as the test metric
            max_exercises_per_day = max(exercises_per_day) if exercises_per_day else 0
            avg_exercises_per_day = sum(exercises_per_day) / len(exercises_per_day) if exercises_per_day else 0
            max_sets_per_day = max(sets_per_day) if sets_per_day else 0
            
            # Check if meets criteria (per day, not total)
            min_ex, max_ex = scenario["expected_exercises"]
            min_sets, max_sets = scenario["expected_sets"]
            
            exercises_ok = min_ex <= max_exercises_per_day <= max_ex
            sets_ok = max_sets_per_day >= min_sets
            valid_sets_ok = max_sets_per_day >= 2  # At least 2 valid sets per day
            
            result = {
                "scenario": scenario,
                "success": exercises_ok and sets_ok and valid_sets_ok,
                "max_exercises_per_day": max_exercises_per_day,
                "avg_exercises_per_day": round(avg_exercises_per_day, 1),
                "max_sets_per_day": max_sets_per_day,
                "exercises_per_day": exercises_per_day,
                "sets_per_day": sets_per_day,
                "exercises_ok": exercises_ok,
                "sets_ok": sets_ok,
                "valid_sets_ok": valid_sets_ok,
                "total_days": len(workout_days)
            }
            
            results.append(result)
            
            if result["success"]:
                self.log(f"✅ {scenario['time']}min: Max {max_exercises_per_day} exercises/day (avg {avg_exercises_per_day}), Max {max_sets_per_day} sets/day across {len(workout_days)} days")
            else:
                self.log(f"❌ {scenario['time']}min: Max {max_exercises_per_day} exercises/day (expected {min_ex}-{max_ex}), Max {max_sets_per_day} sets/day (expected ≥{min_sets}) across {len(workout_days)} days")
                
        return results
        
    def test_diet_generation_meal_count(self):
        """Test diet generation with different meal counts"""
        self.log("\n🍽️ TESTING DIET GENERATION WITH MEAL COUNT")
        
        # Create user for diet testing
        user = self.create_test_user("_diet")
        if not user:
            return {"success": False, "error": "User creation failed"}
            
        # Create profile
        profile = self.create_user_profile(user["user_id"], goal="bulking")
        if not profile:
            return {"success": False, "error": "Profile creation failed"}
            
        user_id = user["user_id"]
        
        # Test settings endpoints first
        self.log("\n--- Testing Settings Endpoints ---")
        
        # 1. GET settings (should return default or create)
        self.log("Testing GET /api/user/settings/{user_id}")
        response = self.session.get(f"{self.base_url}/user/settings/{user_id}")
        
        if response.status_code == 200:
            settings = response.json()
            self.log(f"✅ GET settings successful: meal_count = {settings.get('meal_count', 'not found')}")
        elif response.status_code == 404:
            self.log("ℹ️ Settings not found (expected for new user)")
            settings = None
        else:
            self.log(f"❌ GET settings failed: {response.status_code} - {response.text}")
            return {"success": False, "error": f"GET settings failed: {response.status_code}"}
            
        # 2. PATCH settings to set meal_count = 4
        self.log("Testing PATCH /api/user/settings/{user_id} with meal_count: 4")
        settings_update = {"meal_count": 4}
        response = self.session.patch(f"{self.base_url}/user/settings/{user_id}", json=settings_update)
        
        if response.status_code != 200:
            self.log(f"❌ PATCH settings failed: {response.status_code} - {response.text}")
            return {"success": False, "error": f"PATCH settings failed: {response.status_code}"}
            
        updated_settings = response.json()
        saved_meal_count = updated_settings.get("meal_count")
        
        if saved_meal_count == 4:
            self.log(f"✅ Settings saved successfully: meal_count = {saved_meal_count}")
        else:
            self.log(f"❌ Settings not saved correctly: expected meal_count=4, got {saved_meal_count}")
            return {"success": False, "error": f"meal_count not saved correctly: {saved_meal_count}"}
            
        # 3. Generate diet and verify meal count
        self.log("Generating diet to verify meal_count is used...")
        response = self.session.post(f"{self.base_url}/diet/generate?user_id={user_id}")
        
        if response.status_code != 200:
            self.log(f"❌ Diet generation failed: {response.status_code} - {response.text}")
            return {"success": False, "error": f"Diet generation failed: {response.status_code}"}
            
        diet = response.json()
        meals = diet.get("meals", [])
        actual_meal_count = len(meals)
        
        if actual_meal_count == 4:
            self.log(f"✅ Diet generated with correct meal count: {actual_meal_count} meals")
            
            # Show meal details
            for i, meal in enumerate(meals):
                meal_name = meal.get("name", f"Meal {i+1}")
                meal_time = meal.get("time", "N/A")
                foods_count = len(meal.get("foods", []))
                self.log(f"   Meal {i+1}: {meal_name} ({meal_time}) - {foods_count} foods")
                
            return {
                "success": True,
                "meal_count_set": 4,
                "actual_meal_count": actual_meal_count,
                "meals": meals
            }
        else:
            self.log(f"❌ Diet generated with wrong meal count: expected 4, got {actual_meal_count}")
            return {
                "success": False,
                "error": f"Wrong meal count: expected 4, got {actual_meal_count}",
                "meal_count_set": 4,
                "actual_meal_count": actual_meal_count
            }
            
    def test_settings_endpoints(self):
        """Test settings endpoints independently"""
        self.log("\n⚙️ TESTING SETTINGS ENDPOINTS")
        
        # Create user for settings testing
        user = self.create_test_user("_settings")
        if not user:
            return {"success": False, "error": "User creation failed"}
            
        user_id = user["user_id"]
        
        # Create profile first (required for settings)
        profile = self.create_user_profile(user_id)
        if not profile:
            return {"success": False, "error": "Profile creation failed"}
        
        results = {
            "get_settings": None,
            "patch_settings": None,
            "get_after_patch": None
        }
        
        # Test GET settings
        self.log("Testing GET /api/user/settings/{user_id}")
        response = self.session.get(f"{self.base_url}/user/settings/{user_id}")
        
        if response.status_code == 200:
            settings = response.json()
            results["get_settings"] = {"success": True, "data": settings}
            self.log(f"✅ GET settings: {settings.get('meal_count', 'default')}")
        elif response.status_code == 404:
            results["get_settings"] = {"success": True, "data": None, "note": "No settings found (expected)"}
            self.log("ℹ️ No settings found (expected for new user)")
        else:
            results["get_settings"] = {"success": False, "error": f"Status {response.status_code}: {response.text}"}
            self.log(f"❌ GET settings failed: {response.status_code}")
            
        # Test PATCH settings
        self.log("Testing PATCH /api/user/settings/{user_id}")
        patch_data = {"meal_count": 5}
        response = self.session.patch(f"{self.base_url}/user/settings/{user_id}", json=patch_data)
        
        if response.status_code == 200:
            patched_settings = response.json()
            results["patch_settings"] = {"success": True, "data": patched_settings}
            self.log(f"✅ PATCH settings: meal_count = {patched_settings.get('meal_count')}")
        else:
            results["patch_settings"] = {"success": False, "error": f"Status {response.status_code}: {response.text}"}
            self.log(f"❌ PATCH settings failed: {response.status_code}")
            
        # Test GET after PATCH
        self.log("Testing GET after PATCH to verify persistence")
        response = self.session.get(f"{self.base_url}/user/settings/{user_id}")
        
        if response.status_code == 200:
            final_settings = response.json()
            results["get_after_patch"] = {"success": True, "data": final_settings}
            final_meal_count = final_settings.get('meal_count')
            if final_meal_count == 5:
                self.log(f"✅ Settings persisted correctly: meal_count = {final_meal_count}")
            else:
                self.log(f"❌ Settings not persisted: expected 5, got {final_meal_count}")
                results["get_after_patch"]["success"] = False
        else:
            results["get_after_patch"] = {"success": False, "error": f"Status {response.status_code}: {response.text}"}
            self.log(f"❌ GET after PATCH failed: {response.status_code}")
            
        return results
        
    def run_all_tests(self):
        """Run all priority tests"""
        self.log("🚀 STARTING LAF BACKEND PRIORITY TESTS")
        self.log(f"Backend URL: {self.base_url}")
        
        results = {
            "workout_time_variation": None,
            "diet_meal_count": None,
            "settings_endpoints": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Test 1: Workout generation with time variation
            results["workout_time_variation"] = self.test_workout_generation_time_variation()
            
            # Test 2: Diet generation with meal count
            results["diet_meal_count"] = self.test_diet_generation_meal_count()
            
            # Test 3: Settings endpoints
            results["settings_endpoints"] = self.test_settings_endpoints()
            
        except Exception as e:
            self.log(f"❌ Test execution failed: {str(e)}")
            results["error"] = str(e)
            
        return results
        
    def print_summary(self, results):
        """Print test summary"""
        self.log("\n" + "="*60)
        self.log("📊 TEST SUMMARY")
        self.log("="*60)
        
        # Workout time variation summary
        workout_results = results.get("workout_time_variation", [])
        if workout_results:
            self.log("\n🏋️ WORKOUT TIME VARIATION:")
            for result in workout_results:
                scenario = result["scenario"]
                if result.get("success"):
                    max_ex = result.get("max_exercises_per_day", "N/A")
                    avg_ex = result.get("avg_exercises_per_day", "N/A")
                    max_sets = result.get("max_sets_per_day", "N/A")
                    days = result.get("total_days", "N/A")
                    self.log(f"  ✅ {scenario['time']}min: Max {max_ex} exercises/day (avg {avg_ex}) across {days} days")
                else:
                    error_msg = result.get("error", "Criteria not met")
                    max_ex = result.get("max_exercises_per_day", "N/A")
                    expected = scenario.get("expected_exercises", [])
                    if expected:
                        self.log(f"  ❌ {scenario['time']}min: Max {max_ex} exercises/day (expected {expected[0]}-{expected[1]})")
                    else:
                        self.log(f"  ❌ {scenario['time']}min: {error_msg}")
        
        # Diet meal count summary
        diet_result = results.get("diet_meal_count")
        if diet_result:
            self.log("\n🍽️ DIET MEAL COUNT:")
            if diet_result.get("success"):
                self.log(f"  ✅ meal_count=4 → {diet_result['actual_meal_count']} meals generated")
            else:
                error_msg = diet_result.get("error", "Unknown error")
                self.log(f"  ❌ meal_count=4 → {error_msg}")
                
        # Settings endpoints summary
        settings_result = results.get("settings_endpoints")
        if settings_result:
            self.log("\n⚙️ SETTINGS ENDPOINTS:")
            get_ok = settings_result.get("get_settings", {}).get("success", False)
            patch_ok = settings_result.get("patch_settings", {}).get("success", False)
            persist_ok = settings_result.get("get_after_patch", {}).get("success", False)
            
            self.log(f"  {'✅' if get_ok else '❌'} GET /api/user/settings/{{user_id}}")
            self.log(f"  {'✅' if patch_ok else '❌'} PATCH /api/user/settings/{{user_id}}")
            self.log(f"  {'✅' if persist_ok else '❌'} Settings persistence")

if __name__ == "__main__":
    tester = LAFBackendTester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    # Save results to file
    with open("/app/test_results_priority.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Detailed results saved to: /app/test_results_priority.json")