# agentic-lead-generation

A runnable Python starter project for agentic lead generation with NinjaPear, PydanticAI, and OpenRouter.

This repo accompanies the article: https://nubela.co/blog/agentic-lead-generation

## What is in here

- Real NinjaPear API wrappers for the company, customer, competitor, people, and updates loops
- Mocked email verification and email sending helpers
- Typed Pydantic models for accounts, people, updates, and final output
- A 4-loop pipeline that starts from competitor domains and ends with a prioritized outreach queue
- A runnable example under `examples/run_demo.py`

## Quickstart

1. Copy `.env.example` to `.env`
2. Add your `NINJAPEAR_API_KEY` and `OPENROUTER_API_KEY`
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the demo:

```bash
python examples/run_demo.py
```

## Notes

- NinjaPear calls are real
- Email verification and sending are mocked on purpose
- Start with 2 competitor domains, not 200
