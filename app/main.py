from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .db import init_db
from .schemas import TicketCreate, TicketUpdate, AIRequest, Ticket, ClassificationResult, AIResponse, CATEGORIES, DEPENDENCIES, STATES
from .services import create_ticket, get_ticket, list_tickets, update_ticket, dashboard, history, email_history
from .classifier import classify
from .ai import ai_classify

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins if origins != ["*"] else ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.get("/api/metadata")
def metadata():
    return {"categories": CATEGORIES, "dependencies": DEPENDENCIES, "states": STATES}

@app.post("/api/tickets", response_model=dict, status_code=201)
def create(payload: TicketCreate):
    if payload.state not in STATES:
        raise HTTPException(400, "Invalid state")
    ticket, classification, email_status = create_ticket(payload)
    return {"ticket": ticket, "classification": classification.model_dump(), "email_status": email_status}

@app.get("/api/tickets", response_model=list[dict])
def tickets():
    return list_tickets()

@app.get("/api/tickets/{ticket_id}")
def ticket(ticket_id: int):
    result = get_ticket(ticket_id)
    if not result:
        raise HTTPException(404, "Ticket not found")
    return result

@app.patch("/api/tickets/{ticket_id}")
def patch(ticket_id: int, payload: TicketUpdate):
    try:
        result = update_ticket(ticket_id, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    if not result:
        raise HTTPException(404, "Ticket not found")
    return result

@app.get("/api/tickets/{ticket_id}/history")
def ticket_history(ticket_id: int):
    if not get_ticket(ticket_id):
        raise HTTPException(404, "Ticket not found")
    return history(ticket_id)

@app.get("/api/dependencies/{category}")
def dependencies(category: str):
    return {"category": category, "subcategories": DEPENDENCIES.get(category, [])}

@app.post("/api/classify", response_model=ClassificationResult)
def deterministic_classify(payload: AIRequest):
    return classify(payload.short_description, payload.description)

@app.post("/api/ai/classify", response_model=AIResponse)
async def llm_classify(payload: AIRequest):
    return await ai_classify(payload.short_description, payload.description)

@app.get("/api/dashboard")
def dashboard_api():
    return dashboard()

@app.get("/api/emails")
def emails():
    return email_history()
