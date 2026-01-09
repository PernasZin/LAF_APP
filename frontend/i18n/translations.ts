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
    cancel: string;
    save: string;
    confirm: string;
    delete: string;
    edit: string;
    back: string;
    next: string;
    done: string;
    yes: string;
    no: string;
  };
  // Tab names
  tabs: {
    home: string;
    diet: string;
    workout: string;
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
  };
  // Progress screen
  progress: {
    title: string;
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
  };
  // Settings screen
  settings: {
    title: string;
    account: string;
    editProfile: string;
    logout: string;
    notifications: string;
    enableNotifications: string;
    notificationsDesc: string;
    configureReminders: string;
    remindersDesc: string;
    appearance: string;
    theme: string;
    themeDesc: string;
    system: string;
    light: string;
    dark: string;
    language: string;
    data: string;
    clearCache: string;
    clearCacheDesc: string;
    legal: string;
    privacy: string;
    terms: string;
    version: string;
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
}

export const translations: Record<SupportedLanguage, Translations> = {
  'pt-BR': {
    common: {
      loading: 'Carregando...',
      error: 'Erro',
      success: 'Sucesso',
      cancel: 'Cancelar',
      save: 'Salvar',
      confirm: 'Confirmar',
      delete: 'Excluir',
      edit: 'Editar',
      back: 'Voltar',
      next: 'Próximo',
      done: 'Concluído',
      yes: 'Sim',
      no: 'Não',
    },
    tabs: {
      home: 'Início',
      diet: 'Dieta',
      workout: 'Treino',
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
    },
    progress: {
      title: 'Seu Progresso',
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
  },
  'en-US': {
    common: {
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      cancel: 'Cancel',
      save: 'Save',
      confirm: 'Confirm',
      delete: 'Delete',
      edit: 'Edit',
      back: 'Back',
      next: 'Next',
      done: 'Done',
      yes: 'Yes',
      no: 'No',
    },
    tabs: {
      home: 'Home',
      diet: 'Diet',
      workout: 'Workout',
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
    },
    progress: {
      title: 'Your Progress',
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
  },
  'es-ES': {
    common: {
      loading: 'Cargando...',
      error: 'Error',
      success: 'Éxito',
      cancel: 'Cancelar',
      save: 'Guardar',
      confirm: 'Confirmar',
      delete: 'Eliminar',
      edit: 'Editar',
      back: 'Volver',
      next: 'Siguiente',
      done: 'Hecho',
      yes: 'Sí',
      no: 'No',
    },
    tabs: {
      home: 'Inicio',
      diet: 'Dieta',
      workout: 'Entreno',
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
    },
    progress: {
      title: 'Tu Progreso',
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
  },
};
