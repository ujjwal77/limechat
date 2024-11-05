import os
from dotenv import load_dotenv
import requests
import json
import openai

# Load environment variables
load_dotenv()

SERPAPI_KEY = os.getenv('SERPAPI_KEY')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY

class PerplexityQNA:
    def __init__(self):
        self.serpapi_key = SERPAPI_KEY
        self.client = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            system_prompt=f"The following text is a prompt for generating an answer to a user's query. The generated answer should be concise, accurate, and well-structured. It should incorporate information from the provided search results. Do not include any external sources or citations.",
            temperature=0.7,
            top_p=1,
            max_tokens=200,
            stream=False,
            stop=["\n\n", "\n"]
        )

    def perform_serpapi_search(self, query):
        """Perform a search using SerpApi based on the given query."""
        url = "https://serpapi.com/search.json"
        params = {
            "q": query,
            "api_key": self.serpapi_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()

    def process_search_results(self, results):
        summaries = []
        for item in results['organic_results']:
            summaries.append({
                "title": item['title'],
                "link": item['link'],
                "snippet": item['snippet']
            })
        
        return "\n".join([f"{summary['title']}: {summary['snippet']} ({summary['link']})" for summary in summaries])

    def generate_answer(self, query, results):
        prompt = f"""Generate a concise answer to the following query:
        {query}

        Based on the following search results:
        {results}

        Do not include any external sources or citations."""

        response = self.client.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            top_p=1,
            max_tokens=200,
            stream=False,
            stop=["\n\n", "\n"]
        )
        
        return response.choices[0].message.content.strip()

    def perplexity_qna(self):
        while True:
            query = input("Enter your query (type 'exit' to quit): ")
            if query.lower() == 'exit':
                break
            
            try:
                print('start')
                search_results = self.perform_serpapi_search(query)
                print(search_results)
                # break
                
                summary = self.process_search_results(search_results)
                
                answer = self.generate_answer(query, summary)
                
                print("\nAnswer:")
                print(answer)
                print("\nSources:")
                print(summary)
            except Exception as e:
                print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    perplexity_qna = PerplexityQNA()
    perplexity_qna.perplexity_qna()


