from app.ai_complaint import analyze_complaint_text


complaint = """
Apollo Pharmacy reported discolored capsules in
Amoxicillin Capsules 500 mg.

Batch number AMX240602.

Manufacturing date March 2026.

Expiry date February 2028.

12 capsules are affected.
"""


result = analyze_complaint_text(complaint)


print("\n===== AI COMPLAINT DATA =====\n")

for field, value in result.items():
    print(f"{field}: {value}")