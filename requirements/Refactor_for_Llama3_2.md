### Refactoring Plan: OpenAI to Ollama and Llama 3.2

This document outlines the plan to refactor the chatbot application, migrating it from the OpenAI API to a local setup using Ollama, Llama 3.2, and Llama Guard for moderation.

**1. Environment and Dependencies:**

*   **Create `requirements.txt`:** A `requirements.txt` file will be created to manage project dependencies.
*   **Remove OpenAI Dependency:** The `openai` library will be removed from the project's dependencies.
*   **Add Ollama Dependency:** The `ollama` library will be added to `requirements.txt` to enable communication with the local Ollama server.

**2. Moderation (`chatbot.py` & `utils.py`):**

*   **Replace Moderation API:** The current `_get_moderation_flag` function in `chatbot.py` uses the OpenAI Moderation API. This will be replaced with a call to a local Llama Guard model served via Ollama.
*   **Implement Llama Guard Logic:**
    *   A new function will be created in `utils.py` (e.g., `get_llama_guard_moderation`).
    *   This function will make a request to the Ollama API, specifying `model='llama-guard'`.
    *   It will parse the response from Llama Guard (typically "safe" or "unsafe") to return a boolean moderation flag.
    *   The `collect_messages` function in `chatbot.py` will be updated to call this new local moderation function.

**3. Core Language Model (`chatbot.py`):**

*   **Switch to Ollama Chat:** The `_get_completion_from_messages` function will be refactored to use `ollama.chat` instead of `openai.ChatCompletion.create`.
*   **Update Model Identifier:** The `model` parameter will be set to `llama3.2` to use the locally downloaded model.
*   **Adapt Message Format:** The message history and system prompts will be formatted according to the requirements of the `ollama.chat` function.

**4. Entity Extraction (`utils.py`):**

*   **Refactor `find_category_and_product_only`:** This function currently relies on OpenAI's proprietary "Function Calling" feature to extract product and category information. This will be refactored to use a "Structured Prompting" technique compatible with Llama 3.2.
*   **Implement Structured Prompting:**
    *   The system prompt within this function will be significantly changed. It will be a detailed instruction that explicitly commands the model to act as a JSON-generating entity extractor.
    *   The prompt will define the exact JSON structure required (e.g., `{"category": "...", "product": "..."}`), provide examples, and state that *only* the JSON object should be in the response.
    *   The function will call `ollama.chat` with this new, detailed prompt.
    *   The string response from the model (which will be the JSON object) will be parsed using `json.loads()` to extract the category and product information.

**5. Configuration and Cleanup:**

*   **Remove API Key Handling:** All code related to loading and using the `OPENAI_API_KEY` will be removed from the project.
*   **Configure Ollama Host (Optional):** The implementation will default to the standard Ollama address (`http://localhost:11434`) but can be configured if the user has a different setup.

This plan ensures a complete migration to a local, open-source-based LLM setup, removing reliance on cloud APIs and leveraging the power of Llama 3.2 for both conversation and structured data extraction.

**6. Bug Fixes and Refinements:**

*   **Case-Insensitive Product Lookup:** Implemented case-insensitive lookups for products and categories to prevent empty responses caused by capitalization mismatches between the user's query and the product data.
*   **Redundant Information Fix:** Corrected a logical bug in the `generate_output_string` function that caused redundant information to be returned. The function now prioritizes specific product details and falls back to category-wide results only when necessary.
*   **Efficient Data Loading:** Optimized the application by loading the `products.json` data only once at startup, rather than on each product lookup, improving overall performance and efficiency.

**7. Post-Refactoring Analysis and Testing:**

*   **Empty Response Bug Fix:** A critical bug causing empty chatbot responses was resolved by refactoring the `process_user_message` function in `chatbot.py`. The fix involved correcting the prompt structure and conversation history management to prevent the model from getting confused by invalid message sequences.
*   **Model Hallucination in Entity Extraction:** An investigation into the `find_category_and_product_only` function revealed that the `llama3.2` model was hallucinating, i.e., identifying products (e.g., "iPhone X") that were not present in the `products.json` file. This highlighted the model's tendency to rely on its general knowledge instead of strictly following the provided context and instructions.
*   **Accuracy Evaluation Framework:** To systematically measure the performance of the entity extraction function, a new test class was created in `test_utils.py`. This class uses a ground-truth based evaluation method, comparing the function's output for 100 diverse, randomly generated prompts against manually defined expected outcomes. This provides a clear metric for the model's accuracy and its adherence to the specified constraints.