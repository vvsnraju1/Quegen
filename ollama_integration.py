import requests
import json


def get_mcq_question_answers(text):
    text=text.replace("\t"," ").replace("\n"," ").replace("\\","\\\\");
    print(f"text for ollama:: {text}")
    print("getting MCQ from ollama")
    url = 'http://203.112.158.82:11434/api/generate'
    payload={"model": "llama3.1:70b","prompt":"summarize the given text \""+text+"\"","stream": False}
    data = (json.dumps(payload,sort_keys=True)).encode('utf-8')

    response = requests.post(url, data=data)
    template = {
        "MCQ": [
            {
                "question":"",
                "options":["","","",""],
                "answer": "",
                "context":""
            }
          ]
        }
    
    if response.text and response.text!="" :
        jsonData=json.loads(response.text)
        val=jsonData['response'];
        val=val.replace("\t"," ").replace("\n"," ").replace("\\","\\\\");
        payload={"model": "llama3.1:70b","prompt":f"Generate 10 Multiple Choice Questions from given text \"{text}\". Respond in Json.\nUse the following template: {json.dumps(template)}.","stream": False,"format":"json"}
        data = (json.dumps(payload,sort_keys=True)).encode('utf-8')
        response = requests.post(url, data=data)
        if(response.text and response.text!=""):
            mcqJson=json.loads(response.text)
            mcqVal=mcqJson['response'];
            return json.loads(mcqVal.replace("\t","").replace("\n",""));
    print("recieved message")
    print("resp "+response.text)
    return response.content



def get_true_false_questions(text):
    text = text.replace("\t", " ").replace("\n", " ").replace("\\", "\\\\")
    print(f"text for ollama:: {text}")
    print("Getting True or False questions from Ollama")
    url = 'http://203.112.158.82:11434/api/generate'
    payload = {"model": "llama3.1:70b", "prompt": "summarize the given text \"" + text + "\"", "stream": False}
    data = (json.dumps(payload, sort_keys=True)).encode('utf-8')

    response = requests.post(url, data=data)
    template = {
        "TFQ": [
            {
                "question": "",
                "answer": "True",
                "context":""
            }
        ]
    }
    if response.text and response.text != "":
        jsonData = json.loads(response.text)
        val = jsonData['response']
        val = val.replace("\t", " ").replace("\n", " ").replace("\\", "\\\\")
        payload = {
            "model": "llama3.1:70b",
            "prompt": f"Generate 10 True or False questions from the given text \"{text}\". Respond in JSON.\nUse the following template: {json.dumps(template)}.",
            "stream": False,
            "format": "json"
        }
        data = (json.dumps(payload, sort_keys=True)).encode('utf-8')
        response = requests.post(url, data=data)
        if response.text and response.text != "":
            tfJson = json.loads(response.text)
            tfVal = tfJson['response']
            return json.loads(tfVal.replace("\t", "").replace("\n", ""))
    print("Received message")
    print("Response: " + response.text)
    return response.content

def get_saq_question_answers(text):
    # Prepare the text for the API request
    text = text.replace("\t", " ").replace("\n", " ").replace("\\", "\\\\")
    print(f"text for ollama:: {text}")
    
    # API URL and initial payload
    url = 'http://203.112.158.82:11434/api/generate'
    payload = {
        "model": "llama3.1:70b",
        "prompt": f"summarize the given text \"{text}\"",
        "stream": False
    }
    data = json.dumps(payload, sort_keys=True).encode('utf-8')
    
    # Send the first request
    response = requests.post(url, data=data)

    # Define the template for questions and context
    template = {
        "SAQ": [
            {
                "question": "",
                "context": ""
            }
        ]
    }
    
    # Check if the response contains data
    if response.text and response.text != "":
        jsonData = json.loads(response.text)
        val = jsonData['response']
        val = val.replace("\t", " ").replace("\n", " ").replace("\\", "\\\\")

        # Update the payload to generate questions with corresponding context
        payload = {
            "model": "llama3.1:70b",
            "prompt": (
                f"Generate 10 Short Answer Questions randomly from the given text \"{text}\". "
                f"For each question, mandatorily provide a context of 6-7 lines from the text, which includes the sentences that the question is based on. "
                f"The context should be detailed enough to give a clear understanding of the question. "
                f"Ensure the questions are not repetitive. Respond in JSON format.\n"
                f"Use the following template: {json.dumps(template)}."
            ),
            "stream": False,
            "format": "json"
        }
        data = json.dumps(payload, sort_keys=True).encode('utf-8')
        
        # Send the second request to generate questions and context
        response = requests.post(url, data=data)
        
        if response.text and response.text != "":
            saqJson = json.loads(response.text)
            saqVal = saqJson['response']
            return json.loads(saqVal.replace("\t", "").replace("\n", ""))
    
    # If there was an issue, return the raw response content
    print("received message")
    print("resp " + response.text)
    return response.content


def evaluate_user_answer(question, generated_answer, user_answer):

    prompt = (
        f"Question: \"{question}\"\n"
        f"Model Answer: \"{generated_answer}\"\n"
        f"User Answer: \"{user_answer}\"\n\n"
        "You are evaluating the User Answer based on its correctness and relevance to the Model Answer. "
        "Here’s how you should score:\n"
        "1. If the User Answer is correct and fully aligns with the Model Answer, give a score of 5.\n"
        "2. If the User Answer is partially correct but missing key details, give a score of 3 or 4.\n"
        "3. If the User Answer contradicts the Model Answer, or if it is incorrect, give a score of 1 or 2.\n"
        "4. If the User Answer is completely irrelevant or nonsensical, give a score of 0.\n"
        "Remember to be very stringent in scoring. Provide a score only."
    )
    
    # Define the API endpoint and payload
    url = 'http://203.112.158.82:11434/api/generate'
    payload = {
        "model": "llama3.1:70b",
        "prompt": prompt,
        "stream": False
    }
    
    
    # Convert payload to JSON
    try:
        data = json.dumps(payload, sort_keys=True).encode('utf-8')
    except TypeError as e:
        print(f"Serialization error: {e}")
        return None
    
    # Make the API request
    response = requests.post(url, data=data)
    
    # Process the response to extract the score
    if response.text and response.text != "":
        jsonData = json.loads(response.text)
        score = jsonData.get('response', '').strip()
        return score
    
    # Handle cases where no score is returned
    print("received message")
    print("resp " + response.text)
    return None

