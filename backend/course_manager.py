import os
import json
from typing import Dict, Any, List, Optional
from backend.config import SAMPLE_MATERIALS_DIR, DATA_DIR

class CourseManager:
    """
    Centralized Multi-Course & Subject Management Engine for CogniTutor.
    Maintains independent curricula, topic competencies, question banks,
    concept ontologies, examiner personas, and dynamic study roadmaps.
    """

    COURSES_METADATA_FILE = os.path.join(DATA_DIR, "courses_registry.json")

    PRECONFIGURED_COURSES = {
        "deep_learning": {
            "id": "deep_learning",
            "title": "Deep Learning & Neural Networks",
            "code": "CS-482",
            "category": "Artificial Intelligence",
            "description": "Master deep neural architectures, backpropagation, CNNs, LSTMs, and modern attention-based Transformer models.",
            "icon": "brain",
            "color": "blue",
            "sample_files": [
                "Deep_Learning_Fundamentals.txt",
                "Convolutional_Neural_Networks.pdf",
                "Recurrent_Neural_Networks_and_LSTMs.docx",
                "Transformers_and_Attention_Mechanisms.pptx"
            ],
            "examiner": {
                "name": "Prof. Alan Turing",
                "title": "Academic Examiner • Deep Learning Viva Board",
                "initials": "PT",
                "avatar_bg": "bg-slate-900"
            },
            "doubt_chips": [
                "LSTM Memory Cells",
                "Backpropagation Chain Rule",
                "CNN Convolutions",
                "Transformer Self-Attention",
                "Overfitting & Regularization"
            ],
            "sample_queries": [
                "Explain the backpropagation chain rule step by step.",
                "What are the advantages of CNN mentioned in Chapter 4?",
                "Why do vanilla RNNs suffer from vanishing gradients?",
                "Explain the Scaled Dot-Product Attention formula."
            ],
            "competencies": {
                "Neural Networks": 85.0,
                "Convolutional Neural Networks (CNN)": 78.0,
                "Backpropagation & Optimization": 82.0,
                "Overfitting & Regularization": 68.0,
                "Recurrent Neural Networks (RNN)": 42.0,
                "Long Short-Term Memory (LSTM)": 48.0,
                "Attention & Transformers": 35.0
            }
        },
        "dsa": {
            "id": "dsa",
            "title": "Data Structures & Algorithms",
            "code": "CS-201",
            "category": "Computer Science Core",
            "description": "Asymptotic complexity, hash maps, balanced search trees, graph traversals (BFS/DFS/Dijkstra), and dynamic programming.",
            "icon": "network",
            "color": "emerald",
            "sample_files": [
                "DSA_Core_Curriculum.txt"
            ],
            "examiner": {
                "name": "Prof. Donald Knuth",
                "title": "Distinguished Examiner • Algorithms & Complexity Board",
                "initials": "DK",
                "avatar_bg": "bg-emerald-950"
            },
            "doubt_chips": [
                "Asymptotic Big-O",
                "Hash Collisions & Chaining",
                "AVL Balanced Trees",
                "Dijkstra Shortest Path",
                "0/1 Knapsack DP"
            ],
            "sample_queries": [
                "Explain the difference between Big-O and Big-Theta notation.",
                "How does separate chaining resolve hash table collisions?",
                "What is the rotation mechanism used by AVL trees to rebalance?",
                "Explain the optimal substructure requirement for Dynamic Programming."
            ],
            "competencies": {
                "Asymptotic Analysis & Big-O": 88.0,
                "Arrays & Dynamic Resizing": 92.0,
                "Hash Tables & Collision Resolution": 75.0,
                "Binary Search Trees & AVL": 64.0,
                "Graph Traversals (BFS & DFS)": 58.0,
                "Dijkstra Shortest Paths": 45.0,
                "Dynamic Programming & Memoization": 38.0
            }
        },
        "operating_systems": {
            "id": "operating_systems",
            "title": "Operating Systems & Systems Programming",
            "code": "CS-350",
            "category": "Computer Systems",
            "description": "Processes, threads, CPU scheduling algorithms, mutex synchronization, deadlocks, and virtual memory page replacement.",
            "icon": "cpu",
            "color": "amber",
            "sample_files": [
                "OS_Concepts_and_Architecture.txt"
            ],
            "examiner": {
                "name": "Prof. Andrew Tanenbaum",
                "title": "Chief Examiner • Systems Architecture & Kernel Viva Board",
                "initials": "AT",
                "avatar_bg": "bg-amber-950"
            },
            "doubt_chips": [
                "Process Context Switching",
                "Round Robin vs MLFQ",
                "Mutex & Deadlock Conditions",
                "Virtual Memory & TLB",
                "Inode File Systems"
            ],
            "sample_queries": [
                "What hardware state is saved during an operating system context switch?",
                "How does Round Robin scheduling prevent process starvation?",
                "Explain the 4 Coffman conditions required for a system deadlock.",
                "Why does Belady's Anomaly occur in FIFO page replacement?"
            ],
            "competencies": {
                "Process Lifecycle & Context Switching": 84.0,
                "Threads & Concurrency": 76.0,
                "CPU Scheduling (FCFS, SJF, RR)": 80.0,
                "Process Synchronization & Semaphores": 55.0,
                "Deadlocks & Banker's Algorithm": 48.0,
                "Virtual Memory & Paging": 62.0,
                "Page Replacement (FIFO, LRU, Clock)": 39.0
            }
        },
        "linear_algebra": {
            "id": "linear_algebra",
            "title": "Linear Algebra & Optimization",
            "code": "MATH-214",
            "category": "Mathematics & Machine Learning",
            "description": "Vector spaces, four fundamental subspaces, orthogonal projections, eigendecomposition, SVD, and multivariate optimization.",
            "icon": "binary",
            "color": "purple",
            "sample_files": [
                "Linear_Algebra_Core_Concepts.txt"
            ],
            "examiner": {
                "name": "Prof. Gilbert Strang",
                "title": "Emeritus Examiner • Applied Linear Algebra Viva Board",
                "initials": "GS",
                "avatar_bg": "bg-purple-950"
            },
            "doubt_chips": [
                "Linear Independence & Basis",
                "Four Fundamental Subspaces",
                "Orthogonal Projection & Least Squares",
                "Eigenvalues & Diagonalization",
                "Singular Value Decomposition (SVD)"
            ],
            "sample_queries": [
                "State the Rank-Nullity Theorem and explain its geometric meaning.",
                "How does the normal equation A^T * A * x = A^T * b solve least squares?",
                "Why are eigenvectors of real symmetric matrices always mutually orthogonal?",
                "Explain the geometric intuition of Singular Value Decomposition (A = U * Sigma * V^T)."
            ],
            "competencies": {
                "Vector Spaces & Basis": 86.0,
                "Linear Independence & Span": 82.0,
                "Four Fundamental Subspaces": 70.0,
                "Orthogonal Projections & Least Squares": 65.0,
                "Eigenvalues & Eigenvectors": 54.0,
                "Spectral Theorem & Diagonalization": 46.0,
                "Singular Value Decomposition (SVD)": 36.0
            }
        }
    }

    def __init__(self):
        self.active_course_id: str = "deep_learning"
        self.custom_courses: Dict[str, Dict[str, Any]] = {}
        self.load_registry()

    def load_registry(self):
        if os.path.exists(self.COURSES_METADATA_FILE):
            try:
                with open(self.COURSES_METADATA_FILE, "r", encoding="utf-8") as f:
                    self.custom_courses = json.load(f)
            except Exception as e:
                print(f"Warning: could not load courses registry: {e}")
                self.custom_courses = {}

    def save_registry(self):
        try:
            with open(self.COURSES_METADATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.custom_courses, f, indent=2)
        except Exception as e:
            print(f"Warning: could not save courses registry: {e}")

    def get_all_courses(self) -> List[Dict[str, Any]]:
        from backend.competency_engine import competency_engine
        from backend.storage import storage_manager

        courses_list = []
        all_courses = {**self.PRECONFIGURED_COURSES, **self.custom_courses}

        for c_id, c in all_courses.items():
            # Calculate mastery
            if c_id == self.active_course_id:
                scores = list(competency_engine.topic_scores.values())
            else:
                scores = list(c.get("competencies", {}).values())

            avg_mastery = round(sum(scores) / len(scores), 1) if scores else 50.0

            # Count documents for this course
            sample_files = c.get("sample_files", [])
            doc_count = sum(1 for d in storage_manager.documents.values() if d.get("file_name") in sample_files or d.get("course_id") == c_id)
            if doc_count == 0 and sample_files:
                doc_count = len(sample_files)

            courses_list.append({
                "id": c_id,
                "title": c["title"],
                "code": c["code"],
                "category": c.get("category", "General"),
                "description": c.get("description", ""),
                "icon": c.get("icon", "book-open"),
                "color": c.get("color", "blue"),
                "is_active": (c_id == self.active_course_id),
                "examiner": c.get("examiner", {
                    "name": "Prof. Academic Mentor",
                    "title": "Academic Faculty Board",
                    "initials": "AM",
                    "avatar_bg": "bg-slate-900"
                }),
                "topics_count": len(c.get("competencies", {})),
                "mastery_percent": int(avg_mastery),
                "doc_count": max(doc_count, 1),
                "doubt_chips": c.get("doubt_chips", []),
                "sample_queries": c.get("sample_queries", [])
            })
        return courses_list

    def get_active_course(self) -> Dict[str, Any]:
        all_courses = {**self.PRECONFIGURED_COURSES, **self.custom_courses}
        return all_courses.get(self.active_course_id, self.PRECONFIGURED_COURSES["deep_learning"])

    def switch_course(self, course_id: str) -> Dict[str, Any]:
        all_courses = {**self.PRECONFIGURED_COURSES, **self.custom_courses}
        if course_id not in all_courses:
            raise ValueError(f"Course '{course_id}' not found.")

        self.active_course_id = course_id
        course = all_courses[course_id]

        # Update Competency Engine
        from backend.competency_engine import competency_engine
        competency_engine.topic_scores = dict(course.get("competencies", {}))

        # Update Knowledge Graph Engine
        from backend.knowledge_graph import knowledge_graph_engine
        knowledge_graph_engine.switch_course(course_id)

        # Update Quiz Engine
        from backend.quiz_engine import quiz_engine
        quiz_engine.switch_course(course_id)

        # Update Viva Engine
        from backend.viva_engine import socratic_viva_engine
        socratic_viva_engine.switch_course(course_id)

        # Update Storage & RAG Chunks filter for course materials
        from backend.storage import storage_manager
        storage_manager.refresh_for_active_course(course_id, course.get("sample_files", []))

        return {
            "success": True,
            "active_course_id": course_id,
            "course": course
        }

    def create_custom_course(self, title: str, code: str, description: str, category: str = "Custom Course", initial_notes: str = "") -> Dict[str, Any]:
        c_id = code.lower().replace("-", "_").replace(" ", "_")
        if not c_id:
            c_id = f"custom_{len(self.custom_courses) + 1}"

        # If notes text is provided, write to sample_materials
        sample_file_name = f"{code.replace(' ', '_')}_Notes.txt"
        file_path = os.path.join(SAMPLE_MATERIALS_DIR, sample_file_name)
        if initial_notes.strip():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"================================================================================\n")
                f.write(f"COURSE {code}: {title.upper()}\n")
                f.write(f"Category: {category}\n")
                f.write(f"================================================================================\n\n")
                f.write(f"[PAGE 1] CHAPTER 1: FOUNDATIONS\n")
                f.write(initial_notes.strip() + "\n")
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"================================================================================\n")
                f.write(f"COURSE {code}: {title.upper()}\n")
                f.write(f"================================================================================\n\n")
                f.write(f"[PAGE 1] CHAPTER 1: OVERVIEW\n{description}\n")

        # Initial topics
        initial_topics = {
            f"{title} Fundamentals": 60.0,
            f"Core Principles & Methodologies": 50.0,
            f"Advanced Applications": 40.0
        }

        course_obj = {
            "id": c_id,
            "title": title,
            "code": code,
            "category": category,
            "description": description,
            "icon": "book-open",
            "color": "indigo",
            "sample_files": [sample_file_name],
            "examiner": {
                "name": f"Prof. {code} Examiner",
                "title": f"Faculty Examiner • {title} Board",
                "initials": "".join([part[0] for part in code.split("-") if part])[:2].upper() or "EX",
                "avatar_bg": "bg-indigo-950"
            },
            "doubt_chips": [
                f"{title} Foundations",
                "Core Methodologies",
                "Edge Cases & Analysis"
            ],
            "sample_queries": [
                f"Explain the core objectives of {title}.",
                f"What are the foundational concepts covered in {code}?"
            ],
            "competencies": initial_topics
        }

        self.custom_courses[c_id] = course_obj
        self.save_registry()

        # Index the file
        from backend.storage import storage_manager
        storage_manager.index_file(file_path, is_sample=True)

        return course_obj

course_manager = CourseManager()
