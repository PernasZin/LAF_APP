/**
 * Sistema de Tradução i18n - LAF App
 * Suporta: pt-BR, en-US, es-ES
 */

export type SupportedLanguage = 'pt-BR' | 'en-US' | 'es-ES';

export interface Translations {
  // Common
  common: {
    loading: string;
    error: string;
    success: string;
    warning: string;
    save: string;
    cancel: string;
    confirm: string;
    delete: string;
    edit: string;
    back: string;
    next: string;
    done: string;
    connectionError: string;
    yes: string;
    no: string;
    saving: string;
  };
  // Tab names
  tabs: {
    home: string;
    diet: string;
    workout: string;
    cardio: string;
    progress: string;
    settings: string;
  };
  // Home screen
  home: {
    greeting: string;
    subtitle: string;
    dailyGoal: string;
    training: string;
    weeklyFrequency: string;
    macrosDistribution: string;
    protein: string;
    carbs: string;
    fat: string;
    yourGoal: string;
    cutting: string;
    bulking: string;
    maintenance: string;
    athlete: string;
    tdee: string;
    comingSoon: string;
    comingSoonText: string;
    waterTracker: string;
    waterGoalReached: string;
    viewDiet: string;
    macrosOfDay: string;
    cups: string;
    ofCups: string;
    active: string;
    welcome: string;
    completeProfile: string;
    perWeek: string;
    exercises: string;
  };
  // Diet screen
  diet: {
    title: string;
    mealsPlanned: string;
    daySummary: string;
    noData: string;
    generateDiet: string;
    generating: string;
    tapToSubstitute: string;
    mealsOfDay: string;
    supplements: string;
    substituteFood: string;
    currentFood: string;
    chooseSubstitute: string;
    noSubstitutes: string;
    substituted: string;
    existingDiet: string;
    existingDietMessage: string;
    categories: {
      protein: string;
      carb: string;
      fat: string;
      fruit: string;
      vegetable: string;
    };
    noDietGenerated: string;
    generateYourDiet: string;
    generateMyDiet: string;
    substitute: string;
    success: string;
  };
  // Workout screen
  workout: {
    title: string;
    noData: string;
    generateWorkout: string;
    generating: string;
    markComplete: string;
    completed: string;
    viewHistory: string;
    history: string;
    noHistory: string;
    sets: string;
    reps: string;
    rest: string;
    exercises: string;
    howToExecute: string;
    restTimer: string;
    start: string;
    restart: string;
    exercises: string;
    thisWeek: string;
    completeHint: string;
    weekProgress: string;
    customWorkout: string;
    training: string;
  };
  // Cardio screen
  cardio: {
    title: string;
    sessionsPerWeek: string;
    minPerWeek: string;
    kcalPerWeek: string;
    yourExercises: string;
    perWeek: string;
    substitutes: string;
    tip: string;
    moderate: string;
    zone: string;
  };
  // Progress screen
  progress: {
    title: string;
    subtitle: string;
    currentWeight: string;
    targetWeight: string;
    remaining: string;
    recordWeight: string;
    weightHistory: string;
    noRecords: string;
    last30Days: string;
    evolution: string;
    addWeight: string;
    enterWeight: string;
    inPeriod: string;
    nextRecordIn: string;
    days: string;
    total: string;
    records: string;
    recordEvery2Weeks: string;
    history: string;
    howWasYourWeek: string;
    sleep: string;
    weightSaved: string;
  };
  // Settings screen
  settings: {
    title: string;
    subtitle: string;
    account: string;
    editProfile: string;
    diet: string;
    mealsPerDay: string;
    meals: string;
    training: string;
    configureTraining: string;
    timesPerWeek: string;
    preferences: string;
    lightMode: string;
    notifications: string;
    support: string;
    privacy: string;
    termsOfUse: string;
    help: string;
    logout: string;
    logoutTitle: string;
    logoutConfirm: string;
    cancel: string;
    version: string;
    madeWithLove: string;
    user: string;
  };
  // Notifications settings
  notificationSettings: {
    title: string;
    enableAll: string;
    enableAllDesc: string;
    sendTest: string;
    mealReminders: string;
    mealRemindersTitle: string;
    mealRemindersDesc: string;
    mealTimes: string;
    workoutReminder: string;
    workoutReminderTitle: string;
    workoutReminderDesc: string;
    weightReminder: string;
    weightReminderTitle: string;
    weightReminderDesc: string;
    day: string;
    time: string;
    infoText: string;
  };
  // Training config screen
  trainingConfig: {
    title: string;
    experienceLevel: string;
    weeklyFrequency: string;
    availableTime: string;
    saveSettings: string;
    savingSettings: string;
    successTitle: string;
    successMessage: string;
    errorTitle: string;
    errorSave: string;
    errorConnect: string;
    // Levels
    novice: string;
    noviceDesc: string;
    beginner: string;
    beginnerDesc: string;
    intermediate: string;
    intermediateDesc: string;
    advanced: string;
    advancedDesc: string;
    lowVolume: string;
    lowVolumeDesc: string;
    noviceHint: string;
    // Frequencies
    freq2x: string;
    freq2xDesc: string;
    freq3x: string;
    freq3xDesc: string;
    freq4x: string;
    freq4xDesc: string;
    freq5x: string;
    freq5xDesc: string;
    freq6x: string;
    freq6xDesc: string;
    // Durations
    dur30: string;
    dur30Desc: string;
    dur60: string;
    dur60Desc: string;
    dur90: string;
    dur90Desc: string;
    dur120: string;
    dur120Desc: string;
  };
  // Privacy screen
  privacy: {
    title: string;
    dataSecurity: string;
    dataSecurityDesc: string;
    protectedAccess: string;
    protectedAccessDesc: string;
    transparency: string;
    transparencyDesc: string;
    localStorage: string;
    localStorageDesc: string;
    requestDeletion: string;
  };
  // Terms screen
  terms: {
    title: string;
    acceptance: string;
    acceptanceDesc: string;
    responsibleUse: string;
    responsibleUseDesc: string;
    limitations: string;
    limitationsDesc: string;
    health: string;
    healthDesc: string;
    lastUpdate: string;
  };
  // Settings screen (edit profile, meal config)
  settingsScreen: {
    profileUpdated: string;
    information: string;
    goal: string;
    saveChanges: string;
    mealConfigTitle: string;
    mealConfigSubtitle: string;
    mealsPerDay: string;
    mealsUpdated: string;
    settingsSavedDiet: string;
    mealsPerDayLabel: string;
  };
  // Meals
  meals: {
    breakfast: string;
    morningSnack: string;
    lunch: string;
    afternoonSnack: string;
    dinner: string;
    supper: string;
    eveningSnack: string;
  };
  // Days of week
  weekDays: {
    sunday: string;
    monday: string;
    tuesday: string;
    wednesday: string;
    thursday: string;
    friday: string;
    saturday: string;
  };
  // Athlete phases
  athletePhases: {
    offSeason: string;
    prePrep: string;
    prep: string;
    peakWeek: string;
    postShow: string;
  };
  // Auth
  auth: {
    login: string;
    signup: string;
    email: string;
    password: string;
    forgotPassword: string;
    noAccount: string;
    hasAccount: string;
    createAccount: string;
    enterAccount: string;
  };
  // Onboarding
  onboarding: {
    // Steps titles
    steps: {
      basicInfo: string;
      physicalData: string;
      trainingLevel: string;
      yourGoal: string;
      preferences: string;
      meals: string;
    };
    // Buttons
    saving: string;
    finish: string;
    // BasicInfoStep
    letsStart: string;
    tellUsAboutYou: string;
    name: string;
    yourName: string;
    age: string;
    yourAge: string;
    sex: string;
    male: string;
    female: string;
    // PhysicalDataStep
    physicalDataTitle: string;
    physicalDataDesc: string;
    height: string;
    heightPlaceholder: string;
    currentWeight: string;
    currentWeightPlaceholder: string;
    targetWeight: string;
    targetWeightPlaceholder: string;
    bodyFatPercentage: string;
    bodyFatPlaceholder: string;
    bodyFatHint: string;
    // TrainingLevelStep
    trainingLevelTitle: string;
    trainingLevelDesc: string;
    currentLevel: string;
    beginner: string;
    beginnerDesc: string;
    intermediate: string;
    intermediateDesc: string;
    advanced: string;
    advancedDesc: string;
    daysPerWeek: string;
    daysPlaceholder: string;
    timePerSession: string;
    timePlaceholder: string;
    // GoalStep
    goalTitle: string;
    goalDesc: string;
    cutting: string;
    cuttingDesc: string;
    bulking: string;
    bulkingDesc: string;
    maintenance: string;
    maintenanceDesc: string;
    athlete: string;
    athleteDesc: string;
    competitionDate: string;
    competitionDateDesc: string;
    selectDate: string;
    weeksToCompetition: string;
    competitionPassed: string;
    // RestrictionsStep
    foodPreferences: string;
    foodPreferencesDescAthlete: string;
    foodPreferencesDescGeneral: string;
    athleteMode: string;
    flexibleMode: string;
    dietaryRestrictions: string;
    vegetarian: string;
    lactoseFree: string;
    glutenFree: string;
    lowCarb: string;
    availableFoods: string;
    selected: string;
    proteins: string;
    proteinsDesc: string;
    carbs: string;
    carbsDesc: string;
    fats: string;
    fatsDesc: string;
    fruits: string;
    fruitsDesc: string;
    vegetables: string;
    vegetablesDesc: string;
    supplements: string;
    supplementsDesc: string;
    separate: string;
    mealsPerDay: string;
    distribution: string;
    athleteInfoBox: string;
    generalInfoBox: string;
    skipHint: string;
    // Extended restrictions (RestrictionsStep)
    vegan: string;
    eggFree: string;
    peanutFree: string;
    restrictions: string;
    restrictionsDesc: string;
    preferences: string;
    preferencesDesc: string;
    highProtein: string;
    mediterranean: string;
    wholeFoods: string;
    // Validation errors
    requiredFields: string;
    fillNameAgeSex: string;
    invalidAge: string;
    fillHeightWeight: string;
    invalidHeight: string;
    invalidWeight: string;
    fillTrainingFields: string;
    invalidFrequency: string;
    selectGoal: string;
    dateRequired: string;
    dateRequiredMessage: string;
    sessionExpired: string;
    // Success/Error
    error: string;
    couldNotSaveProfile: string;
  };
}

export const translations: Record<SupportedLanguage, Translations> = {
  'pt-BR': {
    common: {
      loading: 'Carregando...',
      error: 'Erro',
      success: 'Sucesso',
      warning: 'Aviso',
      cancel: 'Cancelar',
      save: 'Salvar',
      confirm: 'Confirmar',
      delete: 'Excluir',
      edit: 'Editar',
      back: 'Voltar',
      next: 'Próximo',
      done: 'Concluído',
      connectionError: 'Erro de Conexão',
      yes: 'Sim',
      no: 'Não',
      saving: 'Salvando...',
    },
    // Language Selection Screen
    languageSelect: {
      title: 'Escolha seu idioma',
      subtitle: 'Select your language / Selecciona tu idioma',
      continue: 'Continuar',
      yourAssistant: 'Seu assistente de nutrição',
    },
    // Paywall
    paywall: {
      subscribeMonthly: 'Assinar por R$ 29,90/mês',
      subscribeAnnual: 'Assinar por R$ 199,90/ano',
    },
    tabs: {
      home: 'Início',
      diet: 'Alimentação',
      workout: 'Exercícios',
      cardio: 'Cardio',
      progress: 'Progresso',
      settings: 'Config',
    },
    home: {
      greeting: 'Olá',
      subtitle: 'Vamos conquistar seus objetivos',
      dailyGoal: 'Meta Diária',
      training: 'Treino',
      weeklyFrequency: 'x/semana',
      macrosDistribution: 'Distribuição de Macros',
      protein: 'Proteínas',
      carbs: 'Carboidratos',
      fat: 'Gorduras',
      yourGoal: 'Seu Objetivo',
      cutting: 'Emagrecimento (Cutting)',
      bulking: 'Ganho de Massa (Bulking)',
      maintenance: 'Manutenção',
      athlete: 'Atleta/Competição',
      tdee: 'TDEE',
      comingSoon: 'Em Breve',
      comingSoonText: 'Sugestões inteligentes de alimentação e exercícios com IA',
      waterTracker: 'Hidratação',
      waterGoalReached: 'Meta de hidratação atingida! 🎉',
      viewDiet: 'Ver sugestões',
      macrosOfDay: 'Macros do Dia',
      cups: 'copos',
      ofCups: 'de',
      active: 'ATIVO',
      welcome: 'Bem-vindo ao LAF!',
      completeProfile: 'Complete seu perfil para começar',
      perWeek: 'POR SEMANA',
      exercises: 'exercícios',
    },
    diet: {
      title: 'Alimentação',
      mealsPlanned: 'refeições planejadas',
      daySummary: 'Resumo do Dia',
      noData: 'Nenhuma sugestão gerada',
      generateDiet: 'Gerar Minha Dieta',
      generating: 'Preparando sugestões alimentares...',
      tapToSubstitute: 'Toque em um alimento para substituir',
      mealsOfDay: 'Refeições do Dia',
      supplements: 'Suplementação',
      substituteFood: 'Substituir Alimento',
      currentFood: 'Alimento atual',
      chooseSubstitute: 'Escolha um substituto',
      noSubstitutes: 'Nenhum substituto disponível para este alimento.',
      substituted: 'Alimento substituído com sucesso!',
      existingDiet: 'Dieta Existente',
      existingDietMessage: 'Você já possui sugestões geradas. Para alterar, use a substituição de alimentos.',
      categories: {
        protein: 'Proteína',
        carb: 'Carboidrato',
        fat: 'Gordura',
        fruit: 'Fruta',
        vegetable: 'Vegetal',
      },
      noDietGenerated: 'Nenhuma sugestão foi gerada ainda',
      generateYourDiet: 'Gerar sugestões',
      generateMyDiet: 'Gerar Minha Dieta',
      substitute: 'Substituir',
      success: 'Sucesso',
    },
    workout: {
      title: 'Exercícios',
      noData: 'Nenhuma sugestão gerada',
      generateWorkout: 'Gerar Meu Treino',
      generating: 'Preparando sugestões de exercícios...',
      markComplete: 'Marcar como Concluído',
      completed: 'Concluído!',
      viewHistory: 'Ver Histórico',
      history: 'Histórico de Exercícios',
      noHistory: 'Nenhum exercício registrado ainda.',
      sets: 'Séries',
      reps: 'Repetições',
      rest: 'Descanso',
      exercises: 'exercícios',
      howToExecute: 'Como executar',
      restTimer: 'Timer de Descanso',
      start: 'Iniciar',
      restart: 'Reiniciar',
      exercises: 'Exercícios',
      thisWeek: 'Esta Semana',
      completeHint: 'Complete exercícios para ver seu histórico aqui',
      weekProgress: 'Progresso da Semana',
      customWorkout: 'Exercícios adaptados',
      training: 'Treino',
    },
    cardio: {
      title: 'Cardio',
      sessionsPerWeek: 'sessões/semana',
      minPerWeek: 'min/semana',
      kcalPerWeek: 'kcal/semana',
      yourExercises: 'Seus Exercícios',
      perWeek: 'por semana',
      substitutes: 'Substitutos',
      tip: 'Dica',
      moderate: 'Moderado',
      zone: 'Zona',
    },
    progress: {
      title: 'Seu Progresso',
      subtitle: 'Acompanhe sua evolução',
      currentWeight: 'Peso Atual',
      targetWeight: 'Peso Meta',
      remaining: 'Faltam',
      recordWeight: 'Registrar Peso',
      weightHistory: 'Histórico de Peso',
      noRecords: 'Nenhum registro ainda',
      last30Days: 'Últimos 30 dias',
      evolution: 'Evolução',
      addWeight: 'Adicionar Peso',
      enterWeight: 'Digite seu peso em kg',
      inPeriod: 'no período',
      nextRecordIn: 'Próximo registro em',
      days: 'dias',
      total: 'Total',
      records: 'Registros',
      recordEvery2Weeks: 'Registre seu peso a cada 2 semanas',
      history: 'Histórico',
      howWasYourWeek: 'COMO FOI SUA SEMANA?',
      sleep: 'Sono',
      weightSaved: 'Peso registrado com sucesso!',
    },
    settings: {
      title: 'Configurações',
      subtitle: 'Configure suas preferências',
      account: 'Conta',
      editProfile: 'Editar Perfil',
      diet: 'Alimentação',
      mealsPerDay: 'Refeições por dia',
      meals: 'Refeições',
      training: 'Treino',
      configureTraining: 'Configurar Treino',
      timesPerWeek: 'vezes por semana',
      preferences: 'Preferências',
      lightMode: 'Modo Claro',
      notifications: 'Notificações',
      support: 'Suporte',
      privacy: 'Política de Privacidade',
      termsOfUse: 'Termos de Uso',
      methodology: 'Metodologia e Fontes',
      help: 'Ajuda',
      logout: 'Sair',
      logoutTitle: 'Sair da Conta',
      logoutConfirm: 'Tem certeza que deseja sair?',
      cancel: 'Cancelar',
      version: 'Versão',
      madeWithLove: 'Feito com ❤️',
      user: 'Usuário',
    },
    notificationSettings: {
      title: 'Notificações',
      enableAll: 'Ativar Notificações',
      enableAllDesc: 'Habilita todas as notificações do app',
      sendTest: 'Enviar Notificação de Teste',
      mealReminders: 'Lembretes de Refeições',
      mealRemindersTitle: 'Lembretes de Refeições',
      mealRemindersDesc: 'Receba lembretes nos horários das suas refeições',
      mealTimes: 'Horários das Refeições',
      workoutReminder: 'Lembrete de Exercício',
      workoutReminderTitle: 'Lembrete de Exercício',
      workoutReminderDesc: 'Lembrete diário',
      weightReminder: 'Lembrete de Peso',
      weightReminderTitle: 'Lembrete Semanal',
      weightReminderDesc: 'Lembre-se de registrar seu peso',
      day: 'Dia',
      time: 'Horário',
      infoText: 'As notificações push funcionam mesmo com o app fechado. Certifique-se de permitir notificações nas configurações do seu dispositivo.',
    },
    trainingConfig: {
      title: 'Configurar Treino',
      experienceLevel: 'Nível de Experiência',
      weeklyFrequency: 'Frequência Semanal',
      availableTime: 'Tempo Disponível',
      saveSettings: 'Salvar Configurações',
      savingSettings: 'Salvando...',
      successTitle: 'Sucesso!',
      successMessage: 'Configurações salvas e exercícios atualizados!',
      errorTitle: 'Erro',
      errorSave: 'Não foi possível salvar',
      errorConnect: 'Não foi possível conectar ao servidor',
      novice: '🆕 Novato',
      noviceDesc: 'Nunca treinei',
      beginner: '🌱 Iniciante',
      beginnerDesc: '0-1 anos de academia',
      intermediate: '💪 Intermediário',
      intermediateDesc: '1-2 anos de academia',
      advanced: '🏆 Avançado',
      advancedDesc: '3+ anos de academia',
      lowVolume: '🎯 Low Volume',
      lowVolumeDesc: 'Treino intenso com poucas séries',
      noviceHint: '💡 Novatos começam com adaptação por 4-8 semanas. Após 30 exercícios concluídos, você receberá exercícios para hipertrofia!',
      freq2x: '2x por semana',
      freq2xDesc: 'Full Body',
      freq3x: '3x por semana',
      freq3xDesc: 'ABC',
      freq4x: '4x por semana',
      freq4xDesc: 'ABCD',
      freq5x: '5x por semana',
      freq5xDesc: 'ABCDE',
      freq6x: '6x por semana',
      freq6xDesc: 'PPL 2x',
      dur30: '30 minutos',
      dur30Desc: 'Treino rápido',
      dur60: '1 hora',
      dur60Desc: 'Treino padrão',
      dur90: '1h 30min',
      dur90Desc: 'Treino completo',
      dur120: '2 horas',
      dur120Desc: 'Treino extenso',
    },
    privacy: {
      title: 'Privacidade',
      dataSecurity: 'Segurança dos Dados',
      dataSecurityDesc: 'Seus dados são armazenados de forma segura e criptografada. Não compartilhamos suas informações com terceiros.',
      protectedAccess: 'Acesso Protegido',
      protectedAccessDesc: 'Suas credenciais são protegidas e apenas você tem acesso aos seus dados pessoais e de saúde.',
      transparency: 'Transparência',
      transparencyDesc: 'Você pode visualizar, editar ou excluir seus dados a qualquer momento através das configurações do app.',
      localStorage: 'Armazenamento Local',
      localStorageDesc: 'Parte dos seus dados são armazenados localmente no seu dispositivo para melhor performance.',
      requestDeletion: 'Solicitar Exclusão de Dados',
      // Account Deletion
      deleteAccountTitle: 'Excluir Conta',
      deleteAccountWarning: 'Esta ação é irreversível. Todos os seus dados serão permanentemente excluídos, incluindo:',
      deleteListProfile: 'Perfil e configurações',
      deleteListDiet: 'Histórico de dietas',
      deleteListWorkout: 'Histórico de exercícios',
      deleteListProgress: 'Progresso e medições',
      confirmPassword: 'Digite sua senha para confirmar:',
      passwordPlaceholder: 'Sua senha',
      passwordRequired: 'Digite sua senha para confirmar',
      accountDeleted: 'Conta Excluída',
      accountDeletedDesc: 'Sua conta e todos os dados foram excluídos permanentemente.',
      deleteError: 'Erro ao excluir conta. Verifique sua senha.',
      confirmDelete: 'Excluir Conta',
    },
    terms: {
      title: 'Termos de Uso',
      acceptance: '1. Aceitação',
      acceptanceDesc: 'Ao utilizar o LAF, você concorda com estes termos de uso. O aplicativo oferece sugestões para auxiliar em seus objetivos de saúde e fitness.',
      responsibleUse: '2. Uso Responsável',
      responsibleUseDesc: 'As informações fornecidas pelo app são apenas sugestões e não substituem o acompanhamento profissional de nutricionistas ou médicos.',
      limitations: '3. Limitações',
      limitationsDesc: 'O LAF não se responsabiliza por resultados individuais. Cada pessoa responde de forma diferente a alimentação e exercícios.',
      health: '4. Saúde',
      healthDesc: 'Antes de iniciar qualquer rotina de alimentação ou exercícios, consulte um profissional de saúde. Seu bem-estar é nossa prioridade.',
      lastUpdate: 'Última atualização: Janeiro 2025',
    },
    settingsScreen: {
      profileUpdated: 'Perfil atualizado com sucesso!',
      information: 'INFORMAÇÕES',
      goal: 'OBJETIVO',
      saveChanges: 'Salvar Alterações',
      mealConfigTitle: 'Configurar Refeições',
      mealConfigSubtitle: 'Ajuste o número de refeições do seu dia',
      mealsPerDay: 'Refeições por dia',
      mealsUpdated: 'Refeições atualizadas com sucesso!',
      settingsSavedDiet: 'Configurações salvas e sugestões atualizadas!',
      mealsPerDayLabel: 'refeições/dia',
    },
    meals: {
      breakfast: 'Café da Manhã',
      morningSnack: 'Lanche Manhã',
      lunch: 'Almoço',
      afternoonSnack: 'Lanche Tarde',
      dinner: 'Jantar',
      supper: 'Ceia',
      eveningSnack: 'Ceia',
    },
    weekDays: {
      sunday: 'Domingo',
      monday: 'Segunda',
      tuesday: 'Terça',
      wednesday: 'Quarta',
      thursday: 'Quinta',
      friday: 'Sexta',
      saturday: 'Sábado',
    },
    athletePhases: {
      offSeason: 'Off-Season',
      prePrep: 'Pré-Prep',
      prep: 'Preparação',
      peakWeek: 'Peak Week',
      postShow: 'Pós-Show',
    },
    auth: {
      login: 'Entrar',
      signup: 'Criar Conta',
      email: 'Email',
      password: 'Senha',
      forgotPassword: 'Esqueceu a senha?',
      noAccount: 'Não tem conta?',
      hasAccount: 'Já tem conta?',
      createAccount: 'Criar conta',
      enterAccount: 'Entre na sua conta',
    },
    onboarding: {
      steps: {
        basicInfo: 'Dados Básicos',
        physicalData: 'Dados Físicos',
        trainingLevel: 'Nível de Treino',
        yourGoal: 'Seu Objetivo',
        preferences: 'Preferências',
        meals: 'Refeições',
      },
      saving: 'Salvando...',
      finish: 'Finalizar',
      letsStart: 'Vamos começar!',
      tellUsAboutYou: 'Conte-nos sobre você para ajustarmos as sugestões.',
      name: 'Nome',
      yourName: 'Seu nome',
      age: 'Idade',
      yourAge: 'Sua idade',
      sex: 'Sexo',
      male: 'Masculino',
      female: 'Feminino',
      physicalDataTitle: 'Dados Físicos',
      physicalDataDesc: 'Essas informações são essenciais para calcular suas necessidades calóricas.',
      height: 'Altura (cm)',
      heightPlaceholder: 'Ex: 175',
      currentWeight: 'Peso Atual (kg)',
      currentWeightPlaceholder: 'Ex: 80',
      targetWeight: 'Peso Meta (kg) - Opcional',
      targetWeightPlaceholder: 'Ex: 75',
      bodyFatPercentage: 'Percentual de Gordura (%) - Opcional',
      bodyFatPlaceholder: 'Ex: 15',
      bodyFatHint: 'Se não souber, pode deixar em branco.',
      trainingLevelTitle: 'Nível de Treino',
      trainingLevelDesc: 'Isso nos ajuda a calibrar a intensidade e volume dos seus exercícios.',
      currentLevel: 'Qual seu nível atual?',
      novice: '🆕 Novato',
      noviceDesc: 'Nunca treinei',
      beginner: 'Iniciante',
      beginnerDesc: '0-1 ano de prática',
      intermediate: 'Intermediário',
      intermediateDesc: '1-3 anos de prática',
      advanced: 'Avançado',
      advancedDesc: '3+ anos de prática',
      daysPerWeek: 'Quantos dias por semana você pode treinar?',
      daysPlaceholder: 'Ex: 4',
      timePerSession: 'Tempo disponível por sessão (minutos)',
      timePlaceholder: 'Ex: 60',
      goalTitle: 'Qual seu objetivo?',
      goalDesc: 'Vamos ajustar as sugestões de alimentação e exercícios para seu objetivo.',
      cutting: 'Emagrecimento (Cutting)',
      cuttingDesc: 'Perder gordura e definir',
      bulking: 'Ganho de Massa (Bulking)',
      bulkingDesc: 'Ganhar músculo e força',
      maintenance: 'Manutenção',
      maintenanceDesc: 'Manter peso e melhorar performance',
      athlete: 'Atleta/Competição',
      athleteDesc: 'Preparação automática até o campeonato (Off-Season, Pré-Contest, Peak Week)',
      competitionDate: 'Data do Campeonato *',
      competitionDateDesc: 'Informe a data do seu campeonato. O sistema controlará sua preparação automaticamente até o dia do evento.',
      selectDate: 'Selecionar data',
      weeksToCompetition: 'semanas até o campeonato',
      competitionPassed: 'Campeonato passou',
      foodPreferences: 'Preferências Alimentares',
      foodPreferencesDescAthlete: 'Lista restrita de alimentos base para dieta de atleta. Apenas alimentos limpos e de fácil medição.',
      foodPreferencesDescGeneral: 'Selecione os alimentos que você gosta. Maior variedade para uma dieta flexível.',
      athleteMode: 'Modo Atleta: Lista Restrita',
      flexibleMode: 'Modo Flexível: Lista Expandida',
      dietaryRestrictions: 'Restrições Alimentares',
      vegetarian: 'Vegetariano',
      lactoseFree: 'Sem Lactose',
      glutenFree: 'Sem Glúten',
      lowCarb: 'Low Carb',
      availableFoods: 'Alimentos Disponíveis',
      selected: 'selecionados',
      proteins: 'Proteínas',
      proteinsDesc: 'Fontes de proteína',
      carbs: 'Carboidratos',
      carbsDesc: 'Fontes de energia',
      fats: 'Gorduras',
      fatsDesc: 'Gorduras boas',
      fruits: 'Frutas',
      fruitsDesc: 'Vitaminas e fibras',
      vegetables: 'Vegetais e Legumes',
      vegetablesDesc: 'Fibras e micronutrientes',
      supplements: 'Suplementação',
      supplementsDesc: 'Não substitui refeições',
      separate: 'SEPARADO',
      mealsPerDay: 'Refeições por dia',
      distribution: 'Distribuição',
      athleteInfoBox: 'Dieta de atleta: quantidades em múltiplos de 10g para medição precisa.',
      generalInfoBox: 'Você pode ajustar suas preferências depois nas configurações.',
      skipHint: 'Você pode pular esta etapa e ajustar depois nas configurações.',
      // Extended restrictions (RestrictionsStep)
      vegan: 'Vegano',
      eggFree: 'Sem Ovo',
      peanutFree: 'Sem Amendoim',
      restrictions: 'Restrições Alimentares',
      restrictionsDesc: 'Marque se você possui alguma restrição alimentar.',
      preferences: 'Preferências de Dieta',
      preferencesDesc: 'Escolha o estilo alimentar que prefere.',
      highProtein: 'Alta Proteína',
      mediterranean: 'Mediterrânea',
      wholeFoods: 'Alimentos Integrais',
      requiredFields: 'Campos Obrigatórios',
      fillNameAgeSex: 'Preencha nome, idade e sexo.',
      invalidAge: 'Idade deve estar entre 15 e 100 anos.',
      fillHeightWeight: 'Preencha altura e peso atual.',
      invalidHeight: 'Altura deve estar entre 100cm e 250cm.',
      invalidWeight: 'Peso deve estar entre 30kg e 300kg.',
      fillTrainingFields: 'Preencha todos os campos de exercício.',
      invalidFrequency: 'Frequência deve estar entre 0 e 7 dias por semana.',
      selectGoal: 'Selecione seu objetivo principal.',
      dateRequired: 'Data Obrigatória',
      dateRequiredMessage: 'Para o modo Atleta, você precisa informar a data do seu campeonato.',
      sessionExpired: 'Sessão expirada. Faça login novamente.',
      error: 'Erro',
      couldNotSaveProfile: 'Não foi possível salvar seu perfil.',
    },
  },
  'en-US': {
    common: {
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      warning: 'Warning',
      cancel: 'Cancel',
      save: 'Save',
      confirm: 'Confirm',
      delete: 'Delete',
      edit: 'Edit',
      back: 'Back',
      next: 'Next',
      done: 'Done',
      connectionError: 'Connection Error',
      yes: 'Yes',
      no: 'No',
      saving: 'Saving...',
    },
    // Language Selection Screen
    languageSelect: {
      title: 'Choose your language',
      subtitle: 'Escolha seu idioma / Selecciona tu idioma',
      continue: 'Continue',
      yourAssistant: 'Your nutrition assistant',
    },
    // Paywall
    paywall: {
      subscribeMonthly: 'Subscribe for $5.99/month',
      subscribeAnnual: 'Subscribe for $39.99/year',
    },
    tabs: {
      home: 'Home',
      diet: 'Nutrition',
      workout: 'Exercises',
      cardio: 'Cardio',
      progress: 'Progress',
      settings: 'Settings',
    },
    home: {
      greeting: 'Hello',
      subtitle: "Let's achieve your goals",
      dailyGoal: 'Daily Goal',
      training: 'Training',
      weeklyFrequency: 'x/week',
      macrosDistribution: 'Macros Distribution',
      protein: 'Protein',
      carbs: 'Carbs',
      fat: 'Fat',
      yourGoal: 'Your Goal',
      cutting: 'Weight Loss (Cutting)',
      bulking: 'Muscle Gain (Bulking)',
      maintenance: 'Maintenance',
      athlete: 'Athlete/Competition',
      tdee: 'TDEE',
      comingSoon: 'Coming Soon',
      comingSoonText: 'Smart nutrition and AI-powered exercise suggestions',
      waterTracker: 'Hydration',
      waterGoalReached: 'Hydration goal reached! 🎉',
      viewDiet: 'View suggestions',
      macrosOfDay: 'Daily Macros',
      cups: 'cups',
      ofCups: 'of',
      active: 'ACTIVE',
      welcome: 'Welcome to LAF!',
      completeProfile: 'Complete your profile to get started',
      perWeek: 'PER WEEK',
      exercises: 'exercises',
    },
    diet: {
      title: 'Nutrition',
      mealsPlanned: 'meals planned',
      daySummary: 'Day Summary',
      noData: 'No suggestions generated',
      generateDiet: 'Generate My Diet',
      generating: 'Preparing nutrition suggestions...',
      tapToSubstitute: 'Tap on a food to substitute',
      mealsOfDay: 'Meals of the Day',
      supplements: 'Supplements',
      substituteFood: 'Substitute Food',
      currentFood: 'Current food',
      chooseSubstitute: 'Choose a substitute',
      noSubstitutes: 'No substitutes available for this food.',
      substituted: 'Food substituted successfully!',
      existingDiet: 'Existing Diet',
      existingDietMessage: 'You already have generated suggestions. To change, use food substitution.',
      categories: {
        protein: 'Protein',
        carb: 'Carbohydrate',
        fat: 'Fat',
        fruit: 'Fruit',
        vegetable: 'Vegetable',
      },
      noDietGenerated: 'No suggestions have been generated yet',
      generateYourDiet: 'Generate suggestions',
      generateMyDiet: 'Generate My Diet',
      substitute: 'Substitute',
      success: 'Success',
    },
    workout: {
      title: 'Exercises',
      noData: 'No suggestions generated',
      generateWorkout: 'Generate My Workout',
      generating: 'Preparing exercise suggestions...',
      markComplete: 'Mark as Complete',
      completed: 'Completed!',
      viewHistory: 'View History',
      history: 'Workout History',
      noHistory: 'No exercises recorded yet.',
      sets: 'Sets',
      reps: 'Reps',
      rest: 'Rest',
      exercises: 'exercises',
      howToExecute: 'How to execute',
      restTimer: 'Rest Timer',
      start: 'Start',
      restart: 'Restart',
      exercises: 'Exercises',
      thisWeek: 'This Week',
      completeHint: 'Complete exercises to see your history here',
      weekProgress: 'Weekly Progress',
      customWorkout: 'Custom exercises',
      training: 'Workout',
    },
    cardio: {
      title: 'Cardio',
      sessionsPerWeek: 'sessions/week',
      minPerWeek: 'min/week',
      kcalPerWeek: 'kcal/week',
      yourExercises: 'Your Exercises',
      perWeek: 'per week',
      substitutes: 'Substitutes',
      tip: 'Tip',
      moderate: 'Moderate',
      zone: 'Zone',
    },
    progress: {
      title: 'Your Progress',
      subtitle: 'Track your evolution',
      currentWeight: 'Current Weight',
      targetWeight: 'Target Weight',
      remaining: 'Remaining',
      recordWeight: 'Record Weight',
      weightHistory: 'Weight History',
      noRecords: 'No records yet',
      last30Days: 'Last 30 days',
      evolution: 'Evolution',
      addWeight: 'Add Weight',
      enterWeight: 'Enter your weight in kg',
      inPeriod: 'in period',
      nextRecordIn: 'Next record in',
      days: 'days',
      total: 'Total',
      records: 'Records',
      recordEvery2Weeks: 'Record your weight every 2 weeks',
      history: 'History',
      howWasYourWeek: 'HOW WAS YOUR WEEK?',
      sleep: 'Sleep',
      weightSaved: 'Weight saved successfully!',
    },
    settings: {
      title: 'Settings',
      subtitle: 'Customize your experience',
      account: 'Account',
      editProfile: 'Edit Profile',
      diet: 'Nutrition',
      mealsPerDay: 'Meals per day',
      meals: 'Meals',
      training: 'Training',
      configureTraining: 'Configure Training',
      timesPerWeek: 'times per week',
      preferences: 'Preferences',
      lightMode: 'Light Mode',
      notifications: 'Notifications',
      support: 'Support',
      privacy: 'Privacy Policy',
      termsOfUse: 'Terms of Use',
      methodology: 'Methodology & Sources',
      help: 'Help',
      logout: 'Log Out',
      logoutTitle: 'Log Out',
      logoutConfirm: 'Are you sure you want to log out?',
      cancel: 'Cancel',
      version: 'Version',
      madeWithLove: 'Made with ❤️',
      user: 'User',
    },
    notificationSettings: {
      title: 'Notifications',
      enableAll: 'Enable Notifications',
      enableAllDesc: 'Enable all app notifications',
      sendTest: 'Send Test Notification',
      mealReminders: 'Meal Reminders',
      mealRemindersTitle: 'Meal Reminders',
      mealRemindersDesc: 'Receive reminders at your meal times',
      mealTimes: 'Meal Times',
      workoutReminder: 'Exercise Reminder',
      workoutReminderTitle: 'Exercise Reminder',
      workoutReminderDesc: 'Daily reminder',
      weightReminder: 'Weight Reminder',
      weightReminderTitle: 'Weekly Reminder',
      weightReminderDesc: 'Remember to record your weight',
      day: 'Day',
      time: 'Time',
      infoText: 'Push notifications work even when the app is closed. Make sure to allow notifications in your device settings.',
    },
    trainingConfig: {
      title: 'Configure Training',
      experienceLevel: 'Experience Level',
      weeklyFrequency: 'Weekly Frequency',
      availableTime: 'Available Time',
      saveSettings: 'Save Settings',
      savingSettings: 'Saving...',
      successTitle: 'Success!',
      successMessage: 'Settings saved and exercises updated!',
      errorTitle: 'Error',
      errorSave: 'Could not save',
      errorConnect: 'Could not connect to server',
      novice: '🆕 Novice',
      noviceDesc: 'Never trained',
      beginner: '🌱 Beginner',
      beginnerDesc: '0-1 years in gym',
      intermediate: '💪 Intermediate',
      intermediateDesc: '1-2 years in gym',
      advanced: '🏆 Advanced',
      advancedDesc: '3+ years in gym',
      lowVolume: '🎯 Low Volume',
      lowVolumeDesc: 'Intense training with few sets',
      noviceHint: '💡 Novices start with adaptation training for 4-8 weeks. After 30 completed exercises, you\'ll receive hypertrophy exercises!',
      freq2x: '2x per week',
      freq2xDesc: 'Full Body',
      freq3x: '3x per week',
      freq3xDesc: 'ABC',
      freq4x: '4x per week',
      freq4xDesc: 'ABCD',
      freq5x: '5x per week',
      freq5xDesc: 'ABCDE',
      freq6x: '6x per week',
      freq6xDesc: 'PPL 2x',
      dur30: '30 minutes',
      dur30Desc: 'Quick session',
      dur60: '1 hour',
      dur60Desc: 'Standard session',
      dur90: '1h 30min',
      dur90Desc: 'Full session',
      dur120: '2 hours',
      dur120Desc: 'Extended workout',
    },
    privacy: {
      title: 'Privacy',
      dataSecurity: 'Data Security',
      dataSecurityDesc: 'Your data is stored securely and encrypted. We do not share your information with third parties.',
      protectedAccess: 'Protected Access',
      protectedAccessDesc: 'Your credentials are protected and only you have access to your personal and health data.',
      transparency: 'Transparency',
      transparencyDesc: 'You can view, edit, or delete your data at any time through the app settings.',
      localStorage: 'Local Storage',
      localStorageDesc: 'Part of your data is stored locally on your device for better performance.',
      requestDeletion: 'Request Data Deletion',
      // Account Deletion
      deleteAccountTitle: 'Delete Account',
      deleteAccountWarning: 'This action is irreversible. All your data will be permanently deleted, including:',
      deleteListProfile: 'Profile and settings',
      deleteListDiet: 'Diet history',
      deleteListWorkout: 'Workout history',
      deleteListProgress: 'Progress and measurements',
      confirmPassword: 'Enter your password to confirm:',
      passwordPlaceholder: 'Your password',
      passwordRequired: 'Enter your password to confirm',
      accountDeleted: 'Account Deleted',
      accountDeletedDesc: 'Your account and all data have been permanently deleted.',
      deleteError: 'Error deleting account. Check your password.',
      confirmDelete: 'Delete Account',
    },
    terms: {
      title: 'Terms of Use',
      acceptance: '1. Acceptance',
      acceptanceDesc: 'By using LAF, you agree to these terms of use. The app offers suggestions to help with your health and fitness goals.',
      responsibleUse: '2. Responsible Use',
      responsibleUseDesc: 'The information provided by the app is only suggestions and does not replace professional guidance from nutritionists or doctors.',
      limitations: '3. Limitations',
      limitationsDesc: 'LAF is not responsible for individual results. Each person responds differently to nutrition and exercises.',
      health: '4. Health',
      healthDesc: 'Before starting any nutrition or exercise routine, consult a health professional. Your well-being is our priority.',
      lastUpdate: 'Last update: January 2025',
    },
    settingsScreen: {
      profileUpdated: 'Profile updated successfully!',
      information: 'INFORMATION',
      goal: 'GOAL',
      saveChanges: 'Save Changes',
      mealConfigTitle: 'Configure Meals',
      mealConfigSubtitle: 'Adjust the number of meals per day',
      mealsPerDay: 'Meals per day',
      mealsUpdated: 'Meals updated successfully!',
      settingsSavedDiet: 'Settings saved and diet updated!',
      mealsPerDayLabel: 'meals/day',
    },
    meals: {
      breakfast: 'Breakfast',
      morningSnack: 'Morning Snack',
      lunch: 'Lunch',
      afternoonSnack: 'Afternoon Snack',
      dinner: 'Dinner',
      supper: 'Supper',
      eveningSnack: 'Evening Snack',
    },
    weekDays: {
      sunday: 'Sunday',
      monday: 'Monday',
      tuesday: 'Tuesday',
      wednesday: 'Wednesday',
      thursday: 'Thursday',
      friday: 'Friday',
      saturday: 'Saturday',
    },
    athletePhases: {
      offSeason: 'Off-Season',
      prePrep: 'Pre-Prep',
      prep: 'Preparation',
      peakWeek: 'Peak Week',
      postShow: 'Post-Show',
    },
    auth: {
      login: 'Log In',
      signup: 'Sign Up',
      email: 'Email',
      password: 'Password',
      forgotPassword: 'Forgot password?',
      noAccount: "Don't have an account?",
      hasAccount: 'Already have an account?',
      createAccount: 'Create account',
      enterAccount: 'Sign in to your account',
    },
    onboarding: {
      steps: {
        basicInfo: 'Basic Info',
        physicalData: 'Physical Data',
        trainingLevel: 'Training Level',
        yourGoal: 'Your Goal',
        preferences: 'Preferences',
        meals: 'Meals',
      },
      saving: 'Saving...',
      finish: 'Finish',
      letsStart: "Let's get started!",
      tellUsAboutYou: 'Tell us about yourself to adjust the suggestions.',
      name: 'Name',
      yourName: 'Your name',
      age: 'Age',
      yourAge: 'Your age',
      sex: 'Sex',
      male: 'Male',
      female: 'Female',
      physicalDataTitle: 'Physical Data',
      physicalDataDesc: 'This information is essential to calculate your caloric needs.',
      height: 'Height (cm)',
      heightPlaceholder: 'E.g.: 175',
      currentWeight: 'Current Weight (kg)',
      currentWeightPlaceholder: 'E.g.: 80',
      targetWeight: 'Target Weight (kg) - Optional',
      targetWeightPlaceholder: 'E.g.: 75',
      bodyFatPercentage: 'Body Fat Percentage (%) - Optional',
      bodyFatPlaceholder: 'E.g.: 15',
      bodyFatHint: "If you don't know, you can leave it blank.",
      trainingLevelTitle: 'Training Level',
      trainingLevelDesc: 'This helps us calibrate the intensity and volume of exercise suggestions.',
      currentLevel: 'What is your current level?',
      novice: '🆕 Novice',
      noviceDesc: 'Never trained',
      beginner: 'Beginner',
      beginnerDesc: '0-1 year of training',
      intermediate: 'Intermediate',
      intermediateDesc: '1-3 years of training',
      advanced: 'Advanced',
      advancedDesc: '3+ years of training',
      daysPerWeek: 'How many days per week can you train?',
      daysPlaceholder: 'E.g.: 4',
      timePerSession: 'Time available per session (minutes)',
      timePlaceholder: 'E.g.: 60',
      goalTitle: 'What is your goal?',
      goalDesc: "We'll adjust nutrition and exercise suggestions for your goal.",
      cutting: 'Weight Loss (Cutting)',
      cuttingDesc: 'Lose fat and get lean',
      bulking: 'Muscle Gain (Bulking)',
      bulkingDesc: 'Gain muscle and strength',
      maintenance: 'Maintenance',
      maintenanceDesc: 'Maintain weight and improve performance',
      athlete: 'Athlete/Competition',
      athleteDesc: 'Automatic preparation until competition (Off-Season, Pre-Contest, Peak Week)',
      competitionDate: 'Competition Date *',
      competitionDateDesc: 'Enter your competition date. The system will automatically control your preparation until the event day.',
      selectDate: 'Select date',
      weeksToCompetition: 'weeks until competition',
      competitionPassed: 'Competition has passed',
      foodPreferences: 'Food Preferences',
      foodPreferencesDescAthlete: 'Restricted list of base foods for athlete diet. Only clean foods easy to measure.',
      foodPreferencesDescGeneral: 'Select the foods you like. More variety for a flexible diet.',
      athleteMode: 'Athlete Mode: Restricted List',
      flexibleMode: 'Flexible Mode: Expanded List',
      dietaryRestrictions: 'Dietary Restrictions',
      vegetarian: 'Vegetarian',
      lactoseFree: 'Lactose Free',
      glutenFree: 'Gluten Free',
      lowCarb: 'Low Carb',
      availableFoods: 'Available Foods',
      selected: 'selected',
      proteins: 'Proteins',
      proteinsDesc: 'Protein sources',
      carbs: 'Carbohydrates',
      carbsDesc: 'Energy sources',
      fats: 'Fats',
      fatsDesc: 'Healthy fats',
      fruits: 'Fruits',
      fruitsDesc: 'Vitamins and fiber',
      vegetables: 'Vegetables',
      vegetablesDesc: 'Fiber and micronutrients',
      supplements: 'Supplements',
      supplementsDesc: 'Does not replace meals',
      separate: 'SEPARATE',
      mealsPerDay: 'Meals per day',
      distribution: 'Distribution',
      athleteInfoBox: 'Athlete diet: quantities in multiples of 10g for precise measurement.',
      generalInfoBox: 'You can adjust your preferences later in settings.',
      skipHint: 'You can skip this step and adjust later in settings.',
      // Extended restrictions (RestrictionsStep)
      vegan: 'Vegan',
      eggFree: 'Egg Free',
      peanutFree: 'Peanut Free',
      restrictions: 'Dietary Restrictions',
      restrictionsDesc: 'Mark if you have any dietary restrictions.',
      preferences: 'Diet Preferences',
      preferencesDesc: 'Choose the diet style you prefer.',
      highProtein: 'High Protein',
      mediterranean: 'Mediterranean',
      wholeFoods: 'Whole Foods',
      requiredFields: 'Required Fields',
      fillNameAgeSex: 'Fill in name, age, and sex.',
      invalidAge: 'Age must be between 15 and 100 years.',
      fillHeightWeight: 'Fill in height and current weight.',
      invalidHeight: 'Height must be between 100cm and 250cm.',
      invalidWeight: 'Weight must be between 30kg and 300kg.',
      fillTrainingFields: 'Fill in all training fields.',
      invalidFrequency: 'Frequency must be between 0 and 7 days per week.',
      selectGoal: 'Select your main goal.',
      dateRequired: 'Date Required',
      dateRequiredMessage: 'For Athlete mode, you need to provide your competition date.',
      sessionExpired: 'Session expired. Please log in again.',
      error: 'Error',
      couldNotSaveProfile: 'Could not save your profile.',
    },
  },
  'es-ES': {
    common: {
      loading: 'Cargando...',
      error: 'Error',
      success: 'Éxito',
      warning: 'Advertencia',
      cancel: 'Cancelar',
      save: 'Guardar',
      confirm: 'Confirmar',
      delete: 'Eliminar',
      edit: 'Editar',
      back: 'Volver',
      next: 'Siguiente',
      done: 'Hecho',
      connectionError: 'Error de Conexión',
      yes: 'Sí',
      no: 'No',
      saving: 'Guardando...',
    },
    // Language Selection Screen
    languageSelect: {
      title: 'Elige tu idioma',
      subtitle: 'Escolha seu idioma / Select your language',
      continue: 'Continuar',
      yourAssistant: 'Tu asistente de nutrición',
    },
    // Paywall
    paywall: {
      subscribeMonthly: 'Suscribirse por €4,99/mes',
      subscribeAnnual: 'Suscribirse por €33,99/año',
    },
    tabs: {
      home: 'Inicio',
      diet: 'Alimentação',
      workout: 'Entreno',
      cardio: 'Cardio',
      progress: 'Progreso',
      settings: 'Config',
    },
    home: {
      greeting: 'Hola',
      subtitle: 'Vamos a lograr tus objetivos',
      dailyGoal: 'Meta Diaria',
      training: 'Entreno',
      weeklyFrequency: 'x/semana',
      macrosDistribution: 'Distribución de Macros',
      protein: 'Proteínas',
      carbs: 'Carbohidratos',
      fat: 'Grasas',
      yourGoal: 'Tu Objetivo',
      cutting: 'Pérdida de Peso (Cutting)',
      bulking: 'Ganancia Muscular (Bulking)',
      maintenance: 'Mantenimiento',
      athlete: 'Atleta/Competición',
      tdee: 'TDEE',
      comingSoon: 'Próximamente',
      comingSoonText: 'Sugerencias inteligentes de alimentación y ejercicios con IA',
      waterTracker: 'Hidratación',
      waterGoalReached: '¡Meta de hidratación alcanzada! 🎉',
      viewDiet: 'Ver sugestões',
      macrosOfDay: 'Macros del Día',
      cups: 'vasos',
      ofCups: 'de',
      active: 'ACTIVO',
      welcome: '¡Bienvenido a LAF!',
      completeProfile: 'Completa tu perfil para empezar',
      perWeek: 'POR SEMANA',
      exercises: 'entrenos',
    },
    diet: {
      title: 'Alimentación',
      mealsPlanned: 'comidas planificadas',
      daySummary: 'Resumen del Día',
      noData: 'Ninguna dieta generada',
      generateDiet: 'Generar Mi Dieta',
      generating: 'Preparando sugestões...',
      tapToSubstitute: 'Toca un alimento para sustituir',
      mealsOfDay: 'Comidas del Día',
      supplements: 'Suplementos',
      substituteFood: 'Sustituir Alimento',
      currentFood: 'Alimento actual',
      chooseSubstitute: 'Elige un sustituto',
      noSubstitutes: 'No hay sustitutos disponibles para este alimento.',
      substituted: '¡Alimento sustituido con éxito!',
      existingDiet: 'Dieta Existente',
      existingDietMessage: 'Ya tienes sugerencias generadas. Para cambiar, usa la sustitución de alimentos.',
      categories: {
        protein: 'Proteína',
        carb: 'Carbohidrato',
        fat: 'Grasa',
        fruit: 'Fruta',
        vegetable: 'Vegetal',
      },
      noDietGenerated: 'Aún no se ha generado ninguna dieta',
      generateYourDiet: 'Genera sugerencias',
      generateMyDiet: 'Generar Mi Dieta',
      substitute: 'Sustituir',
      success: 'Éxito',
    },
    workout: {
      title: 'Ejercicios',
      noData: 'Ningún entreno generado',
      generateWorkout: 'Generar Mi Entreno',
      generating: 'Generando tu plan de entreno...',
      markComplete: 'Marcar como Completado',
      completed: '¡Completado!',
      viewHistory: 'Ver Historial',
      history: 'Historial de Entrenos',
      noHistory: 'Ningún entreno registrado aún.',
      sets: 'Series',
      reps: 'Reps',
      rest: 'Descanso',
      exercises: 'ejercicios',
      howToExecute: 'Cómo ejecutar',
      restTimer: 'Timer de Descanso',
      start: 'Iniciar',
      restart: 'Reiniciar',
      exercises: 'Entrenos',
      thisWeek: 'Esta Semana',
      completeHint: 'Completa ejercicios para ver tu historial aquí',
      weekProgress: 'Progreso Semanal',
      customWorkout: 'Ejercicios adaptados',
      training: 'Entreno',
    },
    cardio: {
      title: 'Cardio',
      sessionsPerWeek: 'sesiones/semana',
      minPerWeek: 'min/semana',
      kcalPerWeek: 'kcal/semana',
      yourExercises: 'Tus Ejercicios',
      perWeek: 'por semana',
      substitutes: 'Sustitutos',
      tip: 'Consejo',
      moderate: 'Moderado',
      zone: 'Zona',
    },
    progress: {
      title: 'Tu Progreso',
      subtitle: 'Sigue tu evolución',
      currentWeight: 'Peso Actual',
      targetWeight: 'Peso Meta',
      remaining: 'Faltan',
      recordWeight: 'Registrar Peso',
      weightHistory: 'Historial de Peso',
      noRecords: 'Sin registros aún',
      last30Days: 'Últimos 30 días',
      evolution: 'Evolución',
      addWeight: 'Agregar Peso',
      enterWeight: 'Ingresa tu peso en kg',
      inPeriod: 'en período',
      nextRecordIn: 'Próximo registro en',
      days: 'días',
      total: 'Total',
      records: 'Registros',
      recordEvery2Weeks: 'Registra tu peso cada 2 semanas',
      history: 'Historial',
      howWasYourWeek: '¿CÓMO FUE TU SEMANA?',
      sleep: 'Sueño',
      weightSaved: '¡Peso guardado con éxito!',
    },
    settings: {
      title: 'Configuración',
      subtitle: 'Configura tus preferencias',
      account: 'Cuenta',
      editProfile: 'Editar Perfil',
      diet: 'Alimentação',
      mealsPerDay: 'Comidas por día',
      meals: 'Comidas',
      training: 'Entreno',
      configureTraining: 'Configurar Entreno',
      timesPerWeek: 'veces por semana',
      preferences: 'Preferencias',
      lightMode: 'Modo Claro',
      notifications: 'Notificaciones',
      support: 'Soporte',
      privacy: 'Política de Privacidad',
      termsOfUse: 'Términos de Uso',
      help: 'Ayuda',
      logout: 'Cerrar Sesión',
      logoutTitle: 'Cerrar Sesión',
      logoutConfirm: '¿Estás seguro de que quieres cerrar sesión?',
      cancel: 'Cancelar',
      version: 'Versión',
      madeWithLove: 'Hecho con ❤️',
      user: 'Usuario',
    },
    notificationSettings: {
      title: 'Notificaciones',
      enableAll: 'Activar Notificaciones',
      enableAllDesc: 'Habilita todas las notificaciones de la app',
      sendTest: 'Enviar Notificación de Prueba',
      mealReminders: 'Recordatorios de Comidas',
      mealRemindersTitle: 'Recordatorios de Comidas',
      mealRemindersDesc: 'Recibe recordatorios en los horarios de tus comidas',
      mealTimes: 'Horarios de Comidas',
      workoutReminder: 'Recordatorio de Entreno',
      workoutReminderTitle: 'Recordatorio de Entreno',
      workoutReminderDesc: 'Recordatorio diario para entrenar',
      weightReminder: 'Recordatorio de Peso',
      weightReminderTitle: 'Recordatorio Semanal',
      weightReminderDesc: 'Recuerda registrar tu peso',
      day: 'Día',
      time: 'Hora',
      infoText: 'Las notificaciones push funcionan incluso con la app cerrada. Asegúrate de permitir notificaciones en la configuración de tu dispositivo.',
    },
    trainingConfig: {
      title: 'Configurar Entreno',
      experienceLevel: 'Nivel de Experiencia',
      weeklyFrequency: 'Frecuencia Semanal',
      availableTime: 'Tiempo Disponible',
      saveSettings: 'Guardar Configuración',
      savingSettings: 'Guardando...',
      successTitle: '¡Éxito!',
      successMessage: '¡Configuración guardada y entreno actualizado!',
      errorTitle: 'Error',
      errorSave: 'No se pudo guardar',
      errorConnect: 'No se pudo conectar al servidor',
      novice: '🆕 Novato',
      noviceDesc: 'Nunca entrené',
      beginner: '🌱 Principiante',
      beginnerDesc: '0-1 años en gimnasio',
      intermediate: '💪 Intermedio',
      intermediateDesc: '1-2 años en gimnasio',
      advanced: '🏆 Avanzado',
      advancedDesc: '3+ años en gimnasio',
      lowVolume: '🎯 Low Volume',
      lowVolumeDesc: 'Entreno intenso con pocas series',
      noviceHint: '💡 Los novatos comienzan con entreno de adaptación por 4-8 semanas. ¡Después de 30 entrenos completados, recibirás entrenos de hipertrofia!',
      freq2x: '2x por semana',
      freq2xDesc: 'Full Body',
      freq3x: '3x por semana',
      freq3xDesc: 'ABC',
      freq4x: '4x por semana',
      freq4xDesc: 'ABCD',
      freq5x: '5x por semana',
      freq5xDesc: 'ABCDE',
      freq6x: '6x por semana',
      freq6xDesc: 'PPL 2x',
      dur30: '30 minutos',
      dur30Desc: 'Entreno rápido',
      dur60: '1 hora',
      dur60Desc: 'Entreno estándar',
      dur90: '1h 30min',
      dur90Desc: 'Entreno completo',
      dur120: '2 horas',
      dur120Desc: 'Entreno extenso',
    },
    privacy: {
      title: 'Privacidad',
      dataSecurity: 'Seguridad de Datos',
      dataSecurityDesc: 'Tus datos se almacenan de forma segura y encriptada. No compartimos tu información con terceros.',
      protectedAccess: 'Acceso Protegido',
      protectedAccessDesc: 'Tus credenciales están protegidas y solo tú tienes acceso a tus datos personales y de salud.',
      transparency: 'Transparencia',
      transparencyDesc: 'Puedes ver, editar o eliminar tus datos en cualquier momento a través de la configuración de la app.',
      localStorage: 'Almacenamiento Local',
      localStorageDesc: 'Parte de tus datos se almacenan localmente en tu dispositivo para mejor rendimiento.',
      requestDeletion: 'Solicitar Eliminación de Datos',
      // Account Deletion
      deleteAccountTitle: 'Eliminar Cuenta',
      deleteAccountWarning: 'Esta acción es irreversible. Todos tus datos serán eliminados permanentemente, incluyendo:',
      deleteListProfile: 'Perfil y configuración',
      deleteListDiet: 'Historial de dietas',
      deleteListWorkout: 'Historial de entrenos',
      deleteListProgress: 'Progreso y mediciones',
      confirmPassword: 'Ingresa tu contraseña para confirmar:',
      passwordPlaceholder: 'Tu contraseña',
      passwordRequired: 'Ingresa tu contraseña para confirmar',
      accountDeleted: 'Cuenta Eliminada',
      accountDeletedDesc: 'Tu cuenta y todos los datos han sido eliminados permanentemente.',
      deleteError: 'Error al eliminar cuenta. Verifica tu contraseña.',
      confirmDelete: 'Eliminar Cuenta',
    },
    terms: {
      title: 'Términos de Uso',
      acceptance: '1. Aceptación',
      acceptanceDesc: 'Al usar LAF, aceptas estos términos de uso. La app ofrece sugerencias para ayudar con tus objetivos de salud y fitness.',
      responsibleUse: '2. Uso Responsable',
      responsibleUseDesc: 'La información proporcionada por la app son solo sugerencias y no reemplazan el acompañamiento profesional de nutricionistas o médicos.',
      limitations: '3. Limitaciones',
      limitationsDesc: 'LAF no se responsabiliza por resultados individuales. Cada persona responde de forma diferente a la alimentación y ejercicios.',
      health: '4. Salud',
      healthDesc: 'Antes de comenzar cualquier rutina de alimentación o ejercicios, consulta a un profesional de salud. Tu bienestar es nuestra prioridad.',
      lastUpdate: 'Última actualización: Enero 2025',
    },
    settingsScreen: {
      profileUpdated: '¡Perfil actualizado con éxito!',
      information: 'INFORMACIÓN',
      goal: 'OBJETIVO',
      saveChanges: 'Guardar Cambios',
      mealConfigTitle: 'Configurar Comidas',
      mealConfigSubtitle: 'Ajusta el número de comidas por día',
      mealsPerDay: 'Comidas por día',
      mealsUpdated: '¡Comidas actualizadas con éxito!',
      settingsSavedDiet: '¡Configuración guardada y dieta actualizada!',
      mealsPerDayLabel: 'comidas/día',
    },
    meals: {
      breakfast: 'Desayuno',
      morningSnack: 'Snack Mañana',
      lunch: 'Almuerzo',
      afternoonSnack: 'Snack Tarde',
      dinner: 'Cena',
      supper: 'Cena Ligera',
      eveningSnack: 'Merienda Nocturna',
    },
    weekDays: {
      sunday: 'Domingo',
      monday: 'Lunes',
      tuesday: 'Martes',
      wednesday: 'Miércoles',
      thursday: 'Jueves',
      friday: 'Viernes',
      saturday: 'Sábado',
    },
    athletePhases: {
      offSeason: 'Off-Season',
      prePrep: 'Pre-Prep',
      prep: 'Preparación',
      peakWeek: 'Peak Week',
      postShow: 'Post-Show',
    },
    auth: {
      login: 'Iniciar Sesión',
      signup: 'Registrarse',
      email: 'Correo',
      password: 'Contraseña',
      forgotPassword: '¿Olvidaste tu contraseña?',
      noAccount: '¿No tienes cuenta?',
      hasAccount: '¿Ya tienes cuenta?',
      createAccount: 'Crear cuenta',
      enterAccount: 'Entra en tu cuenta',
    },
    onboarding: {
      steps: {
        basicInfo: 'Datos Básicos',
        physicalData: 'Datos Físicos',
        trainingLevel: 'Nivel de Entreno',
        yourGoal: 'Tu Objetivo',
        preferences: 'Preferencias',
        meals: 'Comidas',
      },
      saving: 'Guardando...',
      finish: 'Finalizar',
      letsStart: '¡Vamos a empezar!',
      tellUsAboutYou: 'Cuéntanos un poco sobre ti para personalizar tu plan.',
      name: 'Nombre',
      yourName: 'Tu nombre',
      age: 'Edad',
      yourAge: 'Tu edad',
      sex: 'Sexo',
      male: 'Masculino',
      female: 'Femenino',
      physicalDataTitle: 'Datos Físicos',
      physicalDataDesc: 'Esta información es esencial para calcular tus necesidades calóricas.',
      height: 'Altura (cm)',
      heightPlaceholder: 'Ej: 175',
      currentWeight: 'Peso Actual (kg)',
      currentWeightPlaceholder: 'Ej: 80',
      targetWeight: 'Peso Meta (kg) - Opcional',
      targetWeightPlaceholder: 'Ej: 75',
      bodyFatPercentage: 'Porcentaje de Grasa (%) - Opcional',
      bodyFatPlaceholder: 'Ej: 15',
      bodyFatHint: 'Si no lo sabes, puedes dejarlo en blanco.',
      trainingLevelTitle: 'Nivel de Entreno',
      trainingLevelDesc: 'Esto nos ayuda a calibrar la intensidad y volumen de tus entrenos.',
      currentLevel: '¿Cuál es tu nivel actual?',
      novice: '🆕 Novato',
      noviceDesc: 'Nunca entrené',
      beginner: 'Principiante',
      beginnerDesc: '0-1 año de entreno',
      intermediate: 'Intermedio',
      intermediateDesc: '1-3 años de entreno',
      advanced: 'Avanzado',
      advancedDesc: '3+ años de entreno',
      daysPerWeek: '¿Cuántos días por semana puedes entrenar?',
      daysPlaceholder: 'Ej: 4',
      timePerSession: 'Tiempo disponible por sesión (minutos)',
      timePlaceholder: 'Ej: 60',
      goalTitle: '¿Cuál es tu objetivo?',
      goalDesc: 'Ajustaremos tu plan de dieta y entreno a tu objetivo específico.',
      cutting: 'Pérdida de Peso (Cutting)',
      cuttingDesc: 'Perder grasa y definir',
      bulking: 'Ganancia Muscular (Bulking)',
      bulkingDesc: 'Ganar músculo y fuerza',
      maintenance: 'Mantenimiento',
      maintenanceDesc: 'Mantener peso y mejorar rendimiento',
      athlete: 'Atleta/Competición',
      athleteDesc: 'Preparación automática hasta la competición (Off-Season, Pre-Contest, Peak Week)',
      competitionDate: 'Fecha de Competición *',
      competitionDateDesc: 'Ingresa la fecha de tu competición. El sistema controlará automáticamente tu preparación hasta el día del evento.',
      selectDate: 'Seleccionar fecha',
      weeksToCompetition: 'semanas hasta la competición',
      competitionPassed: 'La competición ya pasó',
      foodPreferences: 'Preferencias Alimentarias',
      foodPreferencesDescAthlete: 'Lista restringida de alimentos base para dieta de atleta. Solo alimentos limpios y fáciles de medir.',
      foodPreferencesDescGeneral: 'Selecciona los alimentos que te gustan. Mayor variedad para una dieta flexible.',
      athleteMode: 'Modo Atleta: Lista Restringida',
      flexibleMode: 'Modo Flexible: Lista Expandida',
      dietaryRestrictions: 'Restricciones Dietéticas',
      vegetarian: 'Vegetariano',
      lactoseFree: 'Sin Lactosa',
      glutenFree: 'Sin Gluten',
      lowCarb: 'Low Carb',
      availableFoods: 'Alimentos Disponibles',
      selected: 'seleccionados',
      proteins: 'Proteínas',
      proteinsDesc: 'Fuentes de proteína',
      carbs: 'Carbohidratos',
      carbsDesc: 'Fuentes de energía',
      fats: 'Grasas',
      fatsDesc: 'Grasas saludables',
      fruits: 'Frutas',
      fruitsDesc: 'Vitaminas y fibra',
      vegetables: 'Vegetales y Verduras',
      vegetablesDesc: 'Fibra y micronutrientes',
      supplements: 'Suplementos',
      supplementsDesc: 'No reemplaza comidas',
      separate: 'SEPARADO',
      mealsPerDay: 'Comidas por día',
      distribution: 'Distribución',
      athleteInfoBox: 'Dieta de atleta: cantidades en múltiplos de 10g para medición precisa.',
      generalInfoBox: 'Puedes ajustar tus preferencias después en configuración.',
      skipHint: 'Puedes saltar este paso y ajustar después en configuración.',
      // Extended restrictions (RestrictionsStep)
      vegan: 'Vegano',
      eggFree: 'Sin Huevo',
      peanutFree: 'Sin Maní',
      restrictions: 'Restricciones Alimentarias',
      restrictionsDesc: 'Marca si tienes alguna restricción alimentaria.',
      preferences: 'Preferencias de Dieta',
      preferencesDesc: 'Elige el estilo alimentar que prefieres.',
      highProtein: 'Alta Proteína',
      mediterranean: 'Mediterránea',
      wholeFoods: 'Alimentos Integrales',
      requiredFields: 'Campos Requeridos',
      fillNameAgeSex: 'Completa nombre, edad y sexo.',
      invalidAge: 'La edad debe estar entre 15 y 100 años.',
      fillHeightWeight: 'Completa altura y peso actual.',
      invalidHeight: 'La altura debe estar entre 100cm y 250cm.',
      invalidWeight: 'El peso debe estar entre 30kg y 300kg.',
      fillTrainingFields: 'Completa todos los campos de entreno.',
      invalidFrequency: 'La frecuencia debe estar entre 0 y 7 días por semana.',
      selectGoal: 'Selecciona tu objetivo principal.',
      dateRequired: 'Fecha Requerida',
      dateRequiredMessage: 'Para el modo Atleta, necesitas proporcionar la fecha de tu competición.',
      sessionExpired: 'Sesión expirada. Por favor inicia sesión de nuevo.',
      error: 'Error',
      couldNotSaveProfile: 'No se pudo guardar tu perfil.',
    },
  },
};
