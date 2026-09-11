from datetime import date

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models import Complaint


from app.schemas import (
    ComplaintCreate,
    ComplaintParseRequest,
    ComplaintParseResponse,
)

from app.ai_complaint import analyze_complaint_text
from app.ai_complaint import correct_complaint_data
from app.ai_complaint import check_complaint_completeness
from app.ai_complaint import recommend_complaint_root_cause
from app.ai_complaint import detect_complaint_duplicate
from app.ai_complaint import recommend_complaint_capa
from app.ai_complaint import create_complaint_summary
from app.ai_complaint import classify_complaint_risk_data

from pypdf import PdfReader


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="AIVOA Complaint Management System"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message": "AIVOA Complaint Management System API is running"
    }


# ==================================================
# CREATE COMPLAINT
# ==================================================

@app.post("/complaints")
def create_complaint(
    complaint: ComplaintCreate,
    db: Session = Depends(get_db),
):

    try:

        new_complaint = Complaint(
            **complaint.model_dump()
        )

        db.add(new_complaint)

        db.commit()

        db.refresh(new_complaint)

        return {
            "message": "Complaint committed successfully",
            "complaint_id": new_complaint.id,
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create complaint: {str(e)}",
        )


# ==================================================
# GET ALL COMPLAINTS
# ==================================================

@app.get("/complaints")
def get_complaints(
    db: Session = Depends(get_db),
):

    complaints = (
        db.query(Complaint)
        .order_by(Complaint.id.desc())
        .all()
    )

    return complaints


# ==================================================
# GET SINGLE COMPLAINT
# ==================================================

@app.get("/complaints/{complaint_id}")
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
):

    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if not complaint:

        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    return complaint


# ==================================================
# ANALYZE COMPLAINT TEXT
# ==================================================

@app.post(
    "/complaints/parse",
    response_model=ComplaintParseResponse,
)
def parse_complaint(
    request: ComplaintParseRequest,
):

    try:

        ai_result = analyze_complaint_text(
            request.text
        )

        # ------------------------------------------
        # Convert AI dates
        # ------------------------------------------

        manufacturing_date = None
        expiry_date = None

        if ai_result.get("manufacturing_date"):

            try:

                manufacturing_date = date.fromisoformat(
                    ai_result["manufacturing_date"]
                )

            except Exception:

                manufacturing_date = None

        if ai_result.get("expiry_date"):

            try:

                expiry_date = date.fromisoformat(
                    ai_result["expiry_date"]
                )

            except Exception:

                expiry_date = None

        # ------------------------------------------
        # Severity → Priority
        # ------------------------------------------

        severity = ai_result.get("severity")

        if severity == "Critical":

            priority = "Critical"

        elif severity == "Major":

            priority = "High"

        else:

            priority = "Normal"

        # ------------------------------------------
        # Response
        # ------------------------------------------

        return ComplaintParseResponse(

            complaint_source=ai_result.get(
                "complaint_source"
            ),

            customer_name=ai_result.get(
                "customer_name"
            ),

            product_name=ai_result.get(
                "product_name"
            ),

            product_strength=ai_result.get(
                "product_strength"
            ),

            batch_number=ai_result.get(
                "batch_number"
            ),

            manufacturing_date=manufacturing_date,

            expiry_date=expiry_date,

            quantity_affected=ai_result.get(
                "quantity_affected"
            ),

            originating_site=ai_result.get(
                "originating_site"
            ),

            block_impacted=ai_result.get(
                "block_impacted"
            ),

            npm=ai_result.get(
                "npm"
            ),

            complaint_type=ai_result.get(
                "complaint_category"
            ),

            detailed_description=ai_result.get(
                "complaint_description"
            ),

            initial_severity=severity,

            suggested_next_action=ai_result.get(
                "suggested_next_action"
            ),

            initial_risk_assessment=ai_result.get(
                "initial_risk_assessment"
            ),

            priority=priority,
        )

    except Exception as e:

        print(
            "Complaint AI analysis error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}",
        )


# ==================================================
# CORRECT COMPLAINT
# ==================================================

class ComplaintCorrectionRequest(BaseModel):

    current_data: dict

    correction_text: str


@app.post("/complaints/correct")
def correct_complaint(
    request: ComplaintCorrectionRequest,
):

    try:

        updated_data = correct_complaint_data(
            request.current_data,
            request.correction_text,
        )

        return updated_data

    except Exception as e:

        print(
            "Complaint correction error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=f"Complaint correction failed: {str(e)}",
        )


# ==================================================
# ANALYZE COMPLAINT PDF
# ==================================================

@app.post("/complaints/parse-pdf")
async def parse_pdf(
    file: UploadFile = File(...)
):

    try:

        # ------------------------------------------
        # Check file type
        # ------------------------------------------

        if not file.filename.lower().endswith(".pdf"):

            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported.",
            )

        # ------------------------------------------
        # Read uploaded file
        # ------------------------------------------

        contents = await file.read()

        import io

        pdf_file = io.BytesIO(contents)

        reader = PdfReader(pdf_file)

        # ------------------------------------------
        # Extract text
        # ------------------------------------------

        extracted_text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                extracted_text += (
                    page_text + "\n"
                )

        # ------------------------------------------
        # Check extracted text
        # ------------------------------------------

        if not extracted_text.strip():

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from this PDF.",
            )

        # ------------------------------------------
        # Send PDF text to AI
        # ------------------------------------------

        ai_result = analyze_complaint_text(
            extracted_text
        )

        # ------------------------------------------
        # Convert dates
        # ------------------------------------------

        manufacturing_date = None
        expiry_date = None

        if ai_result.get("manufacturing_date"):

            try:

                manufacturing_date = date.fromisoformat(
                    ai_result["manufacturing_date"]
                )

            except Exception:

                manufacturing_date = None

        if ai_result.get("expiry_date"):

            try:

                expiry_date = date.fromisoformat(
                    ai_result["expiry_date"]
                )

            except Exception:

                expiry_date = None

        # ------------------------------------------
        # Severity → Priority
        # ------------------------------------------

        severity = ai_result.get("severity")

        if severity == "Critical":

            priority = "Critical"

        elif severity == "Major":

            priority = "High"

        else:

            priority = "Normal"

        # ------------------------------------------
        # Map AI result to frontend fields
        # ------------------------------------------

        response_data = {

            "complaint_source":
                ai_result.get(
                    "complaint_source"
                ),

            "customer_name":
                ai_result.get(
                    "customer_name"
                ),

            "product_name":
                ai_result.get(
                    "product_name"
                ),

            "product_strength":
                ai_result.get(
                    "product_strength"
                ),

            "batch_number":
                ai_result.get(
                    "batch_number"
                ),

            "manufacturing_date":
                manufacturing_date,

            "expiry_date":
                expiry_date,

            "quantity_affected":
                ai_result.get(
                    "quantity_affected"
                ),

            "originating_site":
                ai_result.get(
                    "originating_site"
                ),

            "block_impacted":
                ai_result.get(
                    "block_impacted"
                ),

            "npm":
                ai_result.get(
                    "npm"
                ),

            # --------------------------------------
            # IMPORTANT FIELD MAPPING
            # --------------------------------------

            "complaint_type":
                ai_result.get(
                    "complaint_category"
                ),

            "detailed_description":
                ai_result.get(
                    "complaint_description"
                ),

            "initial_severity":
                severity,

            "suggested_next_action":
                ai_result.get(
                    "suggested_next_action"
                ),

            "initial_risk_assessment":
                ai_result.get(
                    "initial_risk_assessment"
                ),

            "priority":
                priority,
        }

        # ------------------------------------------
        # Return result
        # ------------------------------------------

        return {

            "filename":
                file.filename,

            "extracted_text":
                extracted_text,

            **response_data,
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "PDF processing error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}",
        )
    # ==================================================
# COMPLAINT COMPLETENESS CHECKER
# ==================================================

class ComplaintCompletenessRequest(BaseModel):

    complaint_data: dict


@app.post("/complaints/check-completeness")
def check_completeness(
    request: ComplaintCompletenessRequest,
):

    try:

        result = check_complaint_completeness(
            request.complaint_data
        )

        return result

    except Exception as e:

        print(
            "Completeness checker error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=f"Completeness check failed: {str(e)}",
        )
    # ==================================================
# ROOT CAUSE RECOMMENDATION
# ==================================================

class RootCauseRequest(BaseModel):
    complaint_data: dict


@app.post("/complaints/root-cause")
def root_cause_recommendation(
    request: RootCauseRequest,
):
    try:
        result = recommend_complaint_root_cause(
            request.complaint_data
        )

        return result

    except Exception as e:
        print("Root cause recommendation error:", e)

        raise HTTPException(
            status_code=500,
            detail=f"Root cause recommendation failed: {str(e)}",
        )
    # ==================================================
# DUPLICATE COMPLAINT DETECTION
# ==================================================

class DuplicateComplaintRequest(BaseModel):
    new_complaint: dict
    existing_complaints: list


@app.post("/complaints/check-duplicate")
def check_duplicate_complaint(
    request: DuplicateComplaintRequest,
):
    try:
        result = detect_complaint_duplicate(
            request.new_complaint,
            request.existing_complaints,
        )

        return result

    except Exception as e:
        print("Duplicate complaint detection error:", e)

        raise HTTPException(
            status_code=500,
            detail=f"Duplicate complaint detection failed: {str(e)}",
        )
    # ==================================================
# CAPA RECOMMENDATION
# ==================================================

class CAPARequest(BaseModel):
    complaint_data: dict


@app.post("/complaints/capa")
def capa_recommendation(
    request: CAPARequest,
):
    try:

        result = recommend_complaint_capa(
            request.complaint_data
        )

        return result

    except Exception as e:

        print("CAPA recommendation error:", e)

        raise HTTPException(
            status_code=500,
            detail=f"CAPA recommendation failed: {str(e)}",
        )


# ==================================================
# COMPLAINT SUMMARY
# ==================================================

class ComplaintSummaryRequest(BaseModel):
    complaint_data: dict


@app.post("/complaints/summary")
def complaint_summary(
    request: ComplaintSummaryRequest,
):
    try:

        result = create_complaint_summary(
            request.complaint_data
        )

        return result

    except Exception as e:

        print("Complaint summary error:", e)

        raise HTTPException(
            status_code=500,
            detail=f"Complaint summary failed: {str(e)}",
        )


# ==================================================
# AI RISK CLASSIFICATION
# ==================================================

class RiskClassificationRequest(BaseModel):
    complaint_data: dict


@app.post("/complaints/risk-classification")
def risk_classification(
    request: RiskClassificationRequest,
):
    try:

        result = classify_complaint_risk_data(
            request.complaint_data
        )

        return result

    except Exception as e:

        print("Risk classification error:", e)

        raise HTTPException(
            status_code=500,
            detail=f"Risk classification failed: {str(e)}",
        )