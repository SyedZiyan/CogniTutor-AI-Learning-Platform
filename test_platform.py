import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_tests():
    print("[TEST] Running CogniTutor AI Learning Platform Verification Tests...\n")

    # 1. Status
    res = client.get("/api/status")
    assert res.status_code == 200, f"Status failed: {res.text}"
    status_data = res.json()
    print(f"✅ Status Endpoint: OK (Docs indexed: {status_data['total_documents']}, Chunks: {status_data['total_chunks']})")

    # 2. Documents
    res = client.get("/api/documents")
    assert res.status_code == 200, f"Documents failed: {res.text}"
    docs_data = res.json()
    print(f"✅ Documents Endpoint: OK ({len(docs_data['documents'])} sample materials ready)")

    # 2b. Document Raw File Download (PDF.js Streaming)
    sample_doc_id = docs_data['documents'][0]['doc_id']
    res_file = client.get(f"/api/documents/{sample_doc_id}/file")
    assert res_file.status_code == 200, f"File retrieval failed: {res_file.status_code}"
    assert len(res_file.content) > 100
    print(f"✅ Document File Streaming Endpoint: OK ({len(res_file.content)} bytes, {res_file.headers.get('content-type')})")

    # 3. Tutor Chat (RAG)
    res = client.post("/api/tutor/chat", json={"query": "Explain backpropagation in simple words."})
    assert res.status_code == 200, f"Tutor chat failed: {res.text}"
    tutor_data = res.json()
    assert len(tutor_data["citations"]) > 0, "Expected citations"
    print(f"✅ AI Tutor RAG Chat: OK (Grounded with {len(tutor_data['citations'])} citations)")

    # 3b. Real-Time SSE Token Streaming
    res_stream = client.post("/api/tutor/chat/stream", json={"query": "Explain backpropagation in simple words."})
    assert res_stream.status_code == 200, f"Tutor chat stream failed: {res_stream.text}"
    assert "text/event-stream" in res_stream.headers.get("content-type", "")
    stream_events = [e for e in res_stream.text.split("\n\n") if e.strip()]
    assert len(stream_events) >= 3, "Expected at least 3 SSE events (citations, tokens, done)"
    assert 'data: {"event": "citations"' in stream_events[0]
    assert 'data: {"event": "done"' in stream_events[-1]
    print(f"✅ Real-Time SSE Token Streaming: OK ({len(stream_events)} events streamed word-by-word)")

    # 3c. Hybrid Dense + Sparse BM25 RRF Neural Reranking
    res_hybrid = client.post("/api/tutor/chat", json={"query": "CNN spatial pooling and kernel stride"})
    assert res_hybrid.status_code == 200, f"Hybrid tutor chat failed: {res_hybrid.text}"
    hybrid_data = res_hybrid.json()
    assert hybrid_data.get("retrieval_strategy") == "Hybrid-BM25-Dense-RRF", "Expected Hybrid-BM25-Dense-RRF strategy"
    assert len(hybrid_data["citations"]) > 0, "Expected at least one hybrid citation"
    first_cite = hybrid_data["citations"][0]
    assert "retrieval_meta" in first_cite, "Expected retrieval_meta in citations"
    assert first_cite["retrieval_meta"]["method"] == "Hybrid-BM25-Dense-RRF"
    assert "sparse_rank" in first_cite["retrieval_meta"] and "dense_rank" in first_cite["retrieval_meta"]
    print(f"✅ Hybrid BM25 + Dense RRF Reranker: OK (Method: {first_cite['retrieval_meta']['method']}, BM25 Rank #{first_cite['retrieval_meta']['sparse_rank']}, Dense Rank #{first_cite['retrieval_meta']['dense_rank']})")

    # 4. Doubt Solver (3 Levels)
    res = client.post("/api/tutor/doubt-solver", json={"topic_or_question": "lstm"})
    assert res.status_code == 200, f"Doubt solver failed: {res.text}"
    doubt_data = res.json()
    assert "beginner" in doubt_data and "intermediate" in doubt_data and "advanced" in doubt_data
    print("✅ 3-Level Doubt Solver: OK (Beginner, Intermediate, Advanced models verified)")

    # 5. Quiz Generator
    res = client.get("/api/quiz/generate?topic=all&difficulty=adaptive")
    assert res.status_code == 200, f"Quiz generation failed: {res.text}"
    quiz_data = res.json()
    print(f"✅ Quiz Generator: OK ({len(quiz_data['mcqs'])} MCQs, {len(quiz_data['short_questions'])} Short Questions, {len(quiz_data['long_questions'])} Long Questions)")

    # 6. MCQ Evaluation
    sample_mcq = quiz_data['mcqs'][0]
    res = client.post("/api/quiz/evaluate-mcq", json={
        "question_id": sample_mcq["id"],
        "selected_option_index": sample_mcq["correct_index"],
        "current_streak": 1,
        "current_difficulty": "medium"
    })
    assert res.status_code == 200, f"MCQ evaluate failed: {res.text}"
    mcq_eval = res.json()
    assert mcq_eval["is_correct"] is True
    print(f"✅ Adaptive MCQ Auto-Evaluator: OK (XP: +{mcq_eval['xp_earned']}, Next difficulty: {mcq_eval['next_difficulty']})")

    # 7. Competency Engine
    res = client.get("/api/competency/analysis")
    assert res.status_code == 200, f"Competency failed: {res.text}"
    comp_data = res.json()
    print(f"✅ Competency Engine: OK (Overall mastery: {comp_data['overall_mastery']}%, Strong: {len(comp_data['strong'])}, Weak: {len(comp_data['weak'])})")

    # 8. Dynamic Roadmap
    res = client.get("/api/roadmap")
    assert res.status_code == 200, f"Roadmap failed: {res.text}"
    road_data = res.json()
    print(f"✅ Personalized Dynamic Roadmap: OK ({len(road_data['weeks'])} structured weeks generated)")

    # 9. Gamification
    res = client.get("/api/gamification")
    assert res.status_code == 200, f"Gamification failed: {res.text}"
    gam_data = res.json()
    print(f"✅ Gamification & Leaderboard: OK (Level: {gam_data['level_info']['current_level']}, XP: {gam_data['level_info']['current_xp']}, Streak: {gam_data['streak_days']} days)")

    # 10. Frontend static check
    res = client.get("/")
    assert res.status_code == 200, "Frontend index.html failed"
    print("✅ Frontend SPA Delivery: OK (HTTP 200)")

    # 11. Concept Knowledge Graph (Visual Ontology)
    res = client.get("/api/graph")
    assert res.status_code == 200, f"Graph failed: {res.text}"
    graph_data = res.json()
    assert "nodes" in graph_data and "edges" in graph_data
    assert len(graph_data["nodes"]) >= 10, "Expected at least 10 concept nodes"
    assert len(graph_data["edges"]) >= 10, "Expected at least 10 ontology edges"
    print(f"✅ Concept Knowledge Graph: OK ({len(graph_data['nodes'])} concepts, {len(graph_data['edges'])} ontology edges)")

    # 12. Socratic Viva Interview Mode
    res = client.post("/api/viva/start", json={"topic": "Sequential Modeling & RNNs", "student_name": "Scholar"})
    assert res.status_code == 200, f"Viva start failed: {res.text}"
    viva_start = res.json()
    assert "session_id" in viva_start and "question" in viva_start
    session_id = viva_start["session_id"]
    print(f"✅ Socratic Viva Mode Start: OK (Session: {session_id[:8]}..., Round: {viva_start['round']})")

    # Round 1 response
    res = client.post("/api/viva/respond", json={
        "session_id": session_id,
        "student_transcript": "Vanilla RNNs suffer from the vanishing gradient problem because repeatedly multiplying weight matrices across many timesteps causes eigenvalues smaller than 1 to decay exponentially."
    })
    assert res.status_code == 200, f"Viva response failed: {res.text}"
    viva_r1 = res.json()
    assert "feedback" in viva_r1 and "next_question" in viva_r1
    print(f"✅ Socratic Viva Round 1 Defense: OK (Score: {viva_r1['score_this_round']}/100, Examiner Critique received)")

    print("\n🎉 ALL 12 VERIFICATION TEST SUITES PASSED FLAWLESSLY!\n")

if __name__ == "__main__":
    run_tests()

