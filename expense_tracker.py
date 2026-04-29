import os, json, asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from helpers import add_expense, check_budget, get_by_category, get_summary, set_budget, tools

load_dotenv()


client = AsyncOpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)

system_prompt = """\
You are a strict financial advisor agent. You will receive expenditure data from the user. \
You are to track expenses, categorize them, check budgets, and give spending insights.

When categorizing expenses, use these standard categories and follow the examples below:

Categories: Transport, Food, Entertainment, Shopping, Health, Housing, Utilities, Education, Subscriptions, Other

Examples of tricky categorization:
- "Uber to airport" → category: Transport (not Travel)
- "Grabbed coffee at Starbucks" → category: Food (not Shopping)
- "Netflix monthly" → category: Subscriptions (not Entertainment)
- "Gym membership" → category: Health (not Subscriptions)
- "Bought headphones on Amazon" → category: Shopping (not Entertainment)
- "Electricity bill" → category: Utilities (not Housing)
- "Udemy course" → category: Education (not Shopping)
- "Dinner with friends at a restaurant" → category: Food (not Entertainment)
- "Taxi to the hospital" → category: Transport (not Health)
- "Bought groceries from Walmart" → category: Food (not Shopping)

When the user mentions multiple expenses in a single message, call add_expense separately for EACH expense. \
When the user mentions a bulk amount without details (e.g. "I already spent 2735"), ask them to break it down by category before logging it.
"""

    
tool_map = {
    "add_expense": add_expense,
    "get_summary": get_summary,
    "get_by_category": get_by_category,
    "set_budget": set_budget,
    "check_budget": check_budget
}

semaphore = asyncio.Semaphore(5)

MESSAGE_HISTORY = [
    {
        "role": "system",
        "content": system_prompt
    }
]

async def execute_tool(tool_call):
    async with semaphore:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        try:
            result =  await tool_map[function_name](**arguments)
            return {
                "tool_call_id": tool_call.id,
                "content": result
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call.id,
                "content": f"Error executing tool: {e}"
                }

async def react_loop(messages, tools, tool_map, max_iterations=10):
    n = 0
    while n < max_iterations:
        print(f"{n+1} iteration:")
        res = await client.chat.completions.create(
            model="z-ai/glm4.7",
            temperature=0.5,
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        n += 1
        message = res.choices[0].message
        messages.append(message)
        if message.tool_calls:
            print(f"Number of tool calls came back: {len(message.tool_calls)}")
            print(f"Tool calls: {message.tool_calls}")
            
            tasks = [execute_tool(tc) for tc in message.tool_calls]
            result = await asyncio.gather(*tasks, return_exceptions=True)
            
            for tool_call, result in zip(message.tool_calls, result):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result["content"])
                })
        
        else:
            print(f"No tool calls used")
            break
    
    print(res.choices[0].message.content)

async def summarize_messages(message):
    messages_to_summarize = message[1:len(message)-5]
    res = await client.chat.completions.create(
        model="z-ai/glm4.7",
        temperature=0.5,
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": "Summarize these large messages into short form."
            },
            {
                "role": "user",
                "content": json.dumps(messages_to_summarize)
            }
        ]
    )
    
    return res.choices[0].message.content


async def main():
    global MESSAGE_HISTORY
    print("I'm your personal finance tracker AI assistant. What can I do for you?")
    while True:
        print("-----------------------------------------")
        user_input = input()
        if user_input == "exit":
            break
        
        MESSAGE_HISTORY.append({
            "role": "user",
            "content": user_input
        })
        if len(MESSAGE_HISTORY) > 20:
            summary = await summarize_messages(MESSAGE_HISTORY)
            MESSAGE_HISTORY = [MESSAGE_HISTORY[0], {"role": "system", "content": summary}, *MESSAGE_HISTORY[-5:]]
        
        await react_loop(messages=MESSAGE_HISTORY, tools=tools, tool_map=tool_map)
    
    
    
    
if __name__ == "__main__":
    asyncio.run(main())