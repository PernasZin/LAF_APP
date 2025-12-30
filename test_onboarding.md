# 📋 TESTE DE ONBOARDING - CHECKLIST COMPLETO

## ✅ CRITÉRIOS DE ACEITE

### 1. Fluxo Completo (OBRIGATÓRIO)
- [ ] Abrir app → Tela de Welcome aparece
- [ ] Clicar em "Começar Agora" → Vai para Step 1
- [ ] Preencher Step 1 (Nome, Idade, Sexo) → Avança para Step 2
- [ ] Preencher Step 2 (Altura, Peso) → Avança para Step 3
- [ ] Preencher Step 3 (Nível, Frequência, Tempo) → Avança para Step 4
- [ ] Preencher Step 4 (Objetivo) → Avança para Step 5
- [ ] Step 5 (opcional) → Clicar em "Finalizar"
- [ ] Loading aparece no botão
- [ ] Após sucesso → Redireciona automaticamente para /home
- [ ] Home exibe perfil com TDEE e macros

### 2. Validações (OBRIGATÓRIO)
- [ ] Step 1: Tentar avançar sem preencher nome → Mostra alert
- [ ] Step 1: Tentar avançar com idade < 15 → Mostra alert
- [ ] Step 2: Tentar avançar sem altura → Mostra alert
- [ ] Step 2: Tentar avançar com peso inválido → Mostra alert
- [ ] Step 3: Tentar avançar sem nível → Mostra alert
- [ ] Step 4: Tentar avançar sem objetivo → Mostra alert

### 3. Proteção Contra Re-onboarding (OBRIGATÓRIO)
- [ ] Após completar onboarding, recarregar a página
- [ ] App deve ir direto para /home (não mostrar welcome)
- [ ] Tentar acessar /onboarding manualmente
- [ ] Deve redirecionar para /home

### 4. Tratamento de Erros (OBRIGATÓRIO)
- [ ] Simular erro de rede (backend offline)
- [ ] Deve mostrar mensagem de erro clara
- [ ] Usuário pode tentar novamente
- [ ] Loading desaparece após erro

### 5. Logs de Debug (VERIFICAR)
Console deve mostrar:
- [ ] "🎯 OnboardingScreen mounted. Backend URL: [url]"
- [ ] "Validating step: [N]" ao tentar avançar
- [ ] "🚀 handleSubmit called" ao finalizar
- [ ] "📡 Sending to backend: [payload]" antes de enviar
- [ ] "✅ Response received: 200 [data]" após sucesso
- [ ] "💾 Profile saved to AsyncStorage"
- [ ] "🏠 Navigating to home immediately"

### 6. Backend Integration (VERIFICAR)
- [ ] POST /api/user/profile retorna 200
- [ ] Response contém: id, tdee, target_calories, macros
- [ ] Dados salvos no AsyncStorage
- [ ] Profile pode ser recuperado em /home

## 🧪 CASOS DE TESTE ESPECÍFICOS

### Teste 1: Fluxo Feliz (Happy Path)
```
Dados:
- Nome: "João Silva"
- Idade: 28
- Sexo: masculino
- Altura: 178
- Peso: 82
- Meta: 75
- Body Fat: 18
- Nível: intermediario
- Frequência: 4
- Tempo: 60
- Objetivo: cutting

Resultado Esperado:
- TDEE: ~2786 kcal
- Meta: ~2285 kcal
- Proteína: ~180g
- Carbs: ~243g
- Gordura: ~65g
```

### Teste 2: Campos Opcionais Vazios
```
Dados:
- Nome: "Maria Santos"
- Idade: 25
- Sexo: feminino
- Altura: 165
- Peso: 60
- Meta: (vazio)
- Body Fat: (vazio)
- Nível: iniciante
- Frequência: 3
- Tempo: 45
- Objetivo: bulking

Resultado Esperado:
- Perfil criado com sucesso
- target_weight e body_fat_percentage = null
```

### Teste 3: Validação de Limites
```
Testes:
- Idade = 14 → REJECT
- Idade = 15 → ACCEPT
- Idade = 100 → ACCEPT
- Idade = 101 → REJECT
- Altura = 99 → REJECT
- Altura = 100 → ACCEPT
- Altura = 250 → ACCEPT
- Altura = 251 → REJECT
- Peso = 29 → REJECT
- Peso = 30 → ACCEPT
- Peso = 300 → ACCEPT
- Peso = 301 → REJECT
```

## 🚨 PROBLEMAS CONHECIDOS CORRIGIDOS

### ✅ PROBLEMA 1: Alert bloqueava navegação
**Solução**: Removido Alert de sucesso, navegação agora é imediata após salvar

### ✅ PROBLEMA 2: Rota incorreta
**Solução**: Mudado de `/home/` para `/home`

### ✅ PROBLEMA 3: Falta de timeout
**Solução**: Adicionado timeout de 10s nas requisições

### ✅ PROBLEMA 4: Sem proteção contra re-onboarding
**Solução**: Adicionado check de `hasCompletedOnboarding` em Welcome e Onboarding

## 📊 STATUS DOS TESTES

**Última Execução**: Pendente
**Backend Status**: ✅ Funcional (testado com curl)
**Frontend Status**: 🔄 Aguardando teste completo

## 🎯 PRÓXIMO PASSO

Executar todos os testes acima e marcar cada item como:
- ✅ PASSOU
- ❌ FALHOU (com detalhes)
- ⚠️  PARCIAL (com detalhes)
