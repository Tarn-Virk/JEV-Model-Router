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
