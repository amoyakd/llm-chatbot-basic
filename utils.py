import json
import ollama
from collections import defaultdict

# Load products once at the module level for efficiency
try:
    with open('products.json', 'r') as file:
        products_data = json.load(file)
except FileNotFoundError:
    print("Error: products.json not found.")
    products_data = {}

# Create a case-insensitive mapping of product names to their actual keys
products_lower_map = {name.lower(): name for name in products_data}


def llama_guard_moderation(user_input):
    response = ollama.chat(
        model='llama-guard3',
        messages=[{'role': 'user', 'content': user_input}]
    )
    return response['message']['content'] == 'unsafe'


def get_products_and_category():
    products_by_category = defaultdict(list)
    for product_info in products_data.values():
        category = product_info.get('category')
        if category:
            products_by_category[category].append(product_info.get('name'))
    return dict(products_by_category)


def get_products():
    # Return the pre-loaded data
    return products_data


def find_category_and_product_only(user_input, products_and_category):
    delimiter = "####"
    system_message = f"""
    You will be provided with a customer service query. The query will be delimited with {delimiter} characters.
    Your task is to identify products and categories from the query that are present in the allowed products list provided below.

    Output a Python list of JSON objects, where each object has ONE of the following formats:
    1. {{'category': '<category_name>'}}
    2. {{'products': ['<product_name_1>', '<product_name_2>', ...]}}

    - The categories and products you identify MUST be from the "Allowed products" list.
    - If a product is mentioned, it must be associated with the correct category from the list.
    - If no specific products are mentioned but a category is, include only the category object.
    - If the mentioned product is not in the list, do not try to infer or guess; simply omit it.
    - If no products or categories from the allowed list are found in the query, you MUST output an empty list: [].
    - Do not provide any other text, explanation, or conversation. Your entire response must be only the Python list of JSON objects.

    Allowed products:
    {json.dumps(products_and_category, indent=4)}

    Example 1:
    Query: "I'm looking for a new laptop, maybe a TechPro Ultrabook."
    Your response:
    [
        {{'category': 'Computers and Laptops'}},
        {{'products': ['TechPro Ultrabook']}}
    ]

    Example 2:
    Query: "Do you have any information on the iPhone?"
    Your response:
    []

    Now, process the following query.
    """
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"},
    ]
    response = ollama.chat(
        model='llama3.2',
        messages=messages,
        options={
            'temperature': 0,
        }
    )
    return response['message']['content']


def get_product_by_name(name):
    """
    Performs a case-insensitive lookup for a product.
    """
    lower_name = name.lower()
    if lower_name in products_lower_map:
        actual_name = products_lower_map[lower_name]
        return products_data.get(actual_name)
    return None


def get_products_by_category(category):
    """
    Performs a case-insensitive lookup for products in a category.
    """
    lower_category = category.lower()
    return [
        product for product in products_data.values()
        if product.get("category", "").lower() == lower_category
    ]


def read_string_to_list(input_string):
    if input_string is None:
        return None

    try:
        # The model should return valid JSON, but we'll keep the quote replacement as a fallback.
        input_string = input_string.replace("'", '"')
        data = json.loads(input_string)
        return data
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON string: {input_string}")
        return None


def generate_output_string(data_list):
    """
    Generates a string of product information.
    - If specific products are mentioned, only their info is returned.
    - If only a category is mentioned, all products in that category are returned.
    """
    if not data_list:
        return ""

    product_names = set()
    category_names = set()

    for item in data_list:
        if "products" in item:
            product_names.update(item["products"])
        elif "category" in item:
            category_names.add(item["category"])

    output_parts = []

    # Prioritize specific products
    if product_names:
        for name in product_names:
            product = get_product_by_name(name)
            if product:
                output_parts.append(json.dumps(product, indent=4))
            else:
                print(f"Error: Product '{name}' not found")
    # Fallback to categories if no specific products were found
    elif category_names:
        for name in category_names:
            products_in_cat = get_products_by_category(name)
            for product in products_in_cat:
                output_parts.append(json.dumps(product, indent=4))

    return "\n".join(output_parts)
