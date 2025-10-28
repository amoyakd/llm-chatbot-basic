# LLM Chatbot Basic

This project is a customer service chatbot for a large electronics store. It uses the Llama 3.2 model locally via Ollama to generate responses and the `panel` library to create a simple graphical user interface.

## Features

*   Answers customer questions about products.
*   Uses basic implementation of RAG
*   Uses Llama 3.2 locally via Ollama to generate responses.
*   Uses `panel` to create a simple graphical user interface.
*   Leverages moderation, reasoning, classification and chaining of prompts to respond to customer requests.

## Getting Started

### Prerequisites

*   Python 3.x
*   Ollama installed and running with the `llama3.2` and `llama-guard3` models.

### Installation

1.  Install Ollama and download model Llama 3.2 and llama-guard. See https://hashnode.com/post/cmh4yf2ms000102kzc64r23dt
2.  Clone the repository.
3.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the application

1.  Run the chatbot:
    ```bash
    panel serve chatbot.py
    ```

## File Structure

*   `chatbot.py`: The main application file. It orchestrates the chatbot's logic.
*   `utils.py`: Contains all the helper functions and data needed by `chatbot.py`.
*   `products.json`: Contains the list of products and their attributes as well as categories in JSON format.
*   `requirements.txt`: A list of all the python libraries required to run the application.
