import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from prompts import system_prompt
from call_function import available_functions
from call_function import call_function


def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        sys.exit(1)


    client = genai.Client(api_key="AIzaSyD7mk4UCOkSR78fxmZzaAWDFJcbhdhvrLk")

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    
    try:
       x=0
       while x < 20:
          generate_content(client, messages, verbose)
          if not has_function_call and  global_response_text.strip() != "":
              print(global_response_text)
              break
          x+=1
    except Exception as e:
        print(e)      
    
def generate_content(client, messages, verbose):
    global global_response_text
    global  has_function_call
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
    has_function_call = bool(response.function_calls) 
    
    if not response.function_calls:
        global_response_text = response.text
        return response.text
    for i in response.function_calls:
        function_call_result =call_function(i, verbose=verbose)
        part = function_call_result.parts[0]
        if not part.function_response or not part.function_response.response:
             raise Exception("response doesn't exist!!")
        response_text =  part.function_response.response
        user_part = types.Part(text=str(response_text))
        messages.append(
        types.Content(role="user", parts=[user_part])
    )
  
        if verbose:
           print("Prompt tokens:", response.usage_metadata.prompt_token_count)
           print("Response tokens:", response.usage_metadata.candidates_token_count)
           print(f"-> {function_call_result.parts[0].function_response.response}")
        global_response_text = response.text
if __name__ == "__main__":
    main()
