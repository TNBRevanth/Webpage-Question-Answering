import requests

# URL of your Flask server
url = 'http://localhost:5000/answer'

# JSON data with URL and question
data = {
    'url': 'https://en.wikipedia.org/wiki/Generative_artificial_intelligence',
    'question': 'What are the concerns around Generative AI?'
}

# Send POST request
response = requests.post(url, json=data)

# Print the response
print(response.json())
