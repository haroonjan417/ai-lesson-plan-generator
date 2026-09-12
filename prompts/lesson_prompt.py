def build_lesson_prompt(
    curriculum,
    grade,
    subject,
    duration,
    topic,
    language="English"
):
    """
    Build a professional prompt for generating a lesson plan.
    """

    prompt = f"""
You are an expert curriculum designer, educational consultant,
and experienced classroom teacher.

Your task is to create a professional, practical, teacher-ready
lesson plan based on the information provided below.

LESSON INFORMATION

Curriculum:
{curriculum}

Grade:
{grade}

Subject:
{subject}

Topic:
{topic}

Class Duration:
{duration} minutes

Language:
{language}


GENERAL REQUIREMENTS

1. Make the lesson appropriate for the specified grade level.
2. Align the lesson with the specified curriculum as far as the
   provided information allows.
3. Create measurable and realistic learning objectives.
4. Use age-appropriate teaching strategies.
5. Include both teacher activities and student activities.
6. Include meaningful formative assessment.
7. Include differentiation for learners who need additional support
   and learners who need extension.
8. Allocate realistic time to each lesson stage.
9. The total duration of all lesson stages MUST equal exactly
   {duration} minutes.
10. The lesson should be practical for a normal classroom.
11. Avoid unnecessary repetition.
12. Use clear professional language.
13. Do not invent curriculum standards that were not provided.
14. If the curriculum information is general, create a curriculum-
   appropriate lesson without claiming a specific official standard.


LESSON STRUCTURE

Create the following sections:

1. Lesson Information
2. Learning Objectives
3. Prior Knowledge
4. Teaching and Learning Materials
5. Lesson Sequence
6. Assessment
7. Differentiation
8. Homework
9. Teacher Notes


LESSON SEQUENCE

For every stage provide:

- Stage name
- Duration in minutes
- Teacher activity
- Student activity
- Assessment/check for understanding


OUTPUT REQUIREMENT

Return ONLY valid JSON.

Do not include Markdown.
Do not include ```json.
Do not include explanations before or after the JSON.

Use exactly this structure:

{{
    "lesson_information": {{
        "curriculum": "",
        "grade": "",
        "subject": "",
        "topic": "",
        "duration_minutes": 0,
        "language": ""
    }},
    "learning_objectives": [
        ""
    ],
    "prior_knowledge": "",
    "materials": [
        ""
    ],
    "lesson_sequence": [
        {{
            "stage": "",
            "duration_minutes": 0,
            "teacher_activity": "",
            "student_activity": "",
            "assessment_check": ""
        }}
    ],
    "assessment": {{
        "formative": [
            ""
        ],
        "summative": ""
    }},
    "differentiation": {{
        "support": "",
        "extension": ""
    }},
    "homework": "",
    "teacher_notes": ""
}}
"""

    return prompt
