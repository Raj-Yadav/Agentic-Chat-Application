
import requests
import json

def test_q(question):
    print(f"Testing Question: {question}")
    try:
        response = requests.post("http://localhost:8000/chat", json={"question": question})
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print("Error:", response.status_code, response.text)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    test_q("What is an Income Share Agreement (ISA) and how is it different from a loan?")
