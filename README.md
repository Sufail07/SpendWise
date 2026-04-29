# Personal Finance Tracker Agent

A conversational AI agent that tracks expenses, manages budgets, and provides spending insights. Built from scratch using raw LLM API calls — no frameworks.

## Features

- **Expense tracking** — log expenses with automatic categorization (Transport, Food, Entertainment, etc.)
- **Budget management** — set a total budget and check remaining balance
- **Spending insights** — get summaries broken down by category
- **Multi-expense support** — handles multiple expenses in a single message
- **Conversation memory** — sliding-window summarization keeps context without unbounded growth

## Files

- `expense_tracker.py` — main agent: ReAct loop, conversation loop, message summarization
- `helpers.py` — Pydantic models, tool schemas, tool functions, in-memory storage

## Setup

```bash
# Install dependencies
uv sync

# Set your API key in .env
NVIDIA_API_KEY=your_key_here

# Run
uv run expense_tracker.py
```

## Tools

| Tool                | Description                                             |
| ------------------- | ------------------------------------------------------- |
| `add_expense`     | Log an expense with amount, category, description, date |
| `get_summary`     | Total spent, per-category breakdown, budget remaining   |
| `get_by_category` | Total amount spent in a specific category               |
| `set_budget`      | Set the total budget                                    |
| `check_budget`    | Check remaining budget after expenses                   |

## Example

```
> Took an Uber to the airport, cost me 45 bucks
✅ Transport: $45 - Uber to airport

> How much did I spend on transport?
Transport: $45 across 1 expense
```
