import math
from typing import Dict, Any, List

class GamificationEngine:
    """
    Gamification system managing XP, levels, learning streaks, badges, achievements, and cohort leaderboard.
    """

    LEVELS = [
        {"level": 1, "title": "Novice Learner", "xp_required": 0},
        {"level": 2, "title": "Curious Explorer", "xp_required": 100},
        {"level": 3, "title": "Concept Builder", "xp_required": 250},
        {"level": 4, "title": "Knowledge Seeker", "xp_required": 450},
        {"level": 5, "title": "Neural Apprentice", "xp_required": 700},
        {"level": 6, "title": "Gradient Climber", "xp_required": 1000},
        {"level": 7, "title": "Pattern Master", "xp_required": 1400},
        {"level": 8, "title": "Deep Architect", "xp_required": 1900},
        {"level": 9, "title": "Attention Pioneer", "xp_required": 2500},
        {"level": 10, "title": "AI Master", "xp_required": 3200}
    ]

    ALL_BADGES = [
        {
            "id": "b_first_upload",
            "name": "Knowledge Pioneer",
            "description": "Uploaded study materials to build personal AI library",
            "icon": "📚",
            "unlocked": True,
            "unlocked_at": "Today"
        },
        {
            "id": "b_quiz_master",
            "name": "Quiz Master",
            "description": "Completed multiple quizzes with >= 75% accuracy",
            "icon": "🎯",
            "unlocked": True,
            "unlocked_at": "Yesterday"
        },
        {
            "id": "b_streak_7",
            "name": "7-Day Streak",
            "description": "Engaged with the AI Learning Platform for 7 days in a row",
            "icon": "🔥",
            "unlocked": True,
            "unlocked_at": "Today"
        },
        {
            "id": "b_deep_thinker",
            "name": "Deep Thinker",
            "description": "Unlocked Advanced level explanations with code & math derivations",
            "icon": "🧠",
            "unlocked": True,
            "unlocked_at": "3 days ago"
        },
        {
            "id": "b_gap_slayer",
            "name": "Skill Gap Slayer",
            "description": "Turned a Weak topic into a Mastered skill through remedial training",
            "icon": "🛡️",
            "unlocked": False,
            "unlocked_at": None
        },
        {
            "id": "b_voice_tutor",
            "name": "Voice Pioneer",
            "description": "Used Voice AI to speak questions and listen to oral tutoring",
            "icon": "🎙️",
            "unlocked": False,
            "unlocked_at": None
        }
    ]

    def __init__(self):
        self.xp: int = 820
        self.streak_days: int = 7
        self.quizzes_completed: int = 24
        self.badges: List[Dict[str, Any]] = [dict(b) for b in self.ALL_BADGES]

    def get_level_info(self) -> Dict[str, Any]:
        current_lvl = self.LEVELS[0]
        next_lvl = self.LEVELS[1]

        for i, lvl in enumerate(self.LEVELS):
            if self.xp >= lvl["xp_required"]:
                current_lvl = lvl
                next_lvl = self.LEVELS[i + 1] if i + 1 < len(self.LEVELS) else None

        if next_lvl:
            xp_in_level = self.xp - current_lvl["xp_required"]
            xp_needed = next_lvl["xp_required"] - current_lvl["xp_required"]
            percent = int((xp_in_level / max(1, xp_needed)) * 100)
            target_xp = next_lvl["xp_required"]
        else:
            percent = 100
            target_xp = self.xp

        return {
            "current_level": current_lvl["level"],
            "title": current_lvl["title"],
            "current_xp": self.xp,
            "next_level_xp": target_xp,
            "level_progress_percent": min(100, percent)
        }

    def add_xp(self, amount: int, reason: str = "") -> Dict[str, Any]:
        self.xp += amount
        return {
            "xp_added": amount,
            "new_xp": self.xp,
            "reason": reason,
            "level_info": self.get_level_info()
        }

    def unlock_badge(self, badge_id: str) -> Optional[Dict[str, Any]]:
        for b in self.badges:
            if b["id"] == badge_id and not b["unlocked"]:
                b["unlocked"] = True
                b["unlocked_at"] = "Just now"
                self.add_xp(50, f"Unlocked Badge: {b['name']}")
                return b
        return None

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        return [
            {"rank": 1, "name": "Sarah Connor", "xp": 1450, "level": 7, "streak": 14, "avatar": "👩‍💻", "badge": "AI Architect"},
            {"rank": 2, "name": "Alex Chen", "xp": 1120, "level": 6, "streak": 9, "avatar": "🧑‍🔬", "badge": "Model Tuner"},
            {"rank": 3, "name": "You (Student)", "xp": self.xp, "level": self.get_level_info()["current_level"], "streak": self.streak_days, "avatar": "🎓", "badge": "Scholar", "is_user": True},
            {"rank": 4, "name": "Priya Sharma", "xp": 740, "level": 5, "streak": 6, "avatar": "👩‍🎓", "badge": "Fast Learner"},
            {"rank": 5, "name": "Marcus Aurelius", "xp": 610, "level": 4, "streak": 4, "avatar": "👨‍💼", "badge": "Explorer"}
        ]

    def get_gamification_overview(self) -> Dict[str, Any]:
        return {
            "level_info": self.get_level_info(),
            "streak_days": self.streak_days,
            "quizzes_completed": self.quizzes_completed,
            "badges": self.badges,
            "leaderboard": self.get_leaderboard()
        }

gamification_engine = GamificationEngine()
