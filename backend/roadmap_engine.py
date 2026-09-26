from typing import List, Dict, Any
from backend.competency_engine import competency_engine

class RoadmapEngine:
    """
    Personalized Learning Path Engine.
    Dynamically adjusts roadmap modules and prerequisite milestones based on the student's competency profile
    across multiple academic courses and subjects.
    """

    def __init__(self):
        self.completed_milestones = set(["m_ann_intro", "m_cnn_basics", "m_dsa_bigo", "m_os_intro", "m_la_vector"])

    def get_roadmap(self) -> Dict[str, Any]:
        from backend.course_manager import course_manager
        active_id = course_manager.active_course_id
        comp = competency_engine.get_competency_analysis()
        weak_topics = [w["topic"] for w in comp["weak"]]

        if active_id == "dsa":
            return self._build_dsa_roadmap(weak_topics)
        elif active_id == "operating_systems":
            return self._build_os_roadmap(weak_topics)
        elif active_id == "linear_algebra":
            return self._build_la_roadmap(weak_topics)
        else:
            return self._build_dl_roadmap(weak_topics)

    def _build_dl_roadmap(self, weak_topics: List[str]) -> Dict[str, Any]:
        rnn_weak = any("rnn" in t.lower() or "sequential" in t.lower() for t in weak_topics)
        trans_weak = any("transformer" in t.lower() or "attention" in t.lower() for t in weak_topics)

        weeks = []
        # Week 1
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

        # Week 2
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

        # Week 3
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

    def _build_dsa_roadmap(self, weak_topics: List[str]) -> Dict[str, Any]:
        dp_weak = any("dp" in t.lower() or "dynamic" in t.lower() for t in weak_topics)
        graph_weak = any("graph" in t.lower() or "dijkstra" in t.lower() for t in weak_topics)

        weeks = [
            {
                "week_number": 1,
                "title": "Week 1: Asymptotics, Arrays & Hash Map Foundations",
                "status": "Completed",
                "progress_percent": 100,
                "description": "Big-O growth rates, amortized array analysis, and separate chaining collision resolution.",
                "items": [
                    {"id": "m_dsa_bigo", "title": "Asymptotic Tight Bounds & Amortized Doubling", "type": "Concept Note", "estimated_time": "25 mins", "completed": True, "remedial_flag": False, "source_ref": "DSA_Core_Curriculum.txt (Chapter 1)"},
                    {"id": "m_dsa_hash", "title": "Hash Tables & Universal Hashing", "type": "Theory", "estimated_time": "20 mins", "completed": True, "remedial_flag": False, "source_ref": "DSA_Core_Curriculum.txt (Chapter 2)"}
                ]
            },
            {
                "week_number": 2,
                "title": "Week 2: Balanced Trees, Graphs & Shortest Paths",
                "status": "Active",
                "progress_percent": 50,
                "description": "AVL self-balancing tree rotations, BFS/DFS traversal invariants, and Dijkstra greedy min-heap paths.",
                "items": [
                    {"id": "m_dsa_avl", "title": "AVL Trees & Single/Double Rotations", "type": "Deep Dive", "estimated_time": "30 mins", "completed": True, "remedial_flag": False, "source_ref": "DSA_Core_Curriculum.txt (Chapter 3)"},
                    {"id": "m_dsa_dijkstra", "title": "Dijkstra Priority Queue Shortest Path", "type": "Algorithm Lab", "estimated_time": "35 mins", "completed": False, "remedial_flag": graph_weak, "source_ref": "DSA_Core_Curriculum.txt (Chapter 4)"}
                ]
            },
            {
                "week_number": 3,
                "title": "Week 3: Dynamic Programming & Recursive Optimization",
                "status": "Active" if dp_weak else "Locked",
                "progress_percent": 0,
                "description": "Master optimal substructure and overlapping subproblems for 0/1 Knapsack and LCS.",
                "items": [
                    {"id": "m_dsa_dp_memo", "title": "Top-Down Memoization vs Bottom-Up Tabulation", "type": "Targeted Remediation", "estimated_time": "35 mins", "completed": False, "remedial_flag": dp_weak, "source_ref": "DSA_Core_Curriculum.txt (Chapter 5)"},
                    {"id": "m_dsa_knapsack", "title": "0/1 Knapsack Recurrence Implementation", "type": "Coding Challenge", "estimated_time": "45 mins", "completed": False, "remedial_flag": dp_weak, "source_ref": "AI Quiz Hub"}
                ]
            }
        ]

        total_items = sum(len(w["items"]) for w in weeks)
        total_completed = sum(sum(1 for i in w["items"] if i["completed"]) for w in weeks)
        overall_progress = int((total_completed / max(1, total_items)) * 100)

        return {
            "roadmap_title": "Adaptive Algorithms & Data Structures Roadmap",
            "overall_progress_percent": overall_progress,
            "total_milestones": total_items,
            "completed_milestones": total_completed,
            "active_week": 2,
            "weeks": weeks
        }

    def _build_os_roadmap(self, weak_topics: List[str]) -> Dict[str, Any]:
        deadlock_weak = any("deadlock" in t.lower() or "banker" in t.lower() for t in weak_topics)
        paging_weak = any("page" in t.lower() or "virtual" in t.lower() for t in weak_topics)

        weeks = [
            {
                "week_number": 1,
                "title": "Week 1: Process Control Blocks & CPU Scheduling",
                "status": "Completed",
                "progress_percent": 100,
                "description": "Dual-mode hardware, context switching, Round Robin, and Multilevel Feedback Queues.",
                "items": [
                    {"id": "m_os_intro", "title": "Dual-Mode CPU & PCB State Invariants", "type": "Concept Note", "estimated_time": "20 mins", "completed": True, "remedial_flag": False, "source_ref": "OS_Concepts_and_Architecture.txt (Chapter 1)"},
                    {"id": "m_os_sched", "title": "CPU Scheduling Algorithms & Convoy Effect", "type": "Theory", "estimated_time": "25 mins", "completed": True, "remedial_flag": False, "source_ref": "OS_Concepts_and_Architecture.txt (Chapter 2)"}
                ]
            },
            {
                "week_number": 2,
                "title": "Week 2: Synchronization Primitives & Deadlock Avoidance",
                "status": "Active",
                "progress_percent": 50,
                "description": "Mutex semaphores, critical section bounded waiting, and Banker's Algorithm safe states.",
                "items": [
                    {"id": "m_os_sync", "title": "Mutex Semaphores & Race Condition Avoidance", "type": "Systems Lab", "estimated_time": "30 mins", "completed": True, "remedial_flag": False, "source_ref": "OS_Concepts_and_Architecture.txt (Chapter 3)"},
                    {"id": "m_os_banker", "title": "Banker's Algorithm & Coffman Conditions", "type": "Remediation", "estimated_time": "35 mins", "completed": False, "remedial_flag": deadlock_weak, "source_ref": "OS_Concepts_and_Architecture.txt (Chapter 3)"}
                ]
            },
            {
                "week_number": 3,
                "title": "Week 3: Virtual Memory Paging & Inode File Systems",
                "status": "Active",
                "progress_percent": 0,
                "description": "Address translation, TLB lookup, LRU page replacement, and Unix inode structures.",
                "items": [
                    {"id": "m_os_paging", "title": "Demand Paging, Page Faults & Belady's Anomaly", "type": "Deep Dive", "estimated_time": "35 mins", "completed": False, "remedial_flag": paging_weak, "source_ref": "OS_Concepts_and_Architecture.txt (Chapter 4)"},
                    {"id": "m_os_inodes", "title": "Unix Inode Triple Indirect Pointer Architecture", "type": "Architecture", "estimated_time": "30 mins", "completed": False, "remedial_flag": False, "source_ref": "OS_Concepts_and_Architecture.txt (Chapter 5)"}
                ]
            }
        ]

        total_items = sum(len(w["items"]) for w in weeks)
        total_completed = sum(sum(1 for i in w["items"] if i["completed"]) for w in weeks)
        overall_progress = int((total_completed / max(1, total_items)) * 100)

        return {
            "roadmap_title": "Adaptive Operating Systems Architecture Roadmap",
            "overall_progress_percent": overall_progress,
            "total_milestones": total_items,
            "completed_milestones": total_completed,
            "active_week": 2,
            "weeks": weeks
        }

    def _build_la_roadmap(self, weak_topics: List[str]) -> Dict[str, Any]:
        svd_weak = any("svd" in t.lower() or "singular" in t.lower() for t in weak_topics)

        weeks = [
            {
                "week_number": 1,
                "title": "Week 1: Vector Spaces, Linear Independence & Subspaces",
                "status": "Completed",
                "progress_percent": 100,
                "description": "Subspace criteria, basis coordinates, and the Four Fundamental Subspaces.",
                "items": [
                    {"id": "m_la_vector", "title": "Vector Spaces, Basis & Dimension", "type": "Foundations", "estimated_time": "25 mins", "completed": True, "remedial_flag": False, "source_ref": "Linear_Algebra_Core_Concepts.txt (Chapter 1)"},
                    {"id": "m_la_subspaces", "title": "Four Fundamental Subspaces & Rank-Nullity", "type": "Theory", "estimated_time": "30 mins", "completed": True, "remedial_flag": False, "source_ref": "Linear_Algebra_Core_Concepts.txt (Chapter 2)"}
                ]
            },
            {
                "week_number": 2,
                "title": "Week 2: Orthogonal Projections & Least Squares",
                "status": "Active",
                "progress_percent": 50,
                "description": "Gram-Schmidt orthogonalization, projection matrices, and normal equations.",
                "items": [
                    {"id": "m_la_proj", "title": "Orthogonal Projection & Normal Equations", "type": "Applied Math", "estimated_time": "30 mins", "completed": True, "remedial_flag": False, "source_ref": "Linear_Algebra_Core_Concepts.txt (Chapter 3)"},
                    {"id": "m_la_eigen", "title": "Eigenvalues, Characteristic Polynomials & Diagonalization", "type": "Deep Dive", "estimated_time": "35 mins", "completed": False, "remedial_flag": False, "source_ref": "Linear_Algebra_Core_Concepts.txt (Chapter 4)"}
                ]
            },
            {
                "week_number": 3,
                "title": "Week 3: Spectral Theorem, SVD & Optimization",
                "status": "Active",
                "progress_percent": 0,
                "description": "Singular Value Decomposition (A = U Sigma V^T), Eckart-Young low rank approximation, and PCA.",
                "items": [
                    {"id": "m_la_svd", "title": "Singular Value Decomposition (SVD) Matrix Geometry", "type": "Targeted Remediation", "estimated_time": "40 mins", "completed": False, "remedial_flag": svd_weak, "source_ref": "Linear_Algebra_Core_Concepts.txt (Chapter 5)"},
                    {"id": "m_la_opt", "title": "Multivariate Optimization, Gradient & Hessian Analysis", "type": "Capstone Lab", "estimated_time": "35 mins", "completed": False, "remedial_flag": False, "source_ref": "AI Quiz Hub"}
                ]
            }
        ]

        total_items = sum(len(w["items"]) for w in weeks)
        total_completed = sum(sum(1 for i in w["items"] if i["completed"]) for w in weeks)
        overall_progress = int((total_completed / max(1, total_items)) * 100)

        return {
            "roadmap_title": "Adaptive Linear Algebra & Optimization Roadmap",
            "overall_progress_percent": overall_progress,
            "total_milestones": total_items,
            "completed_milestones": total_completed,
            "active_week": 2,
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
