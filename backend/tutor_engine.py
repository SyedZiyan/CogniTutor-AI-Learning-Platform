import os
from typing import Dict, Any, List, Optional
import httpx
from backend.rag_engine import rag_engine
from backend.config import settings

class TutorEngine:
    """
    Intelligent AI Tutor and Multi-Level Doubt Solver.
    Supports RAG grounded retrieval, LLM API routing (OpenAI, Gemini, Ollama),
    and adaptive 3-tier cognitive explanations (Beginner, Intermediate, Advanced).
    """

    EXPLANATION_TEMPLATES = {
        "lstm": {
            "title": "Long Short-Term Memory (LSTM) Networks",
            "beginner": {
                "analogy": "The Smart Notebook Analogy",
                "explanation": (
                    "Imagine you are reading a long mystery novel and keeping notes in a small diary:\n\n"
                    "1. **Forget Gate (The Eraser)**: When a character leaves the story or turns out to be irrelevant, you erase their details to save space.\n"
                    "2. **Input Gate (The Pen)**: When a key new clue is discovered, you write it down carefully into your diary.\n"
                    "3. **Cell State (The Notebook)**: This is the actual diary that travels with you from the first chapter to the end without being altered unless you decide to erase or write.\n"
                    "4. **Output Gate (The Answer)**: When someone asks you 'Who is the prime suspect right now?', you look at your diary and speak out only the most relevant summary.\n\n"
                    "Why it matters: Standard RNNs have severe amnesia—by chapter 20, they forget chapter 1! LSTMs keep the notebook safe so memory never fades."
                )
            },
            "intermediate": {
                "title": "Technical Mechanics & Gating Equations",
                "explanation": (
                    "LSTMs mitigate the vanishing gradient problem in Backpropagation Through Time (BPTT) by providing an additive error carousel through the **Cell State \\(C_t\\)**.\n\n"
                    "**The Mathematical Formulations:**\n\n"
                    "$$\\begin{aligned}\n"
                    "f_t &= \\sigma(W_f \\cdot [h_{t-1}, x_t] + b_f) \\quad &\\text{(Forget Gate: 0 to 1 scaling)} \\\\\n"
                    "i_t &= \\sigma(W_i \\cdot [h_{t-1}, x_t] + b_i) \\quad &\\text{(Input Gate: write filter)} \\\\\n"
                    "\\tilde{C}_t &= \\tanh(W_c \\cdot [h_{t-1}, x_t] + b_c) \\quad &\\text{(Candidate new state)} \\\\\n"
                    "C_t &= f_t \\odot C_{t-1} + i_t \\odot \\tilde{C}_t \\quad &\\text{(Cell state additive update)} \\\\\n"
                    "o_t &= \\sigma(W_o \\cdot [h_{t-1}, x_t] + b_o) \\quad &\\text{(Output Gate)} \\\\\n"
                    "h_t &= o_t \\odot \\tanh(C_t) \\quad &\\text{(Updated hidden state)}\n"
                    "\\end{aligned}$$\n\n"
                    "**Key Takeaways:**\n"
                    "- The update to \\(C_t\\) is **linear and additive**, which allows gradients \\(\\frac{\\partial C_t}{\\partial C_{t-1}} \\approx f_t\\) to flow backwards across hundreds of time steps without exponentially decaying to zero."
                )
            },
            "advanced": {
                "title": "Architecture, Jacobian Analysis & PyTorch Implementation",
                "explanation": (
                    "**Gradient Highway & Vanishing Gradient Resolution:**\n"
                    "In vanilla RNNs, \\(\\frac{\\partial h_T}{\\partial h_t} = \\prod_{k=t+1}^T W^T \\text{diag}(1 - h_k^2)\\). If singular values of \\(W\\) are \\(< 1\\), this geometric product vanishes.\n\n"
                    "In LSTMs, the gradient of the loss with respect to cell state \\(C_t\\) contains the term:\n"
                    "$$\\frac{\\partial C_t}{\\partial C_{t-1}} = f_t$$\n"
                    "If the network learns to keep the forget gate \\(f_t \\approx 1\\), the gradient flows backward indefinitely with minimal decay!\n\n"
                    "**PyTorch Production Implementation:**\n"
                    "```python\n"
                    "import torch\n"
                    "import torch.nn as nn\n\n"
                    "class SequenceClassifier(nn.Module):\n"
                    "    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers=2, bidirectional=True):\n"
                    "        super().__init__()\n"
                    "        self.embedding = nn.Embedding(vocab_size, embed_dim)\n"
                    "        self.lstm = nn.LSTM(\n"
                    "            input_size=embed_dim,\n"
                    "            hidden_size=hidden_dim,\n"
                    "            num_layers=num_layers,\n"
                    "            batch_first=True,\n"
                    "            bidirectional=bidirectional,\n"
                    "            dropout=0.2\n"
                    "        )\n"
                    "        directions = 2 if bidirectional else 1\n"
                    "        self.fc = nn.Linear(hidden_dim * directions, 2)\n\n"
                    "    def forward(self, x):\n"
                    "        # x shape: [batch_size, seq_len]\n"
                    "        embeds = self.embedding(x)\n"
                    "        # lstm_out shape: [batch_size, seq_len, hidden_dim * directions]\n"
                    "        lstm_out, (hn, cn) = self.lstm(embeds)\n"
                    "        # Concatenate forward and backward final hidden states\n"
                    "        if self.lstm.bidirectional:\n"
                    "            last_hidden = torch.cat((hn[-2], hn[-1]), dim=1)\n"
                    "        else:\n"
                    "            last_hidden = hn[-1]\n"
                    "        return self.fc(last_hidden)\n"
                    "```"
                )
            }
        },
        "backpropagation": {
            "title": "Backpropagation & Gradient Descent",
            "beginner": {
                "analogy": "The Temperature Dial Analogy",
                "explanation": (
                    "Imagine you are taking a shower in a strange hotel with 10 different knobs that control water temperature.\n\n"
                    "1. You turn on the shower, and the water comes out ice cold (that's your **Error / Loss**).\n"
                    "2. You gently tweak each knob a millimeter to see which ones make it warmer and which make it colder (that's calculating the **Gradient / Derivative**).\n"
                    "3. Once you know which knob is responsible for what, you turn all of them in the exact direction that brings the water to the perfect warm temperature (that's **Parameter Update with Learning Rate**).\n\n"
                    "Backpropagation simply traces backwards from the final temperature error to determine how much each individual knob contributed to the mistake."
                )
            },
            "intermediate": {
                "title": "Chain Rule & Computational Graph",
                "explanation": (
                    "Backpropagation applies the **multivariate chain rule** through a reverse topological traversal of the network's computational graph.\n\n"
                    "For neuron \\(j\\) in layer \\(l\\) with activation \\(a_j = \\sigma(z_j)\\) where \\(z_j = \\sum_i w_{ji} a_i + b_j\\):\n\n"
                    "$$\\delta_j = \\frac{\\partial L}{\\partial z_j} = \\sum_k \\delta_k w_{kj} \\cdot \\sigma'(z_j)$$\n\n"
                    "The parameter gradients are:\n"
                    "$$\\frac{\\partial L}{\\partial w_{ji}} = \\delta_j \\cdot a_i, \\quad \\frac{\\partial L}{\\partial b_j} = \\delta_j$$\n\n"
                    "Modern optimizers update weights via:\n"
                    "- **SGD**: \\(w \\leftarrow w - \\eta \\nabla L\\)\n"
                    "- **Adam**: Maintains first moment \\(m_t\\) (momentum) and second moment \\(v_t\\) (uncentered variance) to scale step sizes per parameter."
                )
            },
            "advanced": {
                "title": "Vectorized Autograd & Custom PyTorch Backward Hook",
                "explanation": (
                    "In batched tensor form, backpropagation computes Vector-Jacobian Products (VJPs) rather than full Jacobians to preserve \\(O(N)\\) memory efficiency.\n\n"
                    "```python\n"
                    "import torch\n\n"
                    "class LinearWithAutograd(torch.autograd.Function):\n"
                    "    @staticmethod\n"
                    "    def forward(ctx, x, w, b):\n"
                    "        # ctx saves tensors for the backward pass\n"
                    "        ctx.save_for_backward(x, w, b)\n"
                    "        return x.mm(w.t()) + b\n\n"
                    "    @staticmethod\n"
                    "    def backward(ctx, grad_output):\n"
                    "        # grad_output is dL/dy of shape [batch, out_features]\n"
                    "        x, w, b = ctx.saved_tensors\n"
                    "        grad_x = grad_output.mm(w)          # dL/dx = (dL/dy) * W\n"
                    "        grad_w = grad_output.t().mm(x)      # dL/dW = (dL/dy)^T * X\n"
                    "        grad_b = grad_output.sum(dim=0)     # dL/db = sum along batch\n"
                    "        return grad_x, grad_w, grad_b\n"
                    "```"
                )
            }
        },
        "cnn": {
            "title": "Convolutional Neural Networks (CNNs)",
            "beginner": {
                "analogy": "The Flashlight & Stamp Analogy",
                "explanation": (
                    "Imagine you are inspecting a large jigsaw puzzle in the dark with a small square magnifying glass or flashlight:\n\n"
                    "1. **Convolution (Sliding Flashlight)**: You move your small lens across the puzzle, one patch at a time, looking specifically for cat ears or whiskers.\n"
                    "2. **Feature Map**: Every time your lens spots a cat ear, you place a green sticker on a map.\n"
                    "3. **Pooling (Squinting from a distance)**: You step back and summarize the green stickers so you don't care whether the cat is sitting on the left or right side of the picture.\n\n"
                    "Instead of trying to memorize millions of individual pixels, CNNs recognize modular patterns that make up the image!"
                )
            },
            "intermediate": {
                "title": "Kernels, Stride, Padding & Spatial Dimensions",
                "explanation": (
                    "A Convolutional layer applies cross-correlation using learnable kernels \\(K \\in \\mathbb{R}^{C_{in} \\times k_h \\times k_w}\\).\n\n"
                    "**Output Spatial Dimension Formula:**\n"
                    "$$W_{out} = \\left\\lfloor \\frac{W_{in} - K_w + 2P}{S} \\right\\rfloor + 1$$\n"
                    "where \\(P\\) is zero-padding and \\(S\\) is stride.\n\n"
                    "**Key Concepts:**\n"
                    "- **Receptive Field**: The area of the raw input image that affects a specific neuron's activation.\n"
                    "- **Max Pooling**: \\(2 \\times 2\\) with stride 2 cuts spatial resolution in half, providing translation invariance and reducing compute."
                )
            },
            "advanced": {
                "title": "ResNet Residual Mappings & Receptive Field Arithmetic",
                "explanation": (
                    "As networks deepen, accuracy saturates and degrades rapidly due to optimization difficulties rather than overfitting.\n\n"
                    "**Residual Learning (He et al., 2015):**\n"
                    "Instead of forcing stacked layers to fit an underlying mapping \\(\\mathcal{H}(x)\\), ResNet fits residual mapping \\(\\mathcal{F}(x) = \\mathcal{H}(x) - x\\), optimizing \\(\\mathcal{F}(x) + x\\).\n\n"
                    "$$\\frac{\\partial \\mathcal{E}}{\\partial x} = \\frac{\\partial \\mathcal{E}}{\\partial y} \\left( \\frac{\\partial \\mathcal{F}}{\\partial x} + \\mathbf{I} \\right)$$\n"
                    "Because of the identity term \\(\\mathbf{I}\\), gradients can flow back directly to early layers even if \\(\\frac{\\partial \\mathcal{F}}{\\partial x} \\approx 0\\), completely eliminating degradation in 152+ layer models."
                )
            }
        },
        "transformers": {
            "title": "Transformers & Multi-Head Self-Attention",
            "beginner": {
                "analogy": "The Cocktail Party Analogy",
                "explanation": (
                    "Imagine you are at a crowded networking cocktail party with 20 people:\n\n"
                    "1. **Query (What I want to know)**: You are looking for an expert on Python.\n"
                    "2. **Key (Everyone's nametag)**: Each person has a badge stating their specialty (e.g., 'Finance', 'Python', 'Marketing').\n"
                    "3. **Attention Score**: You compare your Query to every nametag. The Python badge lights up with a 99% match!\n"
                    "4. **Value (The actual knowledge)**: You listen closely to the words spoken by the Python expert and ignore the background chatter.\n\n"
                    "Every word in a sentence looks at every other word at the exact same moment to understand who it belongs to!"
                )
            },
            "intermediate": {
                "title": "Scaled Dot-Product & Multi-Head Attention",
                "explanation": (
                    "Transformers discard recurrent loops in favor of pure self-attention (Vaswani et al., 2017):\n\n"
                    "$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left( \\frac{Q K^T}{\\sqrt{d_k}} \\right) V$$\n\n"
                    "**Multi-Head Attention** computes \\(h\\) parallel attention heads:\n"
                    "$$\\text{MHA}(Q, K, V) = \\text{Concat}(\\text{head}_1, \\dots, \\text{head}_h) W^O$$\n"
                    "where \\(\\text{head}_i = \\text{Attention}(Q W_i^Q, K W_i^K, V W_i^V)\\).\n\n"
                    "**Why divide by \\(\\sqrt{d_k}\\)?** For large dimensions \\(d_k\\), dot products grow large, driving softmax into regions with near-zero gradients. Scaling maintains unit variance."
                )
            },
            "advanced": {
                "title": "FlashAttention, KV Cache & Rotary Positional Embeddings (RoPE)",
                "explanation": (
                    "Modern LLMs (Llama 3, Mistral, GPT-4) employ major architectural enhancements over the original 2017 Transformer:\n\n"
                    "1. **FlashAttention-2**: Rearranges attention computation via tiling to minimize GPU HBM memory read/write bottlenecks, achieving near-theoretical TFLOPs throughput.\n"
                    "2. **KV Caching**: During autoregressive decoding, keys and values of previous tokens are cached to convert \\(O(N^2)\\) generation step computation to \\(O(N)\\).\n"
                    "3. **RoPE (Rotary Position Embedding)**: Multiplies representations by complex rotation matrices \\(R_{\\Theta, m}^d\\), preserving relative positional distance cleanly across arbitrary context lengths."
                )
            }
        },
        "overfitting": {
            "title": "Overfitting, Underfitting & Regularization",
            "beginner": {
                "analogy": "The Practice Exam Memorization Analogy",
                "explanation": (
                    "Imagine a student studying for a driving test:\n\n"
                    "- **Overfitting**: The student memorizes every exact question on page 4 of the practice book (e.g. 'Question 3 answer is option B'). When taking the actual real-world driving test, they crash because the real world has different questions!\n"
                    "- **Underfitting**: The student barely opened the book at all and doesn't even know what a stop sign means.\n"
                    "- **Good Generalization**: The student understands the rules of the road and drives safely anywhere.\n\n"
                    "Regularization techniques like Dropout force the student to think independently instead of relying on memorization tricks."
                )
            },
            "intermediate": {
                "title": "Bias-Variance Trade-off & Regularization Mathematics",
                "explanation": (
                    "Expected prediction error decomposes into:\n"
                    "$$\\mathbb{E}[(y - \\hat{f}(x))^2] = \\text{Bias}[\\hat{f}(x)]^2 + \\text{Var}[\\hat{f}(x)] + \\sigma^2$$\n\n"
                    "**Regularization Strategies:**\n"
                    "1. **L2 Regularization (Ridge / Weight Decay)**: Adds penalty \\(\\frac{\\lambda}{2} \\sum w_i^2\\) to loss. Gradient update becomes \\(w \\leftarrow w(1 - \\eta \\lambda) - \\eta \\nabla L\\).\n"
                    "2. **L1 Regularization (Lasso)**: Adds penalty \\(\\lambda \\sum |w_i|\\), promoting sparse weights (feature selection).\n"
                    "3. **Dropout (Srivastava et al., 2014)**: At training, each neuron is retained with probability \\(p\\). At test time, weights are scaled by \\(p\\)."
                )
            },
            "advanced": {
                "title": "Weight Decay in AdamW & Double Descent Phenomenon",
                "explanation": (
                    "**L2 Regularization vs Weight Decay in Adam:**\n"
                    "Loshchilov & Hutter (2019) demonstrated that in adaptive optimizers like Adam, \\(L_2\\) penalty is scaled inversely by gradient variance \\(\\sqrt{v_t}\\), causing weights with large gradients to be regularized less than intended. **AdamW** decouples weight decay directly from gradient updates:\n\n"
                    "$$\\theta_{t+1} = \\theta_t - \\eta \\lambda \\theta_t - \\frac{\\eta}{\\sqrt{\\hat{v}_t} + \\epsilon} \\hat{m}_t$$\n\n"
                    "**Modern Deep Learning: The Double Descent Curve:**\n"
                    "In highly over-parameterized regimes where parameters \\(P \\gg N\\), test error spikes near interpolation threshold, then decreases again due to inductive bias of SGD finding minimum-norm solutions."
                )
            }
        }
    }

    @classmethod
    def answer_query(cls, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        RAG AI Tutor Answer generation with document citations.
        """
        retrieval_results = rag_engine.retrieve(query, top_k=top_k)
        response = rag_engine.synthesize_answer(query, retrieval_results, custom_prompt_style="tutor")
        return response

    @classmethod
    def solve_doubt_multilevel(cls, topic_or_question: str) -> Dict[str, Any]:
        """
        AI Doubt Solver with 3 adaptive levels: Beginner, Intermediate, Advanced.
        """
        query_clean = topic_or_question.lower()
        matched_key = None

        for key in cls.EXPLANATION_TEMPLATES.keys():
            if key in query_clean:
                matched_key = key
                break

        # Fallback keyword matching
        if not matched_key:
            if "gradient" in query_clean or "backprop" in query_clean or "weight" in query_clean:
                matched_key = "backpropagation"
            elif "conv" in query_clean or "image" in query_clean or "vision" in query_clean:
                matched_key = "cnn"
            elif "seq" in query_clean or "rnn" in query_clean or "memory" in query_clean:
                matched_key = "lstm"
            elif "self-attention" in query_clean or "bert" in query_clean or "gpt" in query_clean:
                matched_key = "transformers"
            elif "regulariz" in query_clean or "dropout" in query_clean or "overfit" in query_clean:
                matched_key = "overfitting"
            else:
                matched_key = "lstm" # default benchmark

        template = cls.EXPLANATION_TEMPLATES[matched_key]

        # Also retrieve relevant citations from uploaded documents
        citations = rag_engine.retrieve(topic_or_question, top_k=2)

        return {
            "topic": template["title"],
            "key": matched_key,
            "beginner": template["beginner"],
            "intermediate": template["intermediate"],
            "advanced": template["advanced"],
            "citations": [c["chunk"] for c in citations]
        }

tutor_engine = TutorEngine()
