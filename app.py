import streamlit as st

from config import GROQ_API_KEY
from prompts.lesson_prompt import build_lesson_prompt
from services.groq_service import GroqService


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Lesson Plan Generator",
    page_icon="📚",
    layout="wide"
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("📚 AI Lesson Plan Generator")

st.write(
    "Create professional, teacher-ready lesson plans using AI."
)

st.divider()


# ---------------------------------------------------------
# API CONFIGURATION CHECK
# ---------------------------------------------------------

if not GROQ_API_KEY:
    st.error(
        "⚠️ Groq API key is not configured. "
        "Please configure GROQ_API_KEY before generating a lesson plan."
    )
    st.stop()


# ---------------------------------------------------------
# LESSON INPUT FORM
# ---------------------------------------------------------

st.subheader("📝 Lesson Information")

col1, col2 = st.columns(2)

with col1:

    curriculum = st.text_input(
        "Curriculum",
        placeholder="e.g. Punjab Curriculum / Federal Board / Cambridge"
    )

    grade = st.text_input(
        "Grade / Class",
        placeholder="e.g. Grade 5"
    )

    subject = st.text_input(
        "Subject",
        placeholder="e.g. Mathematics"
    )


with col2:

    topic = st.text_input(
        "Lesson Topic",
        placeholder="e.g. Fractions"
    )

    duration = st.number_input(
        "Class Duration (minutes)",
        min_value=10,
        max_value=180,
        value=40,
        step=5
    )

    language = st.selectbox(
        "Lesson Language",
        [
            "English",
            "Urdu",
            "English + Urdu"
        ]
    )


st.divider()


# ---------------------------------------------------------
# GENERATE BUTTON
# ---------------------------------------------------------

generate_button = st.button(
    "✨ Generate Lesson Plan",
    type="primary",
    use_container_width=True
)


# ---------------------------------------------------------
# GENERATION PROCESS
# ---------------------------------------------------------

if generate_button:

    # Validate required fields
    if not curriculum.strip():
        st.warning("Please enter the curriculum.")

    elif not grade.strip():
        st.warning("Please enter the grade/class.")

    elif not subject.strip():
        st.warning("Please enter the subject.")

    elif not topic.strip():
        st.warning("Please enter the lesson topic.")

    else:

        try:

            # ---------------------------------------------
            # BUILD PROMPT
            # ---------------------------------------------

            prompt = build_lesson_prompt(
                curriculum=curriculum,
                grade=grade,
                subject=subject,
                duration=duration,
                topic=topic,
                language=language
            )


            # ---------------------------------------------
            # CONNECT TO GROQ
            # ---------------------------------------------

            groq_service = GroqService(
                api_key=GROQ_API_KEY
            )


            # ---------------------------------------------
            # GENERATE LESSON PLAN
            # ---------------------------------------------

            with st.spinner(
                "🤖 Generating your lesson plan..."
            ):

                response = groq_service.generate_response(
                    prompt=prompt
                )


            # ---------------------------------------------
            # DISPLAY RAW RESPONSE
            # ---------------------------------------------

            st.success(
                "✅ Lesson plan generated successfully!"
            )

            st.subheader("📚 Generated Lesson Plan")

            st.write(response)


        except Exception as e:

            st.error(
                "❌ An error occurred while generating "
                "the lesson plan."
            )

            st.exception(e)
