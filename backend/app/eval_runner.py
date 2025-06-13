"""Evaluation runner for yeest.xyz backend."""

import json
import asyncio
from typing import List, Dict, Any
from pathlib import Path
import logging
from rouge_score import rouge_scorer

from .rag import rag_system
from .memory import ChatMemoryManager

logger = logging.getLogger(__name__)

class EvaluationRunner:
    """Runs automated evaluation on the RAG system."""
    
    def __init__(self, test_file_path: str = "tests/eval_dataset.jsonl"):
        self.test_file_path = test_file_path
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases from JSONL file."""
        test_cases = []
        
        if not Path(self.test_file_path).exists():
            logger.warning(f"Test file {self.test_file_path} not found")
            return test_cases
        
        try:
            with open(self.test_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    test_case = json.loads(line.strip())
                    test_cases.append(test_case)
        except Exception as e:
            logger.error(f"Error loading test cases: {e}")
        
        return test_cases
    
    def evaluate_answer(self, predicted: str, reference: str) -> Dict[str, float]:
        """Evaluate a single answer using ROUGE scores."""
        scores = self.rouge_scorer.score(reference, predicted)
        
        return {
            'rouge1_f': scores['rouge1'].fmeasure,
            'rouge2_f': scores['rouge2'].fmeasure,
            'rougeL_f': scores['rougeL'].fmeasure,
        }
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on all test cases."""
        test_cases = self.load_test_cases()
        
        if not test_cases:
            return {"error": "No test cases found"}
        
        results = []
        total_scores = {'rouge1_f': 0, 'rouge2_f': 0, 'rougeL_f': 0}
        
        for i, test_case in enumerate(test_cases):
            try:
                query = test_case['query']
                reference_answer = test_case['reference_answer']
                
                # Get RAG chain and generate answer
                rag_chain = rag_system.get_rag_chain()
                result = rag_chain({"query": query})
                predicted_answer = result["result"]
                
                # Evaluate the answer
                scores = self.evaluate_answer(predicted_answer, reference_answer)
                
                # Add to results
                result_entry = {
                    'test_case_id': i,
                    'query': query,
                    'predicted_answer': predicted_answer,
                    'reference_answer': reference_answer,
                    'scores': scores
                }
                results.append(result_entry)
                
                # Accumulate scores
                for metric, score in scores.items():
                    total_scores[metric] += score
                
                logger.info(f"Evaluated test case {i+1}/{len(test_cases)}")
                
            except Exception as e:
                logger.error(f"Error evaluating test case {i}: {e}")
                results.append({
                    'test_case_id': i,
                    'query': test_case.get('query', 'Unknown'),
                    'error': str(e)
                })
        
        # Calculate average scores
        num_successful = len([r for r in results if 'scores' in r])
        avg_scores = {}
        if num_successful > 0:
            for metric in total_scores:
                avg_scores[metric] = total_scores[metric] / num_successful
        
        return {
            'total_test_cases': len(test_cases),
            'successful_evaluations': num_successful,
            'average_scores': avg_scores,
            'detailed_results': results
        }
    
    def save_results(self, results: Dict[str, Any], output_file: str = "eval_results.json"):
        """Save evaluation results to file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

# Example test dataset creation
def create_sample_test_dataset():
    """Create a sample test dataset for evaluation."""
    sample_tests = [
        {
            "query": "What is artificial intelligence?",
            "reference_answer": "Artificial intelligence (AI) is a branch of computer science that aims to create machines capable of performing tasks that typically require human intelligence, such as learning, reasoning, and problem-solving."
        },
        {
            "query": "How does climate change affect the environment?",
            "reference_answer": "Climate change affects the environment through rising temperatures, changing precipitation patterns, melting ice caps, rising sea levels, and increased frequency of extreme weather events."
        },
        {
            "query": "What are the benefits of renewable energy?",
            "reference_answer": "Renewable energy benefits include reduced greenhouse gas emissions, decreased dependence on fossil fuels, lower long-term costs, job creation, and improved energy security."
        }
    ]
    
    # Create tests directory if it doesn't exist
    Path("tests").mkdir(exist_ok=True)
    
    with open("tests/eval_dataset.jsonl", 'w', encoding='utf-8') as f:
        for test in sample_tests:
            f.write(json.dumps(test) + '\n')
    
    logger.info("Sample test dataset created at tests/eval_dataset.jsonl")

if __name__ == "__main__":
    # Create sample dataset if it doesn't exist
    if not Path("tests/eval_dataset.jsonl").exists():
        create_sample_test_dataset()
    
    # Run evaluation
    evaluator = EvaluationRunner()
    results = asyncio.run(evaluator.run_evaluation())
    evaluator.save_results(results)
