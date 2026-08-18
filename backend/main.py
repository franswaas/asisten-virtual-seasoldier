"""
Asisten Virtual Seasoldier — FastAPI + Groq AI Backend.
Supports REST and SSE Streaming endpoints with Tool Calling & RAG.
"""

import asyncio
import json
import logging
import os
import re
import sys
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from groq import Groq

from config import (
    BASE_DIR, ENV,
    GROQ_API_KEY, PORT, SAVE_DIR, SYSTEM_PROMPT, GREETING, THANKS_REPLY,
    CORS_ORIGINS, IS_PRODUCTION,
    RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS,
    SESSION_TTL_SECONDS, SESSION_MAX_COUNT, SESSION_MAX_HISTORY,
    DAILY_LIMIT_MAX,
    GROQ_MODEL, GROQ_MODEL_FAST, GROQ_TEMPERATURE, GROQ_MAX_TOKENS,
)
from tools import (
    search_knowledge_base, list_available_topics, get_program_detail,
    get_chapter_info, get_engine,
)
from hooks import (
    log_interaction, log_error, log_feedback,
    get_daily_stats,
)

# ============================================
# LOGGING SETUP
# ============================================
logger = logging.getLogger("seasoldier_assistant")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# ============================================
# GROQ CLIENT & TOOLS
# ============================================
client = Groq(api_key=GROQ_API_KEY)

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Cari informasi dari Knowledge Base resmi Seasoldier Indonesia. "
                "Gunakan tool ini untuk menjawab pertanyaan tentang program konservasi (mangrove, terumbu karang, pohon), "
                "aksi bersih sampah (#BersihkanWarisanKita, Bersihkan Warungku, ecobrick), edukasi (Seasoldier Junior, Pondok Pemuda), "
                "kemitraan CSR perusahaan, gelang komitmen & merchandise, cara menjadi relawan, dan kontak 21+ chapter regional. "
                "WAJIB panggil tool ini sebelum menjawab pertanyaan apapun tentang Seasoldier."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Kata kunci pencarian spesifik. Contoh: 'penanaman mangrove', 'cara jadi relawan', 'program CSR', 'gelang komitmen', 'chapter Surabaya'",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Jumlah hasil relevan (default: 6, max: 10)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_available_topics",
            "description": "Daftar kategori topik informasi yang tersedia di Seasoldier.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_program_detail",
            "description": "Ambil informasi rincian program unggulan spesifik Seasoldier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "Nama program (contoh: 'mangrove', 'clean-up', 'junior', 'pondok pemuda', 'warungku', 'ecobrick', 'gelang', 'dolphin')",
                    },
                },
                "required": ["program_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_chapter_info",
            "description": "Ambil informasi mengenai Chapter Regional Seasoldier di kota/provinsi tertentu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Nama kota atau provinsi (contoh: 'Jakarta', 'Bandung', 'Bali', 'Surabaya', 'Medan', 'Makassar', 'Ambon')",
                    },
                },
                "required": ["region"],
            },
        },
    },
]

TOOL_MAP = {
    "search_knowledge_base": search_knowledge_base,
    "list_available_topics": list_available_topics,
    "get_program_detail": get_program_detail,
    "get_chapter_info": get_chapter_info,
}


def execute_tool(name: str, arguments_str: str) -> str:
    """Safely execute a tool function call."""
    if name not in TOOL_MAP:
        return f"Error: Tool '{name}' tidak ditemukan."
    try:
        args = json.loads(arguments_str) if arguments_str else {}
        return TOOL_MAP[name](**args)
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return f"Terjadi kesalahan saat memproses tool {name}: {e}"


# ============================================
# SESSION MANAGEMENT (In-Memory + Disk Sync)
# ============================================
sessions: dict[str, list[dict]] = {}
session_timestamps: dict[str, float] = {}


def _get_session_path(session_id: str) -> str:
    safe_id = re.sub(r"[^\w\-]", "", session_id)
    return os.path.join(SAVE_DIR, f"{safe_id}.json")


def load_session(session_id: str) -> list[dict]:
    """Load conversation history for a session."""
    _cleanup_expired_sessions()
    if session_id in sessions:
        session_timestamps[session_id] = time.time()
        return sessions[session_id]

    file_path = _get_session_path(session_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
                sessions[session_id] = history
                session_timestamps[session_id] = time.time()
                return history
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")

    sessions[session_id] = []
    session_timestamps[session_id] = time.time()
    return sessions[session_id]


def save_session(session_id: str, history: list[dict]) -> None:
    """Save conversation history to memory and disk."""
    if len(history) > SESSION_MAX_HISTORY * 2:
        history = history[-(SESSION_MAX_HISTORY * 2):]

    sessions[session_id] = history
    session_timestamps[session_id] = time.time()

    file_path = _get_session_path(session_id)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save session {session_id}: {e}")


def _cleanup_expired_sessions() -> None:
    """Remove expired sessions to free memory."""
    now = time.time()
    expired = [
        sid for sid, ts in session_timestamps.items()
        if now - ts > SESSION_TTL_SECONDS
    ]
    for sid in expired:
        sessions.pop(sid, None)
        session_timestamps.pop(sid, None)

    if len(sessions) > SESSION_MAX_COUNT:
        sorted_sids = sorted(session_timestamps.items(), key=lambda x: x[1])
        for sid, _ in sorted_sids[: len(sessions) - SESSION_MAX_COUNT]:
            sessions.pop(sid, None)
            session_timestamps.pop(sid, None)


# ============================================
# RATE LIMITING MIDDLEWARE
# ============================================
request_counts: dict[str, list[float]] = defaultdict(list)
daily_counts: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/stats", "/topics") or request.method == "OPTIONS":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Window rate limiting (per minute)
        timestamps = request_counts[client_ip]
        request_counts[client_ip] = [ts for ts in timestamps if now - ts < RATE_LIMIT_WINDOW_SECONDS]

        if len(request_counts[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"error": "Terlalu banyak permintaan. Mohon tunggu sebentar."},
            )

        # Daily rate limiting
        day_ts = daily_counts[client_ip]
        daily_counts[client_ip] = [ts for ts in day_ts if now - ts < 86400]
        if len(daily_counts[client_ip]) >= DAILY_LIMIT_MAX:
            return JSONResponse(
                status_code=429,
                content={"error": "Batas harian pertanyaan telah tercapai."},
            )

        request_counts[client_ip].append(now)
        daily_counts[client_ip].append(now)
        return await call_next(request)


# ============================================
# LIFESPAN & APP INIT
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-index Knowledge Base
    engine = get_engine()
    logger.info(f"Knowledge base loaded with {len(engine.chunks)} semantic chunks.")
    yield


app = FastAPI(
    title="Asisten Virtual Seasoldier API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)


# ============================================
# INTENT SHORT-CIRCUIT & SANITIZER
# ============================================
def sanitize_response_text(text: str) -> str:
    """Sanitize text to strictly remove forbidden words: yayasan, ai bot, bot."""
    if not text:
        return text
    # Replace 'Yayasan Seasoldier' -> 'Seasoldier'
    text = re.sub(r"\b(yayasan\s+seasoldier(\s+indonesia)?)\b", "Seasoldier Indonesia", text, flags=re.IGNORECASE)
    # Replace 'Yayasan' -> 'Organisasi'
    text = re.sub(r"\byayasan\b", "organisasi", text, flags=re.IGNORECASE)
    text = re.sub(r"\bYayasan\b", "Organisasi", text)
    # Replace 'ai bot' / 'ai-bot' -> 'asisten virtual'
    text = re.sub(r"\bai[-\s]bot\b", "asisten virtual", text, flags=re.IGNORECASE)
    # Replace standalone 'bot' -> 'asisten' (without touching words like 'botol')
    text = re.sub(r"\bbot\b", "asisten", text, flags=re.IGNORECASE)
    text = re.sub(r"\bBot\b", "Asisten", text)
    return text


def _check_simple_intent(question: str) -> str | None:
    q = question.strip().lower()
    if re.match(r"^(halo|hai|hi|hey|assalamualaikum|selamat (pagi|siang|sore|malam))[\s!.]*$", q):
        return sanitize_response_text(GREETING)
    if re.match(r"^(terima kasih|makasih|thanks|thank you|syukur)[\s!.]*$", q):
        return sanitize_response_text(THANKS_REPLY)
    return None


# ============================================
# ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    engine = get_engine()
    return {
        "status": "ok",
        "service": "Asisten Virtual Seasoldier",
        "chunks_indexed": len(engine.chunks),
        "model": GROQ_MODEL,
        "environment": ENV,
    }


@app.get("/topics")
async def get_topics():
    """Get available topics list."""
    return {"topics": list_available_topics()}


@app.get("/stats")
async def get_stats():
    """Get daily interaction statistics."""
    return get_daily_stats()


@app.post("/feedback")
async def handle_feedback(request: Request):
    """Log user feedback."""
    try:
        body = await request.json()
        session_id = body.get("session_id", "anonymous")
        message_id = body.get("message_id", "")
        rating = body.get("rating", "")
        comment = body.get("comment", "")
        log_feedback(session_id, message_id, rating, comment)
        return {"status": "ok", "message": "Terima kasih atas masukannya!"}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.delete("/session/{session_id}")
async def clear_session_endpoint(session_id: str):
    """Clear session history."""
    sessions.pop(session_id, None)
    session_timestamps.pop(session_id, None)
    file_path = _get_session_path(session_id)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
    return {"status": "ok", "message": "Sesi percakapan berhasil dihapus."}


# ============================================
# REST CHAT ENDPOINT
# ============================================
@app.post("/chat")
async def chat_endpoint(request: Request):
    """REST endpoint for Q&A with tool calling."""
    start_time = time.time()
    try:
        body = await request.json()
        question = body.get("question", "").strip()
        session_id = body.get("session_id") or str(uuid.uuid4())

        if not question:
            return JSONResponse(status_code=400, content={"error": "Pertanyaan tidak boleh kosong."})

        # Check simple greetings
        simple_reply = _check_simple_intent(question)
        if simple_reply:
            dur = int((time.time() - start_time) * 1000)
            log_interaction(session_id, question, simple_reply, GROQ_MODEL, dur, [])
            return {"answer": simple_reply, "session_id": session_id, "model": GROQ_MODEL}

        # Build messages with history
        history = load_session(session_id)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": question})

        # Step 1: Initial call with tools
        tool_calls_log = []
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            temperature=GROQ_TEMPERATURE,
            max_tokens=GROQ_MAX_TOKENS,
        )

        response_message = response.choices[0].message

        # Step 2: Handle tool calls if requested
        if response_message.tool_calls:
            messages.append(response_message)
            for tc in response_message.tool_calls:
                func_name = tc.function.name
                func_args = tc.function.arguments
                tool_result = execute_tool(func_name, func_args)
                tool_calls_log.append({
                    "tool": func_name,
                    "arguments": func_args,
                    "result_len": len(tool_result),
                })
                messages.append({
                    "tool_call_id": tc.id,
                    "role": "tool",
                    "name": func_name,
                    "content": tool_result,
                })

            # Step 3: Second call to generate final answer
            second_response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=GROQ_TEMPERATURE,
                max_tokens=GROQ_MAX_TOKENS,
            )
            final_answer = second_response.choices[0].message.content or ""
        else:
            final_answer = response_message.content or ""

        final_answer = sanitize_response_text(final_answer)

        # Update and save session
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": final_answer})
        save_session(session_id, history)

        duration_ms = int((time.time() - start_time) * 1000)
        log_interaction(session_id, question, final_answer, GROQ_MODEL, duration_ms, tool_calls_log)

        return {
            "answer": final_answer,
            "session_id": session_id,
            "model": GROQ_MODEL,
            "duration_ms": duration_ms,
            "tools_used": len(tool_calls_log),
        }

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        log_error(session_id if "session_id" in locals() else "unknown", "chat_exception", str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Maaf, terjadi kendala saat memproses jawaban. Silakan coba beberapa saat lagi."},
        )


# ============================================
# SSE STREAMING CHAT ENDPOINT
# ============================================
@app.post("/chat/stream")
async def chat_stream_endpoint(request: Request):
    """SSE streaming endpoint for token-by-token real-time responses."""
    try:
        body = await request.json()
        question = body.get("question", "").strip()
        session_id = body.get("session_id") or str(uuid.uuid4())

        if not question:
            return JSONResponse(status_code=400, content={"error": "Pertanyaan tidak boleh kosong."})

        async def event_generator():
            start_time = time.time()
            tool_calls_log = []

            # Check simple greeting
            simple_reply = _check_simple_intent(question)
            if simple_reply:
                yield f"data: {json.dumps({'type': 'token', 'content': simple_reply})}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
                dur = int((time.time() - start_time) * 1000)
                log_interaction(session_id, question, simple_reply, GROQ_MODEL, dur, [])
                return

            history = load_session(session_id)
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(history)
            messages.append({"role": "user", "content": question})

            # Call with tools
            try:
                first_response = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                    temperature=GROQ_TEMPERATURE,
                    max_tokens=GROQ_MAX_TOKENS,
                )
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Gagal menghubungi model: {e}'})}\n\n"
                return

            response_msg = first_response.choices[0].message

            if response_msg.tool_calls:
                yield f"data: {json.dumps({'type': 'tool_start', 'tools': [tc.function.name for tc in response_msg.tool_calls]})}\n\n"
                messages.append(response_msg)
                for tc in response_msg.tool_calls:
                    fname = tc.function.name
                    fargs = tc.function.arguments
                    tool_res = execute_tool(fname, fargs)
                    tool_calls_log.append({"tool": fname, "arguments": fargs, "result_len": len(tool_res)})
                    messages.append({
                        "tool_call_id": tc.id,
                        "role": "tool",
                        "name": fname,
                        "content": tool_res,
                    })

                # Stream final completion
                stream = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    temperature=GROQ_TEMPERATURE,
                    max_tokens=GROQ_MAX_TOKENS,
                    stream=True,
                )

                full_answer = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_answer += delta.content
                        yield f"data: {json.dumps({'type': 'token', 'content': delta.content})}\n\n"
            else:
                full_answer = response_msg.content or ""
                sanitized = sanitize_response_text(full_answer)
                yield f"data: {json.dumps({'type': 'token', 'content': sanitized})}\n\n"

            # Sanitize full answer before saving
            full_answer = sanitize_response_text(full_answer)

            # Save session
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": full_answer})
            save_session(session_id, history)

            dur_ms = int((time.time() - start_time) * 1000)
            log_interaction(session_id, question, full_answer, GROQ_MODEL, dur_ms, tool_calls_log)

            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id, 'duration_ms': dur_ms})}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        logger.error(f"Stream endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Maaf, terjadi kendala pada layanan streaming. Silakan coba beberapa saat lagi."}
        )


# ============================================
# STATIC FILES (FRONTEND)
# ============================================
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


# ============================================
# MAIN ENTRYPOINT
# ============================================
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Asisten Virtual Seasoldier on port {PORT}...")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
