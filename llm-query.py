"""
Legal Keyword Extraction Script

This script uses OpenAI's API to extract legal keywords from text input.
It returns a simple set of keywords suitable for database queries.

Requirements:
- OpenAI API key (stored in .env file)
- Python packages: openai, python-dotenv

Usage:
1. Set up your OpenAI API key in the .env file
2. Run the script: python llm-query.py
3. The script will process the input query and output a JSON array of keywords

Example:
    Input: "My ex got a DUI and now I'm fighting over custody of our kid."
    Output: ["dui", "child custody", "ex-spouse", "parental rights", "family law"]
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_keywords(query: str) -> set[str]:
    """
    Extract legal keywords from a natural language query.
    Returns a set of lowercase keywords.
    
    Args:
        query: Natural language query about a legal situation
        
    Returns:
        set: A set of lowercase legal keywords
    """

    prompt = f"""Role: You are a case-law search engine assistant.

    Task: From the user's question, extract 5-10 key legal search terms.

    Requirements:
    - Return ONLY a JSON array of lowercase keywords
    - No explanations or other text
    - Each term should be specific and useful for legal search
    - Avoid generic terms like "case" or "law" unless part of a specific phrase

    Input: {query}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a legal keyword extractor. Respond only with a JSON object containing an array of keywords under the 'keywords' key."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4  # Lower temperature for more consistent output
        )
        
        # Get the response content
        content = response.choices[0].message.content
        print(f"Raw response: {content}")
        
        # Parse the JSON response
        response_data = json.loads(content)
        
        # Extract keywords from the response
        if isinstance(response_data, dict) and 'keywords' in response_data:
            keywords = response_data['keywords']
        elif isinstance(response_data, list):
            keywords = response_data
        else:
            print("Unexpected response format. Using empty set.")
            return set()
            
        return set(keywords)  # Convert to set to remove any duplicates
        
    except Exception as e:
        print(f"Error in keyword extraction: {e}")
        return set()

def main():
    """Process example query and display results."""
    # Example query
    query = "My ex got a DUI and now I'm fighting over custody of our kid. Looking for similar cases."

    # Extract keywords
    print("\nExtracting keywords...")
    keywords = extract_keywords(query)

    # Print keywords as JSON array
    print("\nExtracted Keywords:", json.dumps(list(keywords), indent=2))

if __name__ == "__main__":
    main()