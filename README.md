# Origin

A second UI pass of the Origin chat workspace. Same product idea as [RAG-Chatbot](https://github.com/YashfaZahid/RAG-Chatbot): a system role, a model name, a temperature, and threads saved in `chats.json`. This copy uses a warmer charcoal palette. It still does not retrieve documents.

## What it does

- Editable system role, defaulting to a precise technical assistant
- Model and temperature controls in the sidebar
- Prompt starters
- Local history in `chats.json`
- Layout and type drawn in CSS, without image assets

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.env` beside `app.py`:

```text
OPENAI_API_KEY=sk-...
```

```bash
streamlit run app.py
```

Do not commit `.env`.

## Limits

This is a chat client. It does not index files, and the model name in the sidebar has to be one your API key can call. Grounded answers over a knowledge base live in SupportPearlz, not here.
