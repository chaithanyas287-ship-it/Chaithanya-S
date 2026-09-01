import streamlit as st
import sqlite3
import pandas as pd
from google import genai


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Student Academic Records",
    page_icon="🎓",
    layout="wide"
)


# =====================================================
# GEMINI API KEY
# =====================================================

GEMINI_API_KEY = "AQ.Ab8RN6IXI3peb1EKHUWX7r_HWfyy29JYD13KHet7uFHRfQopBg"

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =====================================================
# DATABASE
# =====================================================

DB_NAME = "university.db"


def create_database():

    try:

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll_no INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                course TEXT NOT NULL,
                marks REAL NOT NULL,
                grade TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    except sqlite3.Error as e:

        st.error(f"Database Error: {e}")


# =====================================================
# GRADE CALCULATION
# =====================================================

def calculate_grade(marks):

    if marks >= 90:
        return "A"

    elif marks >= 75:
        return "B"

    elif marks >= 60:
        return "C"

    else:
        return "D"


# =====================================================
# GEMINI: ENGLISH QUESTION -> SQL
# =====================================================

def generate_sql(question):

    prompt = f"""
You are a SQLite database assistant.

The database contains exactly one table:

students

Columns:

roll_no INTEGER
name TEXT
department TEXT
course TEXT
marks REAL
grade TEXT

Department values can be:
Computer Science
Data Science
Electronics
Mechanical

Grade rules:
90 or above = A
75 to 89.99 = B
60 to 74.99 = C
below 60 = D

The user will ask a question in normal English.

Convert the question into ONE SQLite SELECT query.

User question:
{question}

STRICT RULES:

1. Return ONLY the SQL query.
2. Do not use markdown.
3. Only use SELECT.
4. Do not use INSERT.
5. Do not use UPDATE.
6. Do not use DELETE.
7. Do not use DROP.
8. Do not use ALTER.
9. Do not use CREATE.
10. Use only the students table.
11. Do not invent columns.
12. If the question asks for all students, return:
SELECT * FROM students;
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        sql = response.text.strip()

        # Remove markdown if Gemini returns it
        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

        # =================================================
        # SAFETY CHECK
        # =================================================

        sql_upper = sql.upper().strip()

        if not sql_upper.startswith("SELECT"):

            return None, "Gemini did not generate a SELECT query."

        forbidden_words = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "CREATE",
            "REPLACE",
            "TRUNCATE"
        ]

        for word in forbidden_words:

            if word in sql_upper:

                return None, "Only SELECT queries are allowed."

        return sql, None

    except Exception as e:

        return None, str(e)


# =====================================================
# CREATE DATABASE
# =====================================================

create_database()


# =====================================================
# TITLE
# =====================================================

st.title(
    "🎓 Student Academic Records & Report Studio"
)

st.write(
    "Student database with SQLite, Streamlit and Gemini."
)


# =====================================================
# TABS
# =====================================================

tab1, tab2 = st.tabs([
    "🎓 Register Student",
    "📊 Academic Reports"
])


# =====================================================
# TAB 1 - REGISTER
# =====================================================

with tab1:

    st.header("🎓 Register Student")

    with st.form("student_form"):

        roll_no = st.number_input(
            "Roll Number",
            min_value=1,
            step=1
        )

        name = st.text_input(
            "Full Name"
        )

        department = st.selectbox(
            "Department",
            [
                "Computer Science",
                "Data Science",
                "Electronics",
                "Mechanical"
            ]
        )

        course = st.text_input(
            "Course Name"
        )

        marks = st.number_input(
            "Marks",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0
        )

        submitted = st.form_submit_button(
            "Register Student"
        )


    if submitted:

        if name.strip() == "":

            st.warning(
                "Please enter the student's name."
            )

        elif course.strip() == "":

            st.warning(
                "Please enter the course name."
            )

        else:

            grade = calculate_grade(marks)

            try:

                conn = sqlite3.connect(DB_NAME)

                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO students
                    (
                        roll_no,
                        name,
                        department,
                        course,
                        marks,
                        grade
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    roll_no,
                    name,
                    department,
                    course,
                    marks,
                    grade
                ))

                conn.commit()
                conn.close()

                st.success(
                    f"Student '{name}' registered successfully! "
                    f"Grade: {grade}"
                )

            except sqlite3.Error as e:

                st.error(
                    f"Database Error: {e}"
                )


# =====================================================
# TAB 2 - REPORTS
# =====================================================

with tab2:

    st.header("📊 Academic Reports")

    report_options = [
        "All Students List",
        "Top Performers (≥ 75 Marks)",
        "Department-wise Average Marks",
        "Grade Breakdown Count",
        "Custom Query"
    ]

    selected_report = st.selectbox(
        "Select Report Operation",
        report_options
    )


    # =================================================
    # ALL STUDENTS
    # =================================================

    if selected_report == "All Students List":

        query = """
SELECT *
FROM students;
"""


    # =================================================
    # TOP PERFORMERS
    # =================================================

    elif selected_report == "Top Performers (≥ 75 Marks)":

        query = """
SELECT name, department, marks, grade
FROM students
WHERE marks >= 75
ORDER BY marks DESC;
"""


    # =================================================
    # DEPARTMENT AVERAGE
    # =================================================

    elif selected_report == "Department-wise Average Marks":

        query = """
SELECT department,
       AVG(marks) AS avg_marks
FROM students
GROUP BY department;
"""


    # =================================================
    # GRADE BREAKDOWN
    # =================================================

    elif selected_report == "Grade Breakdown Count":

        query = """
SELECT grade,
       COUNT(*) AS total_students
FROM students
GROUP BY grade;
"""


    # =================================================
    # CUSTOM GEMINI QUERY
    # =================================================

    else:

        st.info(
            "🤖 Ask Gemini a question about the students table "
            "using normal English."
        )

        user_question = st.text_input(
            "Ask your question",
            placeholder=(
                "Example: Show Data Science students "
                "who scored above 80"
            )
        )

        query = None

        if user_question.strip():

            query, error = generate_sql(
                user_question
            )

            if error:

                st.error(
                    f"Gemini Error: {error}"
                )


    # =================================================
    # RUN REPORT
    # =================================================

    if st.button("▶ Run Report"):

        if query is None or query.strip() == "":

            st.warning(
                "Please enter a valid question."
            )

        else:

            try:

                conn = sqlite3.connect(DB_NAME)

                df = pd.read_sql_query(
                    query,
                    conn
                )

                conn.close()


                # =====================================
                # SHOW GENERATED SQL
                # =====================================

                st.subheader(
                    "🤖 Gemini Generated SQL"
                )

                st.code(
                    query,
                    language="sql"
                )


                # =====================================
                # SHOW RESULT
                # =====================================

                st.subheader(
                    "📋 Report Result"
                )

                if df.empty:

                    st.info(
                        "No matching records found."
                    )

                else:

                    st.dataframe(
                        df,
                        use_container_width=True
                    )


                    # ================================
                    # CHART
                    # ================================

                    generate_chart = st.checkbox(
                        "Generate Chart Visualization"
                    )

                    if generate_chart:

                        numeric_columns = (
                            df.select_dtypes(
                                include="number"
                            ).columns
                        )

                        if len(numeric_columns) > 0:

                            st.subheader(
                                "📈 Chart Visualization"
                            )

                            st.bar_chart(
                                df[numeric_columns]
                            )

                        else:

                            st.info(
                                "No numerical data available "
                                "for chart visualization."
                            )


            except sqlite3.Error as e:

                st.error(
                    f"SQLite Error: {e}"
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )