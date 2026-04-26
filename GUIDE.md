# Datasage User Guide

Datasage is a visual NLP pipeline builder that lets you process text through a sequence of LLM-powered stages — ingest, clean, extract, analyze, and export — via a browser-based UI.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Starting the Application](#4-starting-the-application)
5. [Using the Pipeline](#5-using-the-pipeline)
6. [LLM Backends](#6-llm-backends)
7. [Exporting Results](#7-exporting-results)
8. [CLI Reference](#8-cli-reference)

---

## 1. Prerequisites

- **Python 3.10 or later**
- An LLM backend. One of:
  - An [Anthropic API key](https://console.anthropic.com/) (for Claude models)
  - An [OpenAI API key](https://platform.openai.com/) (for GPT models)
  - [Ollama](https://ollama.com/) running locally (for free, offline inference)

Check your Python version:

```bash
python3 --version
```

---

## 2. Installation

### Option A — Install script (recommended)

Clone the repository and run the installer:

```bash
git clone https://github.com/otsolaue/datasage.git
cd datasage
./install.sh --local --backend anthropic
```

Replace `anthropic` with your preferred backend: `openai`, `ollama`, or `all` (installs support for every backend).

The script creates an isolated virtual environment at `~/.datasage/venv` and installs datasage into it.

### Option B — Manual installation

```bash
git clone https://github.com/otsolaue/datasage.git
cd datasage
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[anthropic]"   # or [openai], [ollama], [all]
```

### Option C — Install from PyPI

```bash
pip install "datasage[anthropic]"   # or [openai], [ollama], [all]
```

---

## 3. Configuration

Run the interactive setup wizard to select your backend and provide credentials:

```bash
# If you used the install script:
~/.datasage/venv/bin/datasage config

# If you used a local venv:
source .venv/bin/activate
datasage config
```

The wizard will ask for:

| Prompt | Description |
|--------|-------------|
| Backend | `anthropic`, `openai`, or `ollama` |
| API key | Your Anthropic or OpenAI key (not needed for Ollama) |
| Model | The model to use (defaults shown below) |

Settings are saved to `~/.datasage/config.yaml`. You can also edit this file directly:

```yaml
backend: anthropic
api_key: sk-ant-...
model: claude-opus-4-6
```

**Default models by backend:**

| Backend | Default model |
|---------|--------------|
| Anthropic | `claude-opus-4-6` |
| OpenAI | `gpt-4o` |
| Ollama | `llama3` |

> If you skip `datasage config`, a setup wizard will appear automatically the first time you open the UI (as long as you are not using Ollama).

### Ollama setup

If you want to run models locally with Ollama, first install and start Ollama, then pull a model:

```bash
# Install Ollama (see https://ollama.com for other methods)
curl -fsSL https://ollama.com/install.sh | sh

# Start the Ollama service
ollama serve &

# Pull the default model
ollama pull llama3
```

Datasage connects to Ollama at `http://localhost:11434` by default. You can change this in `~/.datasage/config.yaml`:

```yaml
backend: ollama
model: llama3
ollama_host: http://localhost:11434
```

---

## 4. Starting the Application

```bash
# If you used the install script:
~/.datasage/venv/bin/datasage run

# If you activated a local venv:
datasage run
```

This starts a local web server and opens `http://localhost:8501` in your browser.

**Options:**

```bash
datasage run --port 8080       # Use a different port
datasage run --no-browser      # Don't open the browser automatically
```

---

## 5. Using the Pipeline

The pipeline has five sequential stages. You move through them using the left sidebar, which shows your progress.

```
Ingest → Clean → Extract → Analyze → Export
```

### Stage 1 — Ingest

Load your source text. Three input methods are available:

- **Paste text** — type or paste directly into the text area
- **Upload a file** — supports `.txt`, `.md`, `.csv`, and `.pdf`
- **Fetch from URL** — enter a web URL; datasage fetches and extracts the text

Click **Run Ingest** to store the raw text and proceed.

### Stage 2 — Clean

Remove noise and normalize formatting. Pick a recipe or write your own prompt:

| Recipe | What it does |
|--------|-------------|
| Remove boilerplate | Strips headers, footers, and navigation elements |
| Normalize whitespace & encoding | Fixes encoding artifacts and collapses whitespace |
| Custom prompt | Write your own instruction using `{text}` as the placeholder |

Click **Run Clean**, or click **Skip / use previous result** to pass the raw text through unchanged.

### Stage 3 — Extract

Pull structured information from the text. Built-in recipes:

| Recipe | Output |
|--------|--------|
| Key facts | Numbered list of factual statements |
| Named entities | People, organizations, locations, and dates grouped by type |
| Quotes | Direct quotes with attribution |
| Custom prompt | Your own extraction instruction |

### Stage 4 — Analyze

Derive insights from the extracted or cleaned text:

| Recipe | Output |
|--------|--------|
| Summarize | 3–5 sentence summary |
| Sentiment | Positive / negative / neutral classification with reasoning |
| Themes | Main topics with brief explanations |
| Custom prompt | Your own analysis instruction |

### Stage 5 — Export

Download results from all completed stages. See [Exporting Results](#7-exporting-results) below.

### Navigation tips

- The sidebar shows a checkmark next to each completed stage.
- You can jump to any stage at any time using the sidebar links.
- If you skip the Clean stage, Extract and Analyze will automatically fall back to the Ingest output.
- Click **Start a new pipeline** (in the sidebar) to clear all results and begin fresh.

---

## 6. LLM Backends

Datasage supports three backends. You can switch between them at any time from the **Settings** page in the UI or by re-running `datasage config`.

| Backend | Requires | Best for |
|---------|---------|---------|
| Anthropic | API key | High-quality results with Claude models |
| OpenAI | API key | GPT-4o and other OpenAI models |
| Ollama | Local installation | Offline use, no API costs |

---

## 7. Exporting Results

On the Export stage, three download buttons are available:

| Format | Contents |
|--------|---------|
| **TXT** | Each stage output separated by `=== STAGE_NAME ===` headers |
| **JSON** | `{"ingest": "...", "clean": "...", ...}` |
| **CSV** | Two columns: `stage` and `output` |

Only stages that were actually run will appear in the export.

---

## 8. CLI Reference

```
datasage run [--port INT] [--browser / --no-browser]
    Start the web UI. Default port: 8501.

datasage config
    Interactive wizard to set backend, API key, and model.

datasage --help
    Show all available commands and options.
```
