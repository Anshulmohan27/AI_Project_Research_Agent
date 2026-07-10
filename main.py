import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors
import chromadb

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def research_company(company_name: str) -> dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Research {company_name}. Summarize 2-3 recent, notable, verifiable developments relevant to a B2B sales outreach context.",
        config={"tools": [{"google_search": {}}]}
    )

    sources = []
    metadata = response.candidates[0].grounding_metadata
    if metadata and metadata.grounding_chunks:
        for chunk in metadata.grounding_chunks:
            sources.append({"title": chunk.web.title, "url": chunk.web.uri})

    return {"summary": response.text, "sources": sources}

chroma_client = chromadb.Client()
product_specifications = chroma_client.get_or_create_collection(name="product_specifications")

def set_product_docs(documents: list[str]):
    """Replace the product knowledge base with new documents."""
    global product_specifications
    chroma_client.delete_collection(name="product_specifications")
    product_specifications = chroma_client.create_collection(name="product_specifications")
    ids = [f"doc{i}" for i in range(len(documents))]
    product_specifications.add(documents=documents, ids=ids)

def chunk_text(raw_text: str) -> list[str]:
    return [line.strip() for line in raw_text.split("\n") if line.strip()]

def search_product_docs(question: str) -> str:
    """Search product knowledge base (pricing, features, policies) for relevant info."""
    results = product_specifications.query(query_texts=[question], n_results=2)
    return "\n".join(results["documents"][0])

def draft_outreach_email(company_name: str, research_summary: str, your_company: str, your_product: str) -> str:
    prompt = f"""You are a sales rep at {your_company}, which sells {your_product}.
You are writing a cold outreach email to a prospect at {company_name} (a potential customer, not a competitor or partner).

Research on {company_name} (the prospect, NOT your own company):
{research_summary}

IMPORTANT: Before writing anything about {your_product}'s capabilities, you MUST call search_product_docs to verify what it actually does. Do not describe or assume any product features, pricing, or capabilities that aren't confirmed by that tool.

Step 1: In 1-2 sentences, identify ONE specific angle where something in the research above creates an actual need or opportunity for {your_product} — grounded only in verified product details, not assumptions.

Step 2: Write a short outreach email (under 120 words) built around that specific angle. Reference the research naturally, not as a list. End with a soft call to action.

Format your response as:
ANGLE: <step 1 answer>
EMAIL: <step 2 answer>"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config = {"tools": [search_product_docs]}
    )
    return response.text


if __name__ == "__main__":
    try:
        your_company = ""
        your_product = ""
        company = input("Company name: ")
        research = research_company(company)
        print("\n--- Research ---\n", research["summary"])
        print("\n--- Sources ---")
        for s in research["sources"]:
            print(f"- {s['title']}: {s['url']}")

        email = draft_outreach_email(company, research["summary"], your_company, your_product)
        print("\n--- Draft Email ---\n", email)

    except errors.ClientError:
            print("Assistant: I'm getting rate-limited right now — please wait a moment and try again.\n")