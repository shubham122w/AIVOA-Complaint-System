import json
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

load_dotenv()


# ==================================================
# 1. GROQ LLM
# ==================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# ==================================================
# 2. COMMON JSON HELPER
# ==================================================

def parse_ai_json(response_text: str):
    """
    Convert AI response into Python dictionary.
    Handles accidental markdown code fences.
    """

    response = response_text.strip()

    if response.startswith("```json"):
        response = response[7:]

    elif response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    return json.loads(response.strip())


def safe_parse_ai_json(response_text: str):
    """
    Safely parse AI JSON.
    """

    try:
        return parse_ai_json(response_text)

    except json.JSONDecodeError:
        return {
            "error": "AI returned invalid JSON",
            "raw_response": response_text
        }


# ==================================================
# 3. COMPLAINT ANALYSIS STATE
# ==================================================

class ComplaintState(TypedDict):
    complaint_text: str
    ai_response: str


# ==================================================
# 4. AI COMPLAINT ANALYSIS
# ==================================================

def analyze_complaint(state: ComplaintState):

    complaint = state["complaint_text"]

    prompt = f"""
You are an AI assistant for a pharmaceutical
customer complaint management system.

Analyze the complaint and extract structured
information for a Quality Management System.

Return ONLY valid JSON.

Use EXACTLY these fields:

{{
    "complaint_source": "",
    "customer_name": "",
    "product_name": "",
    "product_strength": "",
    "batch_number": "",
    "manufacturing_date": "",
    "expiry_date": "",
    "quantity_affected": "",
    "originating_site": "",
    "block_impacted": "",
    "npm": "",
    "complaint_category": "",
    "complaint_description": "",
    "severity": "",
    "suggested_next_action": "",
    "initial_risk_assessment": ""
}}

RULES:

1. Return ONLY valid JSON.
2. Do not use markdown.
3. Do not add explanations outside JSON.
4. Do not invent missing information.
5. Missing information must be returned as "".
6. Severity must be exactly:
   "Critical", "Major", or "Minor".
7. Dates must use YYYY-MM-DD format.
8. Keep exact batch numbers.
9. Keep quantity and unit together.
10. Do not create fake dates.

DATE NORMALIZATION:

- If an exact day is provided, convert it normally.

Example:
"25 June 2026" -> "2026-06-25"

- If only month and year are provided, normalize
  the date to the FIRST DAY of that month.

Example:
"March 2026" -> "2026-03-01"
"February 2028" -> "2028-02-01"

- This first-day normalization is only a
  representation for the QMS date field when
  the source provides month/year but no exact day.

- Never guess a specific day when the source
  gives a different exact date.

COMPLAINT SOURCE:

complaint_source means the channel/type through
which the complaint was received.

Examples:

Pharmacy
Hospital
Distributor
Customer
Manufacturer
Email
Phone
Other

Do NOT put the customer's organization name
inside complaint_source.

CUSTOMER NAME:

customer_name means the organization, company,
pharmacy, hospital, distributor or person who
reported the complaint.

Example:

ABC Pharmacy -> customer_name

COMPLAINT CATEGORY:

Identify the main quality/defect category
described in the complaint.

Examples include:

- Product Defect - Discoloration
- Product Defect - Appearance
- Product Defect - Damaged Packaging
- Foreign Matter Contamination
- Missing Product
- Incorrect Product
- Labeling Error
- Packaging Defect
- Quantity Issue
- Other Quality Complaint

If the complaint says that capsules, tablets,
or product are discolored, darkened, changed
color, or have abnormal coloration, classify it as:

"Product Defect - Discoloration"

COMPLAINT DESCRIPTION:

Write a concise description of the actual complaint
using only information provided by the customer.

Example:

"Customer reported discoloration of Amoxicillin
Capsules 500 mg affecting 12 capsules."

Do not add unsupported causes to the description.

COMPLAINT SEVERITY:

Critical:

Potential serious or direct patient/product
safety risk, contamination, product mix-up,
incorrect active ingredient or similar serious
quality issue.

Major:

Significant quality issue without clear immediate
critical patient safety risk.

Minor:

Low-risk issue unlikely to affect product quality,
safety or efficacy.

For discoloration of a pharmaceutical product,
consider it a Major quality issue unless the
complaint provides evidence of a critical
patient safety risk.

Foreign matter contamination should generally
be treated as Critical when it may affect product
purity or patient safety.

SUGGESTED NEXT ACTION:

Recommend a practical QA/QMS action based only
on the complaint information.

INITIAL RISK ASSESSMENT:

Briefly explain the potential quality or patient
risk based only on the complaint information.

Do not claim a confirmed root cause.

COMPLAINT:

{complaint}
"""

    response = llm.invoke(prompt)

    return {
        "ai_response": response.content
    }


# ==================================================
# 5. COMPLAINT ANALYSIS LANGGRAPH
# ==================================================

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


# ==================================================
# 6. PUBLIC COMPLAINT ANALYSIS FUNCTION
# ==================================================

def analyze_complaint_text(complaint_text: str):

    result = graph.invoke({
        "complaint_text": complaint_text,
        "ai_response": ""
    })

    return safe_parse_ai_json(
        result["ai_response"]
    )


# ==================================================
# 7. CORRECTION STATE
# ==================================================

class CorrectionState(TypedDict):
    current_data: dict
    correction_text: str
    updated_data: str


# ==================================================
# 8. AI COMPLAINT CORRECTION
# ==================================================

def correct_complaint(state: CorrectionState):

    current_data = state["current_data"]
    correction_text = state["correction_text"]

    prompt = f"""
You are an AI assistant for a pharmaceutical
customer complaint management system.

The user wants to correct existing complaint data.

CURRENT COMPLAINT DATA:

{json.dumps(current_data, indent=2)}

USER CORRECTION:

{correction_text}

Update ONLY the information requested by the user.

Preserve every other existing value.

Return ONLY valid JSON.

Use EXACTLY these fields:

{{
    "complaint_source": "",
    "customer_name": "",
    "product_name": "",
    "product_strength": "",
    "batch_number": "",
    "manufacturing_date": "",
    "expiry_date": "",
    "quantity_affected": "",
    "originating_site": "",
    "block_impacted": "",
    "npm": "",
    "complaint_type": "",
    "detailed_description": "",
    "initial_severity": "",
    "suggested_next_action": "",
    "initial_risk_assessment": "",
    "priority": ""
}}

RULES:

1. Return ONLY valid JSON.
2. Do not use markdown.
3. Preserve all unchanged values.
4. Change only fields requested by the user.
5. Do not invent information.
6. Preserve exact batch numbers.
7. Preserve exact quantities and units.
8. Dates must remain YYYY-MM-DD.
9. If expiry date is missing, keep it empty.
10. Severity must be Critical, Major or Minor.
11. Priority must be Critical, High or Normal.

If severity changes:

Critical -> Critical
Major -> High
Minor -> Normal

Keep customer_name and complaint_source separate.

IMPORTANT:

If the user says:

"batch number is BMX240602"

then update:

"batch_number": "BMX240602"

If the user says:

"affected quantity is 48 capsules"

then update:

"quantity_affected": "48 capsules"

Do not change unrelated fields.

CURRENT DATA:

{json.dumps(current_data, indent=2)}
"""

    response = llm.invoke(prompt)

    return {
        "updated_data": response.content
    }


# ==================================================
# 9. CORRECTION LANGGRAPH
# ==================================================

correction_builder = StateGraph(
    CorrectionState
)

correction_builder.add_node(
    "correct_complaint",
    correct_complaint
)

correction_builder.add_edge(
    START,
    "correct_complaint"
)

correction_builder.add_edge(
    "correct_complaint",
    END
)

correction_graph = correction_builder.compile()


# ==================================================
# 10. PUBLIC CORRECTION FUNCTION
# ==================================================

def correct_complaint_data(
    current_data: dict,
    correction_text: str
):

    result = correction_graph.invoke({
        "current_data": current_data,
        "correction_text": correction_text,
        "updated_data": ""
    })

    return safe_parse_ai_json(
        result["updated_data"]
    )


# ==================================================
# 11. COMPLETENESS CHECKER STATE
# ==================================================

class CompletenessState(TypedDict):
    complaint_data: dict
    ai_response: str


# ==================================================
# 12. AI COMPLAINT COMPLETENESS CHECKER
# ==================================================

def check_completeness(
    state: CompletenessState
):

    complaint_data = state["complaint_data"]

    prompt = f"""
You are an AI Quality Assurance assistant for a
pharmaceutical customer complaint management system.

Check whether the complaint contains enough
information for initial QMS triage.

CURRENT COMPLAINT DATA:

{json.dumps(complaint_data, indent=2)}

Check these important fields:

1. complaint_source
2. customer_name
3. product_name
4. product_strength
5. batch_number
6. manufacturing_date
7. expiry_date
8. quantity_affected
9. complaint_type
10. detailed_description
11. initial_severity

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "status": "Complete",
    "missing_fields": [],
    "present_fields": [],
    "message": ""
}}

RULES:

1. status must be exactly:
   "Complete" or "Incomplete".

2. If an important field is empty, null,
   missing, or "Not Provided", add its
   human-readable name to missing_fields.

3. Do not mark optional operational fields such as
   originating_site, block_impacted or npm as
   missing unless the complaint contains clues
   that they are necessary for understanding
   the complaint.

4. complaint_description is required.

5. customer_name is required.

6. product_name is required.

7. batch_number is required for batch-related
   pharmaceutical complaints.

8. quantity_affected should be present when
   the complaint describes affected material.

9. severity should be present after AI triage.

10. If all important information is available,
    status should be "Complete".

11. If any important information is missing,
    status should be "Incomplete".

12. missing_fields must contain ONLY fields that
    are actually missing.

13. present_fields should list the important
    fields that are available.

14. message should be a short QA-friendly
    explanation.

Do not invent information.
"""

    response = llm.invoke(prompt)

    return {
        "ai_response": response.content
    }


# ==================================================
# 13. COMPLETENESS LANGGRAPH
# ==================================================

completeness_builder = StateGraph(
    CompletenessState
)

completeness_builder.add_node(
    "check_completeness",
    check_completeness
)

completeness_builder.add_edge(
    START,
    "check_completeness"
)

completeness_builder.add_edge(
    "check_completeness",
    END
)

completeness_graph = completeness_builder.compile()


# ==================================================
# 14. PUBLIC COMPLETENESS FUNCTION
# ==================================================

def check_complaint_completeness(
    complaint_data: dict
):

    result = completeness_graph.invoke({
        "complaint_data": complaint_data,
        "ai_response": ""
    })

    return safe_parse_ai_json(
        result["ai_response"]
    )


# ==================================================
# 15. ROOT CAUSE STATE
# ==================================================

class RootCauseState(TypedDict):
    complaint_data: dict
    ai_response: str


# ==================================================
# 16. AI ROOT CAUSE RECOMMENDATION
# ==================================================

def recommend_root_cause(
    state: RootCauseState
):

    complaint_data = state["complaint_data"]

    prompt = f"""
You are an AI Quality Assurance assistant for a
pharmaceutical manufacturing complaint system.

Analyze the complaint and recommend possible
root causes for investigation.

IMPORTANT:

You are recommending investigation hypotheses,
not confirming a root cause.

CURRENT COMPLAINT:

{json.dumps(complaint_data, indent=2)}

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "summary": "",
    "possible_root_causes": [],
    "recommended_investigation": [],
    "records_to_review": []
}}

RULES:

1. Do not invent facts.
2. Do not claim that a root cause is confirmed.
3. Provide practical pharmaceutical QA
   investigation suggestions.
4. Keep recommendations relevant to the complaint.
5. Return ONLY valid JSON.
"""

    response = llm.invoke(prompt)

    return {
        "ai_response": response.content
    }


# ==================================================
# 17. ROOT CAUSE LANGGRAPH
# ==================================================

root_cause_builder = StateGraph(
    RootCauseState
)

root_cause_builder.add_node(
    "recommend_root_cause",
    recommend_root_cause
)

root_cause_builder.add_edge(
    START,
    "recommend_root_cause"
)

root_cause_builder.add_edge(
    "recommend_root_cause",
    END
)

root_cause_graph = root_cause_builder.compile()


# ==================================================
# 18. PUBLIC ROOT CAUSE FUNCTION
# ==================================================

def recommend_complaint_root_cause(
    complaint_data: dict
):

    result = root_cause_graph.invoke({
        "complaint_data": complaint_data,
        "ai_response": ""
    })

    return safe_parse_ai_json(
        result["ai_response"]
    )


# ==================================================
# 19. DUPLICATE DETECTION STATE
# ==================================================

class DuplicateState(TypedDict):
    new_complaint: dict
    existing_complaints: list
    ai_response: str


# ==================================================
# 20. AI DUPLICATE COMPLAINT DETECTION
# ==================================================

def detect_duplicate(
    state: DuplicateState
):

    new_complaint = state["new_complaint"]
    existing_complaints = state["existing_complaints"]

    prompt = f"""
You are an AI assistant for a pharmaceutical
customer complaint management system.

Determine whether the new complaint may be a
duplicate of any existing complaint.

NEW COMPLAINT:

{json.dumps(new_complaint, indent=2)}

EXISTING COMPLAINTS:

{json.dumps(existing_complaints, indent=2)}

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "duplicate_found": false,
    "confidence": "Low",
    "matching_complaint_id": null,
    "reason": ""
}}

RULES:

1. duplicate_found must be true or false.
2. confidence must be Low, Medium or High.
3. Use matching complaint ID when available.
4. Compare relevant information such as:
   - customer
   - product
   - batch
   - complaint type
   - description
5. Do not claim a duplicate when there is
   insufficient similarity.
6. Return ONLY valid JSON.
"""

    response = llm.invoke(prompt)

    return {
        "ai_response": response.content
    }


# ==================================================
# 21. DUPLICATE LANGGRAPH
# ==================================================

duplicate_builder = StateGraph(
    DuplicateState
)

duplicate_builder.add_node(
    "detect_duplicate",
    detect_duplicate
)

duplicate_builder.add_edge(
    START,
    "detect_duplicate"
)

duplicate_builder.add_edge(
    "detect_duplicate",
    END
)

duplicate_graph = duplicate_builder.compile()


# ==================================================
# 22. PUBLIC DUPLICATE FUNCTION
# ==================================================

def detect_complaint_duplicate(
    new_complaint: dict,
    existing_complaints: list
):

    result = duplicate_graph.invoke({
        "new_complaint": new_complaint,
        "existing_complaints": existing_complaints,
        "ai_response": ""
    })

    return safe_parse_ai_json(
        result["ai_response"]
    )


# ==================================================
# 23. CAPA STATE
# ==================================================

class CAPAState(TypedDict):
    complaint_data: dict
    ai_response: str


# ==================================================
# 24. AI CAPA RECOMMENDATION
# ==================================================

def recommend_capa(
    state: CAPAState
):

    complaint_data = state["complaint_data"]

    prompt = f"""
You are an AI Quality Assurance assistant for a
pharmaceutical manufacturing company.

Based on the complaint, recommend possible
Corrective and Preventive Actions (CAPA).

CURRENT COMPLAINT:

{json.dumps(complaint_data, indent=2)}

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "corrective_actions": [],
    "preventive_actions": [],
    "qa_verification": [],
    "responsible_function": ""
}}

RULES:

1. Recommendations must be practical.
2. Do not invent facts.
3. Do not claim that CAPA has been approved.
4. QA must review and approve the final CAPA.
5. Return ONLY valid JSON.
"""

    response = llm.invoke(prompt)

    return {
        "ai_response": response.content
    }


# ==================================================
# 25. CAPA LANGGRAPH
# ==================================================

capa_builder = StateGraph(
    CAPAState
)

capa_builder.add_node(
    "recommend_capa",
    recommend_capa
)

capa_builder.add_edge(
    START,
    "recommend_capa"
)

capa_builder.add_edge(
    "recommend_capa",
    END
)

capa_graph = capa_builder.compile()


# ==================================================
# 26. PUBLIC CAPA FUNCTION
# ==================================================

def recommend_complaint_capa(
    complaint_data: dict
):

    result = capa_graph.invoke({
        "complaint_data": complaint_data,
        "ai_response": ""
    })

    return safe_parse_ai_json(
        result["ai_response"]
    )


# ==================================================
# 27. SUMMARY STATE
# ==================================================

class SummaryState(TypedDict):
    complaint_data: dict
    ai_response: str


# ==================================================
# 28. AI COMPLAINT SUMMARY
# ==================================================

def generate_summary(
    state: SummaryState
):

    complaint_data = state["complaint_data"]

    prompt = f"""
You are an AI Quality Assurance assistant for a
pharmaceutical complaint management system.

Create a concise professional summary of the
complaint for QMS review.

CURRENT COMPLAINT:

{json.dumps(complaint_data, indent=2)}

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "summary": "",
    "key_details": [],
    "risk_overview": "",
    "recommended_action": ""
}}

RULES:

1. Use only information provided.
2. Do not invent facts.
3. Keep the summary concise and professional.
4. Clearly mention important product/batch
   information when available.
5. Return ONLY valid JSON.
"""

    response = llm.invoke(prompt)

    return {
        "ai_response": response.content
    }


# ==================================================
# 29. SUMMARY LANGGRAPH
# ==================================================

summary_builder = StateGraph(
    SummaryState
)

summary_builder.add_node(
    "generate_summary",
    generate_summary
)

summary_builder.add_edge(
    START,
    "generate_summary"
)

summary_builder.add_edge(
    "generate_summary",
    END
)

summary_graph = summary_builder.compile()


# ==================================================
# 30. PUBLIC SUMMARY FUNCTION
# ==================================================

def create_complaint_summary(
    complaint_data: dict
):

    result = summary_graph.invoke({
        "complaint_data": complaint_data,
        "ai_response": ""
    })

    return safe_parse_ai_json(
        result["ai_response"]
    )


# ==================================================
# 31. RISK CLASSIFICATION STATE
# ==================================================

class RiskState(TypedDict):
    complaint_data: dict
    ai_response: str


# ==================================================
# 32. AI RISK CLASSIFICATION
# ==================================================

def classify_risk(
    state: RiskState
):

    complaint_data = state["complaint_data"]

    prompt = f"""
You are an AI Quality Assurance risk assessment
assistant for a pharmaceutical complaint system.

Assess the initial risk of this complaint.

CURRENT COMPLAINT:

{json.dumps(complaint_data, indent=2)}

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "risk_level": "Low",
    "severity": "Minor",
    "priority": "Normal",
    "risk_factors": [],
    "rationale": "",
    "immediate_attention_required": false
}}

RULES:

1. risk_level must be exactly:
   "Low", "Medium", "High", or "Critical".

2. severity must be:
   "Critical", "Major", or "Minor".

3. priority must be:
   "Critical", "High", or "Normal".

4. Consider:
   - patient safety
   - contamination
   - product quality
   - batch impact
   - quantity affected
   - potential product mix-up
   - defect severity

5. Foreign matter contamination should generally
   receive Critical severity when it may affect
   product purity or patient safety.

6. Product discoloration without evidence of
   immediate patient safety risk should generally
   be considered Major rather than Critical.

7. immediate_attention_required must be true
   for High/Critical risk situations requiring
   prompt QA review.

8. Do not invent facts.

9. This is an initial AI assessment and must be
   reviewed by qualified QA personnel.

10. Return ONLY valid JSON.
"""

    response = llm.invoke(prompt)

    return {
        "ai_response": response.content
    }


# ==================================================
# 33. RISK LANGGRAPH
# ==================================================

risk_builder = StateGraph(
    RiskState
)

risk_builder.add_node(
    "classify_risk",
    classify_risk
)

risk_builder.add_edge(
    START,
    "classify_risk"
)

risk_builder.add_edge(
    "classify_risk",
    END
)

risk_graph = risk_builder.compile()


# ==================================================
# 34. PUBLIC RISK CLASSIFICATION FUNCTION
# ==================================================

def classify_complaint_risk_data(
    complaint_data: dict
):

    result = risk_graph.invoke({
        "complaint_data": complaint_data,
        "ai_response": ""
    })

    return safe_parse_ai_json(
        result["ai_response"]
    )