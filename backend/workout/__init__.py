"""
Workout Module - Modular Workout Generation System
===================================================
Organized structure for workout generation
"""

from .exercises import (
    EXERCISES,
    UPPER_BODY_EXERCISES,
    DAYS,
    SPLITS,
    SMALL_MUSCLES,
    COMPOUND_EXERCISES,
    get_split_for_frequency,
)

from .config import (
    get_config_for_level,
    get_exercises_per_duration,
    get_sets_per_duration,
    get_max_days_for_level,
    parse_rest_seconds,
)

from .translations import (
    get_exercise_name,
    get_muscle_group_name,
    get_workout_day_name,
    get_focus_name,
    translate_exercise,
    translate_workout_day,
    translate_workout_plan,
)

__all__ = [
    # Exercises
    'EXERCISES',
    'UPPER_BODY_EXERCISES',
    'DAYS',
    'SPLITS',
    'SMALL_MUSCLES',
    'COMPOUND_EXERCISES',
    'get_split_for_frequency',
    
    # Config
    'get_config_for_level',
    'get_exercises_per_duration',
    'get_sets_per_duration',
    'get_max_days_for_level',
    'parse_rest_seconds',
    
    # Translations
    'get_exercise_name',
    'get_muscle_group_name',
    'get_workout_day_name',
    'get_focus_name',
    'translate_exercise',
    'translate_workout_day',
    'translate_workout_plan',
]
