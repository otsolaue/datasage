import json
import csv
import io

import streamlit as st

from datasage.config import load_config, save_config, Config, LLMBackend
from datasage.llm import get_client
from datasage.pipeline.stages import StageType, STAGE_LABELS, STAGE_DESCRIPTIONS
from datasage.pipeline.recipes import get_recipes, apply_recipe

st.set_page_config(page_title="datasage", page_icon="🌿", layout="wide")

# ── Session state defaults ────────────────────────────────────────────────────
if "stage_outputs" not in st.session_state:
    st.session_state.stage_outputs: dict[str, str] = {}
if "active_stage" not in st.session_state:
    st.session_state.active_stage = StageType.INGEST


# ── Config / setup wizard ─────────────────────────────────────────────────────
def setup_page():
    st.title("🌿 Welcome to datasage")
    st.markdown("Let's configure your LLM backend before you start.")

    backend: LLMBackend = st.selectbox("LLM Backend", ["anthropic", "openai", "ollama"])
    api_key = ""
    ollama_host = "http://localhost:11434"
    default_models = {"anthropic": "claude-opus-4-6", "openai": "gpt-4o", "ollama": "llama3"}

    if backend in ("anthropic", "openai"):
        api_key = st.text_input(f"{backend.capitalize()} API key", type="password")
    else:
        ollama_host = st.text_input("Ollama host", value="http://localhost:11434")

    model = st.text_input("Model", value=default_models[backend])

    if st.button("Save & continue", type="primary"):
        cfg = Config(backend=backend, api_key=api_key, ollama_host=ollama_host, model=model)
        save_config(cfg)
        st.success("Configuration saved!")
        st.rerun()


# ── Pipeline flowchart sidebar ────────────────────────────────────────────────
def pipeline_nav():
    st.sidebar.title("🌿 datasage")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Pipeline stages")

    stages = list(StageType)
    for stage in stages:
        done = stage.value in st.session_state.stage_outputs
        label = STAGE_LABELS[stage]
        indicator = "✅" if done else "⬜"
        if st.sidebar.button(f"{indicator} {label}", key=f"nav_{stage.value}", use_container_width=True):
            st.session_state.active_stage = stage

    st.sidebar.markdown("---")
    if st.sidebar.button("⚙️ Settings", use_container_width=True):
        st.session_state.active_stage = "settings"


# ── Ingest helpers ────────────────────────────────────────────────────────────
def _read_uploaded_file(uploaded) -> str:
    name = uploaded.name.lower()

    if name.endswith(".pdf"):
        import pypdf
        reader = pypdf.PdfReader(uploaded)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)

    if name.endswith(".csv"):
        import csv as _csv
        import io
        content = uploaded.read().decode("utf-8", errors="replace")
        reader = _csv.reader(io.StringIO(content))
        rows = list(reader)
        if not rows:
            return ""
        # Represent CSV as a readable text table
        header = rows[0]
        lines = [", ".join(header), "-" * 40]
        for row in rows[1:]:
            lines.append(", ".join(f"{h}: {v}" for h, v in zip(header, row)))
        return "\n".join(lines)

    # .txt and .md — plain text
    return uploaded.read().decode("utf-8", errors="replace")


# ── Stage: Ingest ─────────────────────────────────────────────────────────────
def stage_ingest():
    st.header("📥 Ingest")
    st.caption(STAGE_DESCRIPTIONS[StageType.INGEST])

    tab_paste, tab_file = st.tabs(["Paste text", "Upload file"])

    text = ""
    with tab_paste:
        text = st.text_area("Paste your text here", height=300, key="ingest_paste")

    with tab_file:
        uploaded = st.file_uploader(
            "Upload a file",
            type=["txt", "md", "csv", "pdf"],
            help="Supported formats: plain text, Markdown, CSV, PDF",
        )
        if uploaded:
            with st.spinner("Reading file…"):
                text = _read_uploaded_file(uploaded)
            ext = uploaded.name.rsplit(".", 1)[-1].upper()
            st.caption(f"{ext} · {len(text):,} characters extracted")
            st.text_area("Preview", text[:2000], height=200, disabled=True)

    if st.button("Use this text →", type="primary", disabled=not text.strip()):
        st.session_state.stage_outputs[StageType.INGEST.value] = text
        st.session_state.active_stage = StageType.CLEAN
        st.rerun()


# ── Stage: Clean ─────────────────────────────────────────────────────────────
def stage_clean(cfg: Config):
    st.header("🧹 Clean")
    st.caption(STAGE_DESCRIPTIONS[StageType.CLEAN])

    source = st.session_state.stage_outputs.get(StageType.INGEST.value, "")
    if not source:
        st.warning("Complete the Ingest stage first.")
        return

    with st.expander("Source text preview"):
        st.text(source[:1000] + ("…" if len(source) > 1000 else ""))

    recipes = get_recipes(StageType.CLEAN)
    recipe_names = [r["name"] for r in recipes] + ["Custom prompt"]
    choice = st.selectbox("Choose a cleaning recipe", recipe_names)

    if choice == "Custom prompt":
        prompt_text = st.text_area("Your prompt (use {text} as placeholder)", height=150)
    else:
        recipe = next(r for r in recipes if r["name"] == choice)
        prompt_text = recipe["prompt"]
        st.text_area("Prompt", prompt_text, height=150, disabled=True)

    if st.button("Run cleaning →", type="primary"):
        final_prompt = prompt_text.replace("{text}", source)
        with st.spinner("Cleaning…"):
            client = get_client(cfg)
            result = client.complete(final_prompt)
        st.session_state.stage_outputs[StageType.CLEAN.value] = result
        st.success("Done!")
        st.text_area("Result", result, height=300)

    if StageType.CLEAN.value in st.session_state.stage_outputs:
        if st.button("Skip / use previous result →"):
            st.session_state.active_stage = StageType.EXTRACT
            st.rerun()


# ── Stage: Extract ────────────────────────────────────────────────────────────
def stage_extract(cfg: Config):
    st.header("🔍 Extract")
    st.caption(STAGE_DESCRIPTIONS[StageType.EXTRACT])

    source = st.session_state.stage_outputs.get(
        StageType.CLEAN.value,
        st.session_state.stage_outputs.get(StageType.INGEST.value, ""),
    )
    if not source:
        st.warning("Complete the Ingest stage first.")
        return

    with st.expander("Source text preview"):
        st.text(source[:1000] + ("…" if len(source) > 1000 else ""))

    recipes = get_recipes(StageType.EXTRACT)
    recipe_names = [r["name"] for r in recipes] + ["Custom prompt"]
    choice = st.selectbox("Choose an extraction recipe", recipe_names)

    if choice == "Custom prompt":
        prompt_text = st.text_area("Your prompt (use {text} as placeholder)", height=150)
    else:
        recipe = next(r for r in recipes if r["name"] == choice)
        prompt_text = recipe["prompt"]
        st.text_area("Prompt", prompt_text, height=150, disabled=True)

    if st.button("Run extraction →", type="primary"):
        final_prompt = prompt_text.replace("{text}", source)
        with st.spinner("Extracting…"):
            client = get_client(cfg)
            result = client.complete(final_prompt)
        st.session_state.stage_outputs[StageType.EXTRACT.value] = result
        st.success("Done!")
        st.text_area("Result", result, height=300)

    if StageType.EXTRACT.value in st.session_state.stage_outputs:
        if st.button("Next: Analyze →"):
            st.session_state.active_stage = StageType.ANALYZE
            st.rerun()


# ── Stage: Analyze ────────────────────────────────────────────────────────────
def stage_analyze(cfg: Config):
    st.header("📊 Analyze")
    st.caption(STAGE_DESCRIPTIONS[StageType.ANALYZE])

    source = st.session_state.stage_outputs.get(
        StageType.EXTRACT.value,
        st.session_state.stage_outputs.get(StageType.INGEST.value, ""),
    )
    if not source:
        st.warning("Complete the Ingest stage first.")
        return

    recipes = get_recipes(StageType.ANALYZE)
    recipe_names = [r["name"] for r in recipes] + ["Custom prompt"]
    choice = st.selectbox("Choose an analysis recipe", recipe_names)

    if choice == "Custom prompt":
        prompt_text = st.text_area("Your prompt (use {text} as placeholder)", height=150)
    else:
        recipe = next(r for r in recipes if r["name"] == choice)
        prompt_text = recipe["prompt"]
        st.text_area("Prompt", prompt_text, height=150, disabled=True)

    if st.button("Run analysis →", type="primary"):
        final_prompt = prompt_text.replace("{text}", source)
        with st.spinner("Analyzing…"):
            client = get_client(cfg)
            result = client.complete(final_prompt)
        st.session_state.stage_outputs[StageType.ANALYZE.value] = result
        st.success("Done!")
        st.text_area("Result", result, height=300)

    if StageType.ANALYZE.value in st.session_state.stage_outputs:
        if st.button("Next: Export →"):
            st.session_state.active_stage = StageType.EXPORT
            st.rerun()


# ── Stage: Export ─────────────────────────────────────────────────────────────
def stage_export():
    st.header("💾 Export")
    st.caption(STAGE_DESCRIPTIONS[StageType.EXPORT])

    outputs = st.session_state.stage_outputs
    if not outputs:
        st.warning("Nothing to export yet. Complete at least the Ingest stage.")
        return

    fmt = st.selectbox("Export format", ["Plain text", "JSON", "CSV"])

    if fmt == "Plain text":
        content = "\n\n".join(
            f"=== {k.upper()} ===\n{v}" for k, v in outputs.items()
        )
        st.download_button("Download .txt", content, file_name="datasage_output.txt")

    elif fmt == "JSON":
        content = json.dumps(outputs, indent=2, ensure_ascii=False)
        st.download_button("Download .json", content, file_name="datasage_output.json")

    elif fmt == "CSV":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["stage", "output"])
        for k, v in outputs.items():
            writer.writerow([k, v])
        st.download_button("Download .csv", buf.getvalue(), file_name="datasage_output.csv")

    st.markdown("---")
    if st.button("🔄 Start a new pipeline"):
        st.session_state.stage_outputs = {}
        st.session_state.active_stage = StageType.INGEST
        st.rerun()


# ── Settings page ─────────────────────────────────────────────────────────────
def settings_page():
    st.header("⚙️ Settings")
    cfg = load_config()

    backend: LLMBackend = st.selectbox(
        "LLM Backend", ["anthropic", "openai", "ollama"], index=["anthropic", "openai", "ollama"].index(cfg.backend)
    )
    api_key = cfg.api_key
    ollama_host = cfg.ollama_host

    if backend in ("anthropic", "openai"):
        api_key = st.text_input("API key", value=cfg.api_key, type="password")
    else:
        ollama_host = st.text_input("Ollama host", value=cfg.ollama_host)

    model = st.text_input("Model", value=cfg.model)

    if st.button("Save", type="primary"):
        save_config(Config(backend=backend, api_key=api_key, ollama_host=ollama_host, model=model))
        st.success("Saved!")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    cfg = load_config()

    if not cfg.api_key and cfg.backend != "ollama":
        setup_page()
        return

    pipeline_nav()
    active = st.session_state.active_stage

    if active == "settings":
        settings_page()
    elif active == StageType.INGEST:
        stage_ingest()
    elif active == StageType.CLEAN:
        stage_clean(cfg)
    elif active == StageType.EXTRACT:
        stage_extract(cfg)
    elif active == StageType.ANALYZE:
        stage_analyze(cfg)
    elif active == StageType.EXPORT:
        stage_export()


if __name__ == "__main__":
    main()
