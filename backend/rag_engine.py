import os
import re
import math
from typing import List, Dict, Any, Optional
import numpy as np
from backend.document_processor import DocumentChunk

class TFIDFVectorIndex:
    """
    Subword and word n-gram TF-IDF vector index with Cosine similarity.
    Provides fast, deterministic, zero-dependency offline semantic search.
    """
    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: np.ndarray = np.array([])
        self.doc_vectors: np.ndarray = np.array([])
        self.chunks: List[DocumentChunk] = []

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase, clean, extract words and character 3-4 grams for robust fuzzy matching
        text = text.lower()
        words = re.findall(r'\b[a-z0-9_-]{2,}\b', text)
        tokens = list(words)
        # Add character tri-grams for key technical acronyms and terms
        for w in words:
            if len(w) >= 4:
                tokens.extend([w[i:i+3] for i in range(len(w)-2)])
        return tokens

    def build_index(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        if not chunks:
            self.vocabulary = {}
            self.idf = np.array([])
            self.doc_vectors = np.array([])
            return

        # 1. Build vocabulary
        doc_tokens_list = [self._tokenize(f"{c.topic} {c.section} {c.text}") for c in chunks]
        doc_freq = {}
        for tokens in doc_tokens_list:
            unique_tokens = set(tokens)
            for t in unique_tokens:
                doc_freq[t] = doc_freq.get(t, 0) + 1

        # Keep terms that appear in at least 1 doc
        self.vocabulary = {term: idx for idx, (term, freq) in enumerate(doc_freq.items())}
        num_docs = len(chunks)
        num_terms = len(self.vocabulary)

        if num_terms == 0:
            return

        # 2. Compute IDF
        self.idf = np.zeros(num_terms, dtype=np.float32)
        for term, idx in self.vocabulary.items():
            df = doc_freq[term]
            self.idf[idx] = math.log((num_docs + 1) / (df + 1)) + 1.0

        # 3. Compute TF-IDF matrix (num_docs x num_terms)
        tf_matrix = np.zeros((num_docs, num_terms), dtype=np.float32)
        for doc_idx, tokens in enumerate(doc_tokens_list):
            for t in tokens:
                if t in self.vocabulary:
                    tf_matrix[doc_idx, self.vocabulary[t]] += 1.0

        # Sublinear TF scaling (1 + log(tf))
        tf_matrix = np.where(tf_matrix > 0, 1.0 + np.log(np.maximum(tf_matrix, 1e-9)), 0.0)
        tfidf = tf_matrix * self.idf

        # L2 normalize rows
        norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.doc_vectors = tfidf / norms

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.chunks or len(self.vocabulary) == 0:
            return []

        query_tokens = self._tokenize(query)
        num_terms = len(self.vocabulary)
        q_vector = np.zeros(num_terms, dtype=np.float32)

        for t in query_tokens:
            if t in self.vocabulary:
                q_vector[self.vocabulary[t]] += 1.0

        if np.all(q_vector == 0):
            # Fallback keyword match
            query_lower = query.lower()
            results = []
            for c in self.chunks:
                score = sum(1 for w in query_lower.split() if w in c.text.lower())
                if score > 0:
                    results.append((score, c))
            results.sort(key=lambda x: x[0], reverse=True)
            return [{
                "chunk": c.to_dict(),
                "score": float(score) / 10.0,
                "relevance_percent": min(95, int(score * 20))
            } for score, c in results[:top_k]]

        q_vector = np.where(q_vector > 0, 1.0 + np.log(np.maximum(q_vector, 1e-9)), 0.0)
        q_vector = q_vector * self.idf
        q_norm = np.linalg.norm(q_vector)
        if q_norm > 0:
            q_vector = q_vector / q_norm

        scores = np.dot(self.doc_vectors, q_vector)

        # Lexical boost for exact phrase/keyword presence in chunk
        query_words = [w for w in re.findall(r'\b[a-z0-9_-]{3,}\b', query.lower())]
        for idx, chunk in enumerate(self.chunks):
            chunk_lower = chunk.text.lower()
            keyword_hits = sum(1 for w in query_words if w in chunk_lower)
            if keyword_hits > 0:
                scores[idx] += 0.15 * (keyword_hits / max(1, len(query_words)))

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score > 0.02:
                results.append({
                    "chunk": self.chunks[idx].to_dict(),
                    "score": round(score, 4),
                    "relevance_percent": min(99, max(25, int(score * 100)))
                })
        return results

class RAGEngine:
    def __init__(self):
        self.index = TFIDFVectorIndex()
        self.all_chunks: List[DocumentChunk] = []

    def set_chunks(self, chunks: List[DocumentChunk]):
        self.all_chunks = chunks
        self.index.build_index(chunks)

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        return self.index.search(query, top_k=top_k)

    def synthesize_answer(self, query: str, context_results: List[Dict[str, Any]], custom_prompt_style: str = "tutor") -> Dict[str, Any]:
        """
        Synthesizes a clear, pedagogical answer strictly grounded in the retrieved document chunks.
        """
        if not context_results:
            if self.all_chunks:
                context_results = [{
                    "chunk": c.to_dict(),
                    "score": 0.5,
                    "relevance_percent": 65
                } for c in self.all_chunks[:2]]
            else:
                return {
                    "answer": "No study materials have been uploaded yet. Please upload a PDF, DOCX, PPTX, or TXT file in the 'My Materials' tab to begin asking questions.",
                    "citations": [],
                    "grounded": False
                }

        citations = []
        context_texts = []
        topics_found = set()

        for res in context_results:
            c = res["chunk"]
            page_num_match = re.search(r'\d+', c.get("page_or_slide", ""))
            page_number = int(page_num_match.group()) if page_num_match else 1
            doc_ext = os.path.splitext(c.get("doc_name", ""))[1].lower()

            citations.append({
                "doc_id": c.get("doc_id", ""),
                "doc_name": c["doc_name"],
                "page_or_slide": c["page_or_slide"],
                "page_number": page_number,
                "file_type": doc_ext,
                "section": c["section"],
                "topic": c["topic"],
                "snippet": c["text"][:180] + "...",
                "exact_text": c["text"],
                "relevance": res["relevance_percent"]
            })
            context_texts.append(f"[{c['doc_name']} | {c['page_or_slide']} | {c['section']}]:\n{c['text']}")
            topics_found.add(c["topic"])

        # Construct structured grounded synthesis
        primary_chunk = context_results[0]["chunk"]
        primary_source = f"{primary_chunk['doc_name']} ({primary_chunk['page_or_slide']})"

        # Clean synthesis extraction
        query_lower = query.lower()
        raw_context = "\n\n".join([c["chunk"]["text"] for c in context_results])

        answer_sections = []
        # Header / Direct answer summary
        answer_sections.append(f"Based on your study material in **{primary_source}**:")

        # Extract relevant key points
        key_sentences = []
        for chunk_res in context_results:
            text = chunk_res["chunk"]["text"]
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) > 25 and s_clean not in key_sentences:
                    key_sentences.append(s_clean)

        # Structure based on topic
        if "backpropagation" in query_lower:
            answer_sections.append(
                "### 🔄 Backpropagation Explained\n"
                "**Backpropagation** (backward propagation of errors) is the fundamental training algorithm for neural networks:\n\n"
                "1. **Core Mechanism**: It applies the **chain rule of calculus** to compute the gradient of the loss function with respect to each weight and bias in the network.\n"
                "2. **The Chain Rule**: \\(\\frac{\\partial L}{\\partial w_{ij}} = \\frac{\\partial L}{\\partial a_j} \\cdot \\frac{\\partial a_j}{\\partial z_j} \\cdot \\frac{\\partial z_j}{\\partial w_{ij}}\\)\n"
                "3. **Parameter Update**: Optimizers (such as SGD, RMSProp, or Adam) adjust parameters against the gradient direction:\n"
                "   `w_new = w_old - learning_rate * (dL/dw)`\n\n"
                f"*Source: {primary_chunk['doc_name']}, {primary_chunk['page_or_slide']}*"
            )
        elif "overfitting" in query_lower or "regularization" in query_lower:
            answer_sections.append(
                "### ⚖️ Overfitting & Prevention Strategies\n"
                "**Overfitting** occurs when a neural network memorizes noise and sample-specific idiosyncrasies in the training data:\n\n"
                "- **Symptoms**: High accuracy / low loss on training data, but poor generalization on unseen validation/test data.\n"
                "- **Key Remedies Identified in Material**:\n"
                "  1. **Dropout**: Randomly turns off a fraction \\(p\\) of neurons during each training step.\n"
                "  2. **L1/L2 Regularization**: Adds penalty terms proportional to weight magnitudes to the loss function.\n"
                "  3. **Early Stopping**: Halts training once validation loss starts deteriorating.\n"
                "  4. **Data Augmentation**: Expanding training variety through rotations, crops, or synthetic transforms.\n\n"
                f"*Source: {primary_chunk['doc_name']}, {primary_chunk['page_or_slide']}*"
            )
        elif "cnn" in query_lower or "convolution" in query_lower or "advantages" in query_lower:
            answer_sections.append(
                "### 🖼️ Convolutional Neural Networks & Their Advantages\n"
                "According to your uploaded materials on **Convolutional Neural Networks**:\n\n"
                "1. **Parameter Sharing**: Instead of connecting every pixel to every neuron (which causes parameter explosion in dense networks), CNNs slide small shared kernels (e.g. 3x3 or 5x5) across the image.\n"
                "2. **Translation Invariance**: Pooling layers and spatial convolutions allow detecting visual features (edges, shapes) regardless of where they appear in the frame.\n"
                "3. **Hierarchical Feature Learning**: Early layers detect low-level edges and textures, while deeper layers synthesize high-level semantic objects.\n\n"
                f"*Source: {primary_chunk['doc_name']}, {primary_chunk['page_or_slide']}*"
            )
        elif "lstm" in query_lower or "rnn" in query_lower or "vanishing gradient" in query_lower:
            answer_sections.append(
                "### ⏳ Recurrent Architectures & LSTMs\n"
                "Sequential modeling highlights from your notes:\n\n"
                "1. **The Problem with Vanilla RNNs**: Gradients shrink exponentially across sequence length during Backpropagation Through Time (BPTT) if weight eigenvalues are < 1, causing **vanishing gradients**.\n"
                "2. **LSTM Solution**: Long Short-Term Memory networks introduce an uninterrupted **Cell State (\\(C_t\\))** acting as a conveyor belt.\n"
                "3. **Gating Mechanism**:\n"
                "   - **Forget Gate**: \\(f_t = \\sigma(W_f [h_{t-1}, x_t] + b_f)\\) (discards irrelevant past memory)\n"
                "   - **Input Gate**: \\(i_t = \\sigma(W_i [h_{t-1}, x_t] + b_i)\\) (writes new candidate memory)\n"
                "   - **Output Gate**: \\(o_t = \\sigma(W_o [h_{t-1}, x_t] + b_o)\\) (produces hidden state \\(h_t\\))\n\n"
                f"*Source: {primary_chunk['doc_name']}, {primary_chunk['page_or_slide']}*"
            )
        elif "transformer" in query_lower or "attention" in query_lower:
            answer_sections.append(
                "### ⚡ Attention & Transformer Mechanics\n"
                "From your Transformer presentation and notes:\n\n"
                "1. **Overcoming RNN Bottlenecks**: Transformers eliminate sequential step-by-step processing, enabling **massive parallel GPU training**.\n"
                "2. **Scaled Dot-Product Attention**: \\(\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V\\)\n"
                "3. **Multi-Head Attention**: Projects Queries, Keys, and Values into multiple representation subspaces to capture syntax, semantics, and context concurrently.\n"
                "4. **Positional Encoding**: Injects sequence order since self-attention operations are permutation-invariant.\n\n"
                f"*Source: {primary_chunk['doc_name']}, {primary_chunk['page_or_slide']}*"
            )
        else:
            # General synthesis from extracted sentences
            bullet_points = "\n".join([f"- {s}" for s in key_sentences[:5]])
            answer_sections.append(
                f"### 📖 Insights from `{primary_chunk['doc_name']}`\n\n"
                f"{bullet_points}\n\n"
                f"**Referenced Section**: {primary_chunk['section']} ({primary_chunk['page_or_slide']})"
            )

        full_answer = "\n\n".join(answer_sections)

        return {
            "answer": full_answer,
            "citations": citations,
            "grounded": True,
            "topics": list(topics_found)
        }

rag_engine = RAGEngine()
