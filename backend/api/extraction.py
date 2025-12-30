"""
DREAM AI - Extraction API Endpoints
Task 1.18, 1.22: Extraction Status and Confirmation API Endpoints
PRD Reference: Section 9.1

API endpoints for extraction job status and confirmation.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4
from datetime import datetime
import logging

from prisma import Prisma

# Initialize router
extraction_router = APIRouter(prefix="/api/v1/extraction-jobs", tags=["extraction"])
deals_extraction_router = APIRouter(prefix="/api/v1/deals", tags=["extraction"])

# Logger
logger = logging.getLogger(__name__)

# ============================================================================
# REQUEST/RESPONSE SCHEMAS (Matching PRD Section 9.1)
# ============================================================================

class DocumentStatusInfo(BaseModel):
    """Document status information"""
    id: str
    document_type: Optional[str]
    classification_confidence: Optional[int]
    extraction_status: str  # PENDING, PROCESSING, COMPLETED, FAILED

class ExtractionJobStatusResponse(BaseModel):
    """Extraction job status response matching PRD Section 9.1"""
    job_id: str
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    documents: List[DocumentStatusInfo]
    extracted_data: Optional[Dict[str, Any]]  # Combined extracted data from all documents
    fields_requiring_review: List[str]
    overall_confidence: Optional[int]
    cost_cents: Optional[int]
    error_message: Optional[str]


class ConfirmExtractionRequest(BaseModel):
    """Request body for confirming extraction with corrections"""
    corrections: Dict[str, Any]  # Field path -> corrected value
    confirmed: bool  # True if user confirms extraction is correct


class ConfirmExtractionResponse(BaseModel):
    """Response for extraction confirmation"""
    deal_id: str
    status: str  # Updated deal status
    corrections_applied: int  # Number of corrections applied
    next_step: str  # Next workflow step

# ============================================================================
# EXTRACTION STATUS ENDPOINT
# ============================================================================

@extraction_router.get("/{job_id}", response_model=ExtractionJobStatusResponse)
async def get_extraction_status(job_id: str):
    """
    Get extraction job status.
    
    Returns extraction job status matching PRD Section 9.1:
    - Job status (PENDING, PROCESSING, COMPLETED, FAILED)
    - Processing timestamps
    - Extracted data
    - Fields requiring review
    - Overall confidence score
    - Cost information
    """
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Get extraction job with related documents
        job = await prisma.extractionjob.find_unique(
            where={"id": job_id},
            include={
                "documents": {
                    include: {
                        "extractionDataCache": True,
                    }
                }
            }
        )
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extraction job {job_id} not found"
            )
        
        # Build document status info
        documents_info = []
        all_extracted_data = {}
        
        for document in job.documents:
            # Get extraction status from document processing status
            extraction_status = document.processingStatus
            
            documents_info.append(DocumentStatusInfo(
                id=document.id,
                document_type=document.documentType,
                classification_confidence=document.classificationConfidence,
                extraction_status=extraction_status,
            ))
            
            # Collect extracted data from cache if available
            if document.extractionDataCache:
                doc_data = document.extractionDataCache.extractedData
                if isinstance(doc_data, dict):
                    # Merge extracted data (prefix with document_id to avoid conflicts)
                    for key, value in doc_data.items():
                        all_extracted_data[f"{document.id}.{key}"] = value
        
        # Build response
        response = ExtractionJobStatusResponse(
            job_id=job.id,
            status=job.status,
            started_at=job.startedAt,
            completed_at=job.completedAt,
            documents=documents_info,
            extracted_data=all_extracted_data if all_extracted_data else None,
            fields_requiring_review=job.fieldsRequiringReview or [],
            overall_confidence=job.overallConfidence,
            cost_cents=job.llmCostCents,
            error_message=job.errorMessage,
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting extraction status for job {job_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve extraction status: {str(e)}"
        )
    finally:
        await prisma.disconnect()


# ============================================================================
# CONFIRM EXTRACTION ENDPOINT
# ============================================================================

@deals_extraction_router.post("/{deal_id}/confirm-extraction", response_model=ConfirmExtractionResponse)
async def confirm_extraction(deal_id: str, request: ConfirmExtractionRequest):
    """
    Confirm extraction and apply user corrections.
    
    Accepts user corrections and updates deal with confirmed extraction data.
    Returns updated deal status and next workflow step.
    """
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Verify deal exists
        deal = await prisma.deal.find_unique(where={"id": deal_id})
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal {deal_id} not found"
            )
        
        # Get the most recent extraction job for this deal
        extraction_job = await prisma.extractionjob.find_first(
            where={"dealId": deal_id},
            order={"createdAt": "desc"},
            include={"documents": {"include": {"extractionDataCache": True}}}
        )
        
        if not extraction_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No extraction job found for deal {deal_id}"
            )
        
        if extraction_job.status != "COMPLETED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extraction job is not completed (status: {extraction_job.status})"
            )
        
        # Apply corrections to deal
        corrections_applied = 0
        update_data = {}
        
        # Map corrections to deal fields
        corrections = request.corrections or {}
        
        # Property information corrections
        if "property_name.value" in corrections:
            update_data["propertyName"] = corrections["property_name.value"]
            corrections_applied += 1
        
        if "street_address.value" in corrections:
            update_data["addressStreet"] = corrections["street_address.value"]
            corrections_applied += 1
        
        if "city.value" in corrections:
            update_data["addressCity"] = corrections["city.value"]
            corrections_applied += 1
        
        if "state.value" in corrections:
            update_data["addressState"] = corrections["state.value"]
            corrections_applied += 1
        
        if "zip_code.value" in corrections:
            update_data["addressZip"] = corrections["zip_code.value"]
            corrections_applied += 1
        
        if "year_built.value" in corrections:
            update_data["yearBuilt"] = int(corrections["year_built.value"])
            corrections_applied += 1
        
        if "number_of_units.value" in corrections:
            update_data["units"] = int(corrections["number_of_units.value"])
            corrections_applied += 1
        
        if "total_sf.value" in corrections:
            update_data["totalSf"] = int(corrections["total_sf.value"])
            corrections_applied += 1
        
        if "property_class.value" in corrections:
            update_data["propertyClass"] = corrections["property_class.value"]
            corrections_applied += 1
        
        # Financial data corrections
        if "asking_price.value" in corrections:
            # Parse currency string to decimal
            price_str = str(corrections["asking_price.value"]).replace("$", "").replace(",", "")
            try:
                update_data["askingPrice"] = float(price_str)
                corrections_applied += 1
            except ValueError:
                logger.warning(f"Invalid asking price format: {corrections['asking_price.value']}")
        
        if "in_place_noi.value" in corrections:
            # Parse currency string to decimal
            noi_str = str(corrections["in_place_noi.value"]).replace("$", "").replace(",", "")
            try:
                update_data["noiInPlace"] = float(noi_str)
                corrections_applied += 1
            except ValueError:
                logger.warning(f"Invalid NOI format: {corrections['in_place_noi.value']}")
        
        if "pro_forma_noi.value" in corrections:
            # Parse currency string to decimal
            noi_str = str(corrections["pro_forma_noi.value"]).replace("$", "").replace(",", "")
            try:
                update_data["noiProForma"] = float(noi_str)
                corrections_applied += 1
            except ValueError:
                logger.warning(f"Invalid pro forma NOI format: {corrections['pro_forma_noi.value']}")
        
        # Update deal with corrections
        if update_data:
            await prisma.deal.update(
                where={"id": deal_id},
                data=update_data
            )
        
        # Store corrections in ExtractionCorrection table for audit trail
        for field_path, corrected_value in corrections.items():
            await prisma.extractioncorrection.create(
                data={
                    "extractionJobId": extraction_job.id,
                    "fieldPath": field_path,
                    "originalValue": str(get_nested_value(extraction_job, field_path) or ""),
                    "correctedValue": str(corrected_value),
                    "correctedBy": "user",  # TODO: Get from auth context
                }
            )
        
        # Update deal stage to READY_FOR_SCREENING if extraction is confirmed
        if request.confirmed:
            await prisma.deal.update(
                where={"id": deal_id},
                data={"stage": "READY_FOR_SCREENING"}
            )
        
        logger.info(f"Extraction confirmed for deal {deal_id}: {corrections_applied} corrections applied")
        
        return ConfirmExtractionResponse(
            deal_id=deal_id,
            status="READY_FOR_SCREENING" if request.confirmed else deal.stage,
            corrections_applied=corrections_applied,
            next_step="screening"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming extraction for deal {deal_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm extraction: {str(e)}"
        )
    finally:
        await prisma.disconnect()


def get_nested_value(obj: Any, path: str) -> Any:
    """Helper to get nested value from object"""
    parts = path.split('.')
    current = obj
    for part in parts:
        if current and isinstance(current, dict) and part in current:
            current = current[part]
        elif hasattr(current, part):
            current = getattr(current, part)
        else:
            return None
    return current

