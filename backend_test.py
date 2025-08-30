#!/usr/bin/env python3
"""
DevTinder Backend API Test Suite
Tests all backend functionality including authentication, profiles, friend requests, feed, and chat.
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://tech-swipe.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class DevTinderAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.test_users = []
        self.tokens = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    token: Optional[str] = None) -> requests.Response:
        """Make HTTP request with optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            self.log(f"{method} {endpoint} -> {response.status_code}")
            return response
        except Exception as e:
            self.log(f"Request failed: {str(e)}", "ERROR")
            raise
            
    def test_user_signup(self) -> bool:
        """Test user registration functionality"""
        self.log("=== Testing User Signup ===")
        
        # Test data for multiple users
        test_users_data = [
            {
                "name": "Alice Johnson",
                "email": "alice.johnson@techdev.com",
                "password": "SecurePass123!"
            },
            {
                "name": "Bob Smith", 
                "email": "bob.smith@codemaster.com",
                "password": "DevPassword456!"
            },
            {
                "name": "Carol Davis",
                "email": "carol.davis@fullstack.dev",
                "password": "ReactNode789!"
            }
        ]
        
        success_count = 0
        
        for user_data in test_users_data:
            try:
                response = self.make_request("POST", "/auth/signup", user_data)
                
                if response.status_code == 200:
                    result = response.json()
                    if "access_token" in result and "user" in result:
                        self.log(f"✅ Signup successful for {user_data['email']}")
                        self.test_users.append(user_data)
                        self.tokens[user_data['email']] = result["access_token"]
                        success_count += 1
                    else:
                        self.log(f"❌ Signup response missing required fields for {user_data['email']}", "ERROR")
                else:
                    self.log(f"❌ Signup failed for {user_data['email']}: {response.status_code} - {response.text}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ Signup exception for {user_data['email']}: {str(e)}", "ERROR")
        
        # Test duplicate email registration
        try:
            duplicate_response = self.make_request("POST", "/auth/signup", test_users_data[0])
            if duplicate_response.status_code == 400:
                self.log("✅ Duplicate email properly rejected")
                success_count += 1
            else:
                self.log(f"❌ Duplicate email not properly handled: {duplicate_response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ Duplicate email test failed: {str(e)}", "ERROR")
            
        return success_count >= len(test_users_data)
        
    def test_user_login(self) -> bool:
        """Test user login functionality"""
        self.log("=== Testing User Login ===")
        
        success_count = 0
        
        for user_data in self.test_users:
            try:
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                
                response = self.make_request("POST", "/auth/login", login_data)
                
                if response.status_code == 200:
                    result = response.json()
                    if "access_token" in result and "user" in result:
                        self.log(f"✅ Login successful for {user_data['email']}")
                        # Update token in case it changed
                        self.tokens[user_data['email']] = result["access_token"]
                        success_count += 1
                    else:
                        self.log(f"❌ Login response missing required fields for {user_data['email']}", "ERROR")
                else:
                    self.log(f"❌ Login failed for {user_data['email']}: {response.status_code} - {response.text}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ Login exception for {user_data['email']}: {str(e)}", "ERROR")
        
        # Test invalid credentials
        try:
            invalid_login = {
                "email": "nonexistent@test.com",
                "password": "wrongpassword"
            }
            response = self.make_request("POST", "/auth/login", invalid_login)
            if response.status_code == 401:
                self.log("✅ Invalid credentials properly rejected")
                success_count += 1
            else:
                self.log(f"❌ Invalid credentials not properly handled: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ Invalid credentials test failed: {str(e)}", "ERROR")
            
        return success_count >= len(self.test_users)
        
    def test_profile_management(self) -> bool:
        """Test profile GET and PUT operations"""
        self.log("=== Testing Profile Management ===")
        
        if not self.test_users:
            self.log("❌ No test users available for profile testing", "ERROR")
            return False
            
        user_email = self.test_users[0]["email"]
        token = self.tokens.get(user_email)
        
        if not token:
            self.log("❌ No token available for profile testing", "ERROR")
            return False
            
        success_count = 0
        
        # Test GET profile
        try:
            response = self.make_request("GET", "/profile", token=token)
            if response.status_code == 200:
                profile = response.json()
                if "id" in profile and "name" in profile and "email" in profile:
                    self.log("✅ Profile GET successful")
                    success_count += 1
                else:
                    self.log(f"❌ Profile GET missing required fields", "ERROR")
            else:
                self.log(f"❌ Profile GET failed: {response.status_code} - {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Profile GET exception: {str(e)}", "ERROR")
            
        # Test PUT profile update
        try:
            update_data = {
                "name": "Alice Johnson Updated",
                "bio": "Full-stack developer passionate about React and Node.js",
                "skills": ["JavaScript", "Python", "React", "Node.js", "MongoDB"],
                "interests": ["Web Development", "Machine Learning", "Open Source"],
                "profile_pic": "https://example.com/alice-profile.jpg"
            }
            
            response = self.make_request("PUT", "/profile", update_data, token=token)
            if response.status_code == 200:
                updated_profile = response.json()
                if (updated_profile.get("bio") == update_data["bio"] and 
                    updated_profile.get("skills") == update_data["skills"]):
                    self.log("✅ Profile UPDATE successful")
                    success_count += 1
                else:
                    self.log(f"❌ Profile UPDATE data not properly saved", "ERROR")
            else:
                self.log(f"❌ Profile UPDATE failed: {response.status_code} - {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Profile UPDATE exception: {str(e)}", "ERROR")
            
        # Test unauthorized access
        try:
            response = self.make_request("GET", "/profile")  # No token
            if response.status_code == 401 or response.status_code == 403:
                self.log("✅ Unauthorized access properly rejected")
                success_count += 1
            else:
                self.log(f"❌ Unauthorized access not properly handled: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ Unauthorized access test failed: {str(e)}", "ERROR")
            
        return success_count >= 2
        
    def test_friend_request_system(self) -> bool:
        """Test friend request sending and accepting with constraints"""
        self.log("=== Testing Friend Request System ===")
        
        if len(self.test_users) < 2:
            self.log("❌ Need at least 2 users for friend request testing", "ERROR")
            return False
            
        user1_email = self.test_users[0]["email"]
        user2_email = self.test_users[1]["email"]
        token1 = self.tokens.get(user1_email)
        token2 = self.tokens.get(user2_email)
        
        if not token1 or not token2:
            self.log("❌ Missing tokens for friend request testing", "ERROR")
            return False
            
        success_count = 0
        
        # Get user IDs first
        try:
            response1 = self.make_request("GET", "/profile", token=token1)
            response2 = self.make_request("GET", "/profile", token=token2)
            
            if response1.status_code == 200 and response2.status_code == 200:
                user1_id = response1.json()["id"]
                user2_id = response2.json()["id"]
                self.log(f"Got user IDs: {user1_id[:8]}... and {user2_id[:8]}...")
            else:
                self.log("❌ Failed to get user IDs for friend request testing", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception getting user IDs: {str(e)}", "ERROR")
            return False
            
        # Test sending friend request
        try:
            response = self.make_request("POST", f"/users/{user2_id}/friend-request", token=token1)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") == True:
                    self.log("✅ Friend request sent successfully")
                    success_count += 1
                else:
                    self.log(f"❌ Friend request failed: {result.get('message')}", "ERROR")
            else:
                self.log(f"❌ Friend request failed: {response.status_code} - {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Friend request exception: {str(e)}", "ERROR")
            
        # Test duplicate friend request (should fail)
        try:
            response = self.make_request("POST", f"/users/{user2_id}/friend-request", token=token1)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") == False and "already sent" in result.get("message", "").lower():
                    self.log("✅ Duplicate friend request properly rejected")
                    success_count += 1
                else:
                    self.log(f"❌ Duplicate friend request not properly handled", "ERROR")
            else:
                self.log(f"❌ Duplicate friend request test failed: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ Duplicate friend request test exception: {str(e)}", "ERROR")
            
        # Test self friend request (should fail)
        try:
            response = self.make_request("POST", f"/users/{user1_id}/friend-request", token=token1)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") == False and "yourself" in result.get("message", "").lower():
                    self.log("✅ Self friend request properly rejected")
                    success_count += 1
                else:
                    self.log(f"❌ Self friend request not properly handled", "ERROR")
            else:
                self.log(f"❌ Self friend request test failed: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ Self friend request test exception: {str(e)}", "ERROR")
            
        # Test accepting friend request
        try:
            response = self.make_request("POST", f"/users/{user1_id}/accept-request", token=token2)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") == True:
                    self.log("✅ Friend request accepted successfully")
                    success_count += 1
                else:
                    self.log(f"❌ Friend request acceptance failed: {result.get('message')}", "ERROR")
            else:
                self.log(f"❌ Friend request acceptance failed: {response.status_code} - {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Friend request acceptance exception: {str(e)}", "ERROR")
            
        return success_count >= 3
        
    def test_feed_endpoint(self) -> bool:
        """Test feed endpoint that excludes connected users"""
        self.log("=== Testing Feed Endpoint ===")
        
        if not self.test_users:
            self.log("❌ No test users available for feed testing", "ERROR")
            return False
            
        user_email = self.test_users[0]["email"]
        token = self.tokens.get(user_email)
        
        if not token:
            self.log("❌ No token available for feed testing", "ERROR")
            return False
            
        success_count = 0
        
        try:
            response = self.make_request("GET", "/feed", token=token)
            if response.status_code == 200:
                feed_users = response.json()
                if isinstance(feed_users, list):
                    self.log(f"✅ Feed endpoint successful, returned {len(feed_users)} users")
                    success_count += 1
                    
                    # Verify feed doesn't include current user
                    current_user_response = self.make_request("GET", "/profile", token=token)
                    if current_user_response.status_code == 200:
                        current_user_id = current_user_response.json()["id"]
                        user_ids_in_feed = [user["id"] for user in feed_users]
                        if current_user_id not in user_ids_in_feed:
                            self.log("✅ Feed properly excludes current user")
                            success_count += 1
                        else:
                            self.log("❌ Feed includes current user (should be excluded)", "ERROR")
                else:
                    self.log(f"❌ Feed endpoint returned non-list response", "ERROR")
            else:
                self.log(f"❌ Feed endpoint failed: {response.status_code} - {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Feed endpoint exception: {str(e)}", "ERROR")
            
        # Test unauthorized access
        try:
            response = self.make_request("GET", "/feed")  # No token
            if response.status_code == 401 or response.status_code == 403:
                self.log("✅ Unauthorized feed access properly rejected")
                success_count += 1
            else:
                self.log(f"❌ Unauthorized feed access not properly handled: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ Unauthorized feed access test failed: {str(e)}", "ERROR")
            
        return success_count >= 2
        
    def test_connections_endpoint(self) -> bool:
        """Test connections endpoint"""
        self.log("=== Testing Connections Endpoint ===")
        
        if len(self.test_users) < 2:
            self.log("❌ Need at least 2 users for connections testing", "ERROR")
            return False
            
        user1_email = self.test_users[0]["email"]
        token1 = self.tokens.get(user1_email)
        
        if not token1:
            self.log("❌ No token available for connections testing", "ERROR")
            return False
            
        success_count = 0
        
        try:
            response = self.make_request("GET", "/connections", token=token1)
            if response.status_code == 200:
                connections = response.json()
                if isinstance(connections, list):
                    self.log(f"✅ Connections endpoint successful, returned {len(connections)} connections")
                    success_count += 1
                    
                    # Should have at least 1 connection from friend request test
                    if len(connections) >= 1:
                        self.log("✅ Connections list contains expected connections")
                        success_count += 1
                    else:
                        self.log("⚠️ No connections found (may be expected if friend request test failed)")
                else:
                    self.log(f"❌ Connections endpoint returned non-list response", "ERROR")
            else:
                self.log(f"❌ Connections endpoint failed: {response.status_code} - {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Connections endpoint exception: {str(e)}", "ERROR")
            
        return success_count >= 1
        
    def test_chat_endpoints(self) -> bool:
        """Test chat history and send message endpoints"""
        self.log("=== Testing Chat Endpoints ===")
        
        if len(self.test_users) < 2:
            self.log("❌ Need at least 2 users for chat testing", "ERROR")
            return False
            
        user1_email = self.test_users[0]["email"]
        user2_email = self.test_users[1]["email"]
        token1 = self.tokens.get(user1_email)
        token2 = self.tokens.get(user2_email)
        
        if not token1 or not token2:
            self.log("❌ Missing tokens for chat testing", "ERROR")
            return False
            
        success_count = 0
        
        # Get user IDs
        try:
            response1 = self.make_request("GET", "/profile", token=token1)
            response2 = self.make_request("GET", "/profile", token=token2)
            
            if response1.status_code == 200 and response2.status_code == 200:
                user1_id = response1.json()["id"]
                user2_id = response2.json()["id"]
            else:
                self.log("❌ Failed to get user IDs for chat testing", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception getting user IDs for chat: {str(e)}", "ERROR")
            return False
            
        # Test sending a message
        try:
            message_data = {
                "receiver_id": user2_id,
                "text": "Hello! This is a test message from the API test suite."
            }
            
            response = self.make_request("POST", "/chat/send", message_data, token=token1)
            if response.status_code == 200:
                message = response.json()
                if "id" in message and "text" in message and "sender_id" in message:
                    self.log("✅ Message sent successfully")
                    success_count += 1
                else:
                    self.log(f"❌ Message response missing required fields", "ERROR")
            else:
                self.log(f"❌ Message send failed: {response.status_code} - {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Message send exception: {str(e)}", "ERROR")
            
        # Test getting chat history
        try:
            response = self.make_request("GET", f"/chat/{user2_id}", token=token1)
            if response.status_code == 200:
                chat_history = response.json()
                if isinstance(chat_history, list):
                    self.log(f"✅ Chat history retrieved successfully, {len(chat_history)} messages")
                    success_count += 1
                    
                    # Should have at least 1 message from previous test
                    if len(chat_history) >= 1:
                        self.log("✅ Chat history contains expected messages")
                        success_count += 1
                else:
                    self.log(f"❌ Chat history returned non-list response", "ERROR")
            else:
                self.log(f"❌ Chat history failed: {response.status_code} - {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Chat history exception: {str(e)}", "ERROR")
            
        # Test chat with non-connected user (should fail)
        if len(self.test_users) >= 3:
            try:
                user3_email = self.test_users[2]["email"]
                token3 = self.tokens.get(user3_email)
                if token3:
                    response3 = self.make_request("GET", "/profile", token=token3)
                    if response3.status_code == 200:
                        user3_id = response3.json()["id"]
                        
                        # Try to send message to non-connected user
                        message_data = {
                            "receiver_id": user3_id,
                            "text": "This should fail - we're not connected"
                        }
                        
                        response = self.make_request("POST", "/chat/send", message_data, token=token1)
                        if response.status_code == 403:
                            self.log("✅ Message to non-connected user properly rejected")
                            success_count += 1
                        else:
                            self.log(f"❌ Message to non-connected user not properly handled: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"❌ Non-connected user chat test exception: {str(e)}", "ERROR")
                
        return success_count >= 2
        
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all backend API tests"""
        self.log("🚀 Starting DevTinder Backend API Test Suite")
        self.log(f"Testing against: {self.base_url}")
        
        results = {}
        
        # Run tests in order
        results["signup"] = self.test_user_signup()
        results["login"] = self.test_user_login()
        results["profile_management"] = self.test_profile_management()
        results["friend_requests"] = self.test_friend_request_system()
        results["feed"] = self.test_feed_endpoint()
        results["connections"] = self.test_connections_endpoint()
        results["chat"] = self.test_chat_endpoints()
        
        # Summary
        self.log("\n" + "="*50)
        self.log("TEST RESULTS SUMMARY")
        self.log("="*50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.upper()}: {status}")
            if result:
                passed += 1
                
        self.log(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All tests passed! Backend API is working correctly.")
        else:
            self.log(f"⚠️ {total - passed} test(s) failed. Check logs above for details.")
            
        return results

def main():
    """Main test execution"""
    tester = DevTinderAPITester()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    all_passed = all(results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())