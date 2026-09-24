import random
import re
from typing import List, Dict, Any, Optional

class QuizEngine:
    """
    Automatic Quiz and MCQ Generator with Adaptive Difficulty and Auto-Evaluation.
    Generates MCQs, Short Answer questions, and Long Conceptual questions.
    """

    QUESTION_BANK = [
        # Neural Networks & Forward/Loss
        {
            "id": "q1",
            "topic": "Neural Networks",
            "type": "mcq",
            "difficulty": "easy",
            "question": "What is the primary role of an activation function in an artificial neural network?",
            "options": [
                "A. To initialize network weights randomly",
                "B. To introduce non-linearity so the network can learn complex patterns",
                "C. To prevent data from being loaded into GPU memory",
                "D. To calculate the number of training epochs"
            ],
            "correct_index": 1,
            "explanation": "Activation functions (e.g. ReLU, Sigmoid) introduce non-linear transformations. Without them, stacking multiple layers would still result in a purely linear mapping equivalent to a single linear layer.",
            "source_doc": "Deep_Learning_Fundamentals.txt",
            "source_page": "Chapter 1"
        },
        {
            "id": "q2",
            "topic": "Forward & Loss Functions",
            "type": "mcq",
            "difficulty": "easy",
            "question": "Which loss function is most commonly utilized for multi-class classification tasks?",
            "options": [
                "A. Mean Squared Error (MSE)",
                "B. Binary Cross-Entropy",
                "C. Categorical Cross-Entropy",
                "D. Huber Loss"
            ],
            "correct_index": 2,
            "explanation": "Categorical Cross-Entropy is designed for multi-class classification paired with a Softmax output layer, penalizing incorrect probability distributions.",
            "source_doc": "Deep_Learning_Fundamentals.txt",
            "source_page": "Chapter 2"
        },
        {
            "id": "q3",
            "topic": "Backpropagation & Optimization",
            "type": "mcq",
            "difficulty": "medium",
            "question": "What mathematical principle enables backpropagation to calculate parameter gradients across deep layers?",
            "options": [
                "A. Fourier Transform",
                "B. Chain Rule of Calculus",
                "C. Newton-Raphson Root Finding",
                "D. Bayes Theorem"
            ],
            "correct_index": 1,
            "explanation": "Backpropagation repeatedly applies the chain rule of calculus dL/dw = (dL/da) * (da/dz) * (dz/dw) from the output layer backwards.",
            "source_doc": "Deep_Learning_Fundamentals.txt",
            "source_page": "Chapter 3"
        },
        {
            "id": "q4",
            "topic": "Overfitting & Regularization",
            "type": "mcq",
            "difficulty": "easy",
            "question": "What is overfitting?",
            "options": [
                "A. Model performs poorly on training data",
                "B. Model performs well on training data but poorly on unseen test data",
                "C. Model has zero learnable parameters",
                "D. Model cannot learn during gradient descent"
            ],
            "correct_index": 1,
            "explanation": "Overfitting happens when a model learns the training noise so tightly that it fails to generalize to unseen test or validation data.",
            "source_doc": "Deep_Learning_Fundamentals.txt",
            "source_page": "Chapter 4"
        },
        {
            "id": "q5",
            "topic": "Overfitting & Regularization",
            "type": "mcq",
            "difficulty": "medium",
            "question": "How does the Dropout regularization technique function during training?",
            "options": [
                "A. Permanently removes low-weight neurons from the architecture",
                "B. Randomly deactivates a fraction p of neurons during each training pass",
                "C. Drops bad training examples from the dataset",
                "D. Reduces the learning rate to zero"
            ],
            "correct_index": 1,
            "explanation": "Dropout randomly sets a fraction p of neuron activations to zero during each training step, preventing co-adaptation of features.",
            "source_doc": "Deep_Learning_Fundamentals.txt",
            "source_page": "Chapter 4"
        },
        {
            "id": "q6",
            "topic": "Convolutional Neural Networks (CNN)",
            "type": "mcq",
            "difficulty": "easy",
            "question": "Why are CNNs preferred over standard Fully Connected (Dense) networks for image processing?",
            "options": [
                "A. Dense networks have parameter explosion and discard spatial 2D pixel topology",
                "B. Dense networks cannot perform matrix multiplication",
                "C. CNNs do not use activation functions",
                "D. Dense networks cannot output class labels"
            ],
            "correct_index": 0,
            "explanation": "Flattening large images into fully connected layers creates millions of parameters, causing severe overfitting. CNNs preserve 2D topology and share weights.",
            "source_doc": "Convolutional_Neural_Networks.pdf",
            "source_page": "Page 1"
        },
        {
            "id": "q7",
            "topic": "Convolutional Neural Networks (CNN)",
            "type": "mcq",
            "difficulty": "medium",
            "question": "What is the primary benefit of Max Pooling in a CNN?",
            "options": [
                "A. Doubles the number of color channels",
                "B. Provides spatial translation invariance and downsamples feature map dimensions",
                "C. Multiplies weights by negative gradients",
                "D. Converts continuous features into binary tokens"
            ],
            "correct_index": 1,
            "explanation": "Max Pooling takes the peak activation in each window, reducing spatial size and compute while offering translation invariance.",
            "source_doc": "Convolutional_Neural_Networks.pdf",
            "source_page": "Page 1"
        },
        {
            "id": "q8",
            "topic": "Recurrent Neural Networks (RNN)",
            "type": "mcq",
            "difficulty": "medium",
            "question": "What fundamental flaw causes the Vanishing Gradient problem in vanilla RNNs during Backpropagation Through Time (BPTT)?",
            "options": [
                "A. Repeated matrix multiplications of weight matrices with eigenvalues < 1 exponentially diminish gradients",
                "B. The learning rate is multiplied by infinity",
                "C. RNNs cannot use GPUs",
                "D. ReLU activation produces negative infinities"
            ],
            "correct_index": 0,
            "explanation": "Across long sequences, the temporal gradient chain involves multiplying recurrent weights repeatedly. If eigenvalues are less than 1, gradients vanish exponentially.",
            "source_doc": "Recurrent_Neural_Networks_and_LSTMs.docx",
            "source_page": "Section: 2. Vanishing Gradient"
        },
        {
            "id": "q9",
            "topic": "Long Short-Term Memory (LSTM)",
            "type": "mcq",
            "difficulty": "hard",
            "question": "Which specific gate in an LSTM decides what proportion of past information to discard from the cell state?",
            "options": [
                "A. Input Gate",
                "B. Reset Gate",
                "C. Forget Gate",
                "D. Output Gate"
            ],
            "correct_index": 2,
            "explanation": "The Forget Gate f_t = sigmoid(W_f * [h_{t-1}, x_t] + b_f) computes a value between 0 (discard completely) and 1 (retain completely) to scale the past cell state C_{t-1}.",
            "source_doc": "Recurrent_Neural_Networks_and_LSTMs.docx",
            "source_page": "Section: 3. LSTM"
        },
        {
            "id": "q10",
            "topic": "Attention & Transformers",
            "type": "mcq",
            "difficulty": "hard",
            "question": "Why does Scaled Dot-Product Attention divide the dot product Q * K^T by sqrt(d_k)?",
            "options": [
                "A. To convert the result into binary integers",
                "B. To scale variance to 1, preventing large dot products from pushing softmax into near-zero gradient regions",
                "C. Because division by square root is required by matrix algebra",
                "D. To double the speed of GPU memory transfers"
            ],
            "correct_index": 1,
            "explanation": "For large projection dimensions d_k, dot products grow large in magnitude, driving softmax into regions with extremely small gradients. Scaling by sqrt(d_k) stabilizes training.",
            "source_doc": "Transformers_and_Attention_Mechanisms.pptx",
            "source_page": "Slide 3"
        },
        {
            "id": "q11",
            "topic": "Attention & Transformers",
            "type": "mcq",
            "difficulty": "medium",
            "question": "What is the primary reason Transformers process long sequences faster than RNNs during training?",
            "options": [
                "A. Transformers process tokens sequentially one by one",
                "B. Self-attention enables parallel computation of all tokens simultaneously on GPUs",
                "C. Transformers do not calculate loss gradients",
                "D. Transformers use smaller datasets"
            ],
            "correct_index": 1,
            "explanation": "Unlike RNNs which require sequential step-by-step computation (t-1 must finish before t starts), Transformers compute attention across the entire sequence concurrently in parallel matrix operations.",
            "source_doc": "Transformers_and_Attention_Mechanisms.pptx",
            "source_page": "Slide 2"
        },
        {
            "id": "q12",
            "topic": "Convolutional Neural Networks (CNN)",
            "type": "mcq",
            "difficulty": "hard",
            "question": "How do Residual Connections (Skip Connections) in ResNet resolve the degradation problem in ultra-deep networks?",
            "options": [
                "A. By skipping the training process entirely",
                "B. By providing identity shortcut connections F(x) + x allowing gradients to flow directly without vanishing",
                "C. By removing all convolutional filters",
                "D. By replacing backpropagation with genetic algorithms"
            ],
            "correct_index": 1,
            "explanation": "Residual connections add the input directly to the block output F(x) + x. The derivative with respect to input includes an identity term (+1), guaranteeing unimpeded gradient flow backwards.",
            "source_doc": "Convolutional_Neural_Networks.pdf",
            "source_page": "Page 1"
        }
    ]

    SHORT_QUESTIONS = [
        {
            "id": "sq1",
            "topic": "Backpropagation & Optimization",
            "question": "Explain how the chain rule is used in backpropagation to compute weight updates.",
            "model_answer": "Backpropagation uses the chain rule to decompose the total loss derivative into local gradients: dL/dw = (dL/da) * (da/dz) * (dz/dw). It propagates error backwards layer-by-layer to update weights against the gradient.",
            "key_keywords": ["chain rule", "gradient", "loss", "derivative", "update", "layer", "propagate"],
            "difficulty": "medium",
            "source_doc": "Deep_Learning_Fundamentals.txt",
            "source_page": "Chapter 3"
        },
        {
            "id": "sq2",
            "topic": "Overfitting & Regularization",
            "question": "Name two methods to prevent overfitting and briefly describe how each works.",
            "model_answer": "1. Dropout: randomly drops neurons during training to prevent co-adaptation. 2. L1/L2 Regularization (Weight Decay): penalizes large weights in the loss function to encourage simpler models.",
            "key_keywords": ["dropout", "regularization", "l1", "l2", "weight decay", "early stopping", "generalize"],
            "difficulty": "easy",
            "source_doc": "Deep_Learning_Fundamentals.txt",
            "source_page": "Chapter 4"
        },
        {
            "id": "sq3",
            "topic": "Convolutional Neural Networks (CNN)",
            "question": "What are the three main advantages of CNNs over standard feedforward neural networks for image data?",
            "model_answer": "CNNs provide: (1) Parameter sharing, reducing weight count; (2) Translation invariance, recognizing patterns anywhere; and (3) Hierarchical feature learning, capturing edges, textures, and semantic shapes.",
            "key_keywords": ["parameter sharing", "translation invariance", "hierarchical", "spatial", "pooling", "weights"],
            "difficulty": "medium",
            "source_doc": "Convolutional_Neural_Networks.pdf",
            "source_page": "Page 1"
        },
        {
            "id": "sq4",
            "topic": "Long Short-Term Memory (LSTM)",
            "question": "Describe the function of the Forget Gate and the Cell State in an LSTM.",
            "model_answer": "The Cell State acts as a continuous conveyor belt preserving long-term memory across sequence steps. The Forget Gate uses a sigmoid function to decide what proportion of past information to erase or retain.",
            "key_keywords": ["cell state", "forget gate", "sigmoid", "memory", "conveyor", "retain", "erase"],
            "difficulty": "medium",
            "source_doc": "Recurrent_Neural_Networks_and_LSTMs.docx",
            "source_page": "Section: 3. LSTM"
        },
        {
            "id": "sq5",
            "topic": "Attention & Transformers",
            "question": "What are Query, Key, and Value matrices in the Scaled Dot-Product Attention mechanism?",
            "model_answer": "Query (Q) represents what a token is searching for, Key (K) represents what a token offers or contains, and Value (V) holds the actual representation. Attention scores Q*K^T weight the Values.",
            "key_keywords": ["query", "key", "value", "dot product", "softmax", "weight", "attention"],
            "difficulty": "hard",
            "source_doc": "Transformers_and_Attention_Mechanisms.pptx",
            "source_page": "Slide 3"
        }
    ]

    LONG_QUESTIONS = [
        {
            "id": "lq1",
            "topic": "Recurrent Neural Networks (RNN)",
            "question": "Analyze the Vanishing Gradient problem in sequential modeling. Compare how Vanilla RNNs, LSTMs, and Transformers address long-range dependencies.",
            "criteria": [
                "Explanation of exponential gradient decay during BPTT with small eigenvalues",
                "LSTM additive cell state C_t and forget/input/output gating mechanisms",
                "Transformer self-attention bypassing sequential paths with O(1) direct connections",
                "Trade-offs in computational complexity and GPU parallelization"
            ],
            "difficulty": "hard",
            "source_doc": "Recurrent_Neural_Networks_and_LSTMs.docx"
        },
        {
            "id": "lq2",
            "topic": "Convolutional Neural Networks (CNN)",
            "question": "Detail the evolution of CNN architectures from LeNet-5 and AlexNet to VGG and ResNet. How did skip connections solve the degradation problem?",
            "criteria": [
                "Historical progression from early networks to deep stacks of 3x3 convolutions",
                "Explanation of the degradation problem when going beyond 20-30 layers",
                "Mathematical formulation of residual mapping F(x) = H(x) - x and identity skip shortcut",
                "Implications for gradient propagation and training ultra-deep architectures"
            ],
            "difficulty": "hard",
            "source_doc": "Convolutional_Neural_Networks.pdf"
        },
        {
            "id": "lq3",
            "topic": "Overfitting & Regularization",
            "question": "A deep learning model exhibits 99% training accuracy but 64% validation accuracy. Diagnose the issue and propose a step-by-step engineering plan to resolve it.",
            "criteria": [
                "Identification of high variance / overfitting phenomenon",
                "Application of regularization (L2 weight decay, Dropout with tuned probability)",
                "Data augmentation techniques suited to input domain",
                "Model capacity adjustment and Early Stopping strategy based on validation curves"
            ],
            "difficulty": "hard",
            "source_doc": "Deep_Learning_Fundamentals.txt"
        }
    ]

    @classmethod
    def generate_quiz(cls, topic_filter: Optional[str] = None, difficulty: str = "adaptive", count_mcq: int = 10, count_short: int = 5, count_long: int = 3) -> Dict[str, Any]:
        """
        Generates a balanced quiz package:
        - 10 MCQs
        - 5 Short Answer Questions
        - 3 Long Conceptual Questions
        """
        all_mcqs = list(cls.QUESTION_BANK)
        all_short = list(cls.SHORT_QUESTIONS)
        all_long = list(cls.LONG_QUESTIONS)

        if topic_filter and topic_filter.lower() != "all":
            tf = topic_filter.lower()
            all_mcqs = [q for q in all_mcqs if tf in q["topic"].lower()] or all_mcqs
            all_short = [q for q in all_short if tf in q["topic"].lower()] or all_short
            all_long = [q for q in all_long if tf in q["topic"].lower()] or all_long

        # If adaptive, we provide a mix or filter by target difficulty
        if difficulty in ["easy", "medium", "hard"]:
            filtered_mcqs = [q for q in all_mcqs if q.get("difficulty") == difficulty]
            if len(filtered_mcqs) >= 5:
                selected_mcqs = filtered_mcqs[:count_mcq]
            else:
                selected_mcqs = all_mcqs[:count_mcq]
        else:
            selected_mcqs = all_mcqs[:count_mcq]

        selected_short = all_short[:count_short]
        selected_long = all_long[:count_long]

        # Hide answers from student quiz payload
        student_mcqs = []
        for q in selected_mcqs:
            q_clean = dict(q)
            # Retain correct_index in background for instant checking, but frontend can evaluate via API
            student_mcqs.append(q_clean)

        return {
            "quiz_id": f"quiz_{random.randint(1000, 9999)}",
            "topic": topic_filter or "Deep Learning & Neural Networks Curriculum",
            "difficulty_mode": difficulty,
            "mcqs": student_mcqs,
            "short_questions": selected_short,
            "long_questions": selected_long,
            "total_questions": len(student_mcqs) + len(selected_short) + len(selected_long)
        }

    @classmethod
    def evaluate_mcq(cls, question_id: str, selected_option_index: int, current_streak: int = 0, current_difficulty: str = "medium") -> Dict[str, Any]:
        """
        Evaluates a single MCQ submission, adjusts adaptive difficulty, and gives complete explanations.
        """
        question = next((q for q in cls.QUESTION_BANK if q["id"] == question_id), None)
        if not question:
            return {"error": "Question not found"}

        is_correct = (selected_option_index == question["correct_index"])
        new_streak = (current_streak + 1) if is_correct else 0

        # Adaptive difficulty adjustment
        new_difficulty = current_difficulty
        if is_correct:
            if new_streak >= 2:
                if current_difficulty == "easy":
                    new_difficulty = "medium"
                elif current_difficulty == "medium":
                    new_difficulty = "hard"
        else:
            if current_difficulty == "hard":
                new_difficulty = "medium"
            elif current_difficulty == "medium":
                new_difficulty = "easy"

        xp_earned = 15 if is_correct else 2

        return {
            "question_id": question_id,
            "is_correct": is_correct,
            "correct_index": question["correct_index"],
            "correct_option_text": question["options"][question["correct_index"]],
            "user_selection": selected_option_index,
            "explanation": question["explanation"],
            "topic": question["topic"],
            "source_doc": question.get("source_doc", "Study Notes"),
            "source_page": question.get("source_page", "Section 1"),
            "streak": new_streak,
            "next_difficulty": new_difficulty,
            "xp_earned": xp_earned
        }

    @classmethod
    def evaluate_short_answer(cls, question_id: str, student_answer: str) -> Dict[str, Any]:
        """
        Evaluates a student's short answer against key concept rubrics.
        """
        question = next((q for q in cls.SHORT_QUESTIONS if q["id"] == question_id), None)
        if not question:
            return {"error": "Question not found"}

        answer_clean = student_answer.lower().strip()
        if len(answer_clean) < 5:
            return {
                "score": 0,
                "passed": False,
                "feedback": "Answer is too short or empty. Please explain the concept in your own words.",
                "keywords_covered": [],
                "model_answer": question["model_answer"]
            }

        required_keywords = question["key_keywords"]
        matched_keywords = []

        for kw in required_keywords:
            if kw.lower() in answer_clean:
                matched_keywords.append(kw)

        coverage_ratio = len(matched_keywords) / max(1, len(required_keywords))
        score = int(coverage_ratio * 100)

        # Length and fluency bonus
        if len(answer_clean.split()) >= 15 and score > 30:
            score = min(100, score + 10)

        passed = score >= 60

        feedback = ""
        if score >= 85:
            feedback = f"🌟 Outstanding answer! You accurately covered key concepts ({', '.join(matched_keywords)})."
        elif score >= 60:
            feedback = f"✅ Good understanding! You captured {len(matched_keywords)}/{len(required_keywords)} core concepts. Review the model answer to strengthen edge cases."
        else:
            feedback = f"⚠️ Incomplete answer. Missing key ideas such as: {', '.join([k for k in required_keywords if k not in matched_keywords][:3])}."

        xp_earned = int(score * 0.4)

        return {
            "question_id": question_id,
            "score": score,
            "passed": passed,
            "topic": question["topic"],
            "feedback": feedback,
            "keywords_covered": matched_keywords,
            "total_keywords": len(required_keywords),
            "model_answer": question["model_answer"],
            "xp_earned": xp_earned
        }

quiz_engine = QuizEngine()
