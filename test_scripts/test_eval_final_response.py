import unittest
from unittest.mock import patch
import sys
import os
import re
import ast
import random

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import chatbot
import utils

class TestEvalFinalResponse(unittest.TestCase):

    def setUp(self):
        """Parse the evaluation log file to get test cases."""
        self.test_cases = []
        log_file_path = os.path.join(os.path.dirname(__file__), 'category_product_eval_01.log')
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
        except FileNotFoundError:
            self.fail(f"Log file not found at {log_file_path}")

        # Split content into individual test cases. This regex keeps the delimiter.
        # The result will be like: ['', '1', content1, '2', content2, ...]
        test_case_parts = re.split(r'--- Test Case (\d+) ---', log_content)
        
        i = 1
        while i < len(test_case_parts):
            case_num = int(test_case_parts[i])
            block = test_case_parts[i+1]

            prompt_match = re.search(r'Prompt: (.*)', block)
            prompt = prompt_match.group(1).strip() if prompt_match else ""

            # Do not use DOTALL, as it will match greedily until the end of the block
            expected_match = re.search(r'Expected: (.*)', block)
            if expected_match:
                expected_str = expected_match.group(1).strip()
            else:
                result_match = re.search(r'Result: (.*)', block)
                expected_str = result_match.group(1).strip() if result_match else "[]"
            
            try:
                # ast.literal_eval is safer for parsing Python literals
                expected_list = ast.literal_eval(expected_str)
            except (ValueError, SyntaxError):
                expected_list = [] # Default to empty list on parsing error

            self.test_cases.append({
                "test_case": case_num,
                "prompt": prompt,
                "expected_list": expected_list
            })
            i += 2
        
        if len(self.test_cases) > 30:
            self.test_cases = random.sample(self.test_cases, 30)

    @patch('utils.llama_guard_moderation', return_value=False)
    @patch('utils.find_category_and_product_only')
    def test_generate_and_log_responses(self, mock_find_cat_prod, mock_moderation):
        """
        Generates responses for test cases and logs them for quality evaluation.
        This test focuses on steps 3 and 4 of `process_user_message`.
        It uses pre-defined "expected" product/category classifications to bypass step 2
        and evaluates the final response generation.
        """
        output_log_path = os.path.join(os.path.dirname(__file__), 'final_response_quality_eval_01.log')
        
        with open(output_log_path, 'w', encoding='utf-8') as log_file:
            for case in self.test_cases:
                prompt = case["prompt"]
                expected_list = case["expected_list"]
                
                # Mock read_string_to_list to return the ground truth product list
                with patch('utils.read_string_to_list', return_value=expected_list):
                    final_response, _ = chatbot.process_user_message(prompt, [], debug=False)

                    log_file.write(f"--- Test Case {case['test_case']} --- \n")
                    log_file.write(f"Prompt: {prompt}\n")
                    log_file.write(f"Used Category/Product: {expected_list}\n")
                    log_file.write(f"Final Response: {final_response}\n")
                    log_file.write("--------------------\n")
        self.assertTrue(os.path.exists(output_log_path))
        print(f"Generated responses for {len(self.test_cases)} test cases. See '{output_log_path}' for details.")

if __name__ == '__main__':
    unittest.main()