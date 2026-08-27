import streamlit as st
import json
from google import genai
from google.genai import types


# ============================================================
# GEMINI API SETUP
# ============================================================

API_KEY = "AQ.Ab8RN6JiJvn_b8EXMseZTTlcdMiedfS-AuUqU-l5hlkAwVkV7g"   # <-- PUT YOUR GEMINI API KEY HERE

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Chethu GPT - Study Buddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM WEB PAGE DESIGN
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .hero {
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        text-align: center;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 18px;
        margin: 0;
    }

    .material-card {
        padding: 30px;
        border-radius: 18px;
        background: rgba(128, 128, 128, 0.08);
        border-left: 6px solid #667eea;
        line-height: 1.8;
        font-size: 17px;
        margin-top: 20px;
        margin-bottom: 30px;
    }

    .quiz-card {
        padding: 18px;
        border-radius: 15px;
        background: rgba(128, 128, 128, 0.08);
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .score-card {
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        border: 2px solid rgba(128,128,128,0.25);
        margin: 25px 0;
    }

    .score-number {
        font-size: 55px;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "stage" not in st.session_state:
    st.session_state.stage = "topic_input"

if "topic" not in st.session_state:
    st.session_state.topic = ""

if "num_questions" not in st.session_state:
    st.session_state.num_questions = 5

if "overview" not in st.session_state:
    st.session_state.overview = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = []

if "score" not in st.session_state:
    st.session_state.score = 0

if "percentage" not in st.session_state:
    st.session_state.percentage = 0

if "grade" not in st.session_state:
    st.session_state.grade = ""

if "results" not in st.session_state:
    st.session_state.results = []


# ============================================================
# RESET FUNCTION
# ============================================================

def reset_study_buddy():

    st.session_state.stage = "topic_input"

    st.session_state.topic = ""

    st.session_state.num_questions = 5

    st.session_state.overview = ""

    st.session_state.quiz = []

    st.session_state.score = 0

    st.session_state.percentage = 0

    st.session_state.grade = ""

    st.session_state.results = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📚 Chethu Study Buddy")

    st.write(
        "Study → Practice → Results"
    )

    st.divider()

    st.subheader("📍 Progress")

    if st.session_state.stage == "topic_input":
        st.markdown("➡️ **1. Choose Topic**")
        st.write("2. Study Material")
        st.write("3. Take Quiz")
        st.write("4. Results")

    elif st.session_state.stage == "study_material":
        st.write("✅ 1. Choose Topic")
        st.markdown("➡️ **2. Study Material**")
        st.write("3. Take Quiz")
        st.write("4. Results")

    elif st.session_state.stage == "quiz_active":
        st.write("✅ 1. Choose Topic")
        st.write("✅ 2. Study Material")
        st.markdown("➡️ **3. Take Quiz**")
        st.write("4. Results")

    elif st.session_state.stage == "graded":
        st.write("✅ 1. Choose Topic")
        st.write("✅ 2. Study Material")
        st.write("✅ 3. Take Quiz")
        st.markdown("➡️ **4. Results**")

    st.divider()

    if st.button(
        "🔄 Start New Study Session",
        use_container_width=True
    ):

        reset_study_buddy()

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>📚 Chethu GPT Study Buddy</h1>

        <p>
            Learn a topic → Take a quiz → Check your score
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# GEMINI FUNCTION
# ============================================================

def generate_study_material(topic, num_questions):

    prompt = f"""
You are an expert educational tutor.

Create a complete study session for the following topic:

TOPIC:
{topic}

The student wants exactly {num_questions} multiple-choice questions.

Create:

1. Clear and useful study material.
2. Exactly {num_questions} multiple-choice questions.
3. Every question must have exactly 4 options.
4. Every question must have exactly one correct answer.
5. Give a short explanation for every correct answer.
6. Questions should test understanding.
7. Make the content suitable for a college student.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add any text outside JSON.

Required JSON format:

{{
    "overview": "Study material about the topic",

    "quiz": [
        {{
            "question": "Question text",

            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],

            "answer": "Option A",

            "explanation": "Explanation of the correct answer"
        }}
    ]
}}

IMPORTANT:

The quiz MUST contain exactly {num_questions} questions.

Each question MUST have exactly 4 options.
"""

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json"

            )
        )

        data = json.loads(response.text)

        # Validate response

        if "overview" not in data:
            raise ValueError(
                "Study material was not generated correctly."
            )

        if "quiz" not in data:
            raise ValueError(
                "Quiz was not generated correctly."
            )

        if len(data["quiz"]) != num_questions:
            raise ValueError(
                f"Expected {num_questions} questions, "
                f"but received {len(data['quiz'])}."
            )

        for question in data["quiz"]:

            if len(question["options"]) != 4:

                raise ValueError(
                    "Each question must contain exactly 4 options."
                )

        return data

    except Exception as e:

        st.error(
            "❌ Could not generate study material."
        )

        st.code(str(e))

        return None


# ============================================================
# PAGE 1 - TOPIC INPUT
# ============================================================

if st.session_state.stage == "topic_input":

    st.header("🎯 Step 1: Create Your Quiz")

    st.write(
        "First choose what you want to study and "
        "how many questions you want."
    )

    st.divider()

    topic = st.text_input(

        "📖 Enter your study topic",

        placeholder="Example: TCP vs UDP"
    )

    num_questions = st.number_input(

        "📝 How many questions do you want?",

        min_value=1,

        max_value=20,

        value=5,

        step=1
    )

    st.info(
        f"Your quiz will contain **{num_questions} questions**."
    )

    st.divider()

    if st.button(

        "📚 Generate Study Material",

        type="primary",

        use_container_width=True
    ):

        if not topic.strip():

            st.warning(
                "⚠️ Please enter a topic."
            )

        else:

            with st.spinner(
                "🤖 Creating your study material and quiz..."
            ):

                material = generate_study_material(

                    topic.strip(),

                    int(num_questions)
                )

            if material:

                st.session_state.topic = topic.strip()

                st.session_state.num_questions = int(
                    num_questions
                )

                st.session_state.overview = material[
                    "overview"
                ]

                st.session_state.quiz = material[
                    "quiz"
                ]

                # GO TO STUDY MATERIAL PAGE

                st.session_state.stage = "study_material"

                st.rerun()


# ============================================================
# PAGE 2 - STUDY MATERIAL
# ============================================================

elif st.session_state.stage == "study_material":

    st.header("📖 Step 2: Study Material")

    st.subheader(
        f"Topic: {st.session_state.topic}"
    )

    st.caption(
        f"Quiz size: "
        f"{st.session_state.num_questions} questions"
    )

    st.divider()

    st.markdown(
        "### 📚 Learn the Topic"
    )

    # Study material

    study_text = st.session_state.overview

    study_text = study_text.replace(
        "\n",
        "<br><br>"
    )

    st.markdown(

        f"""
        <div class="material-card">

            {study_text}

        </div>
        """,

        unsafe_allow_html=True
    )

    # ========================================================
    # TAKE QUIZ BUTTON AT BOTTOM
    # ========================================================

    st.divider()

    st.markdown(
        """
        <div style="text-align:center;">

            <h2>🎯 Ready for the Quiz?</h2>

            <p>
                Review the study material above,
                then start your quiz.
            </p>

        </div>
        """,

        unsafe_allow_html=True
    )

    if st.button(

        f"📝 Take Quiz - "
        f"{st.session_state.num_questions} Questions",

        type="primary",

        use_container_width=True
    ):

        st.session_state.stage = "quiz_active"

        st.rerun()


# ============================================================
# PAGE 3 - QUIZ
# ============================================================

elif st.session_state.stage == "quiz_active":

    st.header("📝 Step 3: Take the Quiz")

    st.subheader(
        f"Topic: {st.session_state.topic}"
    )

    st.info(
        f"Answer all "
        f"{st.session_state.num_questions} questions. "
        "There is ONE Submit button at the bottom."
    )

    st.divider()

    # ========================================================
    # ONE FORM FOR ALL QUESTIONS
    # ========================================================

    with st.form("quiz_form"):

        selected_answers = []

        # ====================================================
        # SHOW ALL QUESTIONS
        # ====================================================

        for index, question in enumerate(
            st.session_state.quiz
        ):

            st.markdown(
                f"""
                <div class="quiz-card">

                    <h3>
                        Question {index + 1}
                    </h3>

                </div>
                """,

                unsafe_allow_html=True
            )

            st.write(
                question["question"]
            )

            answer = st.radio(

                "Choose your answer:",

                question["options"],

                key=f"question_{index}",

                index=None
            )

            selected_answers.append(answer)

            # Separator

            if index < len(
                st.session_state.quiz
            ) - 1:

                st.divider()

        # ====================================================
        # ONE SUBMIT BUTTON AT VERY BOTTOM
        # ====================================================

        st.divider()

        submitted = st.form_submit_button(

            "✅ SUBMIT QUIZ & SEE MY SCORE",

            type="primary",

            use_container_width=True
        )

    # ========================================================
    # AFTER SUBMIT
    # ========================================================

    if submitted:

        # Check unanswered questions

        unanswered = any(

            answer is None

            for answer in selected_answers
        )

        if unanswered:

            st.warning(

                f"⚠️ Please answer all "
                f"{st.session_state.num_questions} "
                "questions before submitting."
            )

        else:

            score = 0

            results = []

            # =================================================
            # CHECK EVERY ANSWER
            # =================================================

            for index, question in enumerate(
                st.session_state.quiz
            ):

                selected = selected_answers[index]

                correct = question["answer"]

                is_correct = (
                    selected == correct
                )

                if is_correct:

                    score += 1

                results.append({

                    "question":
                        question["question"],

                    "selected":
                        selected,

                    "correct":
                        correct,

                    "is_correct":
                        is_correct,

                    "explanation":
                        question["explanation"]
                })

            # =================================================
            # CALCULATE SCORE
            # =================================================

            total = len(
                st.session_state.quiz
            )

            percentage = (
                score / total
            ) * 100

            # =================================================
            # CALCULATE GRADE
            # =================================================

            if percentage >= 90:

                grade = "A+"

            elif percentage >= 80:

                grade = "A"

            elif percentage >= 70:

                grade = "B"

            elif percentage >= 60:

                grade = "C"

            elif percentage >= 50:

                grade = "D"

            else:

                grade = "F"

            # Save results

            st.session_state.score = score

            st.session_state.percentage = percentage

            st.session_state.grade = grade

            st.session_state.results = results

            # Go to result page

            st.session_state.stage = "graded"

            st.rerun()


# ============================================================
# PAGE 4 - RESULTS
# ============================================================

elif st.session_state.stage == "graded":

    st.header("🏆 Step 4: Quiz Results")

    st.subheader(
        f"Topic: {st.session_state.topic}"
    )

    score = st.session_state.score

    total = len(
        st.session_state.quiz
    )

    percentage = st.session_state.percentage

    grade = st.session_state.grade

    # ========================================================
    # SCORE CARD
    # ========================================================

    st.markdown(

        f"""
        <div class="score-card">

            <h2>🎉 Your Final Result</h2>

            <div class="score-number">
                {score} / {total}
            </div>

            <h2>
                {percentage:.1f}%
            </h2>

            <h2>
                Grade: {grade}
            </h2>

        </div>
        """,

        unsafe_allow_html=True
    )

    # ========================================================
    # PASS / FAIL
    # ========================================================

    if percentage >= 50:

        st.success(
            "🎉 PASS! Great job!"
        )

    else:

        st.error(
            "📚 KEEP PRACTICING! "
            "Review the study material and explanations."
        )

    st.divider()

    # ========================================================
    # DETAILED RESULTS
    # ========================================================

    st.subheader(
        "📋 Detailed Results"
    )

    for index, result in enumerate(
        st.session_state.results
    ):

        st.markdown(
            f"### Question {index + 1}"
        )

        st.write(
            result["question"]
        )

        if result["is_correct"]:

            st.success(
                f"✅ Correct — "
                f"Your answer: "
                f"{result['selected']}"
            )

        else:

            st.error(
                f"❌ Incorrect — "
                f"Your answer: "
                f"{result['selected']}"
            )

            st.write(
                f"**Correct answer:** "
                f"{result['correct']}"
            )

        st.info(
            "💡 Explanation: "
            + result["explanation"]
        )

        if index < len(
            st.session_state.results
        ) - 1:

            st.divider()

    # ========================================================
    # NEW STUDY SESSION
    # ========================================================

    st.divider()

    if st.button(

        "🔄 Study Another Topic",

        type="primary",

        use_container_width=True
    ):

        reset_study_buddy()

        st.rerun()