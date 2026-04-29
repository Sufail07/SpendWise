import json
from typing import List
from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict

class Expense(BaseModel):
    amount: float
    category: str
    description: str
    date: datetime


TOTAL_BUDGET = 0
BUDGET_BY_CATEGORY = {}
EXPENSES: List[Expense] = []

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "Store expenditure data",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "category": {"type": "string"},
                    "description": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["amount", "category", "description", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Get the summary of total expenditure, and provide spending insights.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_by_category",
            "description": "Get expenditure data ordered by category",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"}
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_budget",
            "description": "Store total budget",
            "parameters": {
                "type": "object",
                "properties": {
                    "budget": {"type": "number"}
                },
                "required": ["budget"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_budget",
            "description": "Check the intial and remaining budget after expenditure.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    
]

async def add_expense(**kwargs):
    expenditure = Expense(**kwargs)
    EXPENSES.append(expenditure)
    return expenditure.model_dump(mode="json")

async def get_summary():
    totals = defaultdict(float)
    for e in EXPENSES:
        totals[e.category] += e.amount
    summary = {
        "expenses": [e.model_dump(mode="json") for e in EXPENSES],
        "total_budget": TOTAL_BUDGET,
        "budget_by_category": BUDGET_BY_CATEGORY,
        "budget_remaining": TOTAL_BUDGET - sum(e.amount for e in EXPENSES),
        "total_spent": sum(e.amount for e in EXPENSES),
        "expense_by_category": totals
    }
    return summary


async def get_by_category(category):
    result = [expense.amount for expense in EXPENSES if expense.category == category]
    
    return {
        "count": len(result),
        "total": sum(result)
    }

async def set_budget(budget):
    global TOTAL_BUDGET
    TOTAL_BUDGET = budget
    return TOTAL_BUDGET

async def check_budget():
    return TOTAL_BUDGET - sum(e.amount for e in EXPENSES)
