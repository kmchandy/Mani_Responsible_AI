from dotenv import load_dotenv
import os
import sys
import traceback
from typing import Dict
from openai import OpenAI
import json
# Set base directory for file paths.
BASE_DIR = os.path.expanduser("~/Documents/Mani_Responsible_AI")

"""
This script uses OpenAI's API to extract structured information from text.
It creates an agent with a persona specified in a file with path `file_path_for_agent_system_content`.
The agent returns the extracted structured data in JSON format that it extracts from
a text file with path 'file_path_for_agent_user_content'.

Usage:
    python extract_structure_from_text.py
"""


def get_text_from_file(file_path: str) -> str:
    """
    This is a utility function that reads the content of a file and
    returns it as a string.

    Parameters:
    -------------
    file_path: str : The path to the file from `~`

    Returns:
    -------------
    str : The content of the file.

    Example:
    ----------
    file_path = "~/Documents/Mani_Responsible_AI/data/agent_content/RescueEx1.md"

    """
    # Expand the tilde (~) to the full home directory path
    file_path = os.path.expanduser(file_path)
    # Read the file
    try:
        with open(file_path, "r") as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        traceback.print_exc()  # Print detailed exception information
        sys.exit(1)  # Exit the script with a non-zero status code
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()  # Print detailed exception information
        sys.exit(1)  # Exit the script with a non-zero status code


def get_structure_in_text(
    agent_system_content: str,
    agent_user_content: str,
) -> Dict:
    """
    This function creates an OpenAI agent with a persona specified by agent_system_content.
    The agent extracts structured information from the text specified by agent_user_content.

    Parameters:
    -------------
    agent_system_content: str, the persona of the agent.
    agent_user_content: str, the text from which the agent extracts structured information.

    Returns:
    -------------
    dict : A dictionary containing the extracted structured information.
    """

    load_dotenv()  # Load environment variables from .env file
    # Check if the OpenAI API key is loaded
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OpenAI API key is missing. Please set it in the .env file.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit the script with a non-zero status code

    # Make agent: Initialize OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Create a response of the agent
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": agent_system_content},
            {"role": "user", "content": agent_user_content},
        ],
        temperature=0.9,
    )

    # result is a text string obtained from the response object.
    result = response.choices[0].message.content
    # Clean the result string. Remove JSON block marker
    cleaned_result = result.strip("``[json").strip(
        "](http://_vscodecontentref_/1)``").strip()

    # Convert the cleaned JSON string to a Python dictionary
    try:
        result_dict = json.loads(cleaned_result)
        return result_dict
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def extract_structure_specified_in_files(
        file_path_for_agent_system_content: str,
        file_path_for_agent_user_content: str,
        file_path_for_agent_output: str) -> None:
    """
    This function creates an agent with a persona specified by the file with path:
    file_path_for_agent_system_content.
    The agent extracts structured information from the text specified by 
    the file with path: file_path_for_agent_user_content
    The structured information is saved in a file with path:
    file_path_for_agent_output.

    Parameters:
    -------------
    file_path_for_agent_system_content: str,
    file_path_for_agent_user_content: str,
    file_path_for_agent_output: str,

    Returns:
    -------------
    None 
    """

    result_str = get_structure_in_text(
        agent_system_content=get_text_from_file(
            file_path_for_agent_system_content),
        agent_user_content=get_text_from_file(
            file_path_for_agent_user_content),
    )
    # Write result_str to the file
    result_file_path = os.path.expanduser(file_path_for_agent_output)
    with open(result_file_path, "w") as result_file:
        json.dump(result_str, result_file, indent=4)
    print(f"text_structure written to {result_file_path}")


if __name__ == "__main__":
    # First agent in sequence carries out analysis.
    file_path_for_agent_system_content = "~/Documents/Mani_Responsible_AI/data/agent_system_content/mission_brief_01.txt"
    file_path_for_agent_user_content = "~/Documents/Mani_Responsible_AI/data/agent_user_content/RescueEx1.md"
    file_path_for_agent_output = "~/Documents/Mani_Responsible_AI/data/agent_output/output_mb01_Ex1.json"
    print(
        f'type(file_path_for_agent_system_content): {type(file_path_for_agent_system_content)}')
    extract_structure_specified_in_files(
        file_path_for_agent_system_content=file_path_for_agent_system_content,
        file_path_for_agent_user_content=file_path_for_agent_user_content,
        file_path_for_agent_output=file_path_for_agent_output,
    )
    # Print output of first analysis
    with open(os.path.expanduser(file_path_for_agent_output), "r") as file:
        agent_output = json.load(file)
    print("Extracted structure in first analysis: \n")
    print(json.dumps(agent_output, indent=4))

    # Next agent in sequence carries out analysis using output from first agent
    # as agent_user_content.
    file_path_for_agent_system_content = "~/Documents/Mani_Responsible_AI/data/agent_system_content/mission_brief_01_health.txt"
    file_path_for_agent_user_content = file_path_for_agent_output
    file_path_for_agent_output = "~/Documents/Mani_Responsible_AI/data/agent_output/output_mb01_Ex1_stage2.json"

    print(
        f'type(file_path_for_agent_system_content): {type(file_path_for_agent_system_content)}')
    extract_structure_specified_in_files(
        file_path_for_agent_system_content=file_path_for_agent_system_content,
        file_path_for_agent_user_content=file_path_for_agent_user_content,
        file_path_for_agent_output=file_path_for_agent_output,
    )
    # Print output of second analysis
    with open(os.path.expanduser(file_path_for_agent_output), "r") as file:
        agent_output = json.load(file)
    print("Extracted structure in second analysis: \n")
    print(json.dumps(agent_output, indent=4))
