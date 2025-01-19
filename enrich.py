# Set up OpenAI API Key
from openai import OpenAI
import time
import pandas as pd
import json

client = OpenAI(
    api_key="YOUR_API_KEY"
    )

# Function to query GPT-4o for company information
def get_company_info(company_name, description):
    """
    Query GPT-4o to retrieve detailed information about a company.

    Parameters:
        company_name (str): The name of the company.
        description (str): A brief description of the company.

    Returns:
        dict: A dictionary containing industries, offerings, and values of the company.
    """
    try:
        # Construct the prompt for GPT-4o
        prompt = (
            f'Please provide detailed information about the company "{company_name}" based on the following description:\n\n'
            f'Description: {description}\n\n'
            f'Include the following details:\n'
            f'1. The industries the company operates in.\n'
            f'2. A clear explanation of what they sell or their key offerings.\n'
            f'3. The company’s values or mission statement.\n\n'
            f'Response format (strict JSON):\n'
            f'{{\n'
            f'  "Industries": "List of industries",\n'
            f'  "What they sell": "Description of products/services",\n'
            f'  "Company values": "Values or mission statement"\n'
            f'}}'
        )

        # Call the GPT-4o API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o",
        )

        # Access the first choice's content
        response_content = response.choices[0].message.content  # Correct attribute-based access
        # Clean up response content for strict JSON parsing
        response_content = response_content.strip("```json").strip("```")

        # Safely parse the JSON response
        try:
            parsed_response = json.loads(response_content)  # Use json.loads for strict parsing
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse response as JSON: {response_content}") from e

        return parsed_response

    except Exception as e:
        print(f"Error processing {company_name}: {e}")
        return {
            "Industries": None,
            "What they sell": None,
            "Company values": None
        }

# Load your DataFrame (change for targets)
df = pd.read_csv("mechy_companies.csv")  # Replace with the path to your company data

# Initialize new columns
df["Industries"] = None
df["What they sell"] = None
df["Company values"] = None

# Loop through each company and query the API
for index, row in df.iterrows():
    print(f"Processing company: {row['Company Name']}")
    company_info = get_company_info(row['Company Name'], row['Description'])

    # Populate the DataFrame with the API results
    df.at[index, "Industries"] = company_info["Industries"]
    df.at[index, "What they sell"] = company_info["What they sell"]
    df.at[index, "Company values"] = company_info["Company values"]

    # Pause to respect rate limits
    time.sleep(1)  # Adjust based on API rate limits

# Save the updated DataFrame
df.to_csv("mechy_companies_with_info.csv", index=False)