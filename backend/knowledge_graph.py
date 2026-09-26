from typing import List, Dict, Any
from backend.competency_engine import competency_engine

class KnowledgeGraphEngine:
    """
    Constructs and serves the interactive concept knowledge graph (Visual Ontology).
    Maps prerequisites, hierarchical dependencies, and overlays real-time student mastery
    across multiple academic courses and subjects.
    """

    COURSE_GRAPHS = {
        "deep_learning": {
            "title": "Deep Learning Concept Knowledge Graph (Visual Ontology)",
            "nodes": [
                {
                    "id": "node_perceptron",
                    "label": "Perceptron & Neurons",
                    "topic": "Neural Networks",
                    "category": "Foundations",
                    "description": "Biological inspirations, weighted sums, biases, and non-linear activations.",
                    "x": 100, "y": 200
                },
                {
                    "id": "node_activations",
                    "label": "Activation Functions",
                    "topic": "Neural Networks",
                    "category": "Foundations",
                    "description": "Sigmoid, ReLU, Leaky ReLU, and Softmax non-linearities.",
                    "x": 220, "y": 120
                },
                {
                    "id": "node_forward_loss",
                    "label": "Forward Pass & Losses",
                    "topic": "Forward & Loss Functions",
                    "category": "Foundations",
                    "description": "Layer transformations, MSE, Binary & Categorical Cross-Entropy.",
                    "x": 240, "y": 280
                },
                {
                    "id": "node_backprop",
                    "label": "Backpropagation (Chain Rule)",
                    "topic": "Backpropagation & Optimization",
                    "category": "Optimization",
                    "description": "Reverse-mode autodiff, error decomposition, and partial derivatives.",
                    "x": 380, "y": 200
                },
                {
                    "id": "node_optimizers",
                    "label": "Gradient Optimizers",
                    "topic": "Backpropagation & Optimization",
                    "category": "Optimization",
                    "description": "SGD with Momentum, RMSProp, and Adam adaptive moment estimation.",
                    "x": 480, "y": 120
                },
                {
                    "id": "node_regularization",
                    "label": "Overfitting & Regularization",
                    "topic": "Overfitting & Regularization",
                    "category": "Generalization",
                    "description": "Bias-variance trade-off, Dropout, L1/L2 weight decay, and Early Stopping.",
                    "x": 480, "y": 280
                },
                {
                    "id": "node_cnn",
                    "label": "Convolutional Networks (CNN)",
                    "topic": "Convolutional Neural Networks (CNN)",
                    "category": "Computer Vision",
                    "description": "Spatial 2D kernels, parameter sharing, stride, padding, and max pooling.",
                    "x": 620, "y": 100
                },
                {
                    "id": "node_resnet",
                    "label": "ResNet & Skip Connections",
                    "topic": "Convolutional Neural Networks (CNN)",
                    "category": "Computer Vision",
                    "description": "Identity shortcuts F(x) + x resolving ultra-deep degradation.",
                    "x": 760, "y": 70
                },
                {
                    "id": "node_rnn",
                    "label": "Recurrent Networks (RNN)",
                    "topic": "Recurrent Neural Networks (RNN)",
                    "category": "Sequential Modeling",
                    "description": "Temporal state persistence and Backpropagation Through Time (BPTT).",
                    "x": 620, "y": 280
                },
                {
                    "id": "node_vanishing_grad",
                    "label": "Vanishing Gradient Problem",
                    "topic": "Recurrent Neural Networks (RNN)",
                    "category": "Sequential Modeling",
                    "description": "Exponential gradient decay from repeated matrix multiplications with eigenvalues < 1.",
                    "x": 740, "y": 220
                },
                {
                    "id": "node_lstm",
                    "label": "Long Short-Term Memory (LSTM)",
                    "topic": "Long Short-Term Memory (LSTM)",
                    "category": "Sequential Modeling",
                    "description": "Constant error carousel, forget gate, input gate, and output gate.",
                    "x": 860, "y": 200
                },
                {
                    "id": "node_gru",
                    "label": "Gated Recurrent Unit (GRU)",
                    "topic": "Long Short-Term Memory (LSTM)",
                    "category": "Sequential Modeling",
                    "description": "Streamlined two-gate recurrent architecture (Reset & Update gates).",
                    "x": 860, "y": 290
                },
                {
                    "id": "node_attention",
                    "label": "Scaled Dot-Product Attention",
                    "topic": "Attention & Transformers",
                    "category": "Modern Architecture",
                    "description": "Query, Key, Value projections bypassing sequential bottlenecks with O(1) paths.",
                    "x": 920, "y": 100
                },
                {
                    "id": "node_transformers",
                    "label": "Transformers & LLM Foundations",
                    "topic": "Attention & Transformers",
                    "category": "Modern Architecture",
                    "description": "Multi-Head Self-Attention, Positional Encoding, BERT, and GPT architectures.",
                    "x": 1050, "y": 160
                }
            ],
            "edges": [
                {"source": "node_perceptron", "target": "node_activations", "relationship": "uses"},
                {"source": "node_perceptron", "target": "node_forward_loss", "relationship": "composes"},
                {"source": "node_forward_loss", "target": "node_backprop", "relationship": "prerequisite_of"},
                {"source": "node_activations", "target": "node_backprop", "relationship": "derivatives_in"},
                {"source": "node_backprop", "target": "node_optimizers", "relationship": "guides"},
                {"source": "node_backprop", "target": "node_regularization", "relationship": "controlled_by"},
                {"source": "node_backprop", "target": "node_cnn", "relationship": "foundation_of"},
                {"source": "node_cnn", "target": "node_resnet", "relationship": "evolves_into"},
                {"source": "node_backprop", "target": "node_rnn", "relationship": "temporal_variant"},
                {"source": "node_rnn", "target": "node_vanishing_grad", "relationship": "causes"},
                {"source": "node_vanishing_grad", "target": "node_lstm", "relationship": "mitigated_by"},
                {"source": "node_lstm", "target": "node_gru", "relationship": "streamlined_into"},
                {"source": "node_rnn", "target": "node_attention", "relationship": "bottleneck_solved_by"},
                {"source": "node_attention", "target": "node_transformers", "relationship": "core_block_of"}
            ]
        },
        "dsa": {
            "title": "Data Structures & Algorithms Concept Knowledge Graph",
            "nodes": [
                {"id": "dsa_asymptotics", "label": "Big-O & Asymptotics", "topic": "Asymptotic Analysis & Big-O", "category": "Foundations", "description": "Resource upper/lower bounds O(n), Omega(n), Theta(n).", "x": 100, "y": 160},
                {"id": "dsa_arrays", "label": "Dynamic Arrays", "topic": "Arrays & Dynamic Resizing", "category": "Sequences", "description": "Contiguous memory, base address arithmetic, amortized O(1) resizing.", "x": 240, "y": 100},
                {"id": "dsa_linked_lists", "label": "Linked Lists", "topic": "Arrays & Dynamic Resizing", "category": "Sequences", "description": "Non-contiguous nodes, pointer traversal, O(1) head insertion.", "x": 240, "y": 230},
                {"id": "dsa_hash_tables", "label": "Hash Maps & Chaining", "topic": "Hash Tables & Collision Resolution", "category": "Associative", "description": "Hash function distribution, open addressing, and collision chaining.", "x": 390, "y": 100},
                {"id": "dsa_bst", "label": "Binary Search Trees", "topic": "Binary Search Trees & AVL", "category": "Trees", "description": "BST ordering invariant, inorder traversal, and search bounds.", "x": 390, "y": 230},
                {"id": "dsa_avl", "label": "AVL Balanced Trees", "topic": "Binary Search Trees & AVL", "category": "Trees", "description": "Height balance factors (-1, 0, 1) and single/double rotation rebalancing.", "x": 520, "y": 230},
                {"id": "dsa_graphs", "label": "Graph Representations", "topic": "Graph Traversals (BFS & DFS)", "category": "Graphs", "description": "Adjacency matrices vs adjacency lists space/time trade-offs.", "x": 620, "y": 140},
                {"id": "dsa_bfs_dfs", "label": "BFS & DFS Traversals", "topic": "Graph Traversals (BFS & DFS)", "category": "Graphs", "description": "FIFO queue for level search vs LIFO recursion for cycle detection.", "x": 750, "y": 90},
                {"id": "dsa_dijkstra", "label": "Dijkstra Shortest Path", "topic": "Dijkstra Shortest Paths", "category": "Graph Algorithms", "description": "Greedy min-heap single-source shortest path O((V+E) log V).", "x": 880, "y": 90},
                {"id": "dsa_recursion", "label": "Optimal Substructure", "topic": "Dynamic Programming & Memoization", "category": "Optimization", "description": "Recursive decomposition into overlapping subproblems.", "x": 750, "y": 240},
                {"id": "dsa_dp", "label": "Dynamic Programming", "topic": "Dynamic Programming & Memoization", "category": "Optimization", "description": "Memoization (top-down) and Tabulation (bottom-up) optimization.", "x": 900, "y": 240}
            ],
            "edges": [
                {"source": "dsa_asymptotics", "target": "dsa_arrays", "relationship": "analyzes"},
                {"source": "dsa_asymptotics", "target": "dsa_linked_lists", "relationship": "analyzes"},
                {"source": "dsa_arrays", "target": "dsa_hash_tables", "relationship": "underlies"},
                {"source": "dsa_linked_lists", "target": "dsa_bst", "relationship": "hierarchical_generalization"},
                {"source": "dsa_bst", "target": "dsa_avl", "relationship": "balanced_by"},
                {"source": "dsa_avl", "target": "dsa_graphs", "relationship": "non_linear_abstraction"},
                {"source": "dsa_graphs", "target": "dsa_bfs_dfs", "relationship": "traversed_via"},
                {"source": "dsa_bfs_dfs", "target": "dsa_dijkstra", "relationship": "extended_by"},
                {"source": "dsa_asymptotics", "target": "dsa_recursion", "relationship": "evaluates"},
                {"source": "dsa_recursion", "target": "dsa_dp", "relationship": "optimized_into"}
            ]
        },
        "operating_systems": {
            "title": "Operating Systems & Systems Architecture Knowledge Graph",
            "nodes": [
                {"id": "os_dual_mode", "label": "Dual-Mode CPU Execution", "topic": "Process Lifecycle & Context Switching", "category": "Hardware", "description": "User mode vs Kernel mode, syscall traps, interrupt vector table.", "x": 100, "y": 150},
                {"id": "os_pcb", "label": "Process Control Block (PCB)", "topic": "Process Lifecycle & Context Switching", "category": "Processes", "description": "PID, registers, state transitions (Ready, Running, Blocked).", "x": 230, "y": 90},
                {"id": "os_context_switch", "label": "Context Switching", "topic": "Process Lifecycle & Context Switching", "category": "Processes", "description": "Register persistence, cache invalidation, and scheduling latency.", "x": 370, "y": 90},
                {"id": "os_threads", "label": "Threads & Shared Memory", "topic": "Threads & Concurrency", "category": "Concurrency", "description": "Shared heap and data segment, independent program counters.", "x": 370, "y": 220},
                {"id": "os_scheduling", "label": "CPU Scheduling (RR/MLFQ)", "topic": "CPU Scheduling (FCFS, SJF, RR)", "category": "Scheduling", "description": "Turnaround time, Convoy Effect, quantum sizing, starvation.", "x": 510, "y": 90},
                {"id": "os_sync", "label": "Semaphores & Mutexes", "topic": "Process Synchronization & Semaphores", "category": "Synchronization", "description": "Atomic test-and-set, critical section mutual exclusion, and progress.", "x": 510, "y": 220},
                {"id": "os_deadlocks", "label": "Coffman Deadlock Conditions", "topic": "Deadlocks & Banker's Algorithm", "category": "Deadlocks", "description": "Mutual exclusion, hold & wait, no preemption, and circular wait.", "x": 660, "y": 220},
                {"id": "os_banker", "label": "Banker's Avoidance Algorithm", "topic": "Deadlocks & Banker's Algorithm", "category": "Deadlocks", "description": "Dijkstra safe state trajectory evaluation against need matrices.", "x": 800, "y": 220},
                {"id": "os_paging", "label": "Paging & Page Tables", "topic": "Virtual Memory & Paging", "category": "Virtual Memory", "description": "Logical pages mapped to physical frames with valid/invalid bits.", "x": 660, "y": 90},
                {"id": "os_tlb", "label": "TLB Associative Cache", "topic": "Virtual Memory & Paging", "category": "Virtual Memory", "description": "Hardware translation cache minimizing effective memory access time.", "x": 800, "y": 90},
                {"id": "os_page_replace", "label": "LRU & Clock Page Replacement", "topic": "Page Replacement (FIFO, LRU, Clock)", "category": "Virtual Memory", "description": "Belady anomaly avoidance, LRU stack, reference bit clock sweep.", "x": 930, "y": 90},
                {"id": "os_inodes", "label": "Unix Inode Architecture", "topic": "Process Lifecycle & Context Switching", "category": "Storage", "description": "Direct, single, double, and triple indirect pointers with journaling.", "x": 930, "y": 220}
            ],
            "edges": [
                {"source": "os_dual_mode", "target": "os_pcb", "relationship": "isolates"},
                {"source": "os_pcb", "target": "os_context_switch", "relationship": "saved_during"},
                {"source": "os_pcb", "target": "os_threads", "relationship": "lightweight_variant"},
                {"source": "os_context_switch", "target": "os_scheduling", "relationship": "driven_by"},
                {"source": "os_threads", "target": "os_sync", "relationship": "requires"},
                {"source": "os_sync", "target": "os_deadlocks", "relationship": "vulnerable_to"},
                {"source": "os_deadlocks", "target": "os_banker", "relationship": "avoided_by"},
                {"source": "os_scheduling", "target": "os_paging", "relationship": "allocates_for"},
                {"source": "os_paging", "target": "os_tlb", "relationship": "accelerated_by"},
                {"source": "os_paging", "target": "os_page_replace", "relationship": "swapped_via"},
                {"source": "os_page_replace", "target": "os_inodes", "relationship": "backed_by"}
            ]
        },
        "linear_algebra": {
            "title": "Linear Algebra & Optimization Concept Knowledge Graph",
            "nodes": [
                {"id": "la_vector_space", "label": "Vector Spaces & Subspaces", "topic": "Vector Spaces & Basis", "category": "Foundations", "description": "Closure under addition and scalar multiplication.", "x": 100, "y": 150},
                {"id": "la_linear_indep", "label": "Linear Independence & Span", "topic": "Linear Independence & Span", "category": "Foundations", "description": "Linear combinations c1*v1 + ... + ck*vk = 0 requiring zero weights.", "x": 240, "y": 90},
                {"id": "la_basis_dim", "label": "Basis & Dimension", "topic": "Vector Spaces & Basis", "category": "Foundations", "description": "Minimal spanning sets and coordinate representations.", "x": 380, "y": 90},
                {"id": "la_subspaces", "label": "Four Fundamental Subspaces", "topic": "Four Fundamental Subspaces", "category": "Subspaces", "description": "Column space C(A), Nullspace N(A), Row space C(A^T), Left nullspace.", "x": 520, "y": 90},
                {"id": "la_rank_nullity", "label": "Rank-Nullity Theorem", "topic": "Four Fundamental Subspaces", "category": "Subspaces", "description": "rank(A) + nullity(A) = n with orthogonal subspace complements.", "x": 660, "y": 90},
                {"id": "la_inner_product", "label": "Inner Products & Orthogonality", "topic": "Orthogonal Projections & Least Squares", "category": "Orthogonality", "description": "Dot products, orthogonal matrices Q^T * Q = I, length preservation.", "x": 380, "y": 230},
                {"id": "la_projections", "label": "Orthogonal Projections", "topic": "Orthogonal Projections & Least Squares", "category": "Orthogonality", "description": "Projection matrices P = A(A^T A)^-1 A^T onto column space.", "x": 520, "y": 230},
                {"id": "la_least_squares", "label": "Normal Equations (Least Squares)", "topic": "Orthogonal Projections & Least Squares", "category": "Applied", "description": "Solving inconsistent systems via A^T A x_hat = A^T b.", "x": 660, "y": 230},
                {"id": "la_eigenvalues", "label": "Eigenvalues & Characteristic Eq", "topic": "Eigenvalues & Eigenvectors", "category": "Spectral", "description": "A*v = lambda*v, det(A - lambda*I) = 0 roots, trace and det invariants.", "x": 800, "y": 90},
                {"id": "la_diagonalization", "label": "Matrix Diagonalization", "topic": "Spectral Theorem & Diagonalization", "category": "Spectral", "description": "A = S * Lambda * S^-1 with powers A^k computed in O(n).", "x": 930, "y": 90},
                {"id": "la_spectral", "label": "Spectral Theorem (Symmetric)", "topic": "Spectral Theorem & Diagonalization", "category": "Spectral", "description": "Real eigenvalues, orthogonal eigenvectors, A = Q * Lambda * Q^T.", "x": 1060, "y": 90},
                {"id": "la_svd", "label": "Singular Value Decomposition (SVD)", "topic": "Singular Value Decomposition (SVD)", "category": "Decompositions", "description": "A = U * Sigma * V^T, Eckart-Young optimal low-rank matrix approximation.", "x": 800, "y": 230},
                {"id": "la_opt", "label": "Gradient & Hessian Optimization", "topic": "Singular Value Decomposition (SVD)", "category": "Optimization", "description": "Jacobians, positive definite Hessians, steepest descent and PCA.", "x": 950, "y": 230}
            ],
            "edges": [
                {"source": "la_vector_space", "target": "la_linear_indep", "relationship": "spanned_by"},
                {"source": "la_linear_indep", "target": "la_basis_dim", "relationship": "defines"},
                {"source": "la_basis_dim", "target": "la_subspaces", "relationship": "applied_in"},
                {"source": "la_subspaces", "target": "la_rank_nullity", "relationship": "governed_by"},
                {"source": "la_vector_space", "target": "la_inner_product", "relationship": "metric_structure"},
                {"source": "la_inner_product", "target": "la_projections", "relationship": "constructs"},
                {"source": "la_projections", "target": "la_least_squares", "relationship": "computes"},
                {"source": "la_subspaces", "target": "la_eigenvalues", "relationship": "invariant_directions"},
                {"source": "la_eigenvalues", "target": "la_diagonalization", "relationship": "enables"},
                {"source": "la_diagonalization", "target": "la_spectral", "relationship": "orthogonal_refinement"},
                {"source": "la_spectral", "target": "la_svd", "relationship": "generalizes_to_arbitrary"},
                {"source": "la_svd", "target": "la_opt", "relationship": "powers_pca_and"}
            ]
        }
    }

    # Backward compatibility default nodes/edges for deep learning
    NODES = COURSE_GRAPHS["deep_learning"]["nodes"]
    EDGES = COURSE_GRAPHS["deep_learning"]["edges"]

    def __init__(self):
        self.active_course_id = "deep_learning"

    def switch_course(self, course_id: str):
        self.active_course_id = course_id
        if course_id in self.COURSE_GRAPHS:
            KnowledgeGraphEngine.NODES = self.COURSE_GRAPHS[course_id]["nodes"]
            KnowledgeGraphEngine.EDGES = self.COURSE_GRAPHS[course_id]["edges"]

    def get_graph_data(self) -> Dict[str, Any]:
        """
        Returns graph nodes and edges enriched with live competency scores from CompetencyEngine.
        """
        graph_def = self.COURSE_GRAPHS.get(self.active_course_id, self.COURSE_GRAPHS["deep_learning"])
        nodes = graph_def["nodes"]
        edges = graph_def["edges"]
        title = graph_def.get("title", "Concept Knowledge Graph")

        topic_scores = competency_engine.topic_scores

        enriched_nodes = []
        for node in nodes:
            topic = node["topic"]
            # Look up score or match partial topic
            score = 50.0
            if topic in topic_scores:
                score = topic_scores[topic]
            else:
                for k, v in topic_scores.items():
                    if k.lower() in topic.lower() or topic.lower() in k.lower():
                        score = v
                        break

            status = "Strong" if score >= 75 else ("Average" if score >= 50 else "Weak")
            badge_color = "emerald" if score >= 75 else ("amber" if score >= 50 else "rose")

            enriched_nodes.append({
                **node,
                "score": score,
                "status": status,
                "badge_color": badge_color,
                "is_weak_gap": (score < 50)
            })

        return {
            "title": title,
            "total_concepts": len(enriched_nodes),
            "total_relationships": len(edges),
            "nodes": enriched_nodes,
            "edges": edges
        }

knowledge_graph_engine = KnowledgeGraphEngine()
