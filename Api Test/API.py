import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from transformers import pipeline
import re

# Initialize Flask app
app = Flask(__name__)

# Initialize question answering pipeline
qa_pipeline = pipeline("question-answering")

@app.route('/answer', methods=['POST'])
def answer_question():
    # Get data from the request
    data = request.get_json()
    
    # Extract URL and question from the request
    url = data.get("url")
    question = data.get("question")
    
    # Retrieve relevant webpage sections
    webpage_sections = retrieve_relevant_sections(url, question)
    
    # Perform question answering for each section
    answers = []
    for section_content in webpage_sections:
        answer = perform_question_answering(section_content, question)
        if answer != "I don't know the answer":
            answers.append(answer.strip())  # Remove leading and trailing whitespace
        
    # Concatenate all relevant answers into a single paragraph
    combined_answer = " ".join(answers)
    
    # Return the combined answer
    if combined_answer:
        return jsonify({"answer": combined_answer})
    else:
        return jsonify({"answer": "I don't know the answer"})

def retrieve_relevant_sections(url, question):
    try:
        # Fetch webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        
        # Parse webpage content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract relevant sections from the webpage based on semantic analysis and keyword matching
        webpage_sections = []
        webpage_text = soup.get_text()
        
        # Extract headings and subheadings
        headings = [tag.text.strip() for tag in soup.find_all(re.compile(r'^h[1-6]$'))]
        
        # Extract lists
        lists = [tag.text.strip() for tag in soup.find_all(['ul', 'ol'])]
        
        # Combine headings and lists to form potential sections
        potential_sections = headings + lists
        
        # Filter potential sections based on keyword matching with the question
        relevant_sections = [section for section in potential_sections if any(keyword in section.lower() for keyword in question.lower().split())]
        
        # Add entire visible text as a fallback option
        relevant_sections.append(webpage_text)
        
        return relevant_sections
    except Exception as e:
        print(f"Error fetching webpage content: {e}")
        return []

def perform_question_answering(content, question):
    if not content:
        return "I don't know the answer"

    try:
        # Perform question answering using transformer pipeline
        result = qa_pipeline(question=question, context=content, topk=3)  # Retrieve top 3 answers
        
        # Check if the answer is found
        if result:
            return result[0]["answer"]  # Return the top answer
        else:
            return "I don't know the answer"
    except Exception as e:
        print(f"Error performing question answering: {e}")
        return "I don't know the answer"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
