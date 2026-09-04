import streamlit as st
from google import genai
import os
import json
import uuid
from datetime import datetime


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Customer Support AI Agent",
    page_icon="🎫",
    layout="wide"
)


# ============================================================
# GEMINI API CONFIGURATION
# ============================================================

API_KEY = ("")

if not API_KEY:
    st.error(
        "❌ GEMINI_API_KEY is not configured.\n\n"
        "Please set your Gemini API key in PowerShell "
        "before starting the application."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

# Requested model
MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# AI TRIAGE AGENT
# ============================================================

def analyze_customer_email(email_text):

    prompt = f"""
You are an enterprise customer support triage agent.

Analyze the customer inquiry below and produce a structured
support ticket.

Your tasks are:

1. Detect customer sentiment.
2. Determine urgency.
3. Assign priority.
4. Route the ticket to the correct department.
5. Identify the main issue.
6. Create a short ticket summary.
7. Extract important details.
8. Draft an empathetic and professional response.

------------------------------------------------------------
ALLOWED SENTIMENT VALUES
------------------------------------------------------------

Positive
Neutral
Negative
Frustrated
Angry

------------------------------------------------------------
ALLOWED URGENCY VALUES
------------------------------------------------------------

Low
Medium
High
Critical

------------------------------------------------------------
ALLOWED PRIORITY VALUES
------------------------------------------------------------

P4
P3
P2
P1

Use:

P1 = Critical
P2 = High
P3 = Medium
P4 = Low

------------------------------------------------------------
ALLOWED DEPARTMENTS
------------------------------------------------------------

Billing
Technical Support
Sales
Account Management
Shipping
Customer Service
Security
General Support

------------------------------------------------------------
IMPORTANT POLICY RULES
------------------------------------------------------------

- Do not invent company policies.
- Do not promise refunds.
- Do not promise credits.
- Do not promise replacements.
- Do not promise compensation.
- Do not claim that an issue has already been fixed.
- Do not claim that a refund has already been processed.
- Do not invent order numbers or account information.
- If information is missing, mention that additional information
  may be required.
- Keep the response empathetic and professional.
- The response should be suitable for human review.
- Do not expose internal reasoning.
- Return ONLY valid JSON.

------------------------------------------------------------
REQUIRED JSON FORMAT
------------------------------------------------------------

{{
    "ticket_id": "string",
    "sentiment": "Positive | Neutral | Negative | Frustrated | Angry",
    "urgency": "Low | Medium | High | Critical",
    "priority": "P4 | P3 | P2 | P1",
    "department": "Billing | Technical Support | Sales | Account Management | Shipping | Customer Service | Security | General Support",
    "issue": "short description of the main issue",
    "summary": "short customer support summary",
    "key_details": [
        "important detail 1",
        "important detail 2",
        "important detail 3"
    ],
    "draft_response": "empathetic professional email response"
}}

------------------------------------------------------------
CUSTOMER INQUIRY
------------------------------------------------------------

{email_text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    result_text = response.text.strip()

    # Remove markdown fences if returned by the model
    if result_text.startswith("```"):
        result_text = result_text.replace("```json", "")
        result_text = result_text.replace("```", "")
        result_text = result_text.strip()

    result = json.loads(result_text)

    # Generate our own ticket ID if the model does not provide one
    if not result.get("ticket_id"):
        result["ticket_id"] = "TKT-" + str(uuid.uuid4())[:8].upper()

    return result


# ============================================================
# HEADER
# ============================================================

st.title("🎫 Customer Support Triage & Ticket Routing Agent")

st.write(
    "AI-powered enterprise support agent that analyzes customer "
    "emails, determines sentiment and urgency, routes tickets, "
    "and drafts empathetic responses."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🤖 Agent Workflow")

    st.write("📩 1. Receive Customer Email")
    st.write("😊 2. Analyze Sentiment")
    st.write("🚨 3. Determine Urgency")
    st.write("⭐ 4. Assign Priority")
    st.write("📍 5. Route Department")
    st.write("📝 6. Summarize Issue")
    st.write("✉️ 7. Draft Response")

    st.divider()

    st.info(
        "AI responses are drafts and should be reviewed "
        "by a support employee before being sent."
    )


# ============================================================
# CUSTOMER EMAIL INPUT
# ============================================================

st.subheader("📧 Customer Inquiry")

email_text = st.text_area(
    "Paste the customer's email below:",
    height=250,
    placeholder="""Example:

Subject: Urgent - I was charged twice!

Hi Support,

I tried to renew my subscription today and I was charged
twice. This is really frustrating because I already contacted
support last week and nobody helped me.

Please look into this as soon as possible.

Thanks."""
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🚀 Analyze & Route Ticket",
    use_container_width=True
):

    if not email_text.strip():

        st.warning(
            "⚠️ Please enter a customer inquiry first."
        )

    else:

        with st.spinner(
            "🤖 AI agent is analyzing the customer inquiry..."
        ):

            try:

                result = analyze_customer_email(email_text)

                st.session_state["result"] = result

            except json.JSONDecodeError:

                st.error(
                    "❌ The AI returned an invalid JSON response. "
                    "Please try again."
                )

            except Exception as e:

                st.error(
                    f"❌ Agent error: {str(e)}"
                )


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "result" in st.session_state:

    result = st.session_state["result"]

    st.divider()

    st.subheader("📊 Ticket Triage Result")


    # ========================================================
    # TICKET ID
    # ========================================================

    st.info(
        f"🎫 Ticket ID: **{result['ticket_id']}**"
    )


    # ========================================================
    # CLASSIFICATION
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "😊 Sentiment",
            result["sentiment"]
        )

    with col2:

        st.metric(
            "🚨 Urgency",
            result["urgency"]
        )

    with col3:

        st.metric(
            "⭐ Priority",
            result["priority"]
        )

    with col4:

        st.metric(
            "📍 Department",
            result["department"]
        )


    # ========================================================
    # ISSUE + SUMMARY
    # ========================================================

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🔎 Main Issue")

        st.write(
            result["issue"]
        )

    with col2:

        st.subheader("📝 Ticket Summary")

        st.write(
            result["summary"]
        )


    # ========================================================
    # KEY DETAILS
    # ========================================================

    st.subheader("📌 Key Details")

    for detail in result["key_details"]:

        st.write(
            f"• {detail}"
        )


    # ========================================================
    # ROUTING
    # ========================================================

    st.divider()

    st.subheader("📍 Ticket Routing")

    st.success(
        f"✅ Route this ticket to: "
        f"**{result['department']}**"
    )


    # ========================================================
    # DRAFT RESPONSE
    # ========================================================

    st.divider()

    st.subheader("✉️ AI-Drafted Response")

    st.text_area(
        "Response draft:",
        value=result["draft_response"],
        height=250
    )

    st.warning(
        "⚠️ Human review required before sending this response."
    )


    # ========================================================
    # RAW TICKET DATA
    # ========================================================

    with st.expander("🔧 View Structured Ticket Data"):

        st.json(result)


# ============================================================
# RESET BUTTON
# ============================================================

st.divider()

if st.button("🔄 Clear Analysis"):

    if "result" in st.session_state:

        del st.session_state["result"]

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    f"Customer Support AI Agent • Model: {MODEL_NAME}"
)
