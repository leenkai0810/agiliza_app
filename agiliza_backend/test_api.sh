#!/bin/bash

# Agiliza API - cURL Testing Commands
# Save your tokens in these variables after running register/login

BASE_URL="http://localhost:8000/api/auth"
ACCESS_TOKEN=""
REFRESH_TOKEN=""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Agiliza API - cURL Commands${NC}"
echo -e "${BLUE}================================${NC}\n"

# Function to register user
register_user() {
    echo -e "${YELLOW}→ Registering new user...${NC}\n"
    
    curl -X POST "${BASE_URL}/register/" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "full_name": "Test User",
        "phone": "+1234567890",
        "role": "CLIENT"
      }' -w "\n\nStatus Code: %{http_code}\n"
    
    echo -e "\n${YELLOW}Note: Copy the access_token and refresh_token from the response above${NC}\n"
}

# Function to login user
login_user() {
    echo -e "${YELLOW}→ Logging in user...${NC}\n"
    
    curl -X POST "${BASE_URL}/login/" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "testuser@example.com",
        "password": "SecurePass123!"
      }' -w "\n\nStatus Code: %{http_code}\n"
}

# Function to get profile
get_profile() {
    if [ -z "$ACCESS_TOKEN" ]; then
        echo -e "${YELLOW}Error: ACCESS_TOKEN is not set. Set it first.${NC}\n"
        return 1
    fi
    
    echo -e "${YELLOW}→ Getting user profile...${NC}\n"
    
    curl -X GET "${BASE_URL}/profile/" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -w "\n\nStatus Code: %{http_code}\n"
}

# Function to update profile
update_profile() {
    if [ -z "$ACCESS_TOKEN" ]; then
        echo -e "${YELLOW}Error: ACCESS_TOKEN is not set. Set it first.${NC}\n"
        return 1
    fi
    
    echo -e "${YELLOW}→ Updating user profile...${NC}\n"
    
    curl -X PATCH "${BASE_URL}/profile/" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{
        "full_name": "Updated User Name",
        "phone": "+9876543210"
      }' -w "\n\nStatus Code: %{http_code}\n"
}

# Function to refresh token
refresh_token() {
    if [ -z "$REFRESH_TOKEN" ]; then
        echo -e "${YELLOW}Error: REFRESH_TOKEN is not set. Set it first.${NC}\n"
        return 1
    fi
    
    echo -e "${YELLOW}→ Refreshing access token...${NC}\n"
    
    curl -X POST "${BASE_URL}/token/refresh/" \
      -H "Content-Type: application/json" \
      -d "{
        \"refresh\": \"${REFRESH_TOKEN}\"
      }" -w "\n\nStatus Code: %{http_code}\n"
}

# Function to logout
logout_user() {
    if [ -z "$ACCESS_TOKEN" ] || [ -z "$REFRESH_TOKEN" ]; then
        echo -e "${YELLOW}Error: ACCESS_TOKEN or REFRESH_TOKEN is not set. Set them first.${NC}\n"
        return 1
    fi
    
    echo -e "${YELLOW}→ Logging out user...${NC}\n"
    
    curl -X POST "${BASE_URL}/logout/" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"refresh\": \"${REFRESH_TOKEN}\"
      }" -w "\n\nStatus Code: %{http_code}\n"
}

# Function to test invalid token
test_invalid_token() {
    echo -e "${YELLOW}→ Testing with invalid token...${NC}\n"
    
    curl -X GET "${BASE_URL}/profile/" \
      -H "Authorization: Bearer invalid_token_here" \
      -H "Content-Type: application/json" \
      -w "\n\nStatus Code: %{http_code}\n"
}

# Function to test invalid credentials
test_invalid_credentials() {
    echo -e "${YELLOW}→ Testing invalid credentials...${NC}\n"
    
    curl -X POST "${BASE_URL}/login/" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "testuser@example.com",
        "password": "WrongPassword123!"
      }' -w "\n\nStatus Code: %{http_code}\n"
}

# Function to test duplicate email
test_duplicate_email() {
    echo -e "${YELLOW}→ Testing duplicate email registration...${NC}\n"
    
    curl -X POST "${BASE_URL}/register/" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "full_name": "Another User",
        "phone": "+1111111111",
        "role": "PROFESSIONAL"
      }' -w "\n\nStatus Code: %{http_code}\n"
}

# Function to test password mismatch
test_password_mismatch() {
    echo -e "${YELLOW}→ Testing password mismatch...${NC}\n"
    
    curl -X POST "${BASE_URL}/register/" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "mismatch@example.com",
        "password": "SecurePass123!",
        "password_confirm": "DifferentPass123!",
        "full_name": "Test User",
        "phone": "+1234567890"
      }' -w "\n\nStatus Code: %{http_code}\n"
}

# Display menu
show_menu() {
    echo -e "${BLUE}Available Commands:${NC}"
    echo "1. register_user          - Register a new user"
    echo "2. login_user             - Login with credentials"
    echo "3. get_profile            - Get current user profile"
    echo "4. update_profile         - Update user profile"
    echo "5. refresh_token          - Refresh access token"
    echo "6. logout_user            - Logout user"
    echo "7. test_invalid_token     - Test with invalid token"
    echo "8. test_invalid_credentials - Test invalid login credentials"
    echo "9. test_duplicate_email   - Test duplicate email registration"
    echo "10. test_password_mismatch - Test password mismatch"
    echo -e "\n${YELLOW}Usage: source test_api.sh && register_user${NC}"
    echo -e "${YELLOW}Or directly run: bash test_api.sh${NC}\n"
}

# Show menu
show_menu

# If script is run directly (not sourced), run all tests
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    echo -e "\n${BLUE}Running all tests in sequence...${NC}\n"
    
    echo -e "${GREEN}=== Test 1: Register User ===${NC}"
    register_user
    
    sleep 2
    
    echo -e "\n${GREEN}=== Test 2: Login User ===${NC}"
    login_user
    echo -e "${YELLOW}Please set ACCESS_TOKEN and REFRESH_TOKEN from the response above${NC}\n"
fi
