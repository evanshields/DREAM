"""
DREAM AI - Documents API Endpoint Implementation
Task 1.10: Backend API - Document Upload Endpoint
PRD Reference: Section 9.1
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime
import logging
import uuid
from pathlib import Path

from prisma import Prisma

# Initialize router
# Note: Route should be /api/v1/deals/{deal_id}/documents per PRD
documents_router = APIRouter(prefix="/api/v1/deals", tags=["documents"])

# Logger
logger = logging.getLogger(__name__)

# Initialize Prisma client
prisma = Prisma()

# ============================================================================
# CONSTANTS
# ============================================================================

# Allowed file types from PRD Section 8.2
ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.ms-excel": ".xls",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".png", ".jpg", ".jpeg", ".docx"}

# File size limit: 50MB per PRD Section 8.2
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

# ============================================================================
# REQUEST/RESPONSE SCHEMAS (Matching PRD Section 9.1)
# ============================================================================

class DocumentInfo(BaseModel):
    """Document info in response"""
    id: str
    filename: str
    size_bytes: int
    status: str  # PROCESSING, COMPLETED, FAILED
    document_type: Optional[str] = None  # Will be classified

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    """Response matching PRD Section 9.1"""
    upload_id: str
    documents: List[DocumentInfo]
    extraction_job_id: str

# ============================================================================
# FILE VALIDATION
# ============================================================================

def validate_file_type(filename: str, content_type: Optional[str]) -> tuple[bool, Optional[str]]:
    """
    Validate file type against allowed types.
    Returns (is_valid, error_message)
    """
    # Check extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Allowed types: PDF, XLSX, XLS, PNG, JPG, DOCX"
    
    # Check MIME type if provided
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        # Allow if extension is valid (some browsers send wrong MIME types)
        logger.warning(f"MIME type {content_type} not in allowed list, but extension {file_ext} is valid")
    
    return True, None

def validate_file_size(size: int) -> tuple[bool, Optional[str]]:
    """
    Validate file size (50MB max).
    Returns (is_valid, error_message)
    """
    if size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        return False, f"File size exceeds maximum of {max_mb}MB"
    
    if size == 0:
        return False, "File is empty"
    
    return True, None

# ============================================================================
# STORAGE SERVICE
# ============================================================================

from services.storage import get_storage_service

async def upload_to_storage(
    file_content: bytes,
    filename: str,
    deal_id: str,
    content_type: Optional[str] = None
) -> tuple[str, str]:
    """
    Upload file to S3-compatible storage.
    Returns (storage_path, storage_provider)
    
    Uses StorageService from Task 1.11.
    """
    # Generate unique filename to avoid collisions
    file_ext = Path(filename).suffix
    unique_filename = f"{deal_id}/{uuid.uuid4()}{file_ext}"
    storage_path = f"documents/{unique_filename}"
    
    # Get storage service instance
    storage_service = get_storage_service()
    
    # Upload file
    try:
        storage_service.upload(
            file_content=file_content,
            storage_path=storage_path,
            content_type=content_type,
            metadata={
                "original_filename": filename,
                "deal_id": deal_id,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        )
        
        # Get provider name (convert to enum value)
        provider = storage_service.provider
        if provider == "S3":
            storage_provider = "S3"
        elif provider == "SUPABASE":
            storage_provider = "SUPABASE"
        elif provider == "GCS":
            storage_provider = "GCS"
        else:
            storage_provider = "LOCAL"
        
        logger.info(f"Successfully uploaded file to {storage_provider}: {storage_path}")
        
        return storage_path, storage_provider
        
    except Exception as e:
        logger.error(f"Failed to upload file to storage: {str(e)}", exc_info=True)
        raise

# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@documents_router.post("/{deal_id}/documents", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_documents(
    deal_id: UUID4,
    files: List[UploadFile] = File(...),
    document_types: Optional[List[Optional[str]]] = None,
    # current_user: User = Depends(get_current_user)
):
    """
    Upload documents for a deal.
    
    Accepts multipart/form-data with:
    - files[]: One or more files (PDF, XLSX, XLS, PNG, JPG, DOCX)
    - document_types[]: (Optional) Pre-specified document types
    
    Returns 202 Accepted with upload_id, documents array, and extraction_job_id.
    
    PRD Reference: Section 9.1
    """
    try:
        # Connect to database
        await prisma.connect()
        
        # Verify deal exists
        deal = await prisma.deal.find_unique(where={"id": str(deal_id)})
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal {deal_id} not found"
            )
        
        # Validate files
        validated_files = []
        for idx, file in enumerate(files):
            # Read file content (up to MAX_FILE_SIZE_BYTES + 1 to detect oversized files)
            content = await file.read()
            
            # Validate file size
            is_valid_size, size_error = validate_file_size(len(content))
            if not is_valid_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename}: {size_error}"
                )
            
            # Validate file type
            is_valid_type, type_error = validate_file_type(file.filename, file.content_type)
            if not is_valid_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename}: {type_error}"
                )
            
            validated_files.append({
                "filename": file.filename,
                "content": content,
                "size": len(content),
                "content_type": file.content_type,
                "document_type": document_types[idx] if document_types and idx < len(document_types) else None
            })
        
        # Generate upload_id
        upload_id = f"upload_{uuid.uuid4().hex[:12]}"
        
        # Create documents in database
        created_documents = []
        for file_info in validated_files:
            # Upload to storage
            storage_path, storage_provider = await upload_to_storage(
                file_info["content"],
                file_info["filename"],
                str(deal_id),
                file_info["content_type"]
            )
            
            # Determine document type enum value
            # Map string to DocumentType enum (from schema.prisma)
            document_type_enum = None
            if file_info["document_type"]:
                # Normalize the document type string
                doc_type_normalized = file_info["document_type"].upper().replace(" ", "_").replace("-", "_")
                # Valid DocumentType enum values from schema
                valid_types = [
                    "OFFERING_MEMORANDUM", "T12_STATEMENT", "RENT_ROLL", "LEASING_REPORT",
                    "CONCESSIONS_REPORT", "AGED_RECEIVABLES", "CAPITAL_EXPENDITURE_REPORT",
                    "LOAN_DOCUMENTS", "PROPERTY_PHOTO", "SITE_PLAN", "FLOOR_PLAN",
                    "INSPECTION_REPORT", "APPRAISAL", "PRIOR_APPRAISAL", "MARKET_STUDY",
                    "ENVIRONMENTAL_REPORT", "TITLE_REPORT", "ORIGINAL_PLANS",
                    "CONSTRUCTION_BUDGET", "PERMITS", "ENGINEERING_REPORT", "OTHER"
                ]
                if doc_type_normalized in valid_types:
                    document_type_enum = doc_type_normalized
                else:
                    logger.warning(f"Unknown document type: {file_info['document_type']}, using None")
            
            # Create document record
            document = await prisma.document.create(
                data={
                    "dealId": str(deal_id),
                    "uploadedBy": "system",  # TODO: Get from current_user when auth is implemented
                    "filename": file_info["filename"],
                    "originalFilename": file_info["filename"],
                    "mimeType": file_info["content_type"] or "application/octet-stream",
                    "sizeBytes": file_info["size"],
                    "storagePath": storage_path,
                    "storageProvider": storage_provider,
                    "documentType": document_type_enum,
                    "processingStatus": "PROCESSING",  # Initial status per PRD
                    "processingStartedAt": datetime.utcnow(),
                }
            )
            
            created_documents.append({
                "id": document.id,
                "filename": document.filename,
                "size_bytes": int(document.sizeBytes),
                "status": document.processingStatus,
                "document_type": document.documentType,
            })
        
        # Create extraction job and connect documents
        # Collect document IDs first
        document_ids = [doc["id"] for doc in created_documents]
        
        # Create extraction job with documents connected
        extraction_job = await prisma.extractionjob.create(
            data={
                "dealId": str(deal_id),
                "status": "PENDING",
                "documents": {
                    "connect": [{"id": doc_id} for doc_id in document_ids]
                }
            }
        )
        
        # TODO: Queue extraction job (async processing)
        # This will be implemented when Celery/background tasks are set up
        logger.info(f"Extraction job {extraction_job.id} created for deal {deal_id}")
        
        # Return response matching PRD Section 9.1
        return DocumentUploadResponse(
            upload_id=upload_id,
            documents=[DocumentInfo(**doc) for doc in created_documents],
            extraction_job_id=extraction_job.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading documents: {str(e)}"
        )
    finally:
        await prisma.disconnect()

@documents_router.get("/{deal_id}/documents", response_model=List[DocumentInfo])
async def list_documents(
    deal_id: UUID4,
    document_type: Optional[str] = None,
    # current_user: User = Depends(get_current_user)
):
    """
    List all documents for a deal.
    
    Optional query parameter:
    - document_type: Filter by document type
    """
    try:
        await prisma.connect()
        
        # Verify deal exists
        deal = await prisma.deal.find_unique(where={"id": str(deal_id)})
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal {deal_id} not found"
            )
        
        # Build query
        where_clause = {"dealId": str(deal_id)}
        if document_type:
            where_clause["documentType"] = document_type.upper().replace(" ", "_")
        
        # Query documents
        documents = await prisma.document.find_many(where=where_clause)
        
        return [
            DocumentInfo(
                id=doc.id,
                filename=doc.filename,
                size_bytes=int(doc.sizeBytes),
                status=doc.processingStatus,
                document_type=doc.documentType,
            )
            for doc in documents
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}"
        )
    finally:
        await prisma.disconnect()

