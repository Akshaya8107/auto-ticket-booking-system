# Auto Ticket Classification using Flow Designer

A complete local implementation inspired by the supplied ServiceNow project documentation. The source project automates school IT incident classification using Flow Designer-style keyword rules, dependent Category/Subcategory choices, auto numbering, and caller email notification.

This implementation is a runnable local simulator, not a claim of direct ServiceNow integration. It preserves the documented behavior while adding a small optional Generative AI assistant for explanations/classification experiments.

## Features

- Create Incident Workflow tickets.
- Auto-number tickets as `INC000001`, `INC000002`, ...
- Caller name/email, short description, description.
- Category and Subcategory are automatically classified after creation.
- Keyword rules:
  - WiFi / Wi-Fi / Network -> Network / Wi-Fi
  - Projector / Hardware -> Hardware / Projector
  - Password / Login / Forgot password -> Access / Forgot Password
  - Slow / Hanging / Slow computer -> Performance / Slow Computer
- Dependent-choice API: subcategory options change with category.
- State: New, In progress, On hold, Resolved, Closed.
- Assigned group and assigned-to fields.
- Email notification log; optional SMTP delivery.
- Flow execution/audit history.
- Dashboard with category/subcategory/state counts.
- Optional Gemini LLM endpoint. The deterministic flow remains the source of truth for automatic ticket routing.
- Swagger/OpenAPI at `/docs`.
- Automated tests.

## Source requirements reproduced

The supplied document defines a custom `Incident Workflow` table, the fields Number, Caller, Category, Subcategory, Short Description, Description, State, Assigned Group and Assigned To, dependent Category/Subcategory choices, and a Flow named `Auto Classify School IT Tickets`. It classifies WiFi, Projector, Password/Login and Slow/Hanging issues and sends a caller email after classification.

## VS Code setup

### 1. Requirements

- Python 3.11 or newer recommended.
- VS Code.

### 2. Open the folder

Open this folder in VS Code:

`Auto-Ticket-Classification-Flow-Designer-Project`

### 3. Create a virtual environment

Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\\Scripts\\Activate.ps1
```

### 4. Configure environment

Copy `.env.example` to `.env`.

Gemini is optional. Leave `GEMINI_API_KEY` empty to use the local deterministic AI fallback.

### 5. Start the server

```powershell
uvicorn app.main:app --reload
```

Open:

- App: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

### 6. Run tests

```powershell
pytest -q
```

## API examples

Create a WiFi ticket:

```powershell
curl -X POST http://127.0.0.1:8000/api/tickets -H "Content-Type: application/json" -d '{"caller_name":"Anu","caller_email":"anu@example.edu","short_description":"WiFi not working in library","description":"Cannot connect to campus WiFi"}'
```

Expected classification:

- Category: Network
- Subcategory: Wi-Fi

Create a projector ticket:

```powershell
curl -X POST http://127.0.0.1:8000/api/tickets -H "Content-Type: application/json" -d '{"caller_name":"Meena","caller_email":"meena@example.edu","short_description":"Projector not turning on","description":"Classroom projector has no display"}'
```

Expected classification:

- Category: Hardware
- Subcategory: Projector

## ServiceNow deployment mapping

See `servicenow/01_setup.md` and `servicenow/02_flow_design.md` for exact mapping to the source documentation. The local app cannot export a real ServiceNow update set because that requires a ServiceNow instance.
