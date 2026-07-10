from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from google.genai import errors
from main import research_company, draft_outreach_email, chunk_text, set_product_docs

app = FastAPI(
    title="Research & Outreach Agent",
    description="Researches a company via live web search and drafts a personalized outreach email grounded in real product data.",
    version="1.0.0"
)

class ProductDocsRequest(BaseModel):
    product_info: str

@app.post("/set-product-docs", summary="Provide your own product info for personalized outreach")
def set_docs(request: ProductDocsRequest):
    documents = chunk_text(request.product_info)
    set_product_docs(documents)
    return {"status": "Product knowledge base updated", "chunks_stored": len(documents)}

class ResearchRequest(BaseModel):
    company_name: str
    your_company: str 
    your_product: str
    your_product_info: str 

@app.post("/generate", summary="Research a company and draft an outreach email")
def generate(request: ResearchRequest):
    try:
        documents = chunk_text(request.your_product_info)
        set_product_docs(documents)

        research = research_company(request.company_name)
        email = draft_outreach_email(
            request.company_name, research["summary"], request.your_company, request.your_product
        )
        return {
            "research_summary": research["summary"],
            "sources": research["sources"],
            "email": email
        }
    except errors.ClientError:
        raise HTTPException(status_code=429, detail="Rate limited — please try again shortly.")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")