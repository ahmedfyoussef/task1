import openai
import re
from typing import List, Dict, Tuple
import json
from datetime import datetime



class PromptReliabilityHarness:
    def __init__(self, api_key: str = None):


        #please make sure to replace this with your own api 
        self.api_key =  "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"


        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass as parameter.")
        

        openai.api_key = self.api_key
        self.results = []

    def test_cases(self) -> List[Dict]:
        """Define test cases with expected patterns"""
        return [
            #Synthetic cases
            {
                "id": "math_1",
                "queries": ["What is 15 + 27?", "Calculate 15 plus 27", "15+27=?"],
                "expected": "42",
                "type": "exact"
            },
            {
                "id": "date_1", 
                "queries": ["What date is 30 days from March 15, 2024?", "30 days after March 15 2024"],
                "expected": r"April\s+14,\s*2024",
                "type": "regex"
            },
            {
                "id": "conversion_1",
                "queries": ["Convert 25 Celsius to Fahrenheit", "25°C in Fahrenheit"],
                "expected": r"77",
                "type": "regex" 
            },
            {
                "id": "vocab_1",
                "queries": ["Define 'ephemeral'", "What does ephemeral mean?"],
                "expected": r"(short-lived|temporary|transient)",
                "type": "regex"
            },
            {
                "id": "logic_1",
                "queries": ["If all humans are mortal and Socrates is human, is Socrates mortal?", "Socrates mortal yes/no"],
                "expected": r"\byes\b",
                "type": "regex"
            },
            #Real world cases (redacted)
            {
                "id": "policy_1",
                "queries": [
                    "What's the vacation accrual rate?",
                    "How do vacation days accumulate?",
                    "Vacation accrual policy"
                ],
                "expected": r"(accru.*\d|earn.*per|rate.*\d)",
                "type": "regex"
            },
            {
                "id": "tech_1", 
                "queries": ["API rate limit", "API rate limmit", "rate limit for API"],
                "expected": r"(\d+.*request|request.*limit|rate.*\d+)",
                "type": "regex"
            },
            {
                "id": "product_1",
                "queries": [
                    "List features A, B, C",
                    "Tell me about C, A, B", 
                    "What features include B, C, A?"
                ],
                "expected": r"(A.*B.*C|A.*C.*B|B.*A.*C|B.*C.*A|C.*A.*B|C.*B.*A)",
                "type": "regex"
            },
            {
                "id": "procedure_1",
                "queries": [
                    "How to reset password",
                    "How to reset password (ignore backup)"
                ],
                "expected": r"(reset.*password|password.*reset)",
                "type": "regex"
            },
            {
                "id": "troubleshoot_1",
                "queries": [
                    "Network issue fix",
                    "  Network   issue  fix  ",
                    "Fix network issues"
                ],
                "expected": r"(check.*connection|restart.*router|network.*troubleshoot)",
                "type": "regex"
            }
        ]
    
    def call_llm(self, prompt: str) -> str:
        """Call LLM with prompt"""
        try:


        
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def evaluate_response(self, response: str, expected: str, eval_type: str) -> bool:
        """Evaluate if response matches expected pattern"""
        if eval_type == "exact":
            return expected.lower() in response.lower()
        elif eval_type == "regex":
            return bool(re.search(expected, response, re.IGNORECASE))
        return False
    
    def run_tests(self) -> Dict:
        """Run all test cases"""
        print('test started')
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_cases": []
        }
        
        for test_case in self.test_cases():
            case_results = {
                "id": test_case["id"],
                "queries": [],
                "consistency_score": 0
            }
            
            query_results = []
            for query in test_case["queries"]:
                response = self.call_llm(query)
                passed = self.evaluate_response(
                    response, 
                    test_case["expected"], 
                    test_case["type"]
                )
                
                query_results.append({
                    "query": query,
                    "response": response,
                    "passed": passed
                })
            
            # Calculate consistency (percentage of queries that passed)
            passed_count = sum(1 for q in query_results if q["passed"])
            consistency = passed_count / len(query_results)
            
            case_results["queries"] = query_results
            case_results["consistency_score"] = consistency
            results["test_cases"].append(case_results)
        
        # Calculate overall metrics
        total_consistency = sum(case["consistency_score"] for case in results["test_cases"])
        results["overall_consistency"] = total_consistency / len(results["test_cases"])
        
        return results
    
    def generate_report(self, results: Dict):
        """Generate simple console report"""
        print("\n" + "="*50)
        print("PROMPT RELIABILITY REPORT")
        print("="*50)
        
        for case in results["test_cases"]:
            print(f"\n{case['id']}: {case['consistency_score']:.1%} consistent")
            for i, query in enumerate(case["queries"]):
                status = "✓" if query["passed"] else "✗"
                print(f"  {status} Query {i+1}: {query['query'][:50]}...")
        
        print(f"\nOVERALL CONSISTENCY: {results['overall_consistency']:.1%}")
        print("="*50)


if __name__ == "__main__":

    harness = PromptReliabilityHarness()  


    results = harness.run_tests()
    

    harness.generate_report(results)
    

    with open("reliability_results.json", "w") as f:
        json.dump(results, f, indent=2)
