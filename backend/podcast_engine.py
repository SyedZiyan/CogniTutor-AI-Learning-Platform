import uuid
import re
from typing import List, Dict, Any, Optional
from backend.rag_engine import rag_engine

class PodcastEngine:
    """
    AI Audio Overview & Deep-Dive Podcast Engine (NotebookLM Style).
    Converts student lecture notes and uploaded materials into an engaging
    two-host conversational podcast:
      - Host 1 (Alex): Lead Professor / Technical Architect (authoritative, clear, mathematical)
      - Host 2 (Jordan): Inquisitive Co-Host / Pragmatic Student (curious, witty, asks intuitive questions)
    """

    PRESET_PODCASTS = {
        "rnn": {
            "id": "pod_rnn_lstm",
            "topic": "Recurrent Neural Networks (RNN) & LSTMs",
            "title": "Deep Dive: Why Vanilla RNNs Break Down & How LSTMs Fixed Memory",
            "duration_minutes": 4.5,
            "estimated_seconds": 270,
            "cover_art": "gradient-rose",
            "hosts": [
                {"id": "alex", "name": "Dr. Alex Rivera", "role": "Lead Explainer", "voice_rate": 1.0, "pitch": 0.95},
                {"id": "jordan", "name": "Jordan Chen", "role": "Inquisitive Co-Host", "voice_rate": 1.05, "pitch": 1.1}
            ],
            "chapters": [
                {"timestamp": "0:00", "title": "The Sequential Memory Dilemma"},
                {"timestamp": "1:05", "title": "Backprop Through Time (BPTT) & Exponential Decay"},
                {"timestamp": "2:15", "title": "The 3 Gates of LSTM (Forget, Input, Output)"},
                {"timestamp": "3:30", "title": "The Highway Cell State Analogy"},
                {"timestamp": "4:00", "title": "Key Exam & Viva Takeaways"}
            ],
            "script": [
                {
                    "turn": 1,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Welcome to CogniTutor Audio Overviews! Today, Jordan and I are digging into sequential modeling—specifically, why standard vanilla RNNs struggle when sentences get long, and the ingenious engineering behind LSTMs."
                },
                {
                    "turn": 2,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "Honestly Alex, when I first saw RNNs in my notes, my immediate question was: if neural nets are universal approximators, why can't a normal feedforward network just handle sentences?"
                },
                {
                    "turn": 3,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "That's the fundamental trap! Feedforward networks assume all inputs are independent and identically distributed. But in language, if you say 'The clouds are in the...', the next word heavily depends on context from five words ago. Vanilla RNNs pass a hidden state vector $h_t$ from step to step like a baton in a relay race."
                },
                {
                    "turn": 4,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "Right, but then the notes talk about the dreaded 'vanishing gradient problem'. Why does passing a baton cause the network to completely forget what happened at step zero?"
                },
                {
                    "turn": 5,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Picture this: in Backpropagation Through Time, you repeatedly multiply by the weight matrix $W_{hh}$ and the derivative of tanh across dozens of timesteps. If the largest eigenvalue of that weight matrix is even slightly less than one—say 0.85—after twenty steps, 0.85 to the power of 20 shrinks to just 0.038. The gradient vanishes to virtually zero."
                },
                {
                    "turn": 6,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "So early words receive no updates! It's like whispering a message down a line of 50 people, but each person mumbles it quieter until the first person hears total silence."
                },
                {
                    "turn": 7,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Exactly right. And that's where Hochreiter and Schmidhuber stepped in with Long Short-Term Memory, or LSTM. Instead of forcing memory through non-linear squashing at every single step, they built an explicit conveyor belt: the cell state $C_t$."
                },
                {
                    "turn": 8,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "And this conveyor belt has three specialized security guards, right? The Forget Gate, the Input Gate, and the Output Gate."
                },
                {
                    "turn": 9,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Spot on. The Forget Gate uses a sigmoid activation to output numbers between 0 and 1. If it sees a period ending a sentence, it outputs zeros, discarding irrelevant subject pronouns. The Input Gate decides what fresh facts to add, and the Output Gate decides what parts of the cell state reach the visible hidden layer."
                },
                {
                    "turn": 10,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "And because information flows additively along the cell state $C_t$, gradients don't get multiplied into oblivion during backprop! That's why LSTMs can retain dependencies over 100+ timesteps."
                },
                {
                    "turn": 11,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "You nailed it. Here is your quick viva recap: Vanilla RNNs suffer from vanishing gradients due to repeated continuous matrix multiplications. LSTMs solve this using an additive linear cell state highway governed by three sigmoid-activated gating units."
                },
                {
                    "turn": 12,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "Awesome breakdown, Alex. Next up, we will look at how Transformers took this even further by eliminating recurrence entirely with Self-Attention. Until next time, keep studying smart!"
                }
            ],
            "key_takeaways": [
                "Vanilla RNNs fail on long sequences due to repeated Jacobian multiplication decaying gradients exponentially.",
                "LSTMs introduce a linear cell state highway ($C_t$) with additive updates.",
                "Forget Gate ($f_t = \\sigma(W_f x + b)$) discards stale historical context.",
                "Input Gate & Candidate State inject new candidate memory.",
                "Output Gate regulates visible prediction hidden state ($h_t$)."
            ]
        },
        "cnn": {
            "id": "pod_cnn_vision",
            "topic": "Convolutional Neural Networks (CNN)",
            "title": "Deep Dive: The Computer Vision Revolution—Convolutions, Receptive Fields & ResNet",
            "duration_minutes": 4.2,
            "estimated_seconds": 250,
            "cover_art": "gradient-blue",
            "hosts": [
                {"id": "alex", "name": "Dr. Alex Rivera", "role": "Lead Explainer", "voice_rate": 1.0, "pitch": 0.95},
                {"id": "jordan", "name": "Jordan Chen", "role": "Inquisitive Co-Host", "voice_rate": 1.05, "pitch": 1.1}
            ],
            "chapters": [
                {"timestamp": "0:00", "title": "The 200,000 Parameter Disaster"},
                {"timestamp": "1:00", "title": "Kernels, Receptive Fields & Stride"},
                {"timestamp": "2:10", "title": "Translation Invariance & Pooling"},
                {"timestamp": "3:20", "title": "He et al. ResNet & Residual Skip Connections"}
            ],
            "script": [
                {
                    "turn": 1,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Welcome to CogniTutor Audio Overviews! Today, Jordan and I are breaking down Convolutional Neural Networks, or CNNs—the architecture that launched the modern deep learning boom in 2012."
                },
                {
                    "turn": 2,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "Alex, let's start with the classic interview question: why can't we just flatten a 256 by 256 pixel image and feed it directly into a standard multilayer perceptron?"
                },
                {
                    "turn": 3,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Because it causes immediate parameter explosion! A 256 by 256 image with 3 color channels is nearly 200,000 numbers. If your first hidden layer has 1,000 neurons, you are asking the network to learn 200 million weights on step one! It will massively overfit and crash your GPU memory."
                },
                {
                    "turn": 4,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "Plus, when you flatten an image into a 1D vector, you completely destroy spatial neighborhood relationships. A pixel has no idea what is above or below it."
                },
                {
                    "turn": 5,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Exactly. Yann LeCun resolved this with two brilliant insights: Local Receptive Fields and Parameter Sharing. Instead of full connectivity, we slide a compact 3x3 kernel across the image. The same nine weights are shared across every single spatial position."
                },
                {
                    "turn": 6,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "And that gives us Translation Invariance! Whether a cat is in the top-left corner or bottom-right corner, the edge detector filter activates identically. Then Max Pooling condenses the feature map."
                },
                {
                    "turn": 7,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "And when networks got deeper—like 50 to 152 layers in ResNet—gradients started vanishing again. Kaiming He introduced residual skip connections: $F(x) + x$. The identity shortcut allows gradients to flow directly back during training."
                },
                {
                    "turn": 8,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "Brilliant. Bottom line for exams: CNNs win through Parameter Sharing, Local Receptive Fields, and Translation Invariance. Thanks for tuning into CogniTutor!"
                }
            ],
            "key_takeaways": [
                "Dense networks fail on images due to parameter explosion and loss of 2D spatial adjacency.",
                "Parameter Sharing: A single small kernel (e.g. 3x3) slides across the entire image.",
                "Translation Invariance: Features are detected regardless of their location in the frame.",
                "Max Pooling reduces spatial dimension while retaining dominant activations.",
                "ResNet skip connections ($F(x) + x$) prevent vanishing gradients in very deep architectures."
            ]
        },
        "transformers": {
            "id": "pod_transformers_attention",
            "topic": "Transformers & Attention Mechanisms",
            "title": "Deep Dive: Attention Is All You Need—Queries, Keys, Values & Scaled Dot Product",
            "duration_minutes": 5.0,
            "estimated_seconds": 300,
            "cover_art": "gradient-amber",
            "hosts": [
                {"id": "alex", "name": "Dr. Alex Rivera", "role": "Lead Explainer", "voice_rate": 1.0, "pitch": 0.95},
                {"id": "jordan", "name": "Jordan Chen", "role": "Inquisitive Co-Host", "voice_rate": 1.05, "pitch": 1.1}
            ],
            "chapters": [
                {"timestamp": "0:00", "title": "The Death of Sequential Recurrence"},
                {"timestamp": "1:10", "title": "Queries, Keys & Values: The Library Analogy"},
                {"timestamp": "2:30", "title": "Why We Scale by Square Root of d_k"},
                {"timestamp": "3:45", "title": "Multi-Head Attention & Positional Encoding"}
            ],
            "script": [
                {
                    "turn": 1,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Welcome to CogniTutor Audio Overviews! In this episode, Jordan and I are examining the landmark 2017 Google paper 'Attention Is All You Need'—the architecture that underpins GPT-4, Gemini, Claude, and every modern foundation model."
                },
                {
                    "turn": 2,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "Alex, before 2017, everyone thought recurrence was mandatory for language. What was the seismic shift that allowed Transformers to discard recurrent loops completely?"
                },
                {
                    "turn": 3,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Parallelization! In an RNN, token 50 cannot be calculated until token 49 finishes. GPUs hate that; they thrive on massive matrix multiplications in parallel. Transformers process all 1,000 words in a prompt simultaneously using Self-Attention."
                },
                {
                    "turn": 4,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "Can you explain Queries, Keys, and Values in plain English? The formulas look intimidating in the slides."
                },
                {
                    "turn": 5,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Think of YouTube or a library! The Query $Q$ is what you type into the search bar: say, 'machine learning'. The Keys $K$ are the video titles on the server. We compute the dot product between your query and every title to see what matches best. That gives attention weights. Then we retrieve the actual video content—the Values $V$!"
                },
                {
                    "turn": 6,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "That's a fantastic analogy. And why the scaling factor $\\sqrt{d_k}$ in the denominator?"
                },
                {
                    "turn": 7,
                    "speaker": "alex",
                    "speaker_name": "Dr. Alex",
                    "text": "Without dividing by $\\sqrt{d_k}$, as the embedding dimension grows large, the dot products explode in magnitude. Large inputs push the Softmax function into saturation regions with tiny gradients, destroying training stability."
                },
                {
                    "turn": 8,
                    "speaker": "jordan",
                    "speaker_name": "Jordan",
                    "text": "And Multi-Head Attention lets the model focus on syntax in one head, pronouns in another, and semantic relations in a third. What a revolutionary design. Thanks for breaking it down, Alex!"
                }
            ],
            "key_takeaways": [
                "Transformers enable full GPU parallelization by replacing recurrence with self-attention.",
                "Attention formula: $\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$.",
                "Division by $\\sqrt{d_k}$ prevents dot products from pushing Softmax into saturated zero-gradient zones.",
                "Multi-Head Attention allows attending to information at different representation subspaces.",
                "Positional Encoding restores order information discarded by permutation-invariant attention."
            ]
        }
    }

    @classmethod
    def get_all_podcasts(cls) -> List[Dict[str, Any]]:
        """Return list of all available podcast overviews."""
        return list(cls.PRESET_PODCASTS.values())

    @classmethod
    def get_podcast_by_id(cls, podcast_id: str) -> Optional[Dict[str, Any]]:
        for pod in cls.PRESET_PODCASTS.values():
            if pod["id"] == podcast_id:
                return pod
        return None

    @classmethod
    def generate_podcast_overview(cls, topic: Optional[str] = None, doc_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Dynamically synthesize a dual-host conversational podcast grounded in uploaded materials.
        """
        topic_lower = (topic or "").lower()

        # If matching a preset core topic, return curated deep dive
        if "rnn" in topic_lower or "lstm" in topic_lower or "sequential" in topic_lower:
            return cls.PRESET_PODCASTS["rnn"]
        elif "cnn" in topic_lower or "vision" in topic_lower or "convolution" in topic_lower:
            return cls.PRESET_PODCASTS["cnn"]
        elif "transformer" in topic_lower or "attention" in topic_lower:
            return cls.PRESET_PODCASTS["transformers"]

        # Otherwise, dynamically retrieve context from student's notes
        query = topic if topic and topic.strip() else "key deep learning fundamentals and concepts"
        retrieved = rag_engine.retrieve(query, top_k=4)

        if not retrieved:
            # Fallback to RNN deep dive
            return cls.PRESET_PODCASTS["rnn"]

        primary_chunk = retrieved[0]["chunk"]
        primary_topic = primary_chunk.get("topic", "Course Concepts")
        doc_name = primary_chunk.get("doc_name", "Uploaded Notes")
        snippets = [r["chunk"]["text"][:220] for r in retrieved]

        generated_id = f"pod_custom_{uuid.uuid4().hex[:8]}"
        title = f"Deep Dive: Master {primary_topic} from {doc_name}"

        script = [
            {
                "turn": 1,
                "speaker": "alex",
                "speaker_name": "Dr. Alex",
                "text": f"Welcome to CogniTutor Audio Overviews! Today Jordan and I are breaking down your uploaded notes on '{primary_topic}', straight from {doc_name}."
            },
            {
                "turn": 2,
                "speaker": "jordan",
                "speaker_name": "Jordan",
                "text": f"Dr. Alex, reviewing these notes, the core concept centers around {primary_topic}. What is the most critical intuition a student needs to grasp first?"
            },
            {
                "turn": 3,
                "speaker": "alex",
                "speaker_name": "Dr. Alex",
                "text": f"The key insight is right here in section {primary_chunk.get('section', 'Core')}: {snippets[0].replace(chr(10), ' ')}"
            },
            {
                "turn": 4,
                "speaker": "jordan",
                "speaker_name": "Jordan",
                "text": "That makes so much sense! When students encounter this in exams, what is the #1 mistake they usually make?"
            },
            {
                "turn": 5,
                "speaker": "alex",
                "speaker_name": "Dr. Alex",
                "text": f"They often forget how the components interact during training. Here is how your notes explain it: {snippets[1] if len(snippets) > 1 else 'Always verify your loss function formulations and regularization parameters.'}"
            },
            {
                "turn": 6,
                "speaker": "jordan",
                "speaker_name": "Jordan",
                "text": "Got it! So keep an eye on gradient updates and make sure data representations match what the model expects."
            },
            {
                "turn": 7,
                "speaker": "alex",
                "speaker_name": "Dr. Alex",
                "text": f"Precisely. In summary: master the mathematical grounding, understand why each layer exists, and test your intuition on our practice quiz!"
            },
            {
                "turn": 8,
                "speaker": "jordan",
                "speaker_name": "Jordan",
                "text": "Thanks for tuning into CogniTutor Audio Overviews. Check out the practice quiz tab to test your mastery!"
            }
        ]

        return {
            "id": generated_id,
            "topic": primary_topic,
            "title": title,
            "duration_minutes": 3.8,
            "estimated_seconds": 230,
            "cover_art": "gradient-indigo",
            "hosts": [
                {"id": "alex", "name": "Dr. Alex Rivera", "role": "Lead Explainer", "voice_rate": 1.0, "pitch": 0.95},
                {"id": "jordan", "name": "Jordan Chen", "role": "Inquisitive Co-Host", "voice_rate": 1.05, "pitch": 1.1}
            ],
            "chapters": [
                {"timestamp": "0:00", "title": f"Introduction to {primary_topic}"},
                {"timestamp": "1:00", "title": "Core Theoretical Foundation"},
                {"timestamp": "2:15", "title": "Practical Mechanisms & Implementation"},
                {"timestamp": "3:10", "title": "Exam Traps & Final Synthesis"}
            ],
            "script": script,
            "key_takeaways": [
                f"Core foundations of {primary_topic} retrieved directly from {doc_name}.",
                "Understand the operational mechanics and why alternatives fail.",
                "Review the key mathematical equations in your study notes.",
                "Complete the practice quiz for this topic to lock in your XP."
            ]
        }

podcast_engine = PodcastEngine()
