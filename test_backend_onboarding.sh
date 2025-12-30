#!/bin/bash

echo "🧪 LAF - TESTE DE ONBOARDING BACKEND"
echo "======================================"
echo ""

BACKEND_URL="http://localhost:8001"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador
PASSED=0
FAILED=0

# Função de teste
test_endpoint() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    echo -n "Testing: $test_name... "
    
    response=$(curl -s -w "\n%{http_code}" -X $method \
        -H "Content-Type: application/json" \
        -d "$data" \
        "$BACKEND_URL$endpoint" 2>&1)
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (Expected: $expected_status, Got: $status_code)"
        echo "Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "1️⃣  Teste 1: Health Check"
test_endpoint "Health check" "GET" "/api/health" "" "200"
echo ""

echo "2️⃣  Teste 2: Criar Perfil - Masculino Cutting"
PROFILE_DATA='{
  "name": "João Silva",
  "age": 28,
  "sex": "masculino",
  "height": 178,
  "weight": 82,
  "target_weight": 75,
  "body_fat_percentage": 18,
  "training_level": "intermediario",
  "weekly_training_frequency": 4,
  "available_time_per_session": 60,
  "goal": "cutting",
  "dietary_restrictions": [],
  "food_preferences": ["Frango", "Arroz"],
  "injury_history": []
}'
test_endpoint "Create profile (cutting)" "POST" "/api/user/profile" "$PROFILE_DATA" "200"

# Extrai o ID do perfil criado
USER_ID=$(echo "$body" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | head -n1)
echo "User ID: $USER_ID"
echo ""

echo "3️⃣  Teste 3: Criar Perfil - Feminino Bulking"
PROFILE_DATA_2='{
  "name": "Maria Santos",
  "age": 25,
  "sex": "feminino",
  "height": 165,
  "weight": 60,
  "training_level": "iniciante",
  "weekly_training_frequency": 3,
  "available_time_per_session": 45,
  "goal": "bulking",
  "dietary_restrictions": ["Vegetariano"],
  "food_preferences": [],
  "injury_history": []
}'
test_endpoint "Create profile (bulking)" "POST" "/api/user/profile" "$PROFILE_DATA_2" "200"
echo ""

echo "4️⃣  Teste 4: Buscar Perfil"
if [ -n "$USER_ID" ]; then
    test_endpoint "Get profile" "GET" "/api/user/profile/$USER_ID" "" "200"
else
    echo -e "${YELLOW}⚠️  SKIPPED${NC} (No user ID)"
fi
echo ""

echo "5️⃣  Teste 5: Atualizar Peso"
if [ -n "$USER_ID" ]; then
    UPDATE_DATA='{"weight": 80}'
    test_endpoint "Update weight" "PUT" "/api/user/profile/$USER_ID" "$UPDATE_DATA" "200"
else
    echo -e "${YELLOW}⚠️  SKIPPED${NC} (No user ID)"
fi
echo ""

echo "======================================"
echo "📊 RESULTADO FINAL"
echo "======================================"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
    exit 0
else
    echo -e "${RED}❌ ALGUNS TESTES FALHARAM${NC}"
    exit 1
fi
