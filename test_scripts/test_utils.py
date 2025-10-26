
import unittest
import json
import random
import utils

class TestFindCategoryAndProduct(unittest.TestCase):

    def setUp(self):
        """Load products and categories for testing."""
        self.products_and_categories = utils.get_products_and_category()
        with open('products.json', 'r') as f:
            self.products_data = json.load(f)
        self.product_names = list(self.products_data.keys())
        self.category_names = list(self.products_and_categories.keys())

    def generate_test_cases(self, num_cases=100):
        """Generate a list of diverse test cases."""
        test_cases = []

        # Case 1: Exact product match
        for i in range(20):
            product_name = random.choice(self.product_names)
            category = self.products_data[product_name]['category']
            test_cases.append({
                "prompt": f"Tell me more about the {product_name}",
                "expected": sorted([{'category': category}, {'products': [product_name]}], key=lambda x: list(x.keys())[0])
            })

        # Case 2: Exact category match
        for i in range(10):
            category_name = random.choice(self.category_names)
            test_cases.append({
                "prompt": f"Show me your selection of {category_name}",
                "expected": [{'category': category_name}]
            })

        # Case 3: Non-existent products (hallucination check)
        non_existent_products = ["iPhone 14", "Samsung Galaxy S23", "Sony PlayStation 5", "MacBook Pro", "Pixel 7"]
        for i in range(10):
            product_name = random.choice(non_existent_products)
            test_cases.append({
                "prompt": f"Do you have the {product_name} in stock?",
                "expected": []
            })

        # Case 4: Multiple products
        for i in range(10):
            p1_name = random.choice(self.product_names)
            p2_name = random.choice(self.product_names)
            while p1_name == p2_name:
                p2_name = random.choice(self.product_names)
            c1 = self.products_data[p1_name]['category']
            c2 = self.products_data[p2_name]['category']
            
            expected = []
            if c1 == c2:
                expected = [{'category': c1}, {'products': sorted([p1_name, p2_name])}]
            else:
                expected = sorted([{'category': c1}, {'products': [p1_name]}, {'category': c2}, {'products': [p2_name]}], key=lambda x: list(x.keys())[0])

            test_cases.append({
                "prompt": f"Compare the {p1_name} and the {p2_name}",
                "expected": expected
            })

        # Case 5: Vague or general questions
        vague_prompts = ["What do you sell?", "I need a new gadget", "Help me choose a gift", "What are your best products?"]
        for i in range(5):
            test_cases.append({
                "prompt": random.choice(vague_prompts),
                "expected": []
            })

        # Case 6: Prompts with typos
        for i in range(5):
            product_name = random.choice(self.product_names)
            product_with_typo = product_name[:-2] + "xx" # Introduce a typo
            test_cases.append({
                "prompt": f"I'm looking for the {product_with_typo}",
                "expected": []
            })

        # Case 7: Product and Category together
        for i in range(10):
            product_name = random.choice(self.product_names)
            category = self.products_data[product_name]['category']
            test_cases.append({
                "prompt": f"Do you have the {product_name} in the {category} section?",
                "expected": sorted([{'category': category}, {'products': [product_name]}], key=lambda x: list(x.keys())[0])
            })
            
        # Case 8: Mix of existing and non-existing
        for i in range(10):
            p_exist = random.choice(self.product_names)
            p_non_exist = random.choice(non_existent_products)
            category = self.products_data[p_exist]['category']
            test_cases.append({
                "prompt": f"I want to see the {p_exist} and the {p_non_exist}",
                "expected": sorted([{'category': category}, {'products': [p_exist]}], key=lambda x: list(x.keys())[0])
            })

        # Case 9: Just a brand name
        brands = list(set(p['brand'] for p in self.products_data.values()))
        for i in range(10):
            brand_name = random.choice(brands)
            # This is tricky, as the model might associate a brand with a category.
            # For this test, we expect it to return nothing if only a brand is mentioned.
            test_cases.append({
                "prompt": f"Do you have any products from {brand_name}?",
                "expected": []
            })
            
        # Case 10: More complex queries
        for i in range(10):
            p1_name = random.choice(self.product_names)
            c1 = self.products_data[p1_name]['category']
            p2_name = random.choice(self.product_names)
            while p1_name == p2_name:
                p2_name = random.choice(self.product_names)
            c2 = self.products_data[p2_name]['category']
            
            expected = []
            if c1 == c2:
                expected = [{'category': c1}, {'products': sorted([p1_name, p2_name])}]
            else:
                expected = sorted([{'category': c1}, {'products': [p1_name]}, {'category': c2}, {'products': [p2_name]}], key=lambda x: list(x.keys())[0])
            
            test_cases.append({
                "prompt": f"I need a {p1_name} for work and a {p2_name} for my living room.",
                "expected": expected
            })

        return test_cases[:100]

    def test_find_category_and_product_only(self):
        """Test the find_category_and_product_only function with generated prompts."""
        test_cases = self.generate_test_cases()
        score = 0
        
        for i, case in enumerate(test_cases):
            prompt = case["prompt"]
            expected = case["expected"]
            
            print(f"--- Test Case {i+1} ---")
            print(f"Prompt: {prompt}")
            
            result_str = utils.find_category_and_product_only(prompt, self.products_and_categories)
            
            try:
                # The model sometimes returns a string that needs parsing.
                result_list = utils.read_string_to_list(result_str)
                
                # Sort the lists for consistent comparison
                if result_list:
                    result_list = sorted(result_list, key=lambda x: list(x.keys())[0])
                    for item in result_list:
                        if 'products' in item:
                            item['products'] = sorted(item['products'])

                print(f"Result: {result_list}")
                
                if result_list == expected:
                    print("Accuracy: Accurate")
                    score += 1
                else:
                    print("Accuracy: Inaccurate")
                    print(f"Expected: {expected}")

            except Exception as e:
                print(f"Accuracy: Inaccurate (Error parsing result: {e})")
                print(f"Raw Result: {result_str}")
                print(f"Expected: {expected}")

            print("-" * 20)

        print(f"\n--- Final Score ---")
        print(f"Accuracy: {score}/{len(test_cases)} ({score / len(test_cases):.2%})")

if __name__ == '__main__':
    unittest.main()
