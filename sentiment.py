import streamlit as st
import os
import json
from dotenv import load_dotenv
from google import genai


# Load API key
load_dotenv()

API_KEY = ("AQ.Ab8RN6L5RRml7a4bq-rfB7AbD2-sOGYUXv6KKLBiPJ-_aadCsw")

if not API_KEY:
    st.error("GEMINI_API_KEY not found.")
    st.stop()


# Connect to Gemini
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.6-flash"


# Streamlit page
st.set_page_config(
    page_title="Sentiment Analyzer Agent",
    page_icon="🤖"
)

st.title("🤖 Sentiment Analyzer Agent")

st.write(
    "Enter text below and the AI agent will identify "
    "the sentiment, mood, confidence, and reason."
)


# Text input
text = st.text_area(
    "📝 Enter text",
    height=200,
    placeholder="Example: I am really disappointed with this service."
)


# Analyze button
if st.button("🔍 Analyze Sentiment"):

    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    prompt = f"""
You are a professional sentiment analysis agent.

Analyze the following text.

Determine:

1. Sentiment
2. Mood
3. Confidence from 0 to 100
4. Reason for your decision
5. Emotional signals

Sentiment must be one of:

Positive
Negative
Neutral
Mixed

Mood can be:

Happy
Excited
Satisfied
Calm
Neutral
Confused
Worried
Sad
Disappointed
Frustrated
Angry
Fearful

Return ONLY valid JSON using this format:

{{
    "sentiment": "Negative",
    "mood": "Frustrated",
    "confidence": 92,
    "reason": "The customer expresses strong dissatisfaction.",
    "emotional_signals": [
        "complaint",
        "negative wording",
        "frustration"
    ]
}}

Important:

- Analyze only the supplied text.
- Do not invent information.
- Lower the confidence if the text is ambiguous.
- Confidence must be between 0 and 100.

TEXT:

{text}
"""

    with st.spinner("🤖 AI is analyzing..."):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            result_text = response.text.strip()

            # Remove markdown code blocks if returned
            if result_text.startswith("```"):
                result_text = result_text.replace(
                    "```json", ""
                )
                result_text = result_text.replace(
                    "```", ""
                )
                result_text = result_text.strip()

            result = json.loads(result_text)

        except Exception as e:

            st.error(f"Error: {e}")
            st.stop()


    # Results
    st.success("Analysis complete!")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "😊 Sentiment",
            result.get("sentiment", "Unknown")
        )

    with col2:
        st.metric(
            "💭 Mood",
            result.get("mood", "Unknown")
        )

    with col3:
        confidence = int(
            result.get("confidence", 0)
        )

        st.metric(
            "🎯 Confidence",
            f"{confidence}%"
        )


    # Confidence bar
    st.subheader("🎯 Confidence Level")

    confidence = max(
        0,
        min(100, confidence)
    )

    st.progress(confidence / 100)


    # Reason
    st.subheader("💡 Reason")

    st.write(
        result.get(
            "reason",
            "No reason provided."
        )
    )


    # Emotional signals
    st.subheader("🔎 Emotional Signals")

    signals = result.get(
        "emotional_signals",
        []
    )

    for signal in signals:
        st.write("•", signal)


    # Raw JSON
    with st.expander("🔧 View AI Data"):
        st.json(result)