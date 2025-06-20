import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.tools.rag_tool import generate_rag_answer

with open("./use_case_tests.json", "r") as f:
    test_cases = json.load(f)

for case in test_cases:
    print(f"\n🧪 DOMAIN: {case['domain']}")
    print(f"🔍 Query: {case['query']}")
    answer = generate_rag_answer(case["query"])
    print(f"✅ Response:\n{answer}")
