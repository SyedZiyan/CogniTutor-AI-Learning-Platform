import uuid
import re
from typing import Dict, Any, List, Optional
from backend.competency_engine import competency_engine
from backend.gamification import gamification_engine

class SocraticVivaEngine:
    """
    Socratic Oral Viva & Technical Interview Simulation Engine.
    Emulates academic university examiners testing conceptual understanding,
    detecting misconceptions, asking follow-up challenges, and generating oral scorecards.
    Supports multiple courses, subjects, and examiner personas.
    """

    COURSE_VIVA_TOPICS = {
        "deep_learning": {
            "examiner_name": "Prof. Alan Turing (AI Examiner)",
            "topics": {
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
        },
        "dsa": {
            "examiner_name": "Prof. Donald Knuth (Algorithms Board)",
            "topics": {
                "Dynamic Programming & Memoization": [
                    {
                        "question": "Welcome to your Algorithms oral exam. Explain the two prerequisite conditions—optimal substructure and overlapping subproblems—necessary for Dynamic Programming.",
                        "key_concepts": ["optimal substructure", "overlapping subproblems", "memoization", "recursion", "table"],
                        "followup": "Compare the space complexity trade-offs between top-down recursive memoization and bottom-up iterative tabulation.",
                        "followup_concepts": ["call stack", "recursion depth", "matrix", "iterative", "space optimization"]
                    }
                ],
                "Graph Traversals & Dijkstra": [
                    {
                        "question": "When finding the shortest path on a weighted graph, why does Breadth-First Search (BFS) fail, necessitating Dijkstra's Algorithm?",
                        "key_concepts": ["edge weights", "hop count", "cost", "greedy", "priority queue"],
                        "followup": "What happens if a graph contains negative edge weights? Why does Dijkstra produce incorrect shortest paths in that case?",
                        "followup_concepts": ["negative weights", "greedy assumption", "visited", "bellman ford", "cycle"]
                    }
                ],
                "Hash Tables & Collision Strategies": [
                    {
                        "question": "In hash tables, explain the mechanical difference between collision resolution via Separate Chaining versus Open Addressing.",
                        "key_concepts": ["linked list", "probing", "bucket", "load factor", "clustering"],
                        "followup": "Explain what primary clustering is in linear probing and how double hashing remedies it.",
                        "followup_concepts": ["consecutive", "stride", "second hash", "independent", "spread"]
                    }
                ],
                "Balanced Trees & AVL Rotations": [
                    {
                        "question": "Why does an unconstrained Binary Search Tree (BST) degenerate into O(n) search time, and how do AVL trees guarantee O(log n) height?",
                        "key_concepts": ["sorted insertion", "linked list", "balance factor", "height", "log n"],
                        "followup": "Describe the difference between an AVL Single Rotation (LL/RR) and a Double Rotation (LR/RL).",
                        "followup_concepts": ["zigzag", "inner child", "two rotations", "balance restored"]
                    }
                ]
            }
        },
        "operating_systems": {
            "examiner_name": "Prof. Andrew Tanenbaum (Systems Board)",
            "topics": {
                "Deadlocks & Banker's Algorithm": [
                    {
                        "question": "Welcome to your Systems Viva. Enumerate the four Coffman conditions, and explain which condition Banker's Algorithm manipulates to ensure avoidance.",
                        "key_concepts": ["mutual exclusion", "hold and wait", "no preemption", "circular wait", "safe state"],
                        "followup": "What is the computational complexity of the Banker's safety check algorithm in terms of processes N and resource types M?",
                        "followup_concepts": ["o(m * n^2)", "matrix", "available", "allocation", "worst case"]
                    }
                ],
                "Virtual Memory & Page Faults": [
                    {
                        "question": "Walk me through the precise step-by-step hardware and kernel sequence when a CPU encounters a Page Fault.",
                        "key_concepts": ["invalid bit", "trap", "interrupt", "swap disk", "frame allocation", "resume"],
                        "followup": "Explain Belady's Anomaly. Why does adding more physical page frames sometimes increase total page faults under FIFO?",
                        "followup_concepts": ["fifo", "stack algorithm", "working set", "eviction", "counter-intuitive"]
                    }
                ],
                "CPU Scheduling & Context Switching": [
                    {
                        "question": "In preemptive CPU scheduling, how does the time quantum size in Round Robin dictate the balance between response time and CPU efficiency?",
                        "key_concepts": ["time quantum", "fcfs", "context switch", "overhead", "turnaround"],
                        "followup": "What hardware and software state must be saved and restored inside the Process Control Block (PCB) during a context switch?",
                        "followup_concepts": ["program counter", "registers", "stack pointer", "tlb flush", "memory map"]
                    }
                ],
                "Process Synchronization & Mutexes": [
                    {
                        "question": "State the three requirements for solving the Critical-Section problem: Mutual Exclusion, Progress, and Bounded Waiting.",
                        "key_concepts": ["mutual exclusion", "progress", "bounded waiting", "starvation", "deadlock"],
                        "followup": "Why is disabling hardware interrupts insufficient as a general synchronization primitive in modern symmetric multiprocessing (SMP) systems?",
                        "followup_concepts": ["multicore", "smp", "other cpus", "bus lock", "atomic instruction"]
                    }
                ]
            }
        },
        "linear_algebra": {
            "examiner_name": "Prof. Gilbert Strang (Mathematics Board)",
            "topics": {
                "Singular Value Decomposition (SVD)": [
                    {
                        "question": "Welcome to your Linear Algebra viva. Explain the geometric intuition behind SVD: factoring any real matrix A into U * Sigma * V^T.",
                        "key_concepts": ["orthogonal", "rotation", "scaling", "singular values", "hypersphere"],
                        "followup": "Explain the Eckart-Young-Mirsky theorem and how truncating SVD provides optimal low-rank matrix approximations for data compression.",
                        "followup_concepts": ["frobenius norm", "rank k", "top singular values", "pca", "noise reduction"]
                    }
                ],
                "Eigenvalues & Diagonalization": [
                    {
                        "question": "Why does the equation A * v = lambda * v imply det(A - lambda * I) = 0? What must be true about the nullspace of (A - lambda * I)?",
                        "key_concepts": ["non-trivial", "nullspace", "non-zero vector", "singular", "determinant zero"],
                        "followup": "Under what condition is an n x n matrix guaranteed to be diagonalizable into S * Lambda * S^-1?",
                        "followup_concepts": ["n linearly independent eigenvectors", "geometric multiplicity", "basis"]
                    }
                ],
                "Four Fundamental Subspaces": [
                    {
                        "question": "State the Rank-Nullity Theorem and explain why the Column Space C(A) is orthogonal to the Left Nullspace N(A^T) in R^m.",
                        "key_concepts": ["rank nullity", "dimension n", "orthogonal complement", "dot product", "zero"],
                        "followup": "If an m x n matrix has rank r, what are the dimensions of its row space and nullspace?",
                        "followup_concepts": ["dim row space r", "dim nullspace n-r", "r + (n-r) = n"]
                    }
                ],
                "Orthogonal Projections & Least Squares": [
                    {
                        "question": "When solving an inconsistent linear system A * x = b, derive the normal equations A^T * A * x = A^T * b using the orthogonality of the error vector.",
                        "key_concepts": ["error vector", "b - ax", "orthogonal to column space", "a^t (b - ax) = 0", "projection"],
                        "followup": "Why is the projection matrix P = A * (A^T * A)^-1 * A^T guaranteed to be idempotent (P^2 = P)?",
                        "followup_concepts": ["project twice", "already in subspace", "p^2 = p", "symmetric"]
                    }
                ]
            }
        }
    }

    # Backward compatibility defaults
    VIVA_TOPICS = COURSE_VIVA_TOPICS["deep_learning"]["topics"]

    def __init__(self):
        self.active_course_id = "deep_learning"
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def switch_course(self, course_id: str):
        self.active_course_id = course_id
        if course_id in self.COURSE_VIVA_TOPICS:
            SocraticVivaEngine.VIVA_TOPICS = self.COURSE_VIVA_TOPICS[course_id]["topics"]

    def get_current_examiner_name(self) -> str:
        course_data = self.COURSE_VIVA_TOPICS.get(self.active_course_id, self.COURSE_VIVA_TOPICS["deep_learning"])
        return course_data.get("examiner_name", "Academic Examiner")

    def get_current_topics_list(self) -> List[str]:
        course_data = self.COURSE_VIVA_TOPICS.get(self.active_course_id, self.COURSE_VIVA_TOPICS["deep_learning"])
        return list(course_data["topics"].keys())

    def start_session(self, topic: str, student_name: str = "Scholar") -> Dict[str, Any]:
        session_id = str(uuid.uuid4())[:8]

        course_data = self.COURSE_VIVA_TOPICS.get(self.active_course_id, self.COURSE_VIVA_TOPICS["deep_learning"])
        topics_dict = course_data["topics"]
        examiner_name = course_data["examiner_name"]

        # Match closest topic
        matched_topic = None
        for t in topics_dict.keys():
            if t.lower() in topic.lower() or topic.lower() in t.lower():
                matched_topic = t
                break
        if not matched_topic:
            matched_topic = list(topics_dict.keys())[0]

        questions = topics_dict[matched_topic]
        first_q = questions[0]

        session = {
            "session_id": session_id,
            "topic": matched_topic,
            "student_name": student_name,
            "examiner_name": examiner_name,
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
            "examiner_name": examiner_name,
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

        course_data = self.COURSE_VIVA_TOPICS.get(self.active_course_id, self.COURSE_VIVA_TOPICS["deep_learning"])
        topics_dict = course_data["topics"]

        # Check if more rounds remaining
        if session["current_round"] <= session["max_rounds"]:
            if session["pending_followup"]:
                next_q = session["pending_followup"]
                session["current_question"] = next_q
                session["current_key_concepts"] = session["pending_followup_concepts"]
                session["pending_followup"] = None
            else:
                # Next primary question
                questions = topics_dict.get(session["topic"], list(topics_dict.values())[0])
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
                "next_round": session["current_round"],
                "examiner_name": session.get("examiner_name", "Academic Examiner")
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
                "examiner_name": session.get("examiner_name", "Academic Examiner"),
                "feedback_summary": (
                    f"Viva Examination Concluded. Final Oral Grade: {avg_score}% ({verdict}). "
                    f"Your conceptual mastery score for '{session['topic']}' has been updated in the Competency Engine."
                ),
                "history": session["history"]
            }

socratic_viva_engine = SocraticVivaEngine()
