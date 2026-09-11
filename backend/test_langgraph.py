import os
import json
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

load_dotenv()


# 1. LangGraph State
class ComplaintState(TypedDict):
    complaint_text: str
    ai_response: str


# 2. Groq LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# 3. AI Analysis Node
def analyze_complaint(state: ComplaintState):
    complaint = state["complaint_text"]

    prompt = f"""
You are an AI assistant for a pharmaceutical customer complaint management system.

Analyze the following customer complaint.

Return ONLY valid JSON using exactly these four fields:

{{
  "complaint_category": "string",
  "severity": "Critical, Major, or Minor",
  "suggested_next_action": "string",
  "initial_risk_assessment": "string"
}}

Rules:
- Do not use markdown.
- Do not add explanations outside the JSON.
- Keep the response concise.
- Severity must be exactly one of: Critical, Major, Minor.

Complaint:
{complaint}
"""

    response = llm.invoke(prompt)

    return {
        "ai_response": response.content
    }


# 4. Create LangGraph
graph_builder = StateGraph(ComplaintState)

graph_builder.add_node(
    "analyze_complaint",
    analyze_complaint
)

graph_builder.add_edge(
    START,
    "analyze_complaint"
)

graph_builder.add_edge(
    "analyze_complaint",
    END
)

graph = graph_builder.compile()


# 5. Test Complaint
result = graph.invoke({
    "complaint_text": """
    Apollo Pharmacy reported discolored capsules in
    Amoxicillin Capsules 500 mg.

    Batch number AMX240602.

    Manufacturing date March 2026.

    Expiry date February 2028.

    12 capsules are affected.
    """,
    "ai_response": ""
})


# 6. Convert AI JSON string into Python dictionary
try:
    ai_data = json.loads(result["ai_response"])

    print("\n===== STRUCTURED DATA =====\n")

    print(
        "Complaint Category:",
        ai_data["complaint_category"]
    )

    print(
        "Severity:",
        ai_data["severity"]
    )

    print(
        "Suggested Next Action:",
        ai_data["suggested_next_action"]
    )

    print(
        "Initial Risk Assessment:",
        ai_data["initial_risk_assessment"]
    )

except json.JSONDecodeError:
    print("\nAI ne valid JSON return nahi kiya.")
    print("\nRaw AI Response:")
    print(result["ai_response"])