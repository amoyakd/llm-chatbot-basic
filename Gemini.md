This project is a customer service chatbot for a large electronics store. It uses the OpenAI API to generate responses and the `panel` library to create a simple graphical user interface.

Here's a breakdown of the Python files:

*   **`chatbot.py`**: This is the main application file. It orchestrates the chatbot's logic. It takes a user's input, uses the OpenAI moderation API to check for inappropriate content, and then calls functions in `utils.py` to identify products and categories in the query. It then constructs a prompt for the OpenAI language model, including relevant product information, to generate a helpful response. Finally, it uses `panel` to create and display the interactive chat interface.
It therefore leverages moderation, reasoning, classification and chaining of prompts to respond to customer requests.

*   **`utils.py`**: This file contains all the helper functions and data needed by `chatbot.py`. It is responsible for:
    *   Loading product and category data from JSON files.
    *   Using the OpenAI API to extract product and category names from the user's message.
    *   Retrieving detailed product information based on the extracted names.
    *   Providing predefined system messages for the AI model to set its persona and task.
    *   A function to generate the `products.json` file with sample data.

## Commented out functions in `utils.py`

The following functions in `utils.py` have been commented out as they are not being used in the project:

- `create_categories`
- `get_categories`
- `get_product_list`
- `find_category_and_product`
- `get_products_from_query`
- `get_mentioned_product_info`
- `answer_user_msg`
- `create_products`

products.json contains the list of products and their attributes as well as categories in JSON format. This should serve as the master list for product details.