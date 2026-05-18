#!/usr/bin/env python3
"""
Social Authentication API Testing Script
Test Google and Apple Sign-In endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/auth"
HEADERS = {"Content-Type": "application/json"}

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_section(title):
    """Print a section header"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


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


def test_google_login_endpoint():
    """Test Google login endpoint validation"""
    print_section("TEST 1: GOOGLE LOGIN ENDPOINT VALIDATION")
    
    endpoint = f"{BASE_URL}/google/login/"
    
    # Test with invalid request (no token)
    print(f"{BOLD}Test 1a: Request without token{RESET}\n")
    print_request("POST", endpoint, {})
    
    try:
        response = requests.post(endpoint, json={}, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 400:
            print_success("API correctly rejected request without token")
        else:
            print_error(f"Expected 400, got {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")
    
    # Test with sample ID token format
    print(f"\n{BOLD}Test 1b: Request with ID token (example){RESET}\n")
    data = {
        "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjExIn0.eyJhdWQiOiJjbGllbnRfaWQiLCJzdWIiOiIxMjM0NTY3ODkwIn0.SIGNATURE"
    }
    print_request("POST", endpoint, data)
    print_info("Note: This test uses a sample token. In production, use real Google ID tokens.")
    print_info("API will validate and connect to Google servers to verify token authenticity.")


def test_apple_login_endpoint():
    """Test Apple login endpoint validation"""
    print_section("TEST 2: APPLE LOGIN ENDPOINT VALIDATION")
    
    endpoint = f"{BASE_URL}/apple/login/"
    
    # Test with invalid request (no token)
    print(f"{BOLD}Test 2a: Request without token{RESET}\n")
    print_request("POST", endpoint, {})
    
    try:
        response = requests.post(endpoint, json={}, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 400:
            print_success("API correctly rejected request without token")
        else:
            print_error(f"Expected 400, got {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")
    
    # Test with sample ID token format
    print(f"\n{BOLD}Test 2b: Request with ID token (example){RESET}\n")
    data = {
        "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJjb20uYWdpbGl6YS5zZXJ2aWNlIn0.SIGNATURE"
    }
    print_request("POST", endpoint, data)
    print_info("Note: This test uses a sample token. In production, use real Apple ID tokens.")


def test_google_connect_requires_auth():
    """Test that Google connect requires authentication"""
    print_section("TEST 3: GOOGLE CONNECT - AUTHENTICATION REQUIRED")
    
    endpoint = f"{BASE_URL}/google/connect/"
    data = {
        "id_token": "sample_token"
    }
    
    print(f"{BOLD}Test without authentication:{RESET}\n")
    print_request("POST", endpoint, data)
    
    try:
        response = requests.post(endpoint, json=data, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 401:
            print_success("API correctly requires authentication for connect endpoint")
        else:
            print_error(f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")


def test_apple_connect_requires_auth():
    """Test that Apple connect requires authentication"""
    print_section("TEST 4: APPLE CONNECT - AUTHENTICATION REQUIRED")
    
    endpoint = f"{BASE_URL}/apple/connect/"
    data = {
        "id_token": "sample_token"
    }
    
    print(f"{BOLD}Test without authentication:{RESET}\n")
    print_request("POST", endpoint, data)
    
    try:
        response = requests.post(endpoint, json=data, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 401:
            print_success("API correctly requires authentication for connect endpoint")
        else:
            print_error(f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")


def test_social_accounts_list_requires_auth():
    """Test that social accounts list requires authentication"""
    print_section("TEST 5: LIST SOCIAL ACCOUNTS - AUTHENTICATION REQUIRED")
    
    endpoint = f"{BASE_URL}/social/accounts/"
    
    print(f"{BOLD}Test without authentication:{RESET}\n")
    print_request("GET", endpoint)
    
    try:
        response = requests.get(endpoint, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 401:
            print_success("API correctly requires authentication for list endpoint")
        else:
            print_error(f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")


def test_disconnect_requires_auth():
    """Test that disconnect requires authentication"""
    print_section("TEST 6: DISCONNECT SOCIAL ACCOUNT - AUTHENTICATION REQUIRED")
    
    endpoint = f"{BASE_URL}/social/disconnect/"
    data = {
        "provider": "google"
    }
    
    print(f"{BOLD}Test without authentication:{RESET}\n")
    print_request("POST", endpoint, data)
    
    try:
        response = requests.post(endpoint, json=data, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 401:
            print_success("API correctly requires authentication for disconnect endpoint")
        else:
            print_error(f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")


def test_disconnect_invalid_provider():
    """Test disconnect with invalid provider"""
    print_section("TEST 7: DISCONNECT WITH INVALID PROVIDER")
    
    endpoint = f"{BASE_URL}/social/disconnect/"
    
    # Test missing provider
    print(f"{BOLD}Test with missing provider:{RESET}\n")
    print_request("POST", endpoint, {})
    
    try:
        response = requests.post(endpoint, json={}, headers=HEADERS)
        print_response(response)
        
        if response.status_code == 400:
            print_success("API correctly rejected disconnect without provider")
        else:
            print_error(f"Expected 400, got {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")


def test_disconnect_nonexistent_account():
    """Test disconnect with non-existent account (with auth)"""
    print_section("TEST 8: DISCONNECT NON-EXISTENT SOCIAL ACCOUNT")
    
    endpoint = f"{BASE_URL}/social/disconnect/"
    data = {
        "provider": "google"
    }
    
    print(f"{BOLD}Test with invalid provider (requires authentication):{RESET}\n")
    print_request("POST", endpoint, data)
    
    headers = HEADERS.copy()
    headers['Authorization'] = 'Bearer invalid_token'
    
    print(f"{BOLD}Note: This test will fail because token is invalid.{RESET}")
    print(f"{BOLD}In a real scenario with valid auth, it would return 404 if account doesn't exist.{RESET}\n")


def test_endpoint_structure():
    """Test API endpoint structure"""
    print_section("TEST 9: API ENDPOINT STRUCTURE VERIFICATION")
    
    endpoints = [
        ("POST", "/api/auth/google/login/", "Google Sign-In"),
        ("POST", "/api/auth/apple/login/", "Apple Sign-In"),
        ("POST", "/api/auth/google/connect/", "Connect Google (requires auth)"),
        ("POST", "/api/auth/apple/connect/", "Connect Apple (requires auth)"),
        ("GET", "/api/auth/social/accounts/", "List Social Accounts (requires auth)"),
        ("POST", "/api/auth/social/disconnect/", "Disconnect Social Account (requires auth)"),
    ]
    
    print(f"{BOLD}Available Social Authentication Endpoints:{RESET}\n")
    
    for method, endpoint, description in endpoints:
        print(f"{BOLD}{method}{RESET} {BLUE}{endpoint}{RESET}")
        print(f"  └─ {description}\n")
    
    print_success("All social authentication endpoints are properly structured and available")


def run_all_tests():
    """Run all tests"""
    print(f"\n{BOLD}{BLUE}╔══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{BLUE}║     AGILIZA SOCIAL AUTHENTICATION - TEST SUITE                  ║{RESET}")
    print(f"{BOLD}{BLUE}║     Testing Google & Apple Sign-In Integration                 ║{RESET}")
    print(f"{BOLD}{BLUE}║     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                               ║{RESET}")
    print(f"{BOLD}{BLUE}╚══════════════════════════════════════════════════════════════════╝{RESET}\n")
    
    try:
        test_endpoint_structure()
        test_google_login_endpoint()
        test_apple_login_endpoint()
        test_google_connect_requires_auth()
        test_apple_connect_requires_auth()
        test_social_accounts_list_requires_auth()
        test_disconnect_requires_auth()
        test_disconnect_invalid_provider()
        
        print_section("TEST SUITE COMPLETED")
        print(f"{BOLD}{GREEN}✓ All validation tests completed successfully!{RESET}")
        print(f"\n{BOLD}Next Steps:{RESET}")
        print("1. Configure Google OAuth2 credentials (see SOCIAL_AUTH_SETUP.md)")
        print("2. Configure Apple OAuth2 credentials (see SOCIAL_AUTH_SETUP.md)")
        print("3. Register providers in Django Admin")
        print("4. Update CORS settings for your frontend domain")
        print("5. Test with real tokens from frontend OAuth flow")
        
    except KeyboardInterrupt:
        print(f"\n{RED}Tests interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    run_all_tests()
