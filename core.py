import requests
import json
import os
import random
import re
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Tuple

FILE_NAME = "vocab.json"
PROGRESS_FILE = "progress.json"
STATS_FILE = "stats.json"

# Spaced repetition intervals (days)
REVIEW_INTERVALS = {
    1: 1,    # Again: 1 day
    2: 3,    # Hard: 3 days
    3: 7,    # Good: 1 week
    4: 14    # Easy: 2 weeks
}

# ==================================================
# FILE MANAGEMENT
# ==================================================

def load_progress() -> Dict:
    """Load progress data with defaults."""
    if not os.path.exists(PROGRESS_FILE):
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_study_date": None,
            "achievements": [],
            "total_reviews": 0,
            "studied_today": 0,
            "xp": 0,
            "history": {}
        }
    with open(PROGRESS_FILE, "r") as f:
        data = json.load(f)
        # Ensure all required fields exist
        data.setdefault("achievements", [])
        data.setdefault("total_reviews", 0)
        data.setdefault("studied_today", 0)
        data.setdefault("xp", 0)
        data.setdefault("history", {})
        return data

def save_progress() -> None:
    """Save progress to file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=4)

def load_vocab() -> Dict:
    """Load vocabulary database."""
    if not os.path.exists(FILE_NAME):
        return {}
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def save_vocab() -> None:
    """Save vocabulary to file."""
    with open(FILE_NAME, "w") as f:
        json.dump(vocab, f, indent=4)

def load_stats() -> Dict:
    """Load statistics."""
    if not os.path.exists(STATS_FILE):
        return {
            "words_added": 0,
            "words_removed": 0,
            "quiz_attempts": 0,
            "quiz_correct": 0
        }
    with open(STATS_FILE, "r") as f:
        return json.load(f)

def save_stats() -> None:
    """Save statistics."""
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

# Initialize data
progress = load_progress()
vocab = load_vocab()
stats = load_stats()


# ==================================================
# VOCABULARY SCHEMA MANAGEMENT
# ==================================================

def upgrade_vocab_schema() -> None:
    """Migrate old vocab entries to new schema."""
    updated = False
    for word, data in vocab.items():
        # Ensure all fields exist
        defaults = {
            "sentence": "",
            "note": "",
            "box": 1,
            "times_reviewed": 0,
            "times_correct": 0,
            "ease": 2.5,
            "history": [],
            "last_reviewed": None,
            "next_review": datetime.now().strftime("%Y-%m-%d"),
            "interval": 1
        }
        for key, default in defaults.items():
            if key not in data:
                data[key] = default
                updated = True
    
    if updated:
        save_vocab()

upgrade_vocab_schema()


# ==================================================
# WORD MANAGEMENT
# ==================================================

def add_word_gui_logic(word: str, sentence: str, note: str) -> bool:
    """Add a word via GUI with validation."""
    word = word.strip()
    sentence = sentence.strip()
    note = note.strip()
    
    if not word or not sentence:
        return False
    
    if word.lower() in [w.lower() for w in vocab.keys()]:
        return False
    
    vocab[word] = {
        "sentence": sentence,
        "note": note,
        "box": 1,
        "times_reviewed": 0,
        "times_correct": 0,
        "ease": 2.5,
        "history": [],
        "last_reviewed": None,
        "next_review": datetime.now().strftime("%Y-%m-%d"),
        "interval": 1
    }
    save_vocab()
    stats["words_added"] = stats.get("words_added", 0) + 1
    save_stats()
    return True

def remove_word(word: str) -> bool:
    """Remove a word from vocabulary."""
    for w in vocab.keys():
        if w.lower() == word.lower():
            del vocab[w]
            break
        save_vocab()
        stats["words_removed"] = stats.get("words_removed", 0) + 1
        save_stats()
        return True
    return False

def edit_word(word: str, new_sentence: str, new_note: str) -> bool:
    """Edit an existing word."""
    if word in vocab:
        vocab[word]["sentence"] = new_sentence.strip()
        vocab[word]["note"] = new_note.strip()
        save_vocab()
        return True
    return False


# ==================================================
# SPACED REPETITION ALGORITHM
# ==================================================

def schedule_next_review(word: str, rating: int) -> None:
    """
    SM-2 Spaced Repetition Algorithm.
    
    Rating: 1=Again, 2=Hard, 3=Good, 4=Easy
    """
    if word not in vocab:
        return
    
    data = vocab[word]
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get current ease factor
    ease = data.get("ease", 2.5)
    interval = data.get("interval", 1)
    
    # SM-2 formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    # where q is quality (1-4)
    q = rating
    ease = max(1.3, ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    
    # Calculate next interval
    if q < 3:  # If failed or hard
        interval = 1
    else:
        if interval == 1:
            interval = 3
        else:
            interval = round(interval * ease)
    
    # Schedule next review
    next_date = datetime.now() + timedelta(days=interval)
    
    # Update word data
    data["ease"] = ease
    data["interval"] = interval
    data["next_review"] = next_date.strftime("%Y-%m-%d")
    data["box"] = min(5, max(1, data.get("box", 1) + (1 if q >= 3 else -1)))
    
    save_vocab()


# ==================================================
# STUDY SESSIONS
# ==================================================

def get_due_words() -> List[str]:
    """Get all words due for review today."""
    today = datetime.now().strftime("%Y-%m-%d")
    due = []
    for word, data in vocab.items():
        next_review = data.get("next_review", today)
        if next_review <= today:
            due.append(word)
    return due

def get_due_count() -> int:
    """Get number of words due today."""
    return len(get_due_words())

def suggested_daily_target() -> int:
    """Calculate suggested daily study target based on due words."""
    due = get_due_count()
    return max(5, min(20, due))

def build_study_plan(target: int) -> List[str]:
    """
    Build a prioritized study plan for the session.
    
    Prioritization factors:
    - Overdue words (higher priority)
    - Words with low accuracy (higher priority)
    - Recently failed words (higher priority)
    - New words (medium priority)
    """
    today = datetime.today().date()
    scored_words = []
    
    for word, data in vocab.items():
        # Parse next_review date
        next_review = data.get("next_review", today)
        if isinstance(next_review, str):
            next_review = datetime.strptime(next_review, "%Y-%m-%d").date()
        
        # Overdue factor: each day overdue adds weight
        overdue_days = max(0, (today - next_review).days)
        overdue_factor = 1 + overdue_days * 0.15
        
        # Difficulty factor: higher ease = lower priority
        ease = data.get("ease", 2.5)
        difficulty_factor = 3.5 / ease
        
        # Accuracy factor: lower accuracy = higher priority
        reviewed = data.get("times_reviewed", 0)
        correct = data.get("times_correct", 0)
        accuracy = correct / reviewed if reviewed > 0 else 0
        accuracy_factor = 1 + (1 - accuracy) * 1.5
        
        # New word boost
        new_word_factor = 1.8 if reviewed == 0 else 1
        
        # Recent performance: check last 5 reviews
        history = data.get("history", [])
        recent = history[-5:]
        recent_errors = sum(1 for h in recent if not h.get("correct", True))
        error_boost = 1 + recent_errors * 0.3
        
        priority = overdue_factor * difficulty_factor * accuracy_factor * new_word_factor * error_boost
        scored_words.append((priority, word))
    
    # Sort by priority and take top N
    scored_words.sort(reverse=True)
    plan = [w for _, w in scored_words[:target]]
    
    return plan


# ==================================================
# STATISTICS & ANALYTICS
# ==================================================

def get_word_accuracy(word: str) -> float:
    """Get accuracy percentage for a word."""
    if word not in vocab:
        return 0.0
    data = vocab[word]
    reviewed = data.get("times_reviewed", 0)
    if reviewed == 0:
        return 0.0
    correct = data.get("times_correct", 0)
    return (correct / reviewed) * 100

def get_overall_accuracy() -> float:
    """Get overall accuracy across all words."""
    total_reviewed = sum(d.get("times_reviewed", 0) for d in vocab.values())
    if total_reviewed == 0:
        return 0.0
    total_correct = sum(d.get("times_correct", 0) for d in vocab.values())
    return (total_correct / total_reviewed) * 100

def get_difficult_words(limit: int = 5) -> List[Tuple[str, float]]:
    """Get most difficult words by error rate."""
    difficulties = []
    for word, data in vocab.items():
        reviewed = data.get("times_reviewed", 0)
        if reviewed >= 3:  # Only consider if reviewed at least 3 times
            error_rate = (reviewed - data.get("times_correct", 0)) / reviewed
            difficulties.append((word, error_rate))
    
    difficulties.sort(key=lambda x: x[1], reverse=True)
    return difficulties[:limit]

def get_box_distribution() -> Dict[int, int]:
    """Get count of words in each memory box."""
    distribution = {i: 0 for i in range(1, 6)}
    for data in vocab.values():
        box = data.get("box", 1)
        distribution[box] = distribution.get(box, 0) + 1
    return distribution

def update_streak() -> None:
    """Update study streak and reset daily counters."""
    today = datetime.now().date()
    last_date = progress.get("last_study_date")
    
    if last_date:
        last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
        
        if today == last_date:
            return  # Already counted today
        elif today == last_date + timedelta(days=1):
            progress["current_streak"] += 1
        else:
            progress["current_streak"] = 1
    else:
        progress["current_streak"] = 1
    
    if progress["current_streak"] > progress.get("longest_streak", 0):
        progress["longest_streak"] = progress["current_streak"]
    
    # Reset daily counter for new day
    progress["studied_today"] = 0
    progress["last_study_date"] = today.strftime("%Y-%m-%d")
    save_progress()

def check_achievements() -> List[str]:
    """Check for unlocked achievements and return new ones."""
    new_achievements = []
    
    xp = progress.get("xp", 0)
    streak = progress.get("current_streak", 0)
    reviewed = progress.get("total_reviews", 0)
    total_words = len(vocab)
    
    achievements_to_check = [
        ("XP_100", xp >= 100, "Earned 100 XP"),
        ("XP_500", xp >= 500, "Earned 500 XP"),
        ("XP_1000", xp >= 1000, "Earned 1000 XP"),
        ("Streak_3", streak >= 3, "3-day study streak"),
        ("Streak_7", streak >= 7, "7-day study streak"),
        ("Streak_30", streak >= 30, "30-day study streak"),
        ("Reviews_100", reviewed >= 100, "100 reviews completed"),
        ("Reviews_500", reviewed >= 500, "500 reviews completed"),
        ("Words_50", total_words >= 50, "Added 50 words"),
    ]
    
    for achievement_id, condition, message in achievements_to_check:
        if condition and achievement_id not in progress.get("achievements", []):
            progress["achievements"].append(achievement_id)
            new_achievements.append(message)
    
    if new_achievements:
        save_progress()
    
    return new_achievements


# ==================================================
# QUIZ & PRACTICE
# ==================================================

def select_random_word() -> Optional[str]:
    """Select a random word from vocabulary."""
    if not vocab:
        return None
    return random.choice(list(vocab.keys()))

def get_random_quiz_word() -> Optional[Tuple[str, str]]:
    """Get a random word and return (word, blank_sentence)."""
    word = select_random_word()
    if not word:
        return None
    
    sentence = vocab[word]["sentence"]
    blank = re.sub(word, "_____", sentence, flags=re.IGNORECASE)
    return word, blank

def quiz_mode_single() -> Optional[Tuple[str, bool]]:
    """
    Run a single quiz question.
    Returns (word, is_correct) or None.
    """
    word_data = get_random_quiz_word()
    if not word_data:
        return None
    
    word, blank = word_data
    stats["quiz_attempts"] = stats.get("quiz_attempts", 0) + 1
    
    # This would be called from GUI with user input
    # For now, return the word data
    return word, blank
