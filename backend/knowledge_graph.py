from typing import List, Dict, Any
from backend.competency_engine import competency_engine

class KnowledgeGraphEngine:
    """
    Constructs and serves the interactive concept knowledge graph (Visual Ontology).
    Maps prerequisites, hierarchical dependencies, and overlays real-time student mastery.
    """

    NODES = [
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
    ]

    EDGES = [
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

    @classmethod
    def get_graph_data(cls) -> Dict[str, Any]:
        """
        Returns graph nodes and edges enriched with live competency scores from CompetencyEngine.
        """
        comp = competency_engine.get_competency_analysis()
        topic_scores = competency_engine.topic_scores

        enriched_nodes = []
        for node in cls.NODES:
            topic = node["topic"]
            score = topic_scores.get(topic, 50.0)

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
            "title": "Deep Learning Concept Knowledge Graph (Visual Ontology)",
            "total_concepts": len(enriched_nodes),
            "total_relationships": len(cls.EDGES),
            "nodes": enriched_nodes,
            "edges": cls.EDGES
        }

knowledge_graph_engine = KnowledgeGraphEngine()
