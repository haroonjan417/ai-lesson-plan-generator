import json
from io import BytesIO

import streamlit as st
from docx import Document

from config import GROQ_API_KEY
from prompts.lesson_prompt import build_lesson_prompt
from services.groq_service import GroqService
def create_word_document(lesson_plan, av_aids=None):
    """Create a professional one-page A4 Word lesson plan."""

    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    document = Document()

    # ---------------------------------------------------------
    # PAGE SETUP - A4
    # ---------------------------------------------------------

    section = document.sections[0]

    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)

    section.top_margin = Inches(0.35)
    section.bottom_margin = Inches(0.35)
    section.left_margin = Inches(0.4)
    section.right_margin = Inches(0.4)

    # ---------------------------------------------------------
    # DEFAULT FONT
    # ---------------------------------------------------------

    styles = document.styles

    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(7.5)

    # ---------------------------------------------------------
    # HELPER FUNCTIONS
    # ---------------------------------------------------------

    def set_cell_shading(cell, fill):
        """Set background color of a table cell."""

        tc_pr = cell._tc.get_or_add_tcPr()

        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), fill)

        tc_pr.append(shd)

    def set_cell_margins(cell, top=40, start=50, bottom=40, end=50):
        """Set compact cell margins."""

        tc = cell._tc
        tc_pr = tc.get_or_add_tcPr()

        tc_mar = tc_pr.first_child_found_in("w:tcMar")

        if tc_mar is None:
            tc_mar = OxmlElement("w:tcMar")
            tc_pr.append(tc_mar)

        for margin, value in [
            ("top", top),
            ("start", start),
            ("bottom", bottom),
            ("end", end)
        ]:
            node = tc_mar.find(qn(f"w:{margin}"))

            if node is None:
                node = OxmlElement(f"w:{margin}")
                tc_mar.append(node)

            node.set(qn("w:w"), str(value))
            node.set(qn("w:type"), "dxa")

    def set_repeat_table_header(row):
        """Repeat table header if table extends to another page."""

        tr_pr = row._tr.get_or_add_trPr()

        tbl_header = OxmlElement("w:tblHeader")
        tbl_header.set(qn("w:val"), "true")

        tr_pr.append(tbl_header)

    def add_compact_text(cell, text, bold=False, size=7.5):
        """Add compact text to a table cell."""

        cell.text = ""

        paragraph = cell.paragraphs[0]

        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1

        run = paragraph.add_run(str(text))
        run.bold = bold
        run.font.name = "Arial"
        run.font.size = Pt(size)

        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

        set_cell_margins(cell)

    # ---------------------------------------------------------
    # LESSON INFORMATION
    # ---------------------------------------------------------

    lesson_info = lesson_plan["lesson_information"]

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    title = document.add_paragraph()

    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    title.paragraph_format.space_before = Pt(0)
    title.paragraph_format.space_after = Pt(3)

    run = title.add_run("LESSON PLAN")

    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(15)

    # ---------------------------------------------------------
    # SCHOOL / TEACHER / LESSON INFORMATION TABLE
    # ---------------------------------------------------------

    info_table = document.add_table(
        rows=5,
        cols=4
    )

    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.autofit = True

    info_data = [
        (
            "School",
            lesson_info["school_name"],
            "Date",
            lesson_info["lesson_date"]
        ),
        (
            "Teacher",
            lesson_info["teacher_name"],
            "Class",
            lesson_info["grade"]
        ),
        (
            "Subject",
            lesson_info["subject"],
            "Topic",
            lesson_info["topic"]
        ),
        (
            "Curriculum",
            lesson_info["curriculum"],
            "Duration",
            f'{lesson_info["duration_minutes"]} min'
        ),
        (
            "Language",
            lesson_info["language"],
            "AV / Teaching Aids",
            ", ".join(av_aids) if av_aids else "None specified"
        )
    ]

    for row_index, row_data in enumerate(info_data):

        row = info_table.rows[row_index]

        for col_index, value in enumerate(row_data):

            cell = row.cells[col_index]

            if col_index in [0, 2]:
                set_cell_shading(cell, "D9EAF7")

                add_compact_text(
                    cell,
                    value,
                    bold=True,
                    size=7
                )

            else:
                add_compact_text(
                    cell,
                    value,
                    size=7
                )

    # ---------------------------------------------------------
    # OBJECTIVES
    # ---------------------------------------------------------

    heading = document.add_paragraph()

    heading.paragraph_format.space_before = Pt(3)
    heading.paragraph_format.space_after = Pt(1)

    run = heading.add_run("LEARNING OBJECTIVES")
    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(9)

    objectives = document.add_paragraph()

    objectives.paragraph_format.space_before = Pt(0)
    objectives.paragraph_format.space_after = Pt(2)
    objectives.paragraph_format.line_spacing = 1

    for index, objective in enumerate(
        lesson_plan["learning_objectives"],
        start=1
    ):

        run = objectives.add_run(
            f"{index}. {objective}  "
        )

        run.font.name = "Arial"
        run.font.size = Pt(7.5)

    # ---------------------------------------------------------
    # PRIOR KNOWLEDGE
    # ---------------------------------------------------------

    heading = document.add_paragraph()

    heading.paragraph_format.space_before = Pt(1)
    heading.paragraph_format.space_after = Pt(1)

    run = heading.add_run("PRIOR KNOWLEDGE")

    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(9)

    prior = document.add_paragraph(
        lesson_plan["prior_knowledge"]
    )

    prior.paragraph_format.space_before = Pt(0)
    prior.paragraph_format.space_after = Pt(2)
    prior.paragraph_format.line_spacing = 1

    for run in prior.runs:
        run.font.name = "Arial"
        run.font.size = Pt(7.5)

    # ---------------------------------------------------------
    # LESSON SEQUENCE TABLE
    # ---------------------------------------------------------

    heading = document.add_paragraph()

    heading.paragraph_format.space_before = Pt(1)
    heading.paragraph_format.space_after = Pt(1)

    run = heading.add_run("LESSON SEQUENCE")

    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(9)

    sequence_table = document.add_table(
        rows=1,
        cols=5
    )

    sequence_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sequence_table.autofit = True

    headers = [
        "Time",
        "Stage",
        "Teacher / Learning Activity",
        "Student Activity",
        "Assessment"
    ]

    header_row = sequence_table.rows[0]

    set_repeat_table_header(header_row)

    for index, header in enumerate(headers):

        cell = header_row.cells[index]

        set_cell_shading(cell, "B4C7E7")

        add_compact_text(
            cell,
            header,
            bold=True,
            size=7
        )

    for stage in lesson_plan["lesson_sequence"]:

        row = sequence_table.add_row()

        values = [
            f'{stage["duration_minutes"]} min',
            stage["stage"],
            stage["teacher_activity"],
            stage["student_activity"],
            stage["assessment_check"]
        ]

        for index, value in enumerate(values):

            add_compact_text(
                row.cells[index],
                value,
                size=6.8
            )

    # ---------------------------------------------------------
    # BOTTOM INFORMATION TABLE
    # ---------------------------------------------------------

    bottom_table = document.add_table(
        rows=2,
        cols=3
    )

    bottom_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    bottom_table.autofit = True

    bottom_headers = [
        "ASSESSMENT",
        "DIFFERENTIATION",
        "HOMEWORK"
    ]

    for index, header in enumerate(bottom_headers):

        cell = bottom_table.rows[0].cells[index]

        set_cell_shading(cell, "D9EAF7")

        add_compact_text(
            cell,
            header,
            bold=True,
            size=7
        )

    formative = lesson_plan["assessment"]["formative"]

    assessment_text = "; ".join(formative)

    summative = lesson_plan["assessment"]["summative"]

    assessment_text = (
        assessment_text
        + " "
        + "Summative: "
        + summative
    )

    differentiation_text = (
        "Support: "
        + lesson_plan["differentiation"]["support"]
        + " "
        + "Extension: "
        + lesson_plan["differentiation"]["extension"]
    )

    bottom_values = [
        assessment_text,
        differentiation_text,
        lesson_plan["homework"]
    ]

    for index, value in enumerate(bottom_values):

        add_compact_text(
            bottom_table.rows[1].cells[index],
            value,
            size=6.7
        )

    # ---------------------------------------------------------
    # TEACHER NOTES
    # ---------------------------------------------------------

    heading = document.add_paragraph()

    heading.paragraph_format.space_before = Pt(2)
    heading.paragraph_format.space_after = Pt(1)

    run = heading.add_run("TEACHER NOTES")

    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(8.5)

    notes = document.add_paragraph(
        lesson_plan["teacher_notes"]
    )

    notes.paragraph_format.space_before = Pt(0)
    notes.paragraph_format.space_after = Pt(0)
    notes.paragraph_format.line_spacing = 1

    for run in notes.runs:
        run.font.name = "Arial"
        run.font.size = Pt(6.8)

    # ---------------------------------------------------------
    # SAVE TO MEMORY
    # ---------------------------------------------------------

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
                lesson_plan,
                av_aids=av_aids
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
