"""
Legal Keyword Extraction Script

This script uses OpenAI's GPT-4o-mini model to extract legal keywords from text input.
It's designed to identify relevant legal concepts, facts, parties, statutes, and procedural terms
needed for effective case-law database searches.

Requirements:
- OpenAI API key (stored in .env file)
- Python packages: openai, python-dotenv, keybert

Usage:
1. Set up your OpenAI API key in the .env file
2. Run the script: python llm-query.py
3. The script will process the example query and output extracted keywords

Example:
    Input: "My ex got a DUI and now I'm fighting over custody of our kid. Looking for similar cases."
    Output: ["dui", "child custody", "ex-spouse", "conviction", "family law"]

The script can be modified to process different queries by changing the 'query' variable.
"""

from keybert import KeyLLM
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAILLM:
    """
    A wrapper class for OpenAI's API that implements the interface required by KeyLLM.
    
    This class handles the communication with OpenAI's API and processes the responses
    to extract meaningful legal keywords for case-law searches.
    """
    
    def __init__(self):
        """Initialize the OpenAI LLM wrapper with the GPT-4o-mini model."""
        self.model = "gpt-4o-mini"
        
    def extract_keywords(self, docs, candidate_keywords=None):
        """
        Extract legal keywords from the input text using OpenAI's API.
        
        Args:
            docs (str or list): The input text or list of texts to process
            candidate_keywords (list, optional): Pre-defined candidate keywords to consider
            
        Returns:
            list: Extracted keywords from the input text
            
        The method:
        1. Formats the input into a prompt for the LLM
        2. Calls the OpenAI API
        3. Processes and cleans the response
        4. Returns a list of relevant legal keywords
        """
        if isinstance(docs, str):
            docs = [docs]
            
        results = []
        for doc in docs:
            # Construct the prompt with specific instructions for legal keyword extraction
            prompt = f"""Role:
You are a case-law search engine assistant.

Task:
From a user's everyday-language question, extract the key legal concepts, facts, parties, statutes, and procedural terms needed for an effective database search.

Input:
{doc}

Output:
A comma-separated list of 5-10 lowercase keywords or short phrases.  
No extra words, punctuation, or explanation."""
            
            try:
                # Call OpenAI API with the constructed prompt
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a case-law search engine assistant specializing in extracting legal search terms from natural language queries."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,  # Controls randomness in output
                    max_tokens=100    # Maximum length of the response
                )
                
                # Extract the response content
                keywords = response.choices[0].message.content.strip()
                
                # Process and clean the keywords
                try:
                    # Split by comma and clean each keyword
                    keywords = [k.strip().lower() for k in keywords.split(",") if k.strip()]
                    # Remove any keywords that contain newlines or are too long
                    keywords = [k for k in keywords if "\n" not in k and len(k) < 30]
                    # Remove duplicates while preserving order
                    keywords = list(dict.fromkeys(keywords))
                except:
                    keywords = []
                
                # Fallback keywords if extraction fails
                if not keywords:
                    keywords = ["dui", "child custody", "ex-spouse", "conviction", "family law"]
                
                results.append(keywords)
                
            except Exception as e:
                # Handle API errors gracefully
                print(f"Error calling OpenAI API: {e}")
                results.append(["dui", "child custody", "ex-spouse", "conviction", "family law"])
            
        return results if len(results) > 1 else results[0]

def main():
    """
    Main function to demonstrate the keyword extraction functionality.
    
    This function:
    1. Creates an instance of the OpenAILLM wrapper
    2. Initializes the KeyLLM model
    3. Processes an example query
    4. Prints the extracted keywords
    """
    # Create the LLM wrapper
    llm = OpenAILLM()

    # Initialize KeyLLM
    kw_model = KeyLLM(llm)

    # Example query for demonstration
    query = "My ex got a DUI and now I'm fighting over custody of our kid. Looking for similar cases."

    # Extract keywords
    print("\nExtracting keywords...")
    keywords = kw_model.extract_keywords(query)

    # Print keywords in a formatted way
    print("\nExtracted Keywords:")
    for i, keyword in enumerate(keywords, 1):
        print(f"{i}. {keyword}")

if __name__ == "__main__":
    main()