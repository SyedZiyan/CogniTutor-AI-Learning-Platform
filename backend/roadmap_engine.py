from typing import List, Dict, Any
from backend.competency_engine import competency_engine

class RoadmapEngine:
    """
    Personalized Learning Path Engine.
    Dynamically adjusts roadmap modules and prerequisite milestones based on the student's competency profile.
    """

    def __init__(self):
        self.completed_milestones = set(["m_ann_intro", "m_cnn_basics"])

    def get_roadmap(self) -> Dict[str, Any]:
        comp = competency_engine.get_competency_analysis()
        weak_topics = [w["topic"] for w in comp["weak"]]

        # Check if RNN/Sequential modeling is weak
        rnn_weak = any("rnn" in t.lower() or "sequential" in t.lower() for t in weak_topics)
        trans_weak = any("transformer" in t.lower() or "attention" in t.lower() for t in weak_topics)

        weeks = []

        # Week 1: Foundational Remediation (Adapted dynamically)
        week1_items = [
            {
                "id": "m_rnn_fund",
                "title": "RNN Fundamentals & Sequential BPTT",
                "type": "Concept Note",
                "estimated_time": "25 mins",
                "completed": "m_rnn_fund" in self.completed_milestones,
                "remedial_flag": rnn_weak,
                "source_ref": "Recurrent_Neural_Networks_and_LSTMs.docx (Section 1)"
            },
            {
                "id": "m_rnn_arch",
                "title": "Vanishing Gradient Problem & Eigenvalue Analysis",
                "type": "Interactive Theory",
                "estimated_time": "20 mins",
                "completed": "m_rnn_arch" in self.completed_milestones,
                "remedial_flag": rnn_weak,
                "source_ref": "Recurrent_Neural_Networks_and_LSTMs.docx (Section 2)"
            },
            {
                "id": "m_rnn_quiz",
                "title": "RNN Prerequisite Recovery Practice Drill",
                "type": "Targeted Quiz",
                "estimated_time": "15 mins",
                "completed": "m_rnn_quiz" in self.completed_milestones,
                "remedial_flag": rnn_weak,
                "source_ref": "AI Quiz Hub (Adaptive)"
            }
        ]

        weeks.append({
            "week_number": 1,
            "title": "Week 1: Recurrent Foundations & Vanishing Gradient Remediation",
            "status": "Active" if not all(i["completed"] for i in week1_items) else "Completed",
            "progress_percent": int(sum(1 for i in week1_items if i["completed"]) / len(week1_items) * 100),
            "description": "Targeted recovery of sequential backpropagation concepts to eliminate identified skill gaps.",
            "items": week1_items
        })

        # Week 2: Advanced Memory Cells
        week2_unlocked = all(i["completed"] for i in week1_items) or not rnn_weak
        week2_items = [
            {
                "id": "m_lstm_gates",
                "title": "Long Short-Term Memory (LSTM) 3-Gate Architecture",
                "type": "Deep Dive",
                "estimated_time": "30 mins",
                "completed": "m_lstm_gates" in self.completed_milestones,
                "remedial_flag": False,
                "source_ref": "Recurrent_Neural_Networks_and_LSTMs.docx (Section 3)"
            },
            {
                "id": "m_gru_study",
                "title": "Gated Recurrent Units (GRU) Comparison",
                "type": "Comparative Analysis",
                "estimated_time": "20 mins",
                "completed": "m_gru_study" in self.completed_milestones,
                "remedial_flag": False,
                "source_ref": "Recurrent_Neural_Networks_and_LSTMs.docx (Section 4)"
            },
            {
                "id": "m_coding_ex",
                "title": "PyTorch LSTM Sequence Classification Coding Exercise",
                "type": "Hands-on Code",
                "estimated_time": "40 mins",
                "completed": "m_coding_ex" in self.completed_milestones,
                "remedial_flag": False,
                "source_ref": "3-Level Doubt Solver (Advanced Level)"
            }
        ]

        weeks.append({
            "week_number": 2,
            "title": "Week 2: LSTM Gated Memory & Sequential Coding",
            "status": "Active" if week2_unlocked and not all(i["completed"] for i in week2_items) else ("Completed" if all(i["completed"] for i in week2_items) else "Locked"),
            "progress_percent": int(sum(1 for i in week2_items if i["completed"]) / len(week2_items) * 100) if week2_unlocked else 0,
            "description": "Master constant error carousels and implement bidirectional recurrent networks.",
            "items": week2_items
        })

        # Week 3: Modern Attention & Transformers
        week3_unlocked = week2_unlocked and (all(i["completed"] for i in week2_items) or not rnn_weak)
        week3_items = [
            {
                "id": "m_trans_intro",
                "title": "Transformers & Limitations of Recurrent Bottlenecks",
                "type": "Architecture Slide",
                "estimated_time": "25 mins",
                "completed": "m_trans_intro" in self.completed_milestones,
                "remedial_flag": trans_weak,
                "source_ref": "Transformers_and_Attention_Mechanisms.pptx (Slide 2)"
            },
            {
                "id": "m_atten_math",
                "title": "Scaled Dot-Product & Multi-Head Self-Attention",
                "type": "Mathematical Formulation",
                "estimated_time": "35 mins",
                "completed": "m_atten_math" in self.completed_milestones,
                "remedial_flag": trans_weak,
                "source_ref": "Transformers_and_Attention_Mechanisms.pptx (Slide 3-4)"
            },
            {
                "id": "m_final_assess",
                "title": "Comprehensive Deep Learning Final Capstone Assessment",
                "type": "Final Exam",
                "estimated_time": "50 mins",
                "completed": "m_final_assess" in self.completed_milestones,
                "remedial_flag": False,
                "source_ref": "Comprehensive 18-Question Master Assessment"
            }
        ]

        weeks.append({
            "week_number": 3,
            "title": "Week 3: Attention Mechanisms, Transformers & Capstone",
            "status": "Active" if week3_unlocked and not all(i["completed"] for i in week3_items) else ("Completed" if all(i["completed"] for i in week3_items) else "Locked"),
            "progress_percent": int(sum(1 for i in week3_items if i["completed"]) / len(week3_items) * 100) if week3_unlocked else 0,
            "description": "Transition to modern foundation models, self-attention algebra, and capstone certification.",
            "items": week3_items
        })

        total_items = sum(len(w["items"]) for w in weeks)
        total_completed = sum(sum(1 for i in w["items"] if i["completed"]) for w in weeks)
        overall_progress = int((total_completed / max(1, total_items)) * 100)

        return {
            "roadmap_title": "Adaptive Personalized Deep Learning Roadmap",
            "overall_progress_percent": overall_progress,
            "total_milestones": total_items,
            "completed_milestones": total_completed,
            "active_week": 1 if not all(i["completed"] for i in week1_items) else (2 if not all(i["completed"] for i in week2_items) else 3),
            "weeks": weeks
        }

    def toggle_milestone(self, milestone_id: str) -> Dict[str, Any]:
        if milestone_id in self.completed_milestones:
            self.completed_milestones.remove(milestone_id)
            state = False
        else:
            self.completed_milestones.add(milestone_id)
            state = True
        return {"milestone_id": milestone_id, "completed": state, "roadmap": self.get_roadmap()}

roadmap_engine = RoadmapEngine()
