import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def extract_structured_json(unstructured_text: str):
    system_prompt = """
    You are an automated Data Extraction Engine.
    Your task is to extract information from unstructured engineering fault logs into a strict JSON object.

    OUTPUT RULES:
    - Return ONLY valid JSON.
    - No conversational preambles, post-explanations, or polite text.
    - Do NOT wrap the JSON in markdown backticks.
    - If a field cannot be determined from the text, set its value to null.

    REQUIRED JSON SCHEMA:
    {
      "incident_id": "string or null",
      "equipment_name": "string",
      "failure_type": "string",
      "severity": "string (CRITICAL, MAJOR, MINOR)",
      "affected_subsystems": ["list of strings"],
      "recommended_action": "string"
    }
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": unstructured_text}
            ],
            temperature=0.0,
            max_tokens=300
        )

        raw_output = response.choices[0].message.content.strip()

        cleaned_output = raw_output.replace(
            "```json", ""
        ).replace(
            "```", ""
        ).strip()

        parsed_json = json.loads(cleaned_output)

        print(
            "\n[SUCCESS] Programmatic Validation Passed! "
            "Valid JSON Object Created:"
        )

        # Print formatted JSON
        print(json.dumps(parsed_json, indent=4))

        # Save JSON to output.json
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, indent=4)

        print("\nSaved to output.json")

        return parsed_json

    except json.JSONDecodeError as e:
        print(f"\n[FAILED] Output failed JSON validation test: {e}")

    except Exception as e:
        print(f"\nAn error occurred during API execution: {e}")


if __name__ == "__main__":

    sample_log = """
    URGENT LOG ENTRY - 02-AUG-2026 14:22 UTC
    System alert raised on High-Pressure Boiler Unit #4. Thermal sensors detected 
    overheating in the primary coolant intake loop and pressure relief valve B. 
    Operator logged issue under INC-88201. Severity classified as CRITICAL. 
    Immediate shutdown initiated and technician dispatch required to replace intake seals.
    """

    extract_structured_json(sample_log)