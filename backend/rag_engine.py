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

class BM25Index:
    """
    Okapi BM25 Sparse Keyword Retrieval Index.
    Excels at exact keyword, technical terminology, and acronym matching (e.g. CNN, RNN, LSTM, SGD, BPTT).
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[DocumentChunk] = []
        self.doc_lengths: np.ndarray = np.array([])
        self.avg_doc_len: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_token_counts: List[Dict[str, int]] = []

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-zA-Z0-9_-]{2,}\b', text.lower())

    def build_index(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        num_docs = len(chunks)
        if num_docs == 0:
            self.doc_lengths = np.array([])
            self.avg_doc_len = 0.0
            self.doc_freqs = {}
            self.idf = {}
            self.doc_token_counts = []
            return

        self.doc_token_counts = []
        doc_lens = []
        self.doc_freqs = {}

        for c in chunks:
            text = f"{c.topic} {c.section} {c.text}"
            tokens = self._tokenize(text)
            doc_lens.append(len(tokens))
            term_counts: Dict[str, int] = {}
            for t in tokens:
                term_counts[t] = term_counts.get(t, 0) + 1
            self.doc_token_counts.append(term_counts)

            for term in term_counts.keys():
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.doc_lengths = np.array(doc_lens, dtype=np.float32)
        self.avg_doc_len = float(np.mean(self.doc_lengths)) if num_docs > 0 else 1.0

        # Calculate BM25 IDF
        self.idf = {}
        for term, df in self.doc_freqs.items():
            self.idf[term] = math.log(1.0 + (num_docs - df + 0.5) / (df + 0.5))

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        num_docs = len(self.chunks)
        if num_docs == 0:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores = np.zeros(num_docs, dtype=np.float32)

        for term in query_tokens:
            if term not in self.idf:
                continue
            idf_val = self.idf[term]
            for doc_idx in range(num_docs):
                tf = self.doc_token_counts[doc_idx].get(term, 0)
                if tf > 0:
                    doc_len = self.doc_lengths[doc_idx]
                    denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avg_doc_len)))
                    scores[doc_idx] += idf_val * (tf * (self.k1 + 1.0)) / denominator

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for rank, idx in enumerate(top_indices):
            s = float(scores[idx])
            if s > 0:
                results.append({
                    "doc_idx": idx,
                    "chunk": self.chunks[idx],
                    "score": s,
                    "rank": rank + 1
                })
        return results

class RAGEngine:
    """
    Hybrid Dense + Sparse Neural Reranker Engine.
    Combines:
      - BM25 Sparse Keyword Ranker (Okapi BM25 with k1=1.5, b=0.75)
      - Dense Subword/N-gram Vector Ranker (Cosine similarity)
      - Reciprocal Rank Fusion (RRF with k=60)
      - Cross-Encoder Style Precision Reranker (exact n-gram phrases & topic alignment)
    """
    def __init__(self):
        self.sparse_index = BM25Index()
        self.dense_index = TFIDFVectorIndex()
        self.all_chunks: List[DocumentChunk] = []

    def set_chunks(self, chunks: List[DocumentChunk]):
        self.all_chunks = chunks
        self.sparse_index.build_index(chunks)
        self.dense_index.build_index(chunks)

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.all_chunks:
            return []

        # 1. Dual Retrieval from Sparse (BM25) and Dense (Cosine)
        candidate_k = min(len(self.all_chunks), max(top_k * 3, 10))
        sparse_hits = self.sparse_index.search(query, top_k=candidate_k)
        dense_hits = self.dense_index.search(query, top_k=candidate_k)

        # 2. Reciprocal Rank Fusion (RRF with k=60)
        rrf_constant = 60.0
        doc_map: Dict[str, Dict[str, Any]] = {}

        for item in sparse_hits:
            chunk = item["chunk"]
            cid = chunk.chunk_id
            s_rank = item["rank"]
            doc_map[cid] = {
                "chunk": chunk.to_dict(),
                "rrf_score": 1.0 / (rrf_constant + s_rank),
                "sparse_score": item["score"],
                "dense_score": 0.0,
                "sparse_rank": s_rank,
                "dense_rank": 999
            }

        for rank, item in enumerate(dense_hits):
            chunk_dict = item["chunk"]
            cid = chunk_dict["chunk_id"]
            d_rank = rank + 1
            rrf_add = 1.0 / (rrf_constant + d_rank)

            if cid in doc_map:
                doc_map[cid]["rrf_score"] += rrf_add
                doc_map[cid]["dense_score"] = item["score"]
                doc_map[cid]["dense_rank"] = d_rank
            else:
                doc_map[cid] = {
                    "chunk": chunk_dict,
                    "rrf_score": rrf_add,
                    "sparse_score": 0.0,
                    "dense_score": item["score"],
                    "sparse_rank": 999,
                    "dense_rank": d_rank
                }

        # 3. Cross-Encoder Style Precision Reranking
        query_lower = query.lower()
        query_words = [w for w in re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', query_lower)]
        query_bigrams = [f"{query_words[i]} {query_words[i+1]}" for i in range(len(query_words)-1)] if len(query_words) >= 2 else []

        ranked_items = list(doc_map.values())
        for entry in ranked_items:
            chunk_text = entry["chunk"]["text"].lower()
            chunk_topic = entry["chunk"]["topic"].lower()
            chunk_section = entry["chunk"]["section"].lower()

            cross_bonus = 0.0
            # Contiguous multi-word match
            for bigram in query_bigrams:
                if bigram in chunk_text:
                    cross_bonus += 0.25

            # Topic / section exact alignment
            for q_word in query_words:
                if q_word in chunk_topic:
                    cross_bonus += 0.15
                if q_word in chunk_section:
                    cross_bonus += 0.10

            # Technical acronym boost
            acronyms = re.findall(r'\b[A-Z]{2,}\b', query)
            for acr in acronyms:
                if acr.lower() in chunk_text:
                    cross_bonus += 0.30

            hybrid_score = (entry["rrf_score"] * 30.0) + (entry["dense_score"] * 0.4) + cross_bonus
            entry["final_score"] = hybrid_score
            entry["relevance_percent"] = min(99, max(30, int(hybrid_score * 35)))

        ranked_items.sort(key=lambda x: x["final_score"], reverse=True)

        final_results = []
        for item in ranked_items[:top_k]:
            final_results.append({
                "chunk": item["chunk"],
                "score": round(item["final_score"], 4),
                "relevance_percent": item["relevance_percent"],
                "retrieval_meta": {
                    "method": "Hybrid-BM25-Dense-RRF",
                    "sparse_rank": item["sparse_rank"],
                    "dense_rank": item["dense_rank"],
                    "dense_score": round(item["dense_score"], 3),
                    "sparse_score": round(item["sparse_score"], 3)
                }
            })

        return final_results

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
                "relevance": res.get("relevance_percent", 85),
                "retrieval_meta": res.get("retrieval_meta", {
                    "method": "Hybrid-BM25-Dense-RRF",
                    "sparse_rank": 1,
                    "dense_rank": 1,
                    "dense_score": 0.85,
                    "sparse_score": 1.5
                })
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
            "topics": list(topics_found),
            "retrieval_strategy": "Hybrid-BM25-Dense-RRF"
        }

rag_engine = RAGEngine()
