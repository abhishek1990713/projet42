import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from typing import Dict, Any

# --------------------------------------------------
# Logger Configuration
# --------------------------------------------------
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Constants
# --------------------------------------------------
PROCESS_INPUT_SOURCE = "PROCESS"
VALIDATION_INPUT_SOURCE = "VALIDATION"
UI_INPUT_SOURCE = "UI"

# --------------------------------------------------
# FastAPI App Initialization
# --------------------------------------------------
app = FastAPI(title="Validation API", description="Processes document validation and field feedback")

# --------------------------------------------------
# Request Model
# --------------------------------------------------
class ValidationRequest(BaseModel):
    document_id: str
    rule_id: str
    status: str
    message: str

# --------------------------------------------------
# Helper: Process Validation Data
# --------------------------------------------------
def process_validation(data: ValidationRequest) -> Dict[str, Any]:
    """
    Process validation request and generate structured field_feedback.
    Includes comment, rule_id, and status.
    """
    try:
        logger.info(f"Processing validation for document_id={data.document_id}, rule_id={data.rule_id}")

        comment_text = f"### Rule: {data.rule_id} - Validation executed successfully."

        field_feedback = {
            data.rule_id: {
                "comment": comment_text,
                "status": data.status
            }
        }

        response = {
            "document_id": data.document_id,
            "rule_id": data.rule_id,
            "status": data.status,
            "message": data.message,
            "field_feedback": field_feedback
        }

        logger.info(f"Validation processed successfully for document_id={data.document_id}")
        return response

    except Exception as e:
        logger.error(f"Error in process_validation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing validation data")

# --------------------------------------------------
# Helper: Handle Validation JSON Upload
# --------------------------------------------------
def handle_validation_json(
    request: Request,
    payload: dict,
    db,
    x_correlation_id: str,
    x_application_id: str,
    x_created_by: str,
    x_document_id: str,
    x_file_id: str,
    x_authorization_coin: str,
    x_feedback_source: str,
    x_input_source: str
) -> Dict[str, Any]:
    """
    Handle JSON request coming from VALIDATION input source.
    """
    try:
        logger.info(f"[handle_validation_json()] Start validation for document {x_document_id}")

        required_fields = ["document_id", "rule_id", "status", "message"]
        for field in required_fields:
            if field not in payload:
                logger.warning(f"Missing field in validation payload: {field}")
                raise HTTPException(status_code=400, detail=f"Missing field: {field}")

        request_data = ValidationRequest(**payload)
        result = process_validation(request_data)

        logger.info(f"[handle_validation_json()] Completed validation for document {x_document_id}")
        return result

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"[handle_validation_json()] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error during validation")

# --------------------------------------------------
# Main Upload Endpoint
# --------------------------------------------------
@app.post("/upload_json")
async def upload_json(
    request: Request,
    file: UploadFile = File(...),
    x_input_source: str = "UI",
    x_correlation_id: str = "N/A",
    x_application_id: str = "APP001",
    x_created_by: str = "SYSTEM",
    x_document_id: str = "DOC001",
    x_file_id: str = "FILE001",
    x_authorization_coin: str = "AUTH123",
    x_feedback_source: str = "SYSTEM"
):
    """
    Handles JSON upload and routes to appropriate handler 
    based on input source (PROCESS / VALIDATION / UI).
    """
    try:
        logger.info(f"[upload_json()] Received file {file.filename} from source {x_input_source}")

        content = await file.read()
        payload = json.loads(content.decode("utf-8"))

        db = None  # Placeholder for DB session if needed later

        if x_input_source == PROCESS_INPUT_SOURCE:
            if logger:
                logger.info(f"[upload_json()] [SOEID: {x_created_by}] [Correlation ID: {x_correlation_id}] [Document ID: {x_document_id}] - Processing request from PROCESS source")

            # Placeholder for existing process handler
            result = {"message": "Processed via PROCESS handler", "document_id": x_document_id}

        elif x_input_source == VALIDATION_INPUT_SOURCE:
            if logger:
                logger.info(
                    f"[upload_json()] [SOEID: {x_created_by}] "
                    f"[Correlation ID: {x_correlation_id}] [Document ID: {x_document_id}] - Processing request from VALIDATION source"
                )

            result = handle_validation_json(
                request,
                payload,
                db,
                x_correlation_id,
                x_application_id,
                x_created_by,
                x_document_id,
                x_file_id,
                x_authorization_coin,
                x_feedback_source,
                x_input_source
            )

        else:
            if logger:
                logger.info(f"[upload_json()] Processing request from UI source for Document ID: {x_document_id}")

            result = {"message": "Processed via UI handler", "document_id": x_document_id}

        return JSONResponse(content=result, status_code=200)

    except json.JSONDecodeError:
        logger.error("Invalid JSON format in uploaded file")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"[upload_json()] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------
@app.get("/")
def root():
    return {"message": "Validation API is running"}
"


{
  "document_id": "DOC1234",
  "rule_id": "date_check_bm_fincen_ao_gssp",
  "status": "thumbs_up",
  "message": "Validation data processed successfully",
  "field_feedback": {
    "date_check_bm_fincen_ao_gssp": {
      "comment": "### Rule: ...",
      "status": "thumbs_up"
    }
  }
}
