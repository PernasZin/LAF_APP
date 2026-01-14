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
    workouts: string;
  };
  // Diet screen
  diet: {
    title: string;
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
    workouts: string;
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
    diabetic: string;
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
    tabs: {
      home: 'Início',
      diet: 'Dieta',
      workout: 'Treino',
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
      comingSoonText: 'Sistema de dieta personalizada e treinos sob medida com IA',
      waterTracker: 'Hidratação',
      waterGoalReached: 'Meta de hidratação atingida! 🎉',
      viewDiet: 'Ver dieta',
      macrosOfDay: 'Macros do Dia',
      cups: 'copos',
      ofCups: 'de',
      active: 'ATIVO',
      welcome: 'Bem-vindo ao LAF!',
      completeProfile: 'Complete seu perfil para começar',
      perWeek: 'POR SEMANA',
      workouts: 'treinos',
    },
    diet: {
      title: 'Seu Plano de Dieta',
      noData: 'Nenhuma dieta gerada',
      generateDiet: 'Gerar Minha Dieta',
      generating: 'Gerando seu plano de dieta...',
      tapToSubstitute: 'Toque em um alimento para substituir',
      mealsOfDay: 'Refeições do Dia',
      supplements: 'Suplementação',
      substituteFood: 'Substituir Alimento',
      currentFood: 'Alimento atual',
      chooseSubstitute: 'Escolha um substituto',
      noSubstitutes: 'Nenhum substituto disponível para este alimento.',
      substituted: 'Alimento substituído com sucesso!',
      existingDiet: 'Dieta Existente',
      existingDietMessage: 'Você já possui uma dieta gerada. Para alterar, use a substituição de alimentos.',
      categories: {
        protein: 'Proteína',
        carb: 'Carboidrato',
        fat: 'Gordura',
        fruit: 'Fruta',
        vegetable: 'Vegetal',
      },
    },
    workout: {
      title: 'Seu Plano de Treino',
      noData: 'Nenhum treino gerado',
      generateWorkout: 'Gerar Meu Treino',
      generating: 'Gerando seu plano de treino...',
      markComplete: 'Marcar como Concluído',
      completed: 'Concluído!',
      viewHistory: 'Ver Histórico',
      history: 'Histórico de Treinos',
      noHistory: 'Nenhum treino registrado ainda.',
      sets: 'Séries',
      reps: 'Repetições',
      rest: 'Descanso',
      exercises: 'exercícios',
      howToExecute: 'Como executar',
      restTimer: 'Timer de Descanso',
      start: 'Iniciar',
      restart: 'Reiniciar',
      workouts: 'Treinos',
      thisWeek: 'Esta Semana',
      completeHint: 'Complete exercícios para ver seu histórico aqui',
      weekProgress: 'Progresso da Semana',
      customWorkout: 'Treino personalizado',
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
      account: 'Conta',
      editProfile: 'Editar Perfil',
      logout: 'Sair da Conta',
      notifications: 'Notificações',
      enableNotifications: 'Ativar Notificações',
      notificationsDesc: 'Receba lembretes de refeições e treinos',
      configureReminders: 'Configurar Lembretes',
      remindersDesc: 'Horários de refeições, treino e peso',
      appearance: 'Aparência',
      theme: 'Tema',
      themeDesc: 'Escolha como o app deve aparecer',
      system: 'Sistema',
      light: 'Claro',
      dark: 'Escuro',
      language: 'Idioma',
      data: 'Dados',
      clearCache: 'Limpar Cache',
      clearCacheDesc: 'Remove dados em cache localmente',
      legal: 'Legal',
      privacy: 'Política de Privacidade',
      terms: 'Termos de Uso',
      version: 'Versão',
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
      workoutReminder: 'Lembrete de Treino',
      workoutReminderTitle: 'Lembrete de Treino',
      workoutReminderDesc: 'Lembrete diário para treinar',
      weightReminder: 'Lembrete de Peso',
      weightReminderTitle: 'Lembrete Semanal',
      weightReminderDesc: 'Lembre-se de registrar seu peso',
      day: 'Dia',
      time: 'Horário',
      infoText: 'As notificações push funcionam mesmo com o app fechado. Certifique-se de permitir notificações nas configurações do seu dispositivo.',
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
      tellUsAboutYou: 'Conte-nos um pouco sobre você para personalizarmos seu plano.',
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
      trainingLevelDesc: 'Isso nos ajuda a calibrar a intensidade e volume dos seus treinos.',
      currentLevel: 'Qual seu nível atual?',
      beginner: 'Iniciante',
      beginnerDesc: '0-1 ano de treino',
      intermediate: 'Intermediário',
      intermediateDesc: '1-3 anos de treino',
      advanced: 'Avançado',
      advancedDesc: '3+ anos de treino',
      daysPerWeek: 'Quantos dias por semana você pode treinar?',
      daysPlaceholder: 'Ex: 4',
      timePerSession: 'Tempo disponível por treino (minutos)',
      timePlaceholder: 'Ex: 60',
      goalTitle: 'Qual seu objetivo?',
      goalDesc: 'Vamos ajustar seu plano de dieta e treino para seu objetivo específico.',
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
      dietaryRestrictions: 'Restrições Dietéticas',
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
      diabetic: 'Diabético',
      eggFree: 'Sem Ovo',
      peanutFree: 'Sem Amendoim',
      restrictions: 'Restrições Alimentares',
      restrictionsDesc: 'Marque se você possui alguma restrição alimentar.',
      preferences: 'Preferências de Dieta',
      preferencesDesc: 'Escolha o estilo de dieta que prefere.',
      highProtein: 'Alta Proteína',
      mediterranean: 'Mediterrânea',
      wholeFoods: 'Alimentos Integrais',
      requiredFields: 'Campos Obrigatórios',
      fillNameAgeSex: 'Preencha nome, idade e sexo.',
      invalidAge: 'Idade deve estar entre 15 e 100 anos.',
      fillHeightWeight: 'Preencha altura e peso atual.',
      invalidHeight: 'Altura deve estar entre 100cm e 250cm.',
      invalidWeight: 'Peso deve estar entre 30kg e 300kg.',
      fillTrainingFields: 'Preencha todos os campos de treino.',
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
    tabs: {
      home: 'Home',
      diet: 'Diet',
      workout: 'Workout',
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
      comingSoonText: 'Personalized diet and AI-powered workout plans',
      waterTracker: 'Hydration',
      waterGoalReached: 'Hydration goal reached! 🎉',
      viewDiet: 'View diet',
      macrosOfDay: 'Daily Macros',
      cups: 'cups',
      ofCups: 'of',
      active: 'ACTIVE',
      welcome: 'Welcome to LAF!',
      completeProfile: 'Complete your profile to get started',
      perWeek: 'PER WEEK',
      workouts: 'workouts',
    },
    diet: {
      title: 'Your Diet Plan',
      noData: 'No diet generated',
      generateDiet: 'Generate My Diet',
      generating: 'Generating your diet plan...',
      tapToSubstitute: 'Tap on a food to substitute',
      mealsOfDay: 'Meals of the Day',
      supplements: 'Supplements',
      substituteFood: 'Substitute Food',
      currentFood: 'Current food',
      chooseSubstitute: 'Choose a substitute',
      noSubstitutes: 'No substitutes available for this food.',
      substituted: 'Food substituted successfully!',
      existingDiet: 'Existing Diet',
      existingDietMessage: 'You already have a generated diet. To change, use food substitution.',
      categories: {
        protein: 'Protein',
        carb: 'Carbohydrate',
        fat: 'Fat',
        fruit: 'Fruit',
        vegetable: 'Vegetable',
      },
    },
    workout: {
      title: 'Your Workout Plan',
      noData: 'No workout generated',
      generateWorkout: 'Generate My Workout',
      generating: 'Generating your workout plan...',
      markComplete: 'Mark as Complete',
      completed: 'Completed!',
      viewHistory: 'View History',
      history: 'Workout History',
      noHistory: 'No workouts recorded yet.',
      sets: 'Sets',
      reps: 'Reps',
      rest: 'Rest',
      exercises: 'exercises',
      howToExecute: 'How to execute',
      restTimer: 'Rest Timer',
      start: 'Start',
      restart: 'Restart',
      workouts: 'Workouts',
      thisWeek: 'This Week',
      completeHint: 'Complete exercises to see your history here',
      weekProgress: 'Weekly Progress',
      customWorkout: 'Custom workout',
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
      account: 'Account',
      editProfile: 'Edit Profile',
      logout: 'Log Out',
      notifications: 'Notifications',
      enableNotifications: 'Enable Notifications',
      notificationsDesc: 'Receive meal and workout reminders',
      configureReminders: 'Configure Reminders',
      remindersDesc: 'Meal, workout, and weight schedules',
      appearance: 'Appearance',
      theme: 'Theme',
      themeDesc: 'Choose how the app should look',
      system: 'System',
      light: 'Light',
      dark: 'Dark',
      language: 'Language',
      data: 'Data',
      clearCache: 'Clear Cache',
      clearCacheDesc: 'Remove locally cached data',
      legal: 'Legal',
      privacy: 'Privacy Policy',
      terms: 'Terms of Use',
      version: 'Version',
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
      workoutReminder: 'Workout Reminder',
      workoutReminderTitle: 'Workout Reminder',
      workoutReminderDesc: 'Daily reminder to workout',
      weightReminder: 'Weight Reminder',
      weightReminderTitle: 'Weekly Reminder',
      weightReminderDesc: 'Remember to record your weight',
      day: 'Day',
      time: 'Time',
      infoText: 'Push notifications work even when the app is closed. Make sure to allow notifications in your device settings.',
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
      tellUsAboutYou: 'Tell us a bit about yourself to personalize your plan.',
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
      trainingLevelDesc: 'This helps us calibrate the intensity and volume of your workouts.',
      currentLevel: 'What is your current level?',
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
      goalDesc: "We'll adjust your diet and workout plan to your specific goal.",
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
      diabetic: 'Diabetic',
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
    tabs: {
      home: 'Inicio',
      diet: 'Dieta',
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
      comingSoonText: 'Sistema de dieta personalizada y entrenamientos con IA',
      waterTracker: 'Hidratación',
      waterGoalReached: '¡Meta de hidratación alcanzada! 🎉',
      viewDiet: 'Ver dieta',
      macrosOfDay: 'Macros del Día',
      cups: 'vasos',
      ofCups: 'de',
      active: 'ACTIVO',
      welcome: '¡Bienvenido a LAF!',
      completeProfile: 'Completa tu perfil para empezar',
      perWeek: 'POR SEMANA',
      workouts: 'entrenos',
    },
    diet: {
      title: 'Tu Plan de Dieta',
      noData: 'Ninguna dieta generada',
      generateDiet: 'Generar Mi Dieta',
      generating: 'Generando tu plan de dieta...',
      tapToSubstitute: 'Toca un alimento para sustituir',
      mealsOfDay: 'Comidas del Día',
      supplements: 'Suplementos',
      substituteFood: 'Sustituir Alimento',
      currentFood: 'Alimento actual',
      chooseSubstitute: 'Elige un sustituto',
      noSubstitutes: 'No hay sustitutos disponibles para este alimento.',
      substituted: '¡Alimento sustituido con éxito!',
      existingDiet: 'Dieta Existente',
      existingDietMessage: 'Ya tienes una dieta generada. Para cambiar, usa la sustitución de alimentos.',
      categories: {
        protein: 'Proteína',
        carb: 'Carbohidrato',
        fat: 'Grasa',
        fruit: 'Fruta',
        vegetable: 'Vegetal',
      },
    },
    workout: {
      title: 'Tu Plan de Entreno',
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
      workouts: 'Entrenos',
      thisWeek: 'Esta Semana',
      completeHint: 'Completa ejercicios para ver tu historial aquí',
      weekProgress: 'Progreso Semanal',
      customWorkout: 'Entreno personalizado',
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
      account: 'Cuenta',
      editProfile: 'Editar Perfil',
      logout: 'Cerrar Sesión',
      notifications: 'Notificaciones',
      enableNotifications: 'Activar Notificaciones',
      notificationsDesc: 'Recibe recordatorios de comidas y entrenos',
      configureReminders: 'Configurar Recordatorios',
      remindersDesc: 'Horarios de comidas, entreno y peso',
      appearance: 'Apariencia',
      theme: 'Tema',
      themeDesc: 'Elige cómo debe verse la app',
      system: 'Sistema',
      light: 'Claro',
      dark: 'Oscuro',
      language: 'Idioma',
      data: 'Datos',
      clearCache: 'Limpiar Caché',
      clearCacheDesc: 'Elimina datos en caché localmente',
      legal: 'Legal',
      privacy: 'Política de Privacidad',
      terms: 'Términos de Uso',
      version: 'Versión',
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
      diabetic: 'Diabético',
      eggFree: 'Sin Huevo',
      peanutFree: 'Sin Maní',
      restrictions: 'Restricciones Alimentarias',
      restrictionsDesc: 'Marca si tienes alguna restricción alimentaria.',
      preferences: 'Preferencias de Dieta',
      preferencesDesc: 'Elige el estilo de dieta que prefieres.',
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
