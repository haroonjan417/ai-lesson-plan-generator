import json
from io import BytesIO

import streamlit as st
from docx import Document

from config import GROQ_API_KEY
from prompts.lesson_prompt import build_lesson_prompt
from services.groq_service import GroqService
def create_word_document(lesson_plan):
    """Create a Word document from a generated lesson plan."""

    document = Document()

    lesson_info = lesson_plan["lesson_information"]

    # Title
    document.add_heading(
        "AI Generated Lesson Plan",
        level=0
    )

    # Lesson Information
    document.add_heading(
        "1. Lesson Information",
        level=1
    )

    table = document.add_table(
        rows=0,
        cols=2
    )

    information = [
        ("Curriculum", lesson_info["curriculum"]),
        ("Grade / Class", lesson_info["grade"]),
        ("Subject", lesson_info["subject"]),
        ("Topic", lesson_info["topic"]),
        ("Duration", f'{lesson_info["duration_minutes"]} minutes'),
        ("Language", lesson_info["language"]),
    ]

    for label, value in information:
        row = table.add_row().cells
        row[0].text = label
        row[1].text = str(value)

    # Learning Objectives
    document.add_heading(
        "2. Learning Objectives",
        level=1
    )

    for objective in lesson_plan["learning_objectives"]:
        document.add_paragraph(
            objective,
            style="List Bullet"
        )

    # Prior Knowledge
    document.add_heading(
        "3. Prior Knowledge",
        level=1
    )

    document.add_paragraph(
        lesson_plan["prior_knowledge"]
    )

    # Materials
    document.add_heading(
        "4. Teaching & Learning Materials",
        level=1
    )

    for material in lesson_plan["materials"]:
        document.add_paragraph(
            material,
            style="List Bullet"
        )

    # Lesson Sequence
    document.add_heading(
        "5. Lesson Sequence",
        level=1
    )

    sequence_table = document.add_table(
        rows=1,
        cols=5
    )

    headers = [
        "Stage",
        "Duration",
        "Teacher Activity",
        "Student Activity",
        "Assessment / Check"
    ]

    for i, header in enumerate(headers):
        sequence_table.rows[0].cells[i].text = header

    for stage in lesson_plan["lesson_sequence"]:

        row = sequence_table.add_row().cells

        row[0].text = stage["stage"]
        row[1].text = (
            f'{stage["duration_minutes"]} minutes'
        )
        row[2].text = stage["teacher_activity"]
        row[3].text = stage["student_activity"]
        row[4].text = stage["assessment_check"]

    # Assessment
    document.add_heading(
        "6. Assessment",
        level=1
    )

    document.add_paragraph(
        "Formative Assessment",
        style="Heading 2"
    )

    for item in lesson_plan["assessment"]["formative"]:
        document.add_paragraph(
            item,
            style="List Bullet"
        )

    document.add_paragraph(
        "Summative Assessment",
        style="Heading 2"
    )

    document.add_paragraph(
        lesson_plan["assessment"]["summative"]
    )

    # Differentiation
    document.add_heading(
        "7. Differentiation",
        level=1
    )

    document.add_paragraph(
        "Support",
        style="Heading 2"
    )

    document.add_paragraph(
        lesson_plan["differentiation"]["support"]
    )

    document.add_paragraph(
        "Extension",
        style="Heading 2"
    )

    document.add_paragraph(
        lesson_plan["differentiation"]["extension"]
    )

    # Homework
    document.add_heading(
        "8. Homework",
        level=1
    )

    document.add_paragraph(
        lesson_plan["homework"]
    )

    # Teacher Notes
    document.add_heading(
        "9. Teacher Notes",
        level=1
    )

    document.add_paragraph(
        lesson_plan["teacher_notes"]
    )

    # Save document in memory
    file_stream = BytesIO()

    document.save(file_stream)

    file_stream.seek(0)

    return file_stream
def format_av_aids(av_aids):
    """Format selected AV aids for display."""
    if not av_aids:
        return "None specified"
    return ", ".join(av_aids)
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

st.subheader("🏫 School & Teacher Information")

school_name = st.text_input(
    "School Name",
    placeholder="e.g. Government High School"
)

teacher_name = st.text_input(
    "Teacher Name",
    placeholder="e.g. Muhammad Haroon Jan"
)

lesson_date = st.date_input(
    "Lesson Date"
)


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

    av_aids = st.multiselect(
        "🎬 AV / Teaching Aids",
        [
            "Slides / PowerPoint",
            "Video",
            "Projector",
            "Whiteboard",
            "Marker",
            "Blackboard",
            "Textbook",
            "Pictures / Charts",
            "Computer / Laptop",
            "Audio",
            "Other"
        ],
        placeholder="Select the teaching aids you will use"
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
    language=language,
    school_name=school_name,
    teacher_name=teacher_name,
    lesson_date=str(lesson_date),
    av_aids=av_aids
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
          
            # -----------------------------------------
            # ONE-PAGE LESSON PLAN
            # -----------------------------------------

            st.markdown(
                "<h1 style='text-align: center;'>LESSON PLAN</h1>",
                unsafe_allow_html=True
            )

            # -----------------------------------------
            # LESSON HEADER
            # -----------------------------------------

            header_col1, header_col2 = st.columns(2)

            with header_col1:

                st.markdown(
                    f"**🏫 School:** "
                    f"{lesson_info['school_name']}"
                )

                st.markdown(
                    f"**👨‍🏫 Teacher:** "
                    f"{lesson_info['teacher_name']}"
                )

                st.markdown(
                    f"**📚 Curriculum:** "
                    f"{lesson_info['curriculum']}"
                )

                st.markdown(
                    f"**📖 Subject:** "
                    f"{lesson_info['subject']}"
                )

                st.markdown(
                    f"**🎓 Class:** "
                    f"{lesson_info['grade']}"
                )

            with header_col2:

                st.markdown(
                    f"**📅 Date:** "
                    f"{lesson_info['lesson_date']}"
                )

                st.markdown(
                    f"**📝 Topic:** "
                    f"{lesson_info['topic']}"
                )

                st.markdown(
                    f"**⏱️ Duration:** "
                    f"{lesson_info['duration_minutes']} minutes"
                )

                st.markdown(
                    f"**🌐 Language:** "
                    f"{lesson_info['language']}"
                )

                st.markdown(
                    f"**🎬 AV / Teaching Aids:** "
                    f"{format_av_aids(av_aids)}"
                )

            st.divider()

            # -----------------------------------------
            # LEARNING OBJECTIVES
            # -----------------------------------------

            st.subheader("🎯 Learning Objectives")

            objectives_text = " • ".join(
                lesson_plan["learning_objectives"]
            )

            st.write(objectives_text)

            # -----------------------------------------
            # PRIOR KNOWLEDGE
            # -----------------------------------------

            st.subheader("🧠 Prior Knowledge")

            st.write(
                lesson_plan["prior_knowledge"]
            )

            # -----------------------------------------
            # LESSON SEQUENCE
            # -----------------------------------------

            st.subheader("📋 Lesson Sequence")

            sequence_data = []

            for stage in lesson_plan["lesson_sequence"]:

                sequence_data.append(
                    {
                        "Time": (
                            f"{stage['duration_minutes']} min"
                        ),
                        "Stage": stage["stage"],
                        "Teacher / Learning Activity": (
                            stage["teacher_activity"]
                        ),
                        "Student Activity": (
                            stage["student_activity"]
                        ),
                        "Assessment": (
                            stage["assessment_check"]
                        )
                    }
                )

            st.table(sequence_data)

            # -----------------------------------------
            # ASSESSMENT & DIFFERENTIATION
            # -----------------------------------------

            assessment_col, differentiation_col = st.columns(2)

            with assessment_col:

                st.subheader("📝 Assessment")

                formative = lesson_plan[
                    "assessment"
                ]["formative"]

                for item in formative:
                    st.markdown(f"- {item}")

                st.markdown(
                    "**Summative:** "
                    + lesson_plan["assessment"]["summative"]
                )

            with differentiation_col:

                st.subheader("🔄 Differentiation")

                st.markdown(
                    "**Support:** "
                    + lesson_plan["differentiation"]["support"]
                )

                st.markdown(
                    "**Extension:** "
                    + lesson_plan["differentiation"]["extension"]
                )

            # -----------------------------------------
            # HOMEWORK & TEACHER NOTES
            # -----------------------------------------

            homework_col, notes_col = st.columns(2)

            with homework_col:

                st.subheader("🏠 Homework")

                st.write(
                    lesson_plan["homework"]
                )

            with notes_col:

                st.subheader("👨‍🏫 Teacher Notes")

                st.write(
                    lesson_plan["teacher_notes"]
                )

            # -----------------------------------------
            # DURATION VALIDATION
            # -----------------------------------------

            total_stage_duration = sum(
                stage["duration_minutes"]
                for stage in lesson_plan["lesson_sequence"]
            )

            if total_stage_duration == duration:

                st.success(
                    f"⏱️ Duration validated: "
                    f"{total_stage_duration} minutes "
                    f"(matches the selected duration)."
                )

            else:

                st.warning(
                    f"⚠️ Duration mismatch: "
                    f"Selected duration = {duration} minutes, "
                    f"but lesson stages total "
                    f"{total_stage_duration} minutes."
                )            # -----------------------------------------
            # WORD DOWNLOAD
            # -----------------------------------------

            st.divider()

            st.subheader("📥 Download Lesson Plan")

            word_file = create_word_document(
                lesson_plan
            )

            st.download_button(
                label="📄 Download as Word",
                data=word_file,
                file_name=(
                    f"{lesson_info['topic']}_Lesson_Plan.docx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True
            )


        except Exception as e:

            st.error(
                "❌ An error occurred while generating "
                "the lesson plan."
            )

            st.exception(e)
