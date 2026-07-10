# Autonomous Research & Outreach Agent

Give it a company name — it researches that company using live web search, then drafts a personalized cold outreach email grounded in real, verified facts about both the prospect and your own product.

**Live demo:** [ai-project-research-agent.onrender.com](https://ai-project-research-agent.onrender.com) — try it with a real company name (note: free-tier hosting spins down after inactivity, so the first request may take 30-60+ seconds)

## Why I built this

My first project (a [Sales Lead AI Assistant](https://github.com/Anshulmohan27/sales_lead_ai_assistant)) worked with static, pre-loaded data. This project pushes further: an agent that autonomously researches live, current information about a real company, then reasons about *why* that information matters to a specific product — the kind of work a sales rep or SDR spends real hours on manually.

## How it works

1. **Research step** — the model is given Gemini's built-in web search tool and asked to summarize 2-3 recent, verifiable developments about the target company. The model decides its own search queries (often 2-3 different angles per company) and returns grounding metadata with real source URLs.
2. **Custom product knowledge base** — the user provides their own product description (any product, any company — not hardcoded). This text is chunked and stored in a ChromaDB vector collection at request time.
3. **Angle + email step** — the model is given the research summary, plus a mandatory tool call to verify real product details against that knowledge base. It must first articulate a *specific* connection between the research and the product before writing the email, rather than jumping straight to generic copy.
4. Both the source citations and the final email are returned to the user, with sources rendered as clickable links.

*Known limitation:* the product knowledge base is a single shared collection, rebuilt on every `/generate` request. If two users hit the API at the same moment with different products, there's a race condition where one request's data could be overwritten mid-request by another. A production version would need per-request or per-session isolated collections rather than one shared global one — the same class of limitation as the shared chat session in my first project.

## A real bug I caught and fixed

Early on, the agent had a tool available to verify real product details — but wasn't *required* to use it. Testing surfaced a subtle hallucination: the agent picked a research angle (device security), then confidently invented a product description that would fit that angle, rather than checking what the product actually does. The output read fluently and would pass a casual review.

The fix: making the tool call explicitly mandatory ("you MUST call search_product_docs before describing any capability"), not just available. This is a good example of why giving a model access to a tool isn't the same as ensuring it uses it — a distinction that matters a lot for anything customer-facing.

## Tech stack

- **Google Gemini API** (`google-genai`) — LLM calls, built-in web search grounding, function calling
- **ChromaDB** — vector database for verified product knowledge
- **FastAPI** — REST API (`POST /generate`) serving research + sources + email
- **python-dotenv** — safe API key management

## Running it locally

```bash
git clone https://github.com/Anshulmohan27/AI_Project_Research_Agent.git
cd AI_Project_Research_Agent
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your-key-here
```

Then run:
```bash
uvicorn api:app --reload
```
Visit `http://127.0.0.1:8000/` for the web UI.

## What I'd build next

- Per-request/session isolated product knowledge base instead of one shared global collection (see known limitation above)
- Add a "regenerate with a different angle" option
- Batch mode: research and draft for a list of companies at once
- Verify numeric/dated claims from research against source pages before including them in the email

## About me

Transitioning from a 6+ year sales and marketing background into AI engineering. This project builds on the tool-use and RAG patterns from my first project, adding live web grounding and a more autonomous, multi-step reasoning flow.
