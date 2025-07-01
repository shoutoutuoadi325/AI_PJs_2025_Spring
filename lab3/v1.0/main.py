import requests
import json
import os
import time

# API Configuration
url = "https://api.deerapi.com/v1/chat/completions"
api_key = "YlfbboEmR0QGY8bl3bDf1h28NhCEdL4GhFxF9yhfri6UsHvc"  # Key without sk- prefix
models = ["gpt-3.5-turbo", "gemini-1.5-flash-latest", "gpt-4.1-nano", "qwen-turbo-2024-11-01", "grok-3-mini-latest"]

# Read questions and prompts
def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

questions = read_jsonl("questions.json")
prompts = read_jsonl("prompts.json")

# Create a dictionary for easy lookup of prompts by category
prompt_by_category = {prompt["category"]: prompt for prompt in prompts}

# Create or clear the answers file
with open("ans.md", 'w', encoding='utf-8') as f:
    f.write("# Language Model Evaluation Results\n\n")

# Group questions by category
questions_by_category = {}
for question in questions:
    category = question["category"]
    if category not in questions_by_category:
        questions_by_category[category] = []
    questions_by_category[category].append(question)

# Process each category
for category, category_questions in questions_by_category.items():
    # Get the prompt for this category
    category_prompt = prompt_by_category[category]
    
    # Add category header to the answers file
    with open("ans.md", 'a', encoding='utf-8') as f:
        f.write(f"## {category.capitalize()}\n\n")
    
    # Process each question in this category
    for question in category_questions:
        question_text = question["turns"][0]
        question_id = question["question_id"]
        
        # Add question header to the answers file
        with open("ans.md", 'a', encoding='utf-8') as f:
            f.write(f"### Question {question_id}: {question_text}\n\n")
        
        # Process each model for this question
        for model in models:
            print(f"Processing {model} for question {question_id} ({category})")
            
            # Prepare the payload
            payload = json.dumps({
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": category_prompt["system_prompt"]
                    },
                    {
                        "role": "user",
                        "content": question_text
                    }
                ]
            })
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_key}',  # Fixed format to Bearer token
                'User-Agent': 'DeerAPI/1.0.0 (https://api.deerapi.com)',
                'Content-Type': 'application/json'
            }
            
            try:
                # Add a delay to avoid rate limiting
                time.sleep(1)
                
                # Make the API request
                response = requests.request("POST", url, headers=headers, data=payload)
                
                # Print response for debugging
                print(f"Status code: {response.status_code}")
                print(f"Response: {response.text[:200]}...")  # Print first 200 chars for debugging
                
                # Parse the response
                response_json = json.loads(response.text)
                
                # Extract answer safely with error handling
                if 'choices' in response_json and len(response_json['choices']) > 0:
                    if 'message' in response_json['choices'][0] and 'content' in response_json['choices'][0]['message']:
                        answer = response_json['choices'][0]['message']['content']
                    else:
                        answer = f"API returned unexpected format: {json.dumps(response_json['choices'][0])}"
                else:
                    answer = f"API response error: {json.dumps(response_json)}"
                
                # Add the model's answer to the answers file
                with open("ans.md", 'a', encoding='utf-8') as f:
                    f.write(f"#### {model}\n\n```\n{answer}\n```\n\n")
                    
            except Exception as e:
                error_message = f"Error calling {model}: {str(e)}\nResponse: {response.text if 'response' in locals() else 'No response'}"
                print(error_message)
                
                # Log the error in the answers file
                with open("ans.md", 'a', encoding='utf-8') as f:
                    f.write(f"#### {model}\n\n```\nError: {error_message}\n```\n\n")
        
        # Add a separator after each question
        with open("ans.md", 'a', encoding='utf-8') as f:
            f.write("---\n\n")

print("Evaluation complete. Results saved to ans.md")

