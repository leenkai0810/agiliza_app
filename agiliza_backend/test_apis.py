#!/usr/bin/env python3
"""
Automated API Testing Script
Run this script to test all API endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/auth"
HEADERS = {"Content-Type": "application/json"}

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Global tokens
ACCESS_TOKEN = None
REFRESH_TOKEN = None
USER_EMAIL = f"testuser{int(time.time())}@example.com"


def print_section(title):
    """Print a section header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_success(message):
    """Print success message"""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message"""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message"""
    print(f"{YELLOW}ℹ {message}{RESET}")


def print_request(method, endpoint, data=None):
    """Print request details"""
    print(f"{BOLD}Request:{RESET}")
    print(f"  Method: {method}")
    print(f"  Endpoint: {endpoint}")
    if data:
        print(f"  Body: {json.dumps(data, indent=4)}")
    print()


def print_response(response):
    """Print response details"""
    print(f"{BOLD}Response:{RESET}")
    print(f"  Status Code: {response.status_code}")
    try:
        print(f"  Body: {json.dumps(response.json(), indent=4)}")
    except:
        print(f"  Body: {response.text}")
    print()


def test_register():
    """Test user registration"""
    global ACCESS_TOKEN, REFRESH_TOKEN
    
    print_section("TEST 1: USER REGISTRATION")
    
    endpoint = f"{BASE_URL}/register/"
    data = {
        "email": USER_EMAIL,
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "full_name": "Test User",
        "phone": "+1234567890",
        "role": "CLIENT"
    }
    
    print_request("POST", endpoint, data)
    
    try:
        response = requests.post(endpoint, json=data, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 201:
            result = response.json()
            ACCESS_TOKEN = result['tokens']['access']
            REFRESH_TOKEN = result['tokens']['refresh']
            print_success(f"User registered successfully!")
            print_info(f"Email: {USER_EMAIL}")
            print_info(f"Access Token: {ACCESS_TOKEN[:50]}...")
            print_info(f"Refresh Token: {REFRESH_TOKEN[:50]}...")
            return True
        else:
            print_error(f"Registration failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False


def test_login():
    """Test user login"""
    global ACCESS_TOKEN, REFRESH_TOKEN
    
    print_section("TEST 2: USER LOGIN")
    
    endpoint = f"{BASE_URL}/login/"
    data = {
        "email": USER_EMAIL,
        "password": "SecurePass123!"
    }
    
    print_request("POST", endpoint, data)
    
    try:
        response = requests.post(endpoint, json=data, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            ACCESS_TOKEN = result['tokens']['access']
            REFRESH_TOKEN = result['tokens']['refresh']
            print_success("Login successful!")
            print_info(f"New Access Token: {ACCESS_TOKEN[:50]}...")
            return True
        else:
            print_error(f"Login failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False


def test_get_profile():
    """Test getting user profile"""
    global ACCESS_TOKEN
    
    print_section("TEST 3: GET USER PROFILE")
    
    endpoint = f"{BASE_URL}/profile/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {ACCESS_TOKEN}'
    
    print_request("GET", endpoint)
    print(f"{BOLD}Headers:{RESET}")
    print(f"  Authorization: Bearer {ACCESS_TOKEN[:50]}...")
    print()
    
    try:
        response = requests.get(endpoint, headers=headers)
        print_response(response)
        
        if response.status_code == 200:
            print_success("Profile retrieved successfully!")
            return True
        else:
            print_error(f"Profile retrieval failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False


def test_update_profile():
    """Test updating user profile"""
    global ACCESS_TOKEN
    
    print_section("TEST 4: UPDATE USER PROFILE (PATCH)")
    
    endpoint = f"{BASE_URL}/profile/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {ACCESS_TOKEN}'
    
    data = {
        "full_name": "Updated User Name",
        "phone": "+9876543210"
    }
    
    print_request("PATCH", endpoint, data)
    print(f"{BOLD}Headers:{RESET}")
    print(f"  Authorization: Bearer {ACCESS_TOKEN[:50]}...")
    print()
    
    try:
        response = requests.patch(endpoint, json=data, headers=headers)
        print_response(response)
        
        if response.status_code == 200:
            print_success("Profile updated successfully!")
            return True
        else:
            print_error(f"Profile update failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False


def test_refresh_token():
    """Test token refresh"""
    global ACCESS_TOKEN, REFRESH_TOKEN
    
    print_section("TEST 5: REFRESH TOKEN")
    
    endpoint = f"{BASE_URL}/token/refresh/"
    data = {
        "refresh": REFRESH_TOKEN
    }
    
    print_request("POST", endpoint, data)
    
    try:
        response = requests.post(endpoint, json=data, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            old_token = ACCESS_TOKEN
            ACCESS_TOKEN = result['access']
            print_success("Token refreshed successfully!")
            print_info(f"Old Token: {old_token[:50]}...")
            print_info(f"New Token: {ACCESS_TOKEN[:50]}...")
            return True
        else:
            print_error(f"Token refresh failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False


def test_logout():
    """Test user logout"""
    global ACCESS_TOKEN, REFRESH_TOKEN
    
    print_section("TEST 6: USER LOGOUT")
    
    endpoint = f"{BASE_URL}/logout/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {ACCESS_TOKEN}'
    
    data = {
        "refresh": REFRESH_TOKEN
    }
    
    print_request("POST", endpoint, data)
    print(f"{BOLD}Headers:{RESET}")
    print(f"  Authorization: Bearer {ACCESS_TOKEN[:50]}...")
    print()
    
    try:
        response = requests.post(endpoint, json=data, headers=headers)
        print_response(response)
        
        if response.status_code == 200:
            print_success("Logout successful!")
            return True
        else:
            print_error(f"Logout failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False


def test_invalid_token():
    """Test API with invalid token"""
    print_section("TEST 7: INVALID TOKEN HANDLING")
    
    endpoint = f"{BASE_URL}/profile/"
    headers = HEADERS.copy()
    headers['Authorization'] = 'Bearer invalid_token_here'
    
    print_request("GET", endpoint)
    print(f"{BOLD}Headers:{RESET}")
    print(f"  Authorization: Bearer invalid_token_here")
    print()
    
    try:
        response = requests.get(endpoint, headers=headers)
        print_response(response)
        
        if response.status_code == 401:
            print_success("API correctly rejected invalid token!")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False


def test_duplicate_email():
    """Test duplicate email registration"""
    print_section("TEST 8: DUPLICATE EMAIL HANDLING")
    
    endpoint = f"{BASE_URL}/register/"
    data = {
        "email": USER_EMAIL,
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "full_name": "Another User",
        "phone": "+1111111111",
        "role": "PROFESSIONAL"
    }
    
    print_request("POST", endpoint, data)
    
    try:
        response = requests.post(endpoint, json=data, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 400:
            print_success("API correctly rejected duplicate email!")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False


def test_invalid_credentials():
    """Test login with invalid credentials"""
    print_section("TEST 9: INVALID CREDENTIALS HANDLING")
    
    endpoint = f"{BASE_URL}/login/"
    data = {
        "email": USER_EMAIL,
        "password": "WrongPassword123!"
    }
    
    print_request("POST", endpoint, data)
    
    try:
        response = requests.post(endpoint, json=data, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 400:
            print_success("API correctly rejected invalid credentials!")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print(f"\n{BOLD}{BLUE}╔════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{BLUE}║     AGILIZA API - COMPREHENSIVE TEST SUITE          ║{RESET}")
    print(f"{BOLD}{BLUE}║     Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║{RESET}")
    print(f"{BOLD}{BLUE}╚════════════════════════════════════════════════════╝{RESET}\n")
    
    results = []
    
    # Run tests in sequence
    results.append(("User Registration", test_register()))
    if results[-1][1]:  # Only continue if registration succeeded
        results.append(("User Login", test_login()))
        results.append(("Get User Profile", test_get_profile()))
        results.append(("Update User Profile", test_update_profile()))
        results.append(("Refresh Token", test_refresh_token()))
        results.append(("User Logout", test_logout()))
    
    # Error handling tests (don't require valid tokens)
    results.append(("Invalid Token Handling", test_invalid_token()))
    results.append(("Duplicate Email Handling", test_duplicate_email()))
    results.append(("Invalid Credentials Handling", test_invalid_credentials()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    failed_tests = total_tests - passed_tests
    
    print(f"{BOLD}Results:{RESET}")
    for test_name, result in results:
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BOLD}Statistics:{RESET}")
    print(f"  Total Tests: {total_tests}")
    print(f"  {GREEN}Passed: {passed_tests}{RESET}")
    print(f"  {RED}Failed: {failed_tests}{RESET}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    if failed_tests == 0:
        print(f"{BOLD}{GREEN}✓ ALL TESTS PASSED!{RESET}")
    else:
        print(f"{BOLD}{RED}✗ {failed_tests} TEST(S) FAILED{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{RED}Tests interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
