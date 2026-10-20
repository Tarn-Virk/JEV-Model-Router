# 🧭 JEV Model Router

> 📺 **Watch the full walkthrough:** `[YouTube link coming soon]`

A Streamlit chat app where every prompt is **classified by [TypeSafe's JEV model](https://typesafe.ai) first**, then routed to the best-in-class LLM for that type of question. "Hi there" goes to a cheap, fast Gemini Flash. "Design me a horizontally scalable rate limiter" goes to Claude Opus. "Reverse a linked list in Python" goes to Claude Sonnet.

Each reply carries a badge — *(via gemini-3.5-flash • chit_chat • conf 0.77 • $0.0001)* — and a sidebar toggle lets you disable routing and send everything to Opus, so viewers can watch the cost difference live.

Built with **Streamlit**, the **TypeSafe SDK (via OpenRouter)**, and the **OpenAI SDK** (also pointed at OpenRouter, so Anthropic + Google + OpenAI all go through one key).

---

## 🎯 What it does

- You type a prompt in a Streamlit chat UI at `localhost:8501`
- **JEV classifies** the prompt into one of **six categories** with a confidence score
- A low-confidence `chit_chat` or `general_knowledge` guess gets **safely promoted** to a stronger category (so a borderline "hi" doesn't accidentally skip over a real question)
- The matching best-in-class model answers
- Running **cost, latency, and the chosen model** show up on every message
- A sidebar toggle disables routing → everything goes to Opus → the cost delta becomes obvious on screen

---

## 🧠 The six categories

| Category | What belongs here | Model | Provider |
|---|---|---|---|
| `chit_chat` | "hi", "thanks", greetings, one-liners | `google/gemini-3.5-flash` | Google |
| `coding` | Writing / reviewing / debugging / explaining code | `anthropic/claude-sonnet-5.5` | Anthropic |
| `reasoning_math` | Multi-step logic, calculations, proofs | `openai/gpt-5.6-sol` | OpenAI |
| `writing_creative` | Emails, posts, essays, copy | `anthropic/claude-opus-5.5` | Anthropic |
| `general_knowledge` | Short factual Q&A | `google/gemini-3.5-flash` | Google |
| `complex_analysis` | System design, synthesis, long-horizon planning | `anthropic/claude-opus-5.5` | Anthropic |

---

## 📁 Final project structure

```text
jev-video/
├── .env                  # OPENROUTER_API_KEY — gitignored
├── .env.example          # template with placeholder
├── .gitignore
├── pyproject.toml
├── uv.lock
├── README.md
├── .python-version
├── smoke.py              # Phase 5 — one JEV Noul test
├── test_router.py        # Phase 6 — test classify() over 6 prompts
├── test_caller.py        # Phase 7 — test one call per provider
├── test_route.py         # Phase 8 — end-to-end route() test
└── src/
    └── jev_video/
        ├── __init__.py
        ├── jev.py        # JEV wrapper (TypeSafe SDK → OpenRouter)
        ├── router.py     # classify() + route()
        ├── models.py     # category → model map + prices
        ├── caller.py     # calls any OpenRouter chat model via OpenAI SDK
        └── chat_app.py   # Streamlit chat UI
```

### 🗺️ What each file does

- **`jev.py`** — thin wrapper around the TypeSafe SDK, base URL pointed at OpenRouter. Exposes `ask_jev(state, questions)`.
- **`router.py`** — two functions:
  - `classify(prompt)` → asks JEV one `Choice` + one `Score` in a single call → returns `{category, raw_category, confidence, bumped}`
  - `route(prompt)` → chains `classify()` → `call_model()` → returns everything (category, model, text, tokens, cost, latency)
- **`models.py`** — single source of truth for which model handles which category + per-million-token prices (used for cost tracking).
- **`caller.py`** — one function `call_model(category, prompt)` → uses the OpenAI SDK pointed at OpenRouter, so Anthropic, OpenAI, and Google all go through one key.
- **`chat_app.py`** — Streamlit UI. Chat bubbles, model badge, running cost, baseline toggle.
- **`smoke.py` / `test_*.py`** — progressive smoke tests, one per layer of abstraction.

---

## 🧰 Prerequisites

Before you start, make sure you have:

| Tool | Why | Check with |
|---|---|---|
| **Python 3.10+** | Runs everything | `python3 --version` |
| **[uv](https://github.com/astral-sh/uv)** | Fast Python package + project manager | `uv --version` |
| **git** | Version control + GitHub push | `git --version` |
| **An OpenRouter API key** | One key fronts JEV + Anthropic + OpenAI + Google — sign up at [openrouter.ai](https://openrouter.ai) | — |
| A terminal | Linux, macOS, or **WSL** on Windows | — |
| A text editor | `vim`, VS Code, nano — pick your poison | — |

> 💡 If `uv` is missing, install it with:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

---

## Phase 1 — ✅ Does your machine have what we need?

Quick sanity check:

```bash
python3 --version
uv --version
```

Both should return a version number. If `uv` is missing, install it with the one-liner above.

---

## Phase 2 — 📦 Initialise a new project

```bash
uv init jev-video
cd jev-video
ls -la
```

**What `uv init` just scaffolded:**

| File / Folder | What it is | What it replaces / means |
|---|---|---|
| `pyproject.toml` | The project's identity card — name, version, Python required, dependencies | The modern standard that replaces `setup.py` and `requirements.txt`. One file does both jobs. |
| `.python-version` | A one-line file pinning the Python version (e.g. `3.12`) | Tells `uv` which Python to use. Teammates get the right version automatically. |
| `main.py` | A hello-world starter | Placeholder — we'll delete it later. |
| `README.md` | Front page on GitHub | Starts nearly empty. Fill in with what the project does. |
| `.gitignore` | Files git must never track | Pre-filled with Python junk (`__pycache__/`, `.venv/`, `*.pyc`). We'll add `.env` later. |
| `.git/` | Hidden folder holding the repo's history | `uv` silently ran `git init` for you. Use `ls -la` to see hidden files. |

Peek inside:

```bash
cat pyproject.toml
```

---

## Phase 3 — 🧪 Virtual environments + add dependencies

### 3a. What's a virtual environment?

Imagine two projects on your laptop:

- Project A needs `requests` version **2.20**
- Project B needs `requests` version **2.31**

Install globally with `pip` and you can only have one. Project A breaks when you upgrade for B. 💥

A **virtual environment** (venv) is a per-project folder holding:

- A private copy of Python
- A private copy of every package that project needs

Each project gets its own sealed box. No conflicts.

### 3b. Where does uv put it?

`uv` creates a hidden `.venv/` folder inside your project the moment you add the first dependency. You **never** activate it manually — `uv run <command>` auto-uses it.

### 3c. Add the dependencies

One command, all six packages:

```bash
uv add typesafe-sdk openai streamlit python-dotenv fastapi "uvicorn[standard]"
```

| Package | What it does | Where we use it |
|---|---|---|
| `typesafe-sdk` | JEV decision model client | `jev.py` |
| `openai` | OpenAI SDK — **also** used for OpenRouter (same wire format) | `caller.py` |
| `streamlit` | Dead-simple Python → web app framework | `chat_app.py` |
| `python-dotenv` | Loads your API key from `.env` into env vars | Everywhere |
| `fastapi` | Fast Python web framework | *(not used in this project — along for the ride)* |
| `uvicorn[standard]` | ASGI server to run FastAPI | *(not used here)* |

> 🧠 **ASGI = Asynchronous Server Gateway Interface.** A standard contract between a web server (uvicorn) and a Python web app (FastAPI). The server handles network + HTTP; the app holds your logic. ASGI is the handshake between them. "Async" matters because the older standard (WSGI) is synchronous — one worker blocks per request. ASGI servers handle many requests concurrently without stalling.

### 3d. Confirm it installed

```bash
cat pyproject.toml
uv run python -c "import typesafe_sdk; print(typesafe_sdk.__version__)"
```

You should see a version number print.

---

## Phase 4 — 🔐 Secrets, folder plan, and the JEV wrapper

### 4a. Create `.env` with your key

Create a file named `.env` in the project root containing exactly:

```env
OPENROUTER_API_KEY=sk-or-v1-your-real-key-here
```

### 4b. Verify the key is there without printing it

```bash
test -f .env && echo "exists" || echo "missing"
wc -l .env
```

### 4c. Protect `.env`

```bash
echo ".env" >> .gitignore
cat .gitignore
```

Confirm `.env` is listed.

### 4d. The folder plan

Here's where we're heading. Create files as we go — no need to make them all now.

```text
src/jev_video/
├── __init__.py          # (already exists, from uv init)
├── jev.py               # JEV wrapper — the SHARED piece
├── models.py            # category → model map
├── caller.py            # calls OpenRouter chat models
├── router.py            # router logic (classify + route)
└── chat_app.py          # Streamlit UI for the router
```

> 💡 **Big teaching point:** `jev.py` is the shared wrapper. In a sister project (shell-script guardrail), `jev.py` gets reused unchanged by a totally different stack. **One JEV wrapper, many jobs.**

### 4e. Create `src/jev_video/jev.py`

```python
"""Shared JEV wrapper used by the router (and any other JEV-powered feature)."""

import os
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient

# Load OPENROUTER_API_KEY from .env into environment variables.
load_dotenv()

# Create one TypeSafe client, pointed at OpenRouter's base URL.
# base_url="https://openrouter.ai/api" → the ONE line that redirects
# the SDK from TypeSafe-direct to OpenRouter.
_client = TypeSafeClient(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api",
)

# TypeSafe maps "jev-latest" to the current best JEV model.
JEV_MODEL = "jev-latest"


def ask_jev(state: str, questions: dict):
    """Send any mix of Choice/Noul/Score questions to JEV in one call.

    state: the thing being judged (a user prompt, a shell command, etc.)
    questions: dict of name → question object (Choice, Noul, or Score)
    """
    return _client.system_one(state, questions, model=JEV_MODEL)
```

Final sanity check:

```bash
cat .gitignore
```

Confirm `.env` is there.

---

## Phase 5 — 🚦 First real JEV call

A **smoke test** is a tiny script that proves nothing is on fire — the one call that confirms every piece from your `.env` key through the SDK through OpenRouter through JEV is wired up.

### 5a. Create `smoke.py` in the project root

```python
"""Smoke test: can we talk to JEV?"""
from typesafe_sdk import Noul
from jev_video.jev import ask_jev

# State is the actual query being judged.
# `is_trivial` is a Noul — yes/no — returns a probability between 0 and 1.
response = ask_jev(
    state="A user asked an AI assistant: what is 2+2?",
    questions={
        "is_trivial": Noul(instructions="Is this a trivial question for an AI to answer?"),
    },
)

answer = response.answers["is_trivial"]

# f"...{...:.3f}" → f-string with .3f meaning "format as a float with 3 decimal places"
print(f"Probability this is trivial: {answer.noul:.3f}")

# Tells you which exact JEV build served the request (useful for debugging).
print(f"Model: {response.model}")
```

### 5b. Run it

```bash
uv run python smoke.py
```

**Expected output:**

```text
Probability this is trivial: 0.9XX
Model: typesafe/jev-1.XX-...
```

A high number means JEV correctly judges "what is 2+2?" as a trivial AI question. ✅

---

## Phase 6 — 🧭 The router brain: classifying prompts

### 6a. The three JEV question types

| Type | What it does | Returns |
|---|---|---|
| `Noul` | Yes/no probability | float 0–1 |
| `Choice` | Pick ONE option from a labelled list | the chosen label (string) |
| `Score` | Rate on an ordered rubric | weighted position (float) |

For routing we need `Choice` (which category?) plus `Score` (how confident?).

### 6b. Create `src/jev_video/router.py`

Start with just the classifier — we'll bolt `route()` on in Phase 8.

```python
"""Classify an incoming prompt into one of our six routing categories."""

from typesafe_sdk import Choice, Score
from jev_video.jev import ask_jev

# The six labels. Keep this as the single source of truth —
# models.py will key off these exact strings.
CATEGORIES = {
    "chit_chat":         "Greetings, thanks, small talk, filler, or one-liners that don't ask for substantive help.",
    "coding":            "Writing, reviewing, debugging, or explaining code, SQL, shell commands, or config.",
    "reasoning_math":    "Problems that need step-by-step logic, calculations, proofs, or formal reasoning.",
    "writing_creative":  "Drafting emails, blog posts, marketing copy, essays, or any structured prose.",
    "general_knowledge": "Short factual questions a dictionary or encyclopedia would answer in one line.",
    "complex_analysis":  "Multi-step analysis, architecture, system design, synthesis, or long-horizon planning.",
}

CONFIDENCE_LEVELS = ["guessing", "unsure", "moderate", "confident", "certain"]
CONFIDENCE_THRESHOLD = 0.35   # below this → escalate to a safer category


def classify(prompt: str) -> dict:
    """Ask JEV which category this prompt belongs to, plus how sure it is."""
    response = ask_jev(
        state=f"A user sent this prompt to an AI assistant:\n\n{prompt}",
        questions={
            "category": Choice(
                instructions="Which category does this prompt belong to? Pick exactly one.",
                criteria=CATEGORIES,
            ),
            "confidence": Score(
                instructions="How confident are you in that category choice?",
                criteria=CONFIDENCE_LEVELS,
            ),
        },
    )

    raw_category = response.answers["category"].choice
    raw_score = response.answers["confidence"].score
    # Score returns a weighted position: 0.0 to len(levels)-1. Normalise to 0–1.
    confidence = raw_score / (len(CONFIDENCE_LEVELS) - 1)

    # Safety net: if JEV is shaky on a cheap category, promote it to a safer one.
    final_category, bumped = raw_category, False
    if confidence < CONFIDENCE_THRESHOLD and raw_category in ("chit_chat", "general_knowledge"):
        final_category = "complex_analysis"
        bumped = True

    return {
        "category": final_category,
        "raw_category": raw_category,
        "confidence": round(confidence, 2),
        "bumped": bumped,
    }
```

### 6c. Test it

Create `test_router.py` in the project root:

```python
"""Test the classifier with a variety of prompts."""

from jev_video.router import classify

prompts = [
    "hi there!",
    "write me a Python function to reverse a linked list",
    "if a train leaves at 8am going 60mph and another at 9am going 80mph, when do they meet?",
    "draft an email asking my boss for a raise",
    "capital of Japan?",
    "design a horizontally scalable rate limiter under network partition",
]

for p in prompts:
    result = classify(p)
    print(f"[{result['category']:<17}] conf={result['confidence']:.2f}  {p[:60]}")
```

Run it:

```bash
uv run python test_router.py
```

You should see each prompt routed into a sensible category with a confidence score.

---

## Phase 7 — 🗺️ Map categories to models + actually call them

### 7a. The OpenRouter + OpenAI SDK trick

Tiny thing that saves enormous amounts of code:

> **OpenRouter speaks the OpenAI wire format.**

That means we use the official OpenAI Python SDK to call Anthropic, Google, Meta, DeepSeek, Mistral — anyone on OpenRouter. **One SDK pattern. Thirty providers. One API key.**

What changes vs calling OpenAI directly:

- `base_url="https://openrouter.ai/api/v1"` instead of OpenAI's URL
- `api_key=OPENROUTER_API_KEY` instead of an OpenAI key
- `model="anthropic/claude-opus-5.5"` (or `"google/gemini-3.5-flash"`, etc.) — just a different string

### 7b. Create `src/jev_video/models.py`

Map each category to its best-in-class model + per-million-token prices.

```python
"""Map each router category to its best-in-class model + per-million-token prices.

Model slugs come from https://openrouter.ai/models. Verify current prices there
before publishing — OpenRouter updates them weekly.
"""

CATEGORY_TO_MODEL = {
    "chit_chat":         "google/gemini-3.5-flash",     # cheap, fast, fine for "hi"
    "coding":            "anthropic/claude-sonnet-5.5", # Anthropic strongest at code
    "reasoning_math":    "openai/gpt-5.6-sol",          # OpenAI strong on reasoning
    "writing_creative":  "anthropic/claude-opus-5.5",   # Anthropic best writing
    "general_knowledge": "google/gemini-3.5-flash",     # fast factual
    "complex_analysis":  "anthropic/claude-opus-5.5",   # long-horizon synthesis
}

# $ per 1 MILLION tokens. in = input (your prompt), out = output (the reply).
# PLACEHOLDER PRICES — verify on openrouter.ai/models before publishing.
PRICES = {
    "google/gemini-3.5-flash":     {"in": 0.16, "out": 0.63},
    "anthropic/claude-sonnet-5.5": {"in": 2.00, "out": 10.00},
    "openai/gpt-5.6-sol":          {"in": 2.00, "out": 10.00},
    "anthropic/claude-opus-5.5":   {"in": 4.00, "out": 20.00},
}
```

### 7c. Create `src/jev_video/caller.py`

The file that actually calls the model.

```python
"""Call any OpenRouter chat model via the OpenAI SDK."""

import os
from openai import OpenAI
from dotenv import load_dotenv
from jev_video.models import CATEGORY_TO_MODEL, PRICES

load_dotenv()

# Same OpenAI SDK — just pointed at OpenRouter.
_client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)


def call_model(category: str, prompt: str) -> dict:
    """Pick the model for this category, call it, return answer + usage + cost."""
    model = CATEGORY_TO_MODEL[category]

    response = _client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    usage = response.usage
    price = PRICES[model]
    cost = (
        usage.prompt_tokens * price["in"]
        + usage.completion_tokens * price["out"]
    ) / 1_000_000

    return {
        "model": model,
        "text": response.choices[0].message.content,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "cost_usd": round(cost, 6),
    }
```

### 7d. Test one call per provider

Create `test_caller.py`:

```python
"""Confirm we can call all three providers via one OpenRouter key."""

from jev_video.caller import call_model

tests = [
    ("chit_chat",      "Say hi in exactly 3 words."),
    ("coding",         "In Python, how do you reverse a list in one line?"),
    ("reasoning_math", "If 3x + 7 = 22, what is x? Just the number."),
]

for category, prompt in tests:
    result = call_model(category, prompt)
    print(f"\n[{category}]  via {result['model']}")
    print(f"  Prompt:  {prompt}")
    print(f"  Answer:  {result['text'].strip()}")
    print(f"  Tokens:  in={result['input_tokens']} out={result['output_tokens']}")
    print(f"  Cost:    ${result['cost_usd']:.6f}")
```

Run it:

```bash
uv run python test_caller.py
```

Three providers, one key. 🎉

---

## Phase 8 — 🔗 Glue it together: the `route()` function

All this does is chain `classify()` → `call_model()` into one function, so you can go from raw prompt to routed answer in one call.

### 8a. Why a glue function?

- Your Streamlit UI (next phase) doesn't want to call `classify`, then `call_model`, then merge the results itself.
- Any eval harness or test suite doesn't want that either.
- **One function. One prompt in. One dict out** with everything a caller could want.
- Bonus: this is where we add latency timing — the final cost + latency badge story.

### 8b. Update `src/jev_video/router.py`

Open the file and add these imports at the top:

```python
import time
from jev_video.caller import call_model
```

Then add this `route()` function at the bottom:

```python
def route(prompt: str) -> dict:
    """End-to-end: classify the prompt, then call the right model.

    Returns a dict with: category, raw_category, confidence, bumped,
    model, text, input_tokens, output_tokens, cost_usd,
    classify_ms, answer_ms.
    """
    t0 = time.perf_counter()
    decision = classify(prompt)
    t1 = time.perf_counter()
    answer = call_model(decision["category"], prompt)
    t2 = time.perf_counter()

    return {
        **decision,
        **answer,
        "classify_ms": round((t1 - t0) * 1000, 1),
        "answer_ms": round((t2 - t1) * 1000, 1),
    }
```

### 8c. The final `router.py` (reference)

Here's what the complete file should look like:

```python
"""Classify an incoming prompt and route it to the best model."""

import time

from typesafe_sdk import Choice, Score

from jev_video.jev import ask_jev
from jev_video.caller import call_model

# Single source of truth for category names. models.py keys off these strings.
CATEGORIES = {
    "chit_chat":         "Greetings, thanks, small talk, filler, or one-liners that don't ask for substantive help.",
    "coding":            "Writing, reviewing, debugging, or explaining code, SQL, shell commands, or config.",
    "reasoning_math":    "Problems that need step-by-step logic, calculations, proofs, or formal reasoning.",
    "writing_creative":  "Drafting emails, blog posts, marketing copy, essays, or any structured prose.",
    "general_knowledge": "Short factual questions a dictionary or encyclopedia would answer in one line.",
    "complex_analysis":  "Multi-step analysis, architecture, system design, synthesis, or long-horizon planning.",
}

CONFIDENCE_LEVELS = ["guessing", "unsure", "moderate", "confident", "certain"]
CONFIDENCE_THRESHOLD = 0.35


def classify(prompt: str) -> dict:
    """Ask JEV which category this prompt belongs to, plus how sure it is."""
    response = ask_jev(
        state=f"A user sent this prompt to an AI assistant:\n\n{prompt}",
        questions={
            "category": Choice(
                instructions="Which category does this prompt belong to? Pick exactly one.",
                criteria=CATEGORIES,
            ),
            "confidence": Score(
                instructions="How confident are you in that category choice?",
                criteria=CONFIDENCE_LEVELS,
            ),
        },
    )

    raw_category = response.answers["category"].choice
    raw_score = response.answers["confidence"].score
    confidence = raw_score / (len(CONFIDENCE_LEVELS) - 1)

    final_category, bumped = raw_category, False
    if confidence < CONFIDENCE_THRESHOLD and raw_category in ("chit_chat", "general_knowledge"):
        final_category = "general_knowledge"
        bumped = True

    return {
        "category": final_category,
        "raw_category": raw_category,
        "confidence": round(confidence, 2),
        "bumped": bumped,
    }


def route(prompt: str) -> dict:
    """End-to-end: classify the prompt, then call the right model."""
    t0 = time.perf_counter()
    decision = classify(prompt)
    t1 = time.perf_counter()
    answer = call_model(decision["category"], prompt)
    t2 = time.perf_counter()

    return {
        **decision,
        **answer,
        "classify_ms": round((t1 - t0) * 1000, 1),
        "answer_ms": round((t2 - t1) * 1000, 1),
    }
```

> 💡 **Why separate `classify_ms` and `answer_ms` instead of one total?** Keeping them apart tells a story: *"classification took 200ms, the actual answer took 3 seconds."* That builds trust — routing isn't the bottleneck, the model is.

### 8d. Test the full pipeline

Create `test_route.py`:

```python
"""End-to-end test: prompt in, routed answer out."""
import json
from jev_video.router import route

prompts = [
    "hi",
    "what is the capital of Japan?",
    "write me a one-line Python regex for a UK postcode",
    "if a train leaves at 8am going 60mph and another at 9am going 80mph, when do they meet?",
]

for p in prompts:
    print(f"\n{'='*70}\nPrompt: {p}")
    result = route(p)
    print(f"Category: {result['category']}  (conf {result['confidence']}, bumped={result['bumped']})")
    print(f"Model:    {result['model']}")
    print(f"Timing:   classify {result['classify_ms']}ms  +  answer {result['answer_ms']}ms")
    print(f"Cost:     ${result['cost_usd']:.6f}")
    print(f"Answer:   {result['text'][:200]}")
```

Run it:

```bash
uv run python test_route.py
```

---

## Phase 9 — 💬 Streamlit chat UI

**Streamlit** is a Python library that turns a script into a web page. Zero HTML, zero JavaScript, zero frontend knowledge. We write Python, it renders a chat.

### 9a. How Streamlit thinks (three concepts that trip beginners up)

- **Streamlit re-runs the whole script on every interaction.** Click a button → script runs top to bottom again. Weird at first, but means your UI is always in sync with your state.
- **`st.session_state`** → a dict that persists across re-runs. Needed for anything you want to remember (chat history, running cost).
- **Widgets return values.** `prompt = st.chat_input("...")` returns the user's typed text when they hit enter, or `None` otherwise.

That's enough to read any Streamlit code.

### 9b. Create `src/jev_video/chat_app.py`

```python
"""Streamlit chat UI showing JEV's live routing decisions and running cost."""

import streamlit as st

from jev_video.router import route
from jev_video.caller import call_model

st.set_page_config(page_title="JEV Model Router", page_icon="🧭")
st.title("🧭 JEV Model Router")
st.caption("Every prompt is classified by JEV and sent to the best model for the job.")

# ---------- Sidebar: toggle + running cost ----------
with st.sidebar:
    st.header("Settings")
    disable_routing = st.toggle(
        "Disable routing (all Opus)",
        value=False,
        help="Flip ON to send every prompt to Claude Opus 5.5 — the baseline.",
    )
    st.divider()
    if "total_cost" not in st.session_state:
        st.session_state.total_cost = 0.0
    st.metric("Session cost", f"${st.session_state.total_cost:.4f}")
    if st.button("Reset conversation"):
        st.session_state.messages = []
        st.session_state.total_cost = 0.0
        st.rerun()

# ---------- Chat history ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("caption"):
            st.caption(msg["caption"])

# ---------- Input + response ----------
if prompt := st.chat_input("Ask anything…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            if disable_routing:
                result = call_model("complex_analysis", prompt)
                model_name = result["model"].split("/")[-1]
                caption = f"via {model_name} • baseline (routing OFF) • ${result['cost_usd']:.4f}"
            else:
                result = route(prompt)
                model_name = result["model"].split("/")[-1]
                bump = f" • bumped from {result['raw_category']}" if result["bumped"] else ""
                total_ms = result["classify_ms"] + result["answer_ms"]
                caption = (
                    f"via {model_name} • {result['category']} • "
                    f"conf {result['confidence']}{bump} • "
                    f"${result['cost_usd']:.4f} • {total_ms:.0f}ms"
                )

        st.markdown(result["text"])
        st.caption(caption)
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["text"],
            "caption": caption,
        })
        st.session_state.total_cost += result["cost_usd"]
        st.rerun()
```

### 9c. Launch it

```bash
uv run streamlit run src/jev_video/chat_app.py
```

**What happens:**

- Streamlit starts a local web server on **http://localhost:8501**
- In native WSL this opens your Windows browser automatically; if not, `Ctrl`+click the URL in the terminal
- You'll see your chat UI

### 9d. Try these prompts in order

| Prompt | Expected badge |
|---|---|
| `hi` | 🟢 Gemini Flash (`chit_chat`) |
| `write me a Python regex for an email` | 🔵 Claude Sonnet (`coding`) |
| `draft me a one-paragraph email saying I need an extra week on a deadline` | 🟣 Claude Opus (`writing_creative`) |
| `capital of Argentina?` | 🟢 Gemini Flash (`general_knowledge`) |
| `design a horizontally scalable rate limiter under network partition` | 🟣 Claude Opus (`complex_analysis`) |

Flip the **"Disable routing (all Opus)"** toggle on the sidebar and watch the session cost climb on simple prompts. That's the demo.

Stop the server with `Ctrl+C` when you're done.

---

## Phase 10 — 📤 Push to GitHub

### 10a. Why bother?

- Your laptop isn't a backup. Dies today, project gone.
- GitHub = canonical copy + version history + a public link for the video description.
- Makes future lessons (shell guardrails, evals) cleaner — each half of the video is a commit viewers can inspect.

### 10b. Confirm `.env` is NOT about to be committed

**Most important git safety check.** Before anything else:

```bash
git status
```

Scan the output. **`.env` must NOT appear** anywhere in the list of files to be added. If it does, your `.gitignore` isn't working. Stop and fix.

Also:

```bash
cat .gitignore
```

Confirm `.env` is listed.

### 10c. First commit locally

```bash
git add .
git status
```

Look at the output. You should see `src/`, `pyproject.toml`, `uv.lock`, `smoke.py`, `test_router.py`, `test_route.py`, `test_caller.py`, `README.md`, `.gitignore`, `.python-version`. **No `.env`. No `.venv/`.**

If clean:

```bash
git commit -m "JEV model router with Streamlit chat UI"
```

> 📸 **What a commit is:** a snapshot of your project at this moment, with a message. Lives in the hidden `.git/` folder — totally local, nothing sent anywhere yet. List commits with `git log`.

### 10d. Create a GitHub repo

In your browser:

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `jev-model-router` (or whatever you prefer)
3. **Public** (so you can link it in the video description) or **Private** — your call
4. **Don't** tick "Add a README", "Add .gitignore", or "Add a license" — we already have those files locally, and ticking creates conflicts
5. Click **Create repository**

GitHub now shows you a page with instructions. Scroll to **"…or push an existing repository from the command line"** and copy those 3 lines.

### 10e. Push

Back in your terminal, paste the three lines GitHub showed you (replace `<your-username>`):

```bash
git remote add origin https://github.com/<your-username>/jev-model-router.git
git branch -M main
git push -u origin main
```

**What each does:**

- `git remote add origin <url>` → tells your local git "there's a copy of this living at this URL, call it `origin`"
- `git branch -M main` → renames the default branch to `main` (GitHub's convention; older git used `master`)
- `git push -u origin main` → actually uploads. `-u` sets `origin/main` as the default so future pushes are just `git push`

> 🔑 **Tip:** If GitHub asks for a password, generate a **Personal Access Token (PAT)** scoped to just this repo and paste it in place of your password. Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.

Refresh the GitHub page — your code is live. 🎉

---

## 🧪 Live demo tips

- Open **two tabs** of the chat UI side-by-side with routing OFF on one, ON on the other — ask the same prompt in both and watch the cost delta appear on screen.
- Try a prompt that **gets bumped** (e.g. "ok") — the badge shows `bumped from chit_chat` and the UI picks a safer model instead of blindly routing to the cheap one.
- Keep an eye on the `classify_ms` vs `answer_ms` split in the caption. JEV classification is usually ~200ms; the downstream model is usually seconds. Classification isn't the bottleneck.

---

## 🧱 Architecture at a glance

```text
┌────────────┐  prompt           ┌──────────────┐
│ Streamlit  │ ─────────────────▶│  router.py   │
│  chat UI   │                   │   route()    │
│            │◀──────────────────│              │
└────────────┘  text + badge     └──────┬───────┘
                                        │
                   ┌────────────────────┼────────────────────┐
                   ▼                                         ▼
          ┌────────────────┐                        ┌────────────────┐
          │  classify()    │                        │  call_model()  │
          │  via ask_jev() │                        │  via OpenAI SDK│
          └────────┬───────┘                        └────────┬───────┘
                   │                                         │
                   ▼                                         ▼
           ┌───────────────┐                         ┌──────────────┐
           │  JEV model    │                         │  OpenRouter  │
           │ (TypeSafe SDK)│                         │  (Anthropic, │
           └───────┬───────┘                         │   OpenAI,    │
                   │                                 │   Google …)  │
                   ▼                                 └──────────────┘
            OpenRouter base URL
```

**One OpenRouter API key** fronts both JEV (classification) and every downstream model (answering).

---

## 📜 License

MIT — do what you like, no warranty.

---

## 🙋 Credits

Built as part of the **de-tech-ify** YouTube series — demystifying IT and AI topics one project at a time.
