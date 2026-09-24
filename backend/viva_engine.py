import uuid
import re
from typing import Dict, Any, List, Optional
from backend.competency_engine import competency_engine
from backend.gamification import gamification_engine

class SocraticVivaEngine:
    """
    Socratic Oral Viva & Technical Interview Simulation Engine.
    Emulates an academic university examiner testing conceptual understanding,
    detecting misconceptions, asking follow-up challenges, and generating oral scorecards.
    """

    VIVA_TOPICS = {
        "Sequential Modeling & RNNs": [
            {
                "question": "Welcome to your viva examination. Let's start with sequential models. In your own words, why do vanilla Recurrent Neural Networks struggle with long-range dependencies during Backpropagation Through Time (BPTT)?",
                "key_concepts": ["vanishing gradient", "eigenvalues", "matrix multiplication", "decay", "sequence length"],
                "followup": "Good observation regarding the gradient decay. Now, how does the LSTM architecture mathematically overcome this vanishing gradient problem compared to the multiplicative updates in standard RNNs?",
                "followup_concepts": ["cell state", "additive", "forget gate", "conveyor", "constant error carousel"]
            },
            {
                "question": "Now, let's examine the Long Short-Term Memory cell. What is the specific mathematical function of the Forget Gate, and why is a Sigmoid activation function chosen for it instead of ReLU or Tanh?",
                "key_concepts": ["sigmoid", "0 and 1", "scaling", "retain", "discard", "percentage"],
                "followup": "Exactly. What would happen if we used ReLU for the forget gate instead of Sigmoid? How would that impact the stability of the cell state?",
                "followup_concepts": ["unbounded", "explode", "overflow", "scale greater than 1"]
            }
        ],
        "Convolutional Neural Networks (CNN)": [
            {
                "question": "Welcome to your CNN viva examination. A colleague suggests flattening a 256x256 RGB image and feeding it directly into a standard dense feedforward network. Why is this a flawed engineering approach for computer vision?",
                "key_concepts": ["parameter explosion", "overfitting", "spatial topology", "weights", "dimensions"],
                "followup": "Correct. How does the concept of 'parameter sharing' (or shared weights) in convolutional kernels solve that parameter bottleneck?",
                "followup_concepts": ["shared kernel", "sliding filter", "receptive field", "translation invariance"]
            },
            {
                "question": "Let's discuss deep CNNs like ResNet. As networks exceed 20 to 30 layers, a degradation problem occurs where training error increases. How do residual skip connections solve this mathematically?",
                "key_concepts": ["identity shortcut", "f(x) + x", "derivative", "plus one", "gradient flow"],
                "followup": "Well explained. When we take the partial derivative d(F(x)+x)/dx, what does the +1 identity term guarantee for the backward pass?",
                "followup_concepts": ["unimpeded flow", "never vanishes", "direct pathway", "early layers"]
            }
        ],
        "Attention & Transformers": [
            {
                "question": "Welcome to your Transformers viva. The seminal paper is titled 'Attention Is All You Need'. What major sequential limitation of RNNs and LSTMs did Transformers eliminate?",
                "key_concepts": ["sequential bottleneck", "parallelization", "gpu", "step by step", "o(1) distance"],
                "followup": "Precisely. Now look at Scaled Dot-Product Attention: Attention(Q, K, V) = softmax((Q*K^T) / sqrt(d_k)) * V. Why is the division by sqrt(d_k) strictly necessary?",
                "followup_concepts": ["large dot products", "softmax saturation", "vanishing gradients", "variance scaling"]
            },
            {
                "question": "In self-attention, the operation is permutation-invariant—if we shuffle the input tokens, the output vectors simply shuffle without changing their values. How do Transformers preserve the sequential order of words?",
                "key_concepts": ["positional encoding", "sinusoidal", "order", "vectors", "add"],
                "followup": "Excellent. Why did the original Transformer use sinusoidal functions with varying frequencies across dimensions rather than just assigning token indices 1, 2, 3...?",
                "followup_concepts": ["relative distance", "extrapolate", "unbounded indices", "geometric progression"]
            }
        ],
        "Backpropagation & Optimization": [
            {
                "question": "Welcome to your optimization viva. Explain how the chain rule of calculus is applied in reverse during backpropagation to update hidden layer weights.",
                "key_concepts": ["chain rule", "partial derivative", "dl/da", "local gradient", "backward traversal"],
                "followup": "Good. Modern networks commonly use the Adam optimizer rather than simple SGD. What two statistical moments does Adam maintain to calculate adaptive step sizes?",
                "followup_concepts": ["first moment", "second moment", "mean", "variance", "momentum", "rmsprop"]
            }
        ]
    }

    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def start_session(self, topic: str, student_name: str = "Scholar") -> Dict[str, Any]:
        session_id = str(uuid.uuid4())[:8]

        # Match closest topic
        matched_topic = None
        for t in self.VIVA_TOPICS.keys():
            if t.lower() in topic.lower() or topic.lower() in t.lower():
                matched_topic = t
                break
        if not matched_topic:
            matched_topic = "Sequential Modeling & RNNs"

        questions = self.VIVA_TOPICS[matched_topic]
        first_q = questions[0]

        session = {
            "session_id": session_id,
            "topic": matched_topic,
            "student_name": student_name,
            "current_round": 1,
            "max_rounds": 3,
            "history": [],
            "scores": [],
            "current_question": first_q["question"],
            "current_key_concepts": first_q["key_concepts"],
            "pending_followup": first_q["followup"],
            "pending_followup_concepts": first_q["followup_concepts"],
            "is_complete": False
        }

        self.active_sessions[session_id] = session

        return {
            "session_id": session_id,
            "topic": matched_topic,
            "examiner_name": "Prof. Turing (AI Examiner)",
            "round": 1,
            "total_rounds": 3,
            "question": first_q["question"],
            "audio_intro": f"Welcome {student_name}. I will be conducting your oral viva on {matched_topic}. {first_q['question']}"
        }

    def process_response(self, session_id: str, student_transcript: str) -> Dict[str, Any]:
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Invalid or expired viva session"}

        if session["is_complete"]:
            return {"error": "This viva examination has already been completed"}

        transcript_lower = student_transcript.lower().strip()
        key_concepts = session["current_key_concepts"]

        # Evaluate conceptual coverage
        matched = [k for k in key_concepts if k.lower() in transcript_lower]
        coverage_ratio = len(matched) / max(1, len(key_concepts))
        
        # Scoring with length & articulation bonus
        base_score = int(coverage_ratio * 80)
        word_count = len(transcript_lower.split())
        if word_count >= 15:
            base_score = min(100, base_score + 15)
        elif word_count < 6:
            base_score = min(30, base_score)

        session["scores"].append(base_score)

        # Examiner Feedback & Socratic Follow-up
        feedback = ""
        if base_score >= 75:
            feedback = f"Strong articulation! You accurately highlighted essential mechanisms: {', '.join(matched)}."
        elif base_score >= 50:
            feedback = f"Fair answer. You touched upon {len(matched)} key points, but missed technical aspects such as: {', '.join([k for k in key_concepts if k not in matched][:2])}."
        else:
            feedback = f"Incomplete explanation. In a formal viva, you must address: {', '.join(key_concepts[:3])}."

        session["history"].append({
            "round": session["current_round"],
            "question": session["current_question"],
            "student_answer": student_transcript,
            "score": base_score,
            "feedback": feedback
        })

        session["current_round"] += 1

        # Check if more rounds remaining
        if session["current_round"] <= session["max_rounds"]:
            if session["pending_followup"]:
                next_q = session["pending_followup"]
                session["current_question"] = next_q
                session["current_key_concepts"] = session["pending_followup_concepts"]
                session["pending_followup"] = None
            else:
                # Next primary question
                questions = self.VIVA_TOPICS[session["topic"]]
                next_item = questions[1] if len(questions) > 1 else questions[0]
                next_q = next_item["question"]
                session["current_question"] = next_q
                session["current_key_concepts"] = next_item["key_concepts"]
                session["pending_followup"] = next_item.get("followup")
                session["pending_followup_concepts"] = next_item.get("followup_concepts", [])

            return {
                "session_id": session_id,
                "is_complete": False,
                "round": session["current_round"] - 1,
                "score_this_round": base_score,
                "feedback": feedback,
                "next_question": next_q,
                "next_round": session["current_round"]
            }
        else:
            # Conclude Viva Examination
            session["is_complete"] = True
            avg_score = int(sum(session["scores"]) / max(1, len(session["scores"])))

            # Update Competency Engine
            competency_engine.update_score_from_assessment(
                topic=session["topic"],
                is_correct=(avg_score >= 65),
                difficulty="hard"
            )

            # Award Gamification XP
            xp_award = avg_score + 50
            gamification_engine.add_xp(xp_award, f"Completed Oral Viva: {session['topic']}")
            gamification_engine.unlock_badge("b_deep_thinker")

            verdict = "Distinction" if avg_score >= 80 else ("Pass with Merit" if avg_score >= 65 else "Conditional Pass / Needs Revision")

            return {
                "session_id": session_id,
                "is_complete": True,
                "final_score": avg_score,
                "verdict": verdict,
                "xp_awarded": xp_award,
                "topic": session["topic"],
                "total_rounds": len(session["scores"]),
                "feedback_summary": (
                    f"Viva Examination Concluded. Final Oral Grade: {avg_score}% ({verdict}). "
                    f"Your conceptual mastery score for '{session['topic']}' has been updated in the Competency Engine."
                ),
                "history": session["history"]
            }

socratic_viva_engine = SocraticVivaEngine()
