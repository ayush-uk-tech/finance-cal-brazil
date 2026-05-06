from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
import io
import os

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

app = FastAPI()

# --- PYDANTIC MODEL (Input Data Validation) ---
class BrazilOfferLetterData(BaseModel):
    name: str
    role: str
    client: str
    start_date: str
    reporting_to: str
    annual_salary: str
    probation: str
    expiry_date: str
    hr_name: str

# --- MAIN API ROUTE ---
@app.post("/generate-brazil-offer")
async def generate_brazil_offer_api(data: BrazilOfferLetterData):
    try:
        # Vercel-safe in-memory buffer
        buffer = io.BytesIO()
        
        # Dynamic File Name
        pdf_filename = f"{data.name.replace(' ', '_')}_Brazil_Offer_Letter.pdf"
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        elements = []

        # Customize styles
        styles = getSampleStyleSheet()
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=10.5
        )

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=15,
            spaceAfter=10
        )

        # 1. Load and Align the Local Logo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "img.png")
        
        if os.path.exists(logo_path):
            try:
                img_reader = ImageReader(logo_path)
                orig_width, orig_height = img_reader.getSize()
                aspect_ratio = orig_height / float(orig_width)

                target_width = 120
                target_height = target_width * aspect_ratio

                logo = Image(logo_path, width=target_width, height=target_height)
                logo.hAlign = 'LEFT'

                elements.append(logo)
                elements.append(Spacer(1, 10))
            except Exception as e:
                print(f"Warning: Could not process the logo ({e}).")

        # 2. Document Title
        title = Paragraph("<b><u>Potentiam Brasil Ltda - Employment Offer</u></b>", title_style)
        elements.append(title)
        elements.append(Spacer(1, 10))

        # 3. Intro Paragraph
        intro_text = f"We are pleased to offer you the full-time position of <b>{data.role}</b> at Potentiam Brasil Ltda, assigned to <b>{data.client}</b> with a start date of <b>{data.start_date}</b>."
        elements.append(Paragraph(intro_text, normal_style))
        elements.append(Spacer(1, 15))

        # 4. Define Static Table Content
        office_hours = """44 hours per week at 8 hours per day (excl. 1 hour break). Your daily work hours will be 09:00 am until 18:00 pm (BRT - Brazilian Time) or as determined by the Client. Standard Brazilian working hours with flexibility for client requirements."""

        work_schedule = """You are required to attend work at the office 5 days a week both during probation and thereafter. Hybrid work arrangement (WFH/Office) is at your manager’s discretion and as per company policy and Brazilian labor law."""

        benefits = """• Health Insurance: Company provided health insurance coverage as per Brazilian law;<br/>
    • FGTS: 8% employer contribution as per Brazilian labor law;<br/>
    • INSS: Employer and employee contributions as per Social Security regulations;<br/>
    • 13th Salary: Mandatory annual bonus as per CLT (Brazilian labor law);<br/>
    • Vacation Pay: 30 days paid vacation with 1/3 constitutional bonus as per Brazilian law."""

        # 5. Formulating the Table Data
        table_data = [
            ["Name:", Paragraph(data.name, normal_style)],
            ["Role:", Paragraph(data.role, normal_style)],
            ["Reporting to:", Paragraph(data.reporting_to, normal_style)],
            ["Start Date:", Paragraph(data.start_date, normal_style)],
            ["Office hours:", Paragraph(office_hours, normal_style)],
            ["Work schedule:", Paragraph(work_schedule, normal_style)],
            ["Annual GROSS Salary Details:", Paragraph(data.annual_salary, normal_style)],
            ["Benefits:", Paragraph(benefits, normal_style)],
            ["Probation Period:", Paragraph(data.probation, normal_style)],
            ["Notice Period:", Paragraph("1 week during probation thereafter 1 months’ notice is required.", normal_style)],
            ["Contractual Terms:",
             Paragraph("As per standard company employment contract – copy will be sent upon signing this offer letter",
                       normal_style)],
            ["Annual leave:", Paragraph("30 calendar days annual leave as per CLT (Brazilian labor law)", normal_style)]
        ]

        # 6. Create and Style the Table
        t = Table(table_data, colWidths=[140, 400])
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), 
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ]))

        elements.append(t)
        elements.append(Spacer(1, 15))

        # 7. Outro & Signature Section
        outro_text = f"""
    If you are happy with the above terms, please sign accordingly, before C.O.B. <b>{data.expiry_date}</b>.<br/><br/>
    We look forward to having you in our community! If you have any questions, please feel free to reach out at your earliest convenience.<br/><br/>
    I, <b>{data.name}</b>, accept the above terms of employment subject only to receipt and agreement to the full employment contract reflecting the above.<br/><br/><br/>
    ……………………………………………….. (signature) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date:- Read, agreed and Accepted<br/><br/>
    On receipt of the signed offer letter, an employment contract detailing all the above terms will be provided for your review and signature.<br/><br/>
    Yours sincerely,<br/>
    <b>{data.hr_name}</b><br/>
    Potentiam Brasil Ltda
    """

        elements.append(Paragraph(outro_text, normal_style))

        # Build PDF into the BytesIO buffer
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Return the generated PDF to the user/n8n
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
        )

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}