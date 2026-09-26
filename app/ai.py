import json
import httpx
from .classifier import classify
from .config import get_settings

async def ai_classify(short_description: str, description: str = ""):
    settings = get_settings()
    local = classify(short_description, description)
    if not settings.gemini_api_key:
        return {
            "provider": "local-fallback",
            "category": local.category,
            "subcategory": local.subcategory,
            "explanation": local.reason + " Gemini is not configured, so the deterministic project rules were used.",
            "confidence": local.confidence,
        }
    prompt = f"""Classify this school IT helpdesk ticket. Return ONLY JSON with keys category, subcategory, explanation, confidence. Allowed categories: Network, Hardware, Access, Performance. Allowed subcategories: Wi-Fi, Projector, Forgot Password, Slow Computer.\nShort description: {short_description}\nDescription: {description}"""
    url = f"{settings.gemini_base_url}/{settings.gemini_model}:generateContent"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, params={"key": settings.gemini_api_key}, json={"contents":[{"parts":[{"text":prompt}]}]})
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip().removeprefix("```json").removesuffix("```").strip()
            parsed = json.loads(text)
            return {
                "provider": "gemini",
                "category": parsed.get("category"),
                "subcategory": parsed.get("subcategory"),
                "explanation": parsed.get("explanation", ""),
                "confidence": float(parsed.get("confidence", 0.0)),
            }
    except Exception as exc:
        return {
            "provider": "local-fallback",
            "category": local.category,
            "subcategory": local.subcategory,
            "explanation": local.reason + f" Gemini call failed ({exc.__class__.__name__}); deterministic fallback used.",
            "confidence": local.confidence,
        }
