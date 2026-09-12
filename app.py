import json

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
        "Please configure GROQ_API_KEY before generating "
        "a lesson plan."
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

    # ---------------------------------------------
    # VALIDATE REQUIRED FIELDS
    # ---------------------------------------------

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

            # -----------------------------------------
            # BUILD PROMPT
            # -----------------------------------------

            prompt = build_lesson_prompt(
                curriculum=curriculum,
                grade=grade,
                subject=subject,
                duration=duration,
                topic=topic,
                language=language
            )


            # -----------------------------------------
            # CONNECT TO GROQ
            # -----------------------------------------

            groq_service = GroqService(
                api_key=GROQ_API_KEY
            )


            # -----------------------------------------
            # GENERATE LESSON PLAN
            # -----------------------------------------

            with st.spinner(
                "🤖 Generating your lesson plan..."
            ):

                response = groq_service.generate_response(
                    prompt=prompt
                )


            # -----------------------------------------
            # PARSE JSON RESPONSE
            # -----------------------------------------

            try:

                lesson_plan = json.loads(response)

            except json.JSONDecodeError:

                st.error(
                    "❌ The AI returned an invalid lesson "
                    "plan format."
                )

                st.code(response)

                st.stop()


            # -----------------------------------------
            # SUCCESS MESSAGE
            # -----------------------------------------

            st.success(
                "✅ Lesson plan generated successfully!"
            )


            # -----------------------------------------
            # LESSON INFORMATION
            # -----------------------------------------

            st.subheader("📚 Lesson Plan")

            lesson_info = lesson_plan["lesson_information"]

            info_col1, info_col2, info_col3 = st.columns(3)

            with info_col1:
                st.markdown(
                    f"**Curriculum:** {lesson_info['curriculum']}"
                )

                st.markdown(
                    f"**Grade:** {lesson_info['grade']}"
                )

            with info_col2:
                st.markdown(
                    f"**Subject:** {lesson_info['subject']}"
                )

                st.markdown(
                    f"**Topic:** {lesson_info['topic']}"
                )

            with info_col3:
                st.markdown(
                    f"**Duration:** "
                    f"{lesson_info['duration_minutes']} minutes"
                )

                st.markdown(
                    f"**Language:** {lesson_info['language']}"
                )


            st.divider()


            # -----------------------------------------
            # LEARNING OBJECTIVES
            # -----------------------------------------

            st.subheader("🎯 Learning Objectives")

            for objective in lesson_plan["learning_objectives"]:

                st.markdown(
                    f"- {objective}"
                )


            # -----------------------------------------
            # PRIOR KNOWLEDGE
            # -----------------------------------------

            st.subheader("🧠 Prior Knowledge")

            st.write(
                lesson_plan["prior_knowledge"]
            )


            # -----------------------------------------
            # MATERIALS
            # -----------------------------------------

            st.subheader("🧰 Teaching & Learning Materials")

            for material in lesson_plan["materials"]:

                st.markdown(
                    f"- {material}"
                )


            # -----------------------------------------
            # LESSON SEQUENCE
            # -----------------------------------------

            st.subheader("📋 Lesson Sequence")

            for stage in lesson_plan["lesson_sequence"]:

                with st.expander(
                    f"{stage['stage']} "
                    f"— {stage['duration_minutes']} minutes",
                    expanded=True
                ):

                    st.markdown("**👨‍🏫 Teacher Activity**")

                    st.write(
                        stage["teacher_activity"]
                    )

                    st.markdown("**👩‍🎓 Student Activity**")

                    st.write(
                        stage["student_activity"]
                    )

                    st.markdown(
                        "**✅ Assessment / Check for Understanding**"
                    )

                    st.write(
                        stage["assessment_check"]
                    )


            # -----------------------------------------
            # ASSESSMENT
            # -----------------------------------------

            st.subheader("📝 Assessment")

            st.markdown("**Formative Assessment**")

            for item in lesson_plan["assessment"]["formative"]:

                st.markdown(
                    f"- {item}"
                )

            st.markdown("**Summative Assessment**")

            st.write(
                lesson_plan["assessment"]["summative"]
            )


            # -----------------------------------------
            # DIFFERENTIATION
            # -----------------------------------------

            st.subheader("🔄 Differentiation")

            diff_col1, diff_col2 = st.columns(2)

            with diff_col1:

                st.markdown("### 🆘 Support")

                st.write(
                    lesson_plan["differentiation"]["support"]
                )

            with diff_col2:

                st.markdown("### 🚀 Extension")

                st.write(
                    lesson_plan["differentiation"]["extension"]
                )


            # -----------------------------------------
            # HOMEWORK
            # -----------------------------------------

            st.subheader("🏠 Homework")

            st.write(
                lesson_plan["homework"]
            )


            # -----------------------------------------
            # TEACHER NOTES
            # -----------------------------------------

            st.subheader("👨‍🏫 Teacher Notes")

            st.write(
                lesson_plan["teacher_notes"]
            )


        except Exception as e:

            st.error(
                "❌ An error occurred while generating "
                "the lesson plan."
            )

            st.exception(e)
