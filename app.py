import re
import sys
import subprocess
import tempfile
from pathlib import Path

import streamlit as st
from google import genai


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Autonomous TDD AI Agent",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "started" not in st.session_state:
    st.session_state.started = False


# ============================================================
# TITLE
# ============================================================

st.title("🤖 Autonomous Test-Driven Development AI Agent")

st.write(
    "Gemini generates Python code → hidden tests run → "
    "failures are captured → Gemini debugs → tests run again."
)

st.divider()


# ============================================================
# GEMINI API KEY
# ============================================================

if st.session_state.api_key == "":

    st.subheader("🔑 Enter Your API KEY")

    api_key = st.text_input(
        "Paste your Gemini API key",
        type="password",
        placeholder="AIza..."
    )

    if st.button(
        "Save API Key",
        type="primary"
    ):

        if api_key.strip() == "":
            st.error("Please enter a Gemini API key.")

        else:
            st.session_state.api_key = api_key.strip()

            st.success(
                "✅ API key saved for this session."
            )

            st.rerun()

    st.info(
        "Your API key is entered through the webpage "
        "and is not hard-coded into this Python file."
    )

    st.stop()


# ============================================================
# API KEY CONNECTED
# ============================================================

st.success("🔐 Gemini API key connected")

if st.button("🔄 Change API Key"):

    st.session_state.api_key = ""

    st.rerun()


# ============================================================
# GEMINI CLIENT
# ============================================================

try:

    client = genai.Client(
        api_key=st.session_state.api_key
    )

except Exception as error:

    st.error(
        "Unable to create Gemini client: "
        + str(error)
    )

    st.stop()


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gemini-3.6-flash"

MAX_ITERATIONS = 5

TIMEOUT_SECONDS = 8


# ============================================================
# GEMINI FUNCTION
# ============================================================

def ask_gemini(prompt):

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if response.text is None:
            raise Exception(
                "Gemini returned an empty response."
            )

        return response.text

    except Exception as error:

        raise Exception(
            "Gemini API Error: "
            + str(error)
        )


# ============================================================
# EXTRACT PYTHON CODE
# ============================================================

def extract_code(text):

    match = re.search(
        r"```python\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    match = re.search(
        r"```\s*(.*?)```",
        text,
        re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return text.strip()


# ============================================================
# BASIC SAFETY CHECK
# ============================================================

def safety_check(code):

    forbidden = [
        "os.system",
        "os.popen",
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "httpx",
        "ctypes",
        "eval(",
        "exec(",
        "__import__"
    ]

    detected = []

    lower_code = code.lower()

    for item in forbidden:

        if item.lower() in lower_code:

            detected.append(item)

    return detected


# ============================================================
# GENERATE INITIAL CODE
# ============================================================

def generate_solution(problem):

    prompt = (
        "You are an expert Python programmer.\n\n"

        "Build a correct solution for this programming "
        "problem:\n\n"

        + problem
        + "\n\n"

        "Requirements:\n"
        "1. Implement the requested function.\n"
        "2. Handle normal inputs.\n"
        "3. Handle boundary cases.\n"
        "4. Handle empty inputs when appropriate.\n"
        "5. Handle single-element inputs when appropriate.\n"
        "6. Consider unusual valid inputs.\n"
        "7. Do not write tests.\n"
        "8. Do not provide explanations.\n"
        "9. Return ONLY complete Python source code."
    )

    response = ask_gemini(prompt)

    return extract_code(response)


# ============================================================
# AUTONOMOUS DEBUGGER
# ============================================================

def debug_solution(
    problem,
    current_code,
    failure,
    iteration
):

    prompt = (
        "You are an autonomous Python debugging agent.\n\n"

        "PROGRAMMING PROBLEM:\n"
        + problem
        + "\n\n"

        "CURRENT IMPLEMENTATION:\n"
        + current_code
        + "\n\n"

        "The implementation failed hidden tests.\n\n"

        "TEST FAILURE:\n"
        + failure
        + "\n\n"

        "DEBUGGING ITERATION:\n"
        + str(iteration)
        + "\n\n"

        "Your job is to fix the implementation.\n\n"

        "Rules:\n"
        "1. Analyze the failure.\n"
        "2. Find the likely bug.\n"
        "3. Fix the implementation.\n"
        "4. Preserve functionality that already works.\n"
        "5. Consider boundary cases.\n"
        "6. Do not hard-code the test result.\n"
        "7. Do not write tests.\n"
        "8. Do not explain the solution.\n"
        "9. Return ONLY the complete corrected Python code."
    )

    response = ask_gemini(prompt)

    return extract_code(response)


# ============================================================
# RUN HIDDEN TESTS
# ============================================================

def run_hidden_tests(
    solution_code,
    hidden_tests
):

    with tempfile.TemporaryDirectory() as temp_dir:

        folder = Path(temp_dir)

        solution_file = folder / "solution.py"

        test_file = folder / "test_hidden.py"

        solution_file.write_text(
            solution_code,
            encoding="utf-8"
        )

        test_file.write_text(
            hidden_tests,
            encoding="utf-8"
        )

        command = [
            sys.executable,
            "-m",
            "pytest",
            "test_hidden.py",
            "-q"
        ]

        try:

            result = subprocess.run(
                command,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS
            )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            return (
                result.returncode == 0,
                output.strip()
            )

        except subprocess.TimeoutExpired:

            return (
                False,
                "TIMEOUT: Program exceeded "
                + str(TIMEOUT_SECONDS)
                + " seconds."
            )

        except Exception as error:

            return (
                False,
                str(error)
            )


# ============================================================
# AUTONOMOUS TDD ENGINE
# ============================================================

def autonomous_tdd(
    problem,
    hidden_tests
):

    history = []

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    st.info(
        "🤖 Gemini is generating the initial solution..."
    )

    code = generate_solution(problem)

    history.append(
        "Iteration 0 → Initial code generated"
    )

    # --------------------------------------------------------
    # TEST / DEBUG LOOP
    # --------------------------------------------------------

    for iteration in range(
        1,
        MAX_ITERATIONS + 1
    ):

        st.subheader(
            "🔄 TDD Iteration "
            + str(iteration)
            + " / "
            + str(MAX_ITERATIONS)
        )

        # ----------------------------------------------------
        # SAFETY CHECK
        # ----------------------------------------------------

        unsafe = safety_check(code)

        if unsafe:

            failure = (
                "Restricted operations detected: "
                + ", ".join(unsafe)
            )

            st.warning(
                "⚠️ " + failure
            )

            with st.spinner(
                "Gemini is repairing the code..."
            ):

                code = debug_solution(
                    problem,
                    code,
                    failure,
                    iteration
                )

            history.append(
                "Iteration "
                + str(iteration)
                + " → Security repair"
            )

            continue

        # ----------------------------------------------------
        # RUN TESTS
        # ----------------------------------------------------

        with st.spinner(
            "🧪 Running hidden boundary tests..."
        ):

            passed, output = run_hidden_tests(
                code,
                hidden_tests
            )

        # ----------------------------------------------------
        # PASS
        # ----------------------------------------------------

        if passed:

            st.success(
                "🎉 ALL HIDDEN TESTS PASSED!"
            )

            history.append(
                "Iteration "
                + str(iteration)
                + " → PASSED"
            )

            return code, history

        # ----------------------------------------------------
        # FAILURE
        # ----------------------------------------------------

        st.error(
            "❌ Hidden tests failed."
        )

        with st.expander(
            "🔎 View captured failure"
        ):

            st.code(
                output,
                language="text"
            )

        history.append(
            "Iteration "
            + str(iteration)
            + " → FAILED"
        )

        # ----------------------------------------------------
        # DEBUG
        # ----------------------------------------------------

        with st.spinner(
            "🧠 Gemini is analyzing the failure..."
        ):

            code = debug_solution(
                problem,
                code,
                output[-6000:],
                iteration
            )

    # --------------------------------------------------------
    # MAX ITERATIONS
    # --------------------------------------------------------

    st.warning(
        "⚠️ Maximum TDD iterations reached."
    )

    return code, history


# ============================================================
# PROGRAMMING PROBLEM
# ============================================================

st.subheader("📝 Programming Problem")

problem = st.text_area(
    "Enter the function you want the AI agent to build",

    value=(
        "Write a Python function called "
        "is_palindrome(text).\n\n"

        "Return True if the input text is a palindrome "
        "and False otherwise.\n\n"

        "Ignore spaces and capitalization.\n\n"

        "Handle empty strings, single characters, "
        "mixed capitalization, spaces, and numeric strings."
    ),

    height=200
)


# ============================================================
# HIDDEN TESTS
# ============================================================

HIDDEN_TESTS = """
from solution import is_palindrome


def test_basic_palindrome():
    assert is_palindrome("madam") is True
    assert is_palindrome("hello") is False


def test_empty_string():
    assert is_palindrome("") is True


def test_single_character():
    assert is_palindrome("a") is True
    assert is_palindrome("Z") is True


def test_two_characters():
    assert is_palindrome("aa") is True
    assert is_palindrome("ab") is False


def test_capitalization():
    assert is_palindrome("Madam") is True
    assert is_palindrome("RaceCar") is True


def test_spaces():
    assert is_palindrome("n u n") is True
    assert is_palindrome("a b a") is True
    assert is_palindrome("n  u  n") is True


def test_numeric_strings():
    assert is_palindrome("12321") is True
    assert is_palindrome("12345") is False


def test_long_palindrome():
    assert is_palindrome(
        "A man a plan a canal Panama"
    ) is True
"""


# ============================================================
# START BUTTON
# ============================================================

st.divider()

if st.button(
    "🚀 START AUTONOMOUS TDD",
    type="primary",
    use_container_width=True
):

    if problem.strip() == "":

        st.warning(
            "Please enter a programming problem."
        )

        st.stop()

    try:

        final_code, history = autonomous_tdd(
            problem,
            HIDDEN_TESTS
        )

        # ----------------------------------------------------
        # FINAL CODE
        # ----------------------------------------------------

        st.divider()

        st.header(
            "🏆 Final Generated Code"
        )

        st.code(
            final_code,
            language="python"
        )

        # ----------------------------------------------------
        # HISTORY
        # ----------------------------------------------------

        st.header(
            "📋 Autonomous TDD History"
        )

        for item in history:

            st.write(
                "• " + item
            )

    except Exception as error:

        st.error(
            "Application Error: "
            + str(error)
        )