import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def research_company(company_name: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Research {company_name}. Summarize 2-3 recent, 
        notable, verifiable developments relevant to a B2B sales outreach context.""",
        config={"tools": [{"google_search": {}}]}
    )
    return response.text


def draft_outreach_email(company_name: str, research_summary: str, your_company: str, your_product: str) -> str:
    prompt = f"""You are a sales rep at {your_company}, which sells {your_product}.
You are writing a cold outreach email to a prospect at {company_name} (a potential customer, not a competitor or partner).

Research on {company_name} (the prospect, NOT your own company):
{research_summary}

Write a short, personalized outreach email (under 120 words) from a rep at {your_company}, reaching out to someone at {company_name}.
Reference one specific, relevant detail from the research naturally — not as a list, and not overly flattering.
End with a soft call to action (e.g., suggesting a short call)."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


if __name__ == "__main__":
    try:
        your_company = "CompanyX"
        your_product = "ProductX"
        company = input("Company name: ")
        research = research_company(company)
        print("\n--- Research ---\n", research)

        email = draft_outreach_email(company, research, your_company, your_product)
        print("\n--- Draft Email ---\n", email)

    except errors.ClientError:
            print("Assistant: I'm getting rate-limited right now — please wait a moment and try again.\n")