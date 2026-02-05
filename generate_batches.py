
import os
import json

QUESTIONS = [
    # 💰 Income Share Agreement (ISA) & Pricing
    "What is an Income Share Agreement (ISA) and how is it different from a loan?",
    "Do I have to pay any tuition upfront?",
    "What is the minimum salary threshold before I start paying the ISA? (Context: usually $81k or $65k depending on terms)",
    "What happens if I lose my job? Do I still have to make monthly payments?",
    "Is there a cap on the total amount I will pay back?",
    "Can I just pay the tuition in cash instead of signing an ISA?",
    "Is the ISA legally binding?",
    "What is the percentage of my income that I have to share? (Context: typically 10-15%)",
    "Do you charge interest on the ISA?",
    "Can I pause my ISA payments if I go back to school?",
    
    # 🚀 Job Placement Program (JOPP)
    "How long does the Job Placement Program take to complete?",
    "What is your placement rate for graduates? (Context: ~91.5%)",
    "Do you guarantee a job after the training?",
    "What is the average starting salary for JOPP graduates? (Context: $75k - $155k)",
    "Do you help with H1B or OPT visa sponsorship?",
    "Is the training remote or do I have to move to Fremont, CA?",
    "Do you have a physical office? (Context: 39141 Civic Center Dr, Fremont, CA)",
    "How does SynergisticIT differ from a regular coding bootcamp?",
    "Can I join JOPP if I don't have a Computer Science degree?",
    "What companies have hired your graduates? (Context: Google, Apple, Visa, Wells Fargo, etc.)",
    
    # 💻 Technical Curriculum & Upskilling
    "Does the Data Science track cover Deep Learning and NLP?",
    "Do you provide AWS certification support?",
    "What specific technologies are covered in the Java Full Stack track?",
    "Is the MERN stack included in the curriculum?",
    "Do we work on real-world projects or just toy examples?",
    "How much time should I commit daily for the training?",
    "Do you offer support for 'Data Engineering' specific roles?",
    "Can I switch tracks (e.g., from Java to Data Science) after joining?",
    "Who are the instructors? Are they industry professionals?",
    
    # 🤝 Support & Career Services
    "Do you help with resume writing and optimization?",
    "Do you conduct mock interviews?",
    "Will you market my profile to clients directly?",
    "Do I work for SynergisticIT or the client directly?",
    "What happens if I fail the technical interviews?",
    "How long is the support period after I get a job?",
    
    # 🛡️ Trust & Verification (Handling Skepticism)
    "I saw some negative reviews on Reddit, can you explain them?",
    "Is SynergisticIT a staffing agency or a school?",
    "Can I talk to previous alumni before joining?",
    "Are your placement statistics verified?",
    "Why do you require a deposit if the program is ISA-based?"
]

BATCH_SIZE = 5

TEMPLATE = """
import requests
import time
import json
import os

QUESTIONS = {questions}

API_URL = "http://localhost:8000/chat"
REPORT_FILE = "test_report_full.md"

def run_tests():
    print(f"Starting batch test for {{len(QUESTIONS)}} questions...")
    results = []
    
    # Ensure report file exists with header if this is the first batch run or if missing
    if not os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("# Test Report\\n\\n")
            f.write("| Batch | Question | Relevance Score | Answer Snippet |\\n")
            f.write("|---|---|---|---|\\n")

    for i, q in enumerate(QUESTIONS):
        print(f"\\n[{{i+1}}/{{len(QUESTIONS)}}] Question: {{q}}")
        try:
            start_time = time.time()
            response = requests.post(API_URL, json={{"question": q}}, timeout=60)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Time: {{elapsed:.2f}}s")
                print(f"  Relevance Score: {{data.get('relevance_score', 'N/A')}}")
                
                # Append to report immediately
                with open(REPORT_FILE, "a", encoding="utf-8") as f:
                    answer_snippet = data.get('answer', '').replace("\\n", " ")[:100] + "..." if data.get('answer') else "No answer"
                    f.write(f"| {batch_name} | {{q}} | {{data.get('relevance_score')}} | {{answer_snippet}} |\\n")
                
            else:
                print(f"  Error: Status {{response.status_code}}")
                with open(REPORT_FILE, "a", encoding="utf-8") as f:
                     f.write(f"| {batch_name} | {{q}} | ERROR | Status {{response.status_code}} |\\n")
                
        except Exception as e:
            print(f"  Exception: {{e}}")
            with open(REPORT_FILE, "a", encoding="utf-8") as f:
                 f.write(f"| {batch_name} | {{q}} | ERROR | {{e}} |\\n")

if __name__ == "__main__":
    run_tests()
"""

def generate_batches():
    for i in range(0, len(QUESTIONS), BATCH_SIZE):
        batch_questions = QUESTIONS[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        filename = f"test_batch_{batch_num}.py"
        
        content = TEMPLATE.format(
            questions=json.dumps(batch_questions, indent=4),
            batch_name=f"Batch {batch_num}"
        )
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Created {filename}")

if __name__ == "__main__":
    generate_batches()
