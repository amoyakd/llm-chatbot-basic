import os
import sys
sys.path.append('../..')
import utils
import ollama

import panel as pn  # GUI
pn.extension()


def get_completion_from_messages(messages, model="llama3.2", temperature=0):
    # print(f"message to model: {messages}")
    response = ollama.chat(
        model=model,
        messages=messages,
        options={
            'temperature': temperature,
        }
    )
    return response['message']["content"]

# System of chained prompts for processing the user query
def process_user_message(user_input, all_messages, debug=True):
    delimiter = "```"
    
    # Step 1: Check input to see if it flags the Moderation API or is a prompt injection
    if utils.llama_guard_moderation(user_input):
        print("Step 1: Input flagged by Moderation API.")
        return "Sorry, we cannot process this request.", all_messages

    if debug: print("Step 1: Input passed moderation check.")
    
    category_and_product_response = utils.find_category_and_product_only(user_input, utils.get_products_and_category())
    # print(category_and_product_response)
    # Step 2: Extract the list of products
    category_and_product_list = utils.read_string_to_list(category_and_product_response)
    if debug: print(f'The list of products and categories: {category_and_product_list}')

    if debug: print("Step 2: Extracted list of products.")

    # Step 3: If products are found, look them up
    product_information = utils.generate_output_string(category_and_product_list)
    if debug: print(f"Step 3: Looked up product information.\n{product_information}")

    # Step 4: Answer the user question
    system_message = f"""
    You are a customer service assistant for a large electronic store. \
    Make sure to use the provided product information to answer the user's question. \
    Do not make up any product information. \
    If the product information does not contain the answer, politely tell them you do not know\
    Respond in a friendly and helpful tone, with concise answers. \
    Make sure to ask the user relevant follow-up questions.
    """
    
    prompt_messages = [ {'role': 'system', 'content': system_message} ]
    prompt_messages.extend(all_messages)
    
    user_message_with_context = f"""{user_input}
    
Relevant product information:
{product_information}
"""
    prompt_messages.append({'role': 'user', 'content': user_message_with_context})
    
    final_response = get_completion_from_messages(prompt_messages)
    
    if debug: print(f"Final response: {final_response}")
    if debug:print("Step 4: Generated response to user question.")
    
    # Augment the user's message with product information for context
    if product_information:
        user_message_for_history = user_message_with_context
    else:
        user_message_for_history = user_input

    updated_history = all_messages + [
        {'role': 'user', 'content': user_message_for_history},
        {'role': 'assistant', 'content': final_response}
    ]

    return final_response, updated_history

# user_input = "tell me about the smartx pro phone and the fotosnap camera, the dslr one. Also what tell me about your tvs"
# response,_ = process_user_message(user_input,[])
# print(response)


def collect_messages(debug=True):
    user_input = inp.value_input
    if debug: print(f"User Input = {user_input}")
    if user_input == "":
        return
    inp.value = ''
    global context
    #response, context = process_user_message(user_input, context, utils.get_products_and_category(),debug=True)
    response, context = process_user_message(user_input, context, debug=True)
    panels.append(
        pn.Row('User:', pn.pane.Markdown(user_input, width=600)))
    panels.append(
        pn.Row('Assistant:', pn.pane.Markdown(response, width=600, styles={'background-color': '#F6F6F6'})))
 
    return pn.Column(*panels)


panels = [] # collect display 

context = []

inp = pn.widgets.TextInput( placeholder='Enter text here…')
button_conversation = pn.widgets.Button(name="Service Assistant")

interactive_conversation = pn.bind(collect_messages, button_conversation)

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation),
    pn.panel(interactive_conversation, loading_indicator=True, height=300),
)

dashboard.servable()