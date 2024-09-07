import os
from dotenv import load_dotenv, find_dotenv
from predibase import Predibase

# Load environment variables
_ = load_dotenv(find_dotenv())

# Initialize Predibase
api_token = os.getenv('PREDIBASE_API_KEY')
pb = Predibase(api_token=api_token)

adapter_id = 'tour-assistant-model/14'
lorax_client = pb.deployments.client("solar-1-mini-chat-240612")

def get_completion(prompt):
    return lorax_client.generate(prompt, adapter_id=adapter_id, max_new_tokens=1000).generated_text

def generate_response(input_question):
    sys_str = "You are a helpful support assistant. Answer the following question."
    qa_list = [
        {"question": "What are the benefits of joining a union?", "answer": "Collective bargaining of salary."},
        {"question": "How much are union dues, and what do they cover?", "answer": "The union dues for our union is 3%."},
        {"question": "How does the union handle grievances and disputes?", "answer": "There will be a panel to oversee disputes"},
        {"question": "Will joining a union affect my job security?", "answer": "No."},
        {"question": "What is the process for joining a union?", "answer": "Please use the contact form."},
        {"question": "How do unions negotiate contracts with employers?", "answer": "Our dear leader will handle the negotiations."},
        {"question": "What role do I play as a union member?", "answer": "You will be invited to our monthly picnics"},
        {"question": "How do unions ensure that employers comply with agreements?", "answer": "We will have a monthly meeting for members"},
        {"question": "Can I be forced to join a union?", "answer": "What kind of questions is that! Of course no!"},
        {"question": "What happens if I disagree with the union's decisions?", "answer": "We will agree to disagree"}
    ]

    n_prompt_str = "\n"
    for qna in qa_list:
        ques_str = qna["question"]
        ans_str = qna["answer"]
        n_prompt_str += f"""
<|im_start|>system\n{sys_str}<|im_end|>
<|im_start|>question\n{ques_str}<|im_end|>
<|im_start|>answer\n{ans_str}<|im_end|>"""

    total_prompt = f"""{n_prompt_str}<|im_start|>system\n{sys_str}<|im_end|><|im_start|>question{input_question}\n<|im_end|><|im_start|>answer"""

    response = get_completion(total_prompt)
    return response