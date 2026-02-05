
import requests
import time
import json
import os

QUESTIONS = [
    "Is the training remote or do I have to move to Fremont, CA?",
    "Do you have a physical office? (Context: 39141 Civic Center Dr, Fremont, CA)",
    "How does SynergisticIT differ from a regular coding bootcamp?",
    "Can I join JOPP if I don't have a Computer Science degree?",
    "What companies have hired your graduates? (Context: Google, Apple, Visa, Wells Fargo, etc.)"
]

API_URL = "http://localhost:8000/chat"
REPORT_FILE = "test_report_full.md"

def run_tests():
    print(f"Starting batch test for {len(QUESTIONS)} questions...")
    results = []
    
    # Ensure report file exists with header if this is the first batch run or if missing
    if not os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("# Test Report\n\n")
            f.write("| Batch | Question | Relevance Score | Answer Snippet |\n")
            f.write("|---|---|---|---|\n")

    for i, q in enumerate(QUESTIONS):
        print(f"\n[{i+1}/{len(QUESTIONS)}] Question: {q}")
        try:
            start_time = time.time()
            response = requests.post(API_URL, json={"question": q}, timeout=60)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Time: {elapsed:.2f}s")
                print(f"  Relevance Score: {data.get('relevance_score', 'N/A')}")
                
                # Append to report immediately
                with open(REPORT_FILE, "a", encoding="utf-8") as f:
                    answer_snippet = data.get('answer', '').replace("\n", " ")[:100] + "..." if data.get('answer') else "No answer"
                    f.write(f"| Batch 4 | {q} | {data.get('relevance_score')} | {answer_snippet} |\n")
                
            else:
                print(f"  Error: Status {response.status_code}")
                with open(REPORT_FILE, "a", encoding="utf-8") as f:
                     f.write(f"| Batch 4 | {q} | ERROR | Status {response.status_code} |\n")
                
        except Exception as e:
            print(f"  Exception: {e}")
            with open(REPORT_FILE, "a", encoding="utf-8") as f:
                 f.write(f"| Batch 4 | {q} | ERROR | {e} |\n")

if __name__ == "__main__":
    run_tests()
