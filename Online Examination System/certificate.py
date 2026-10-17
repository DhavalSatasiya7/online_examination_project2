import os
import random

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate
from werkzeug.utils import secure_filename

def generate_certificate(
        student_name,
        subject_name,
        band_score,
        exam_date
):

    # -----------------------------------------------------
    # CERTIFICATE FOLDER
    # -----------------------------------------------------

    base_folder = os.path.dirname(
        os.path.abspath(__file__)
    )

    folder = os.path.join(
        base_folder,
        "generated_certificates"
    )

    os.makedirs(
        folder,
        exist_ok=True
    )


    # -----------------------------------------------------
    # SAFE NAMES
    # -----------------------------------------------------

    safe_student_name = secure_filename(
        str(student_name)
    )

    safe_subject_name = secure_filename(
        str(subject_name)
    )


    # -----------------------------------------------------
    # CERTIFICATE FILE NAME
    # -----------------------------------------------------

    certificate_id = (
        "CERT-" +
        str(random.randint(100000, 999999))
    )


    filename = (
        f"{safe_student_name}_"
        f"{safe_subject_name}_"
        f"{certificate_id}_"
        f"Certificate.pdf"
    )


    certificate_path = os.path.join(
        folder,
        filename
    )


    # -----------------------------------------------------
    # YOUR EXISTING REPORTLAB CERTIFICATE DESIGN
    # -----------------------------------------------------

    doc = SimpleDocTemplate(
        certificate_path,
        pagesize=(842, 595),
        leftMargin=25,
        rightMargin=25,
        topMargin=25,
        bottomMargin=25
    )


    styles = getSampleStyleSheet()

    story = []


    # Keep your existing certificate design here.
    # The important change is that certificate_path
    # now points to the correct absolute folder.


    # Example basic content:

    story.append(
        Paragraph(
            "CERTIFICATE OF ACHIEVEMENT",
            styles["Title"]
        )
    )


    story.append(
        Spacer(1, 30)
    )


    story.append(
        Paragraph(
            f"This certificate is proudly presented to "
            f"<b>{student_name}</b>",
            styles["Heading2"]
        )
    )


    story.append(
        Spacer(1, 20)
    )


    story.append(
        Paragraph(
            f"for successfully completing the "
            f"<b>{subject_name}</b> examination.",
            styles["Normal"]
        )
    )


    story.append(
        Spacer(1, 20)
    )


    story.append(
        Paragraph(
            f"<b>Band Score: {band_score:.1f}</b>",
            styles["Heading2"]
        )
    )


    story.append(
        Spacer(1, 15)
    )


    story.append(
        Paragraph(
            f"Exam Date: {exam_date}",
            styles["Normal"]
        )
    )


    story.append(
        Spacer(1, 15)
    )


    story.append(
        Paragraph(
            f"Certificate ID: {certificate_id}",
            styles["Normal"]
        )
    )


    # -----------------------------------------------------
    # BUILD
    # -----------------------------------------------------

    doc.build(story)


    print("====================================")
    print("CERTIFICATE GENERATED")
    print("PATH:", certificate_path)
    print("EXISTS:", os.path.isfile(certificate_path))
    print("====================================")


    return certificate_path