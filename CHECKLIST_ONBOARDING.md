# ✅ CHECKLIST DE VALIDAÇÃO - ONBOARDING LAF

## 📋 TESTES OBRIGATÓRIOS (NÃO PULAR NENHUM)

### ✅ 1. Fluxo Completo - Happy Path
**Objetivo**: Verificar que o fluxo normal funciona do início ao fim

**Passos**:
1. [ ] Abrir app → Verificar se Welcome aparece
2. [ ] Clicar "Começar Agora" → Ir para Step 1
3. [ ] Preencher nome: "João Silva"
4. [ ] Preencher idade: 28
5. [ ] Selecionar sexo: Masculino
6. [ ] Clicar "Próximo" → Ir para Step 2
7. [ ] Preencher altura: 178
8. [ ] Preencher peso: 82
9. [ ] Preencher meta (opcional): 75
10. [ ] Clicar "Próximo" → Ir para Step 3
11. [ ] Selecionar nível: Intermediário
12. [ ] Frequência: 4
13. [ ] Tempo: 60
14. [ ] Clicar "Próximo" → Ir para Step 4
15. [ ] Selecionar objetivo: Cutting
16. [ ] Clicar "Próximo" → Ir para Step 5
17. [ ] (Opcional) Selecionar preferências
18. [ ] Clicar "Finalizar"
19. [ ] Verificar loading aparece ("Criando perfil...")
20. [ ] Após 1-3 segundos → Redireciona para /home
21. [ ] Home mostra: TDEE, Meta calórica, Macros

**Resultado esperado**:
- TDEE: ~2786 kcal
- Meta: ~2285 kcal
- Proteína: ~180g
- Carbs: ~243g
- Gordura: ~65g

---

### ❌ 2. Validações - Campos Obrigatórios

#### Teste 2.1: Step 1 - Nome vazio
1. [ ] Abrir onboarding
2. [ ] Deixar nome vazio
3. [ ] Tentar clicar "Próximo"
4. [ ] Deve mostrar alert: "Preencha nome, idade e sexo"
5. [ ] Não deve avançar

#### Teste 2.2: Step 1 - Idade inválida
1. [ ] Preencher nome: "Teste"
2. [ ] Idade: 14 (menor que 15)
3. [ ] Sexo: Masculino
4. [ ] Clicar "Próximo"
5. [ ] Deve mostrar alert: "Idade deve estar entre 15 e 100 anos"

#### Teste 2.3: Step 1 - Idade muito alta
1. [ ] Idade: 101
2. [ ] Deve mostrar alert de idade inválida

#### Teste 2.4: Step 2 - Altura inválida
1. [ ] Altura: 99 (menor que 100)
2. [ ] Deve mostrar alert: "Altura deve estar entre 100cm e 250cm"

#### Teste 2.5: Step 2 - Peso inválido
1. [ ] Peso: 29 (menor que 30)
2. [ ] Deve mostrar alert: "Peso deve estar entre 30kg e 300kg"

#### Teste 2.6: Step 3 - Campos vazios
1. [ ] Deixar nível de treino sem selecionar
2. [ ] Tentar avançar
3. [ ] Deve mostrar alert: "Preencha todos os campos de treino"

#### Teste 2.7: Step 4 - Objetivo não selecionado
1. [ ] Não selecionar objetivo
2. [ ] Tentar avançar
3. [ ] Deve mostrar alert: "Selecione seu objetivo principal"

---

### 🌐 3. Testes de Conectividade e Erros

#### Teste 3.1: Backend Offline (Simular)
**Como simular**: Desligar backend temporariamente
1. [ ] Preencher todo onboarding
2. [ ] Clicar "Finalizar"
3. [ ] Deve mostrar alert com mensagem clara:
   - "Sem conexão com o servidor. Verifique sua internet."
4. [ ] Loading deve parar
5. [ ] Deve oferecer "Tentar Novamente"

#### Teste 3.2: Timeout (Request demorado)
**Como simular**: Backend lento ou timeout forçado
1. [ ] Completar onboarding
2. [ ] Clicar "Finalizar"
3. [ ] Se demorar mais de 15 segundos:
   - Deve mostrar: "A requisição demorou muito tempo..."
4. [ ] Loading deve parar
5. [ ] Botão deve voltar a funcionar

#### Teste 3.3: Erro 400 (Bad Request)
**Cenário**: Dados inválidos no backend
1. [ ] Deve mostrar mensagem específica do servidor
2. [ ] Loading deve parar
3. [ ] Usuário pode tentar novamente

#### Teste 3.4: Erro 500 (Server Error)
1. [ ] Deve mostrar: "Erro no servidor. Tente novamente em alguns instantes."
2. [ ] Não deve travar a aplicação

---

### 🔒 4. Proteção Contra Duplicação

#### Teste 4.1: Double-submit (Clicar rápido várias vezes)
1. [ ] Preencher onboarding completo
2. [ ] Clicar "Finalizar" múltiplas vezes rapidamente
3. [ ] Botão deve desabilitar após primeiro clique
4. [ ] Não deve criar perfis duplicados
5. [ ] Verificar no console: apenas 1 POST request

#### Teste 4.2: Re-onboarding bloqueado
1. [ ] Completar onboarding com sucesso
2. [ ] Ir para /home
3. [ ] Recarregar a página (F5 ou Cmd+R)
4. [ ] App deve ir direto para /home
5. [ ] Não deve mostrar Welcome novamente

#### Teste 4.3: Acesso direto à rota /onboarding
1. [ ] Após completar perfil, tentar acessar /onboarding manualmente
2. [ ] Deve redirecionar automaticamente para /home

---

### 📱 5. Responsividade e UX

#### Teste 5.1: Diferentes tamanhos de tela
- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667 - iPhone SE)
- [ ] Mobile (390x844 - iPhone 12)

Verificar em cada:
- [ ] Botões são clicáveis (min 44x44px)
- [ ] Textos são legíveis
- [ ] Inputs não ficam cortados
- [ ] Progress bar visível

#### Teste 5.2: Orientação (Mobile)
- [ ] Modo retrato (portrait)
- [ ] Modo paisagem (landscape)
- [ ] Layout se adapta corretamente

#### Teste 5.3: Teclado (Mobile)
1. [ ] Abrir input de texto
2. [ ] Teclado deve aparecer
3. [ ] Input deve ficar visível (não coberto pelo teclado)
4. [ ] Scroll deve funcionar se necessário

---

### 🔍 6. Logs e Debug

#### Verificar Console do Browser (F12)

**Logs esperados no fluxo completo**:
```
✅ "🎯 OnboardingScreen mounted. Backend URL: [url]"
✅ "Validating step: 0" (ao avançar Step 1)
✅ "Validating step: 1" (ao avançar Step 2)
✅ "Validating step: 2" (ao avançar Step 3)
✅ "Validating step: 3" (ao avançar Step 4)
✅ "🚀 handleSubmit called"
✅ "📦 Form data: { ... }"
✅ "📡 Sending to backend: { ... }"
✅ "🌐 Backend URL: https://..."
✅ "✅ Response received: 200 { id, tdee, ... }"
✅ "💾 Profile saved to AsyncStorage"
✅ "🏠 Navigating to home immediately"
```

**Logs NÃO devem aparecer**:
❌ Uncaught Error
❌ React Hook error
❌ Network errors sem tratamento
❌ Undefined variables

---

### 🧪 7. Testes de Edge Cases

#### Teste 7.1: Campos opcionais vazios
1. [ ] Deixar "Peso Meta" vazio
2. [ ] Deixar "Body Fat %" vazio
3. [ ] Não selecionar preferências no Step 5
4. [ ] Deve criar perfil normalmente
5. [ ] Backend deve aceitar `null` nesses campos

#### Teste 7.2: Caracteres especiais no nome
1. [ ] Nome: "João Silva-Santos"
2. [ ] Nome: "Maria D'Angelo"
3. [ ] Nome: "José Antônio"
4. [ ] Deve funcionar normalmente

#### Teste 7.3: Números decimais
1. [ ] Altura: 178.5
2. [ ] Peso: 82.3
3. [ ] Body Fat: 18.7
4. [ ] Deve processar corretamente

#### Teste 7.4: Voltar steps
1. [ ] Avançar até Step 3
2. [ ] Clicar botão "Voltar"
3. [ ] Verificar que dados preenchidos foram mantidos
4. [ ] Avançar novamente → Dados devem estar lá

---

### 🔐 8. Persistência de Dados

#### Teste 8.1: AsyncStorage
1. [ ] Completar onboarding
2. [ ] Abrir DevTools → Application → Storage → AsyncStorage
3. [ ] Verificar existência de:
   - `userId` (UUID válido)
   - `userProfile` (JSON com todos dados)
   - `hasCompletedOnboarding` ("true")

#### Teste 8.2: Reload após completar
1. [ ] Completar onboarding
2. [ ] Ir para /home
3. [ ] F5 (reload)
4. [ ] Deve continuar na /home
5. [ ] Perfil deve aparecer corretamente

---

## 🎯 CRITÉRIOS DE ACEITE FINAL

Considere o onboarding **APROVADO** somente se:

✅ Todos os 40+ testes acima passarem  
✅ Nenhum erro no console (exceto warnings não críticos)  
✅ Fluxo completo em < 30 segundos  
✅ Loading sempre aparece quando esperado  
✅ Botão nunca permite double-submit  
✅ Erros sempre têm mensagem clara  
✅ Navegação funciona perfeitamente  
✅ Dados persistem corretamente  
✅ Backend recebe payload correto  
✅ Home exibe dados corretamente  

---

## 📊 TEMPLATE DE REPORTE

Use este template para reportar problemas:

```
❌ TESTE FALHOU: [Nome do teste]

Passos executados:
1. [passo 1]
2. [passo 2]
3. [passo 3]

Resultado esperado:
[descrever o esperado]

Resultado obtido:
[descrever o que aconteceu]

Logs do console:
[colar logs relevantes]

Screenshot: [se aplicável]

Ambiente:
- Browser: [Chrome/Safari/etc]
- Device: [Desktop/Mobile/Tablet]
- Dimensões: [1920x1080/etc]
```

---

## ✅ STATUS DOS TESTES

**Última execução**: [DATA]  
**Executor**: [NOME]  
**Ambiente**: [Preview/Local/etc]

**Resultados**:
- Passou: X/40
- Falhou: X/40
- Pendente: X/40

**Próximos passos**: [descrever]
