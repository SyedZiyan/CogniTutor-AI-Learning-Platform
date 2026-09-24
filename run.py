import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    print(f"\n🚀 Launching CogniTutor AI Learning Platform in browser: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("=" * 70)
    print(" 🧠  COGNITUTOR - AI PERSONAL LEARNING PLATFORM  🧠")
    print("=" * 70)
    print(" • Architecture: RAG Tutor, Competency Engine, Adaptive Quizzes & Voice AI")
    print(" • Server: http://127.0.0.1:8000")
    print(" • API Docs: http://127.0.0.1:8000/docs")
    print("=" * 70)

    # Launch browser thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn server
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
