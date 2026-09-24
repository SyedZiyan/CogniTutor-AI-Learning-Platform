import json
from typing import Dict, Any, List

class CompetencyEngine:
    """
    AI Competency and Skill-Gap Detection Engine.
    Tracks topic-level mastery scores, Bayesian updates, and generates diagnostic learning strategies.
    """

    DEFAULT_TOPIC_MASTERY = {
        "Neural Networks": 85,
        "Convolutional Neural Networks (CNN)": 78,
        "Backpropagation & Optimization": 82,
        "Overfitting & Regularization": 68,
        "Recurrent Neural Networks (RNN)": 42,
        "Long Short-Term Memory (LSTM)": 48,
        "Attention & Transformers": 35
    }

    TOPIC_DESCRIPTIONS = {
        "Neural Networks": "Perceptron architecture, multi-layer perceptrons, and activation function choices.",
        "Convolutional Neural Networks (CNN)": "Spatial convolutions, kernels, receptive fields, and downsampling pooling layers.",
        "Backpropagation & Optimization": "Calculus chain rule, gradient updates, Adam/SGD optimizers, and loss convergence.",
        "Overfitting & Regularization": "Generalization gap, Dropout, L1/L2 penalties, and early stopping.",
        "Recurrent Neural Networks (RNN)": "Sequential state persistence, Backpropagation Through Time (BPTT), and vanishing gradients.",
        "Long Short-Term Memory (LSTM)": "Constant error carousel, forget gate, input gate, and output gate mechanics.",
        "Attention & Transformers": "Scaled dot-product attention, multi-head projection, parallelization, and positional encodings."
    }

    def __init__(self):
        self.topic_scores: Dict[str, float] = dict(self.DEFAULT_TOPIC_MASTERY)
        self.assessment_history: List[Dict[str, Any]] = []

    def update_score_from_assessment(self, topic: str, is_correct: bool, difficulty: str = "medium"):
        """
        Bayesian / Weighted exponential moving average update on topic mastery.
        """
        # Map closest topic if exact match not found
        target_topic = self._match_topic(topic)
        current = self.topic_scores.get(target_topic, 50.0)

        # Weighting based on difficulty
        diff_weights = {
            "easy": {"win": 4.0, "loss": 10.0},
            "medium": {"win": 7.0, "loss": 6.5},
            "hard": {"win": 11.0, "loss": 4.0}
        }
        weights = diff_weights.get(difficulty.lower(), diff_weights["medium"])

        if is_correct:
            # Boost score towards 100
            gain = weights["win"] * (1.0 - (current / 110.0))
            new_score = min(100.0, current + gain)
        else:
            # Decrease score towards 0
            loss = weights["loss"] * (current / 100.0)
            new_score = max(5.0, current - loss)

        self.topic_scores[target_topic] = round(new_score, 1)

    def _match_topic(self, topic_query: str) -> str:
        query_lower = topic_query.lower()
        for k in self.topic_scores.keys():
            if query_lower in k.lower() or k.lower() in query_lower:
                return k
        # Keywords
        if "cnn" in query_lower or "conv" in query_lower:
            return "Convolutional Neural Networks (CNN)"
        if "lstm" in query_lower:
            return "Long Short-Term Memory (LSTM)"
        if "rnn" in query_lower:
            return "Recurrent Neural Networks (RNN)"
        if "transformer" in query_lower or "attention" in query_lower:
            return "Attention & Transformers"
        if "backprop" in query_lower or "loss" in query_lower or "opt" in query_lower:
            return "Backpropagation & Optimization"
        if "overfit" in query_lower or "regular" in query_lower:
            return "Overfitting & Regularization"
        return "Neural Networks"

    def get_competency_analysis(self) -> Dict[str, Any]:
        """
        Analyzes performance across topics, classifying into Strong, Average, Weak with tailored pedagogical strategies.
        """
        strong = []
        average = []
        weak = []

        for topic, score in self.topic_scores.items():
            item = {
                "topic": topic,
                "score": score,
                "description": self.TOPIC_DESCRIPTIONS.get(topic, ""),
                "status": "Strong" if score >= 75 else ("Average" if score >= 50 else "Weak"),
                "strategy": "Maintain" if score >= 75 else ("Practice" if score >= 50 else "Learn & Remediate"),
                "badge_color": "emerald" if score >= 75 else ("amber" if score >= 50 else "rose")
            }
            if score >= 75:
                strong.append(item)
            elif score >= 50:
                average.append(item)
            else:
                weak.append(item)

        # Sort each list
        strong.sort(key=lambda x: x["score"], reverse=True)
        average.sort(key=lambda x: x["score"], reverse=True)
        weak.sort(key=lambda x: x["score"])

        overall_score = round(sum(self.topic_scores.values()) / max(1, len(self.topic_scores)), 1)
        strongest = strong[0]["topic"] if strong else "None"
        weakest = weak[0]["topic"] if weak else "None"

        # Actionable Recommendations
        recommendations = []
        if weak:
            for w in weak:
                recommendations.append({
                    "type": "remedial",
                    "priority": "HIGH",
                    "title": f"Priority: Master {w['topic']}",
                    "action": f"Take 3-Level Doubt Solver on {w['topic']} and complete remedial practice drill.",
                    "topic": w["topic"],
                    "current_score": w["score"]
                })
        if average:
            for a in average:
                recommendations.append({
                    "type": "practice",
                    "priority": "MEDIUM",
                    "title": f"Reinforce: {a['topic']}",
                    "action": f"Complete a 5-question targeted MCQ quiz to achieve 75%+ mastery.",
                    "topic": a["topic"],
                    "current_score": a["score"]
                })
        if strong:
            recommendations.append({
                "type": "challenge",
                "priority": "LOW",
                "title": f"Challenge: Advanced {strong[0]['topic']} Capstone",
                "action": "Attempt timed hard-difficulty assessment to maintain streak.",
                "topic": strong[0]["topic"],
                "current_score": strong[0]["score"]
            })

        return {
            "overall_mastery": overall_score,
            "strongest_topic": strongest,
            "weakest_topic": weakest,
            "strong": strong,
            "average": average,
            "weak": weak,
            "all_topics": list(self.topic_scores.keys()),
            "all_scores": list(self.topic_scores.values()),
            "recommendations": recommendations,
            "diagnostic_summary": (
                f"You have demonstrated high proficiency in {strongest} ({int(self.topic_scores.get(strongest, 0))}%), "
                f"but exhibit critical concept gaps in {weakest} ({int(self.topic_scores.get(weakest, 0))}%). "
                f"Your customized learning roadmap has been adapted to prioritize sequential remediation before unlocking advanced architectures."
            )
        }

competency_engine = CompetencyEngine()
