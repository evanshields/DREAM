"""
DREAM AI - Extraction Job Processor
Task 1.17: Extraction Job Processor
PRD Reference: Section 6

Processes extraction jobs asynchronously, orchestrating the full extraction workflow:
1. Classify document type
2. Route to appropriate extraction service
3. Extract data with confidence scores
4. Calculate overall confidence
5. Identify fields requiring review
6. Update extraction_job status
"""

import os
import json
import logging
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

from prisma import Prisma

# Import services
try:
    from services.classification import ClassificationService
    from services.storage import StorageService
    from services.extraction.om_extraction import get_om_extraction_service
    from services.extraction.t12_extraction import get_t12_extraction_service
    from services.extraction.rent_roll_extraction import get_rent_roll_extraction_service
except ImportError:
    # Fallback for different import paths
    import sys
    from pathlib import Path
    backend_path = Path(__file__).parent.parent.parent
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    from services.classification import ClassificationService
    from services.storage import StorageService
    from services.extraction.om_extraction import get_om_extraction_service
    from services.extraction.t12_extraction import get_t12_extraction_service
    from services.extraction.rent_roll_extraction import get_rent_roll_extraction_service

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Extraction job status enum (matching schema)
class ExtractionJobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# Document type enum (matching schema)
class DocumentType(str, Enum):
    OFFERING_MEMORANDUM = "OFFERING_MEMORANDUM"
    T12_STATEMENT = "T12_STATEMENT"
    RENT_ROLL = "RENT_ROLL"
    # ... other types (using string matching for now)

# ============================================================================
# EXTRACTION PROCESSOR
# ============================================================================

class ExtractionProcessor:
    """
    Extraction job processor that handles document extraction workflow.
    
    Workflow:
    1. Classify document type
    2. Route to appropriate extraction service
    3. Extract data with confidence scores
    4. Calculate overall confidence
    5. Identify fields requiring review
    6. Update extraction_job status
    """
    
    def __init__(self):
        """Initialize extraction processor"""
        self.classification_service = ClassificationService()
        self.storage_service = StorageService()
        self.om_service = get_om_extraction_service()
        self.t12_service = get_t12_extraction_service()
        self.rent_roll_service = get_rent_roll_extraction_service()
        logger.info("Initialized ExtractionProcessor")
    
    async def process_extraction_job(
        self,
        job_id: str,
        deal_id: str,
        document_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Process an extraction job for multiple documents.
        
        Args:
            job_id: Extraction job ID
            deal_id: Deal ID
            document_ids: List of document IDs to process
        
        Returns:
            Dict with processing results
        """
        prisma = Prisma()
        await prisma.connect()
        
        try:
            # Update job status to PROCESSING
            await prisma.extractionjob.update(
                where={"id": job_id},
                data={
                    "status": ExtractionJobStatus.PROCESSING.value,
                    "startedAt": datetime.utcnow(),
                }
            )
            
            logger.info(f"Processing extraction job {job_id} with {len(document_ids)} documents")
            
            # Process each document
            total_cost_cents = 0
            all_fields_requiring_review = []
            all_extracted_data = {}
            processing_errors = []
            
            for document_id in document_ids:
                try:
                    result = await self._process_document(
                        prisma=prisma,
                        document_id=document_id,
                        deal_id=deal_id,
                    )
                    
                    # Accumulate results
                    total_cost_cents += int(result["cost_dollars"] * 100)
                    all_fields_requiring_review.extend(result["fields_requiring_review"])
                    all_extracted_data[document_id] = result["extracted_data"]
                    
                    logger.info(f"Document {document_id} processed successfully")
                    
                except Exception as e:
                    error_msg = f"Error processing document {document_id}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    processing_errors.append(error_msg)
                    
                    # Update document status to failed
                    await prisma.document.update(
                        where={"id": document_id},
                        data={
                            "processingStatus": "FAILED",
                            "processingError": error_msg[:2000],  # Limit to 2000 chars
                            "processingCompletedAt": datetime.utcnow(),
                        }
                    )
            
            # Calculate overall confidence (average of all documents)
            overall_confidence = None
            if all_extracted_data:
                confidences = [
                    data.get("overall_confidence", 0)
                    for data in all_extracted_data.values()
                    if data.get("overall_confidence") is not None
                ]
                if confidences:
                    overall_confidence = int(sum(confidences) / len(confidences))
            
            # Update job status
            if processing_errors and len(processing_errors) == len(document_ids):
                # All documents failed
                status = ExtractionJobStatus.FAILED.value
                error_message = "; ".join(processing_errors)[:1000]  # Limit to 1000 chars
            elif processing_errors:
                # Some documents failed, but some succeeded
                status = ExtractionJobStatus.COMPLETED.value
                error_message = f"Partial success: {len(processing_errors)} documents failed"
            else:
                # All documents succeeded
                status = ExtractionJobStatus.COMPLETED.value
                error_message = None
            
            await prisma.extractionjob.update(
                where={"id": job_id},
                data={
                    "status": status,
                    "completedAt": datetime.utcnow(),
                    "overallConfidence": overall_confidence,
                    "fieldsRequiringReview": all_fields_requiring_review,
                    "llmCostCents": total_cost_cents,
                    "errorMessage": error_message,
                }
            )
            
            logger.info(f"Extraction job {job_id} completed with status {status}")
            
            return {
                "job_id": job_id,
                "status": status,
                "overall_confidence": overall_confidence,
                "fields_requiring_review": all_fields_requiring_review,
                "total_cost_cents": total_cost_cents,
                "documents_processed": len(document_ids) - len(processing_errors),
                "documents_failed": len(processing_errors),
                "errors": processing_errors,
            }
            
        except Exception as e:
            logger.error(f"Fatal error processing extraction job {job_id}: {str(e)}", exc_info=True)
            
            # Update job status to FAILED
            await prisma.extractionjob.update(
                where={"id": job_id},
                data={
                    "status": ExtractionJobStatus.FAILED.value,
                    "completedAt": datetime.utcnow(),
                    "errorMessage": str(e)[:1000],
                }
            )
            
            raise
            
        finally:
            await prisma.disconnect()
    
    async def _process_document(
        self,
        prisma: Prisma,
        document_id: str,
        deal_id: str,
    ) -> Dict[str, Any]:
        """
        Process a single document through the extraction workflow.
        
        Args:
            prisma: Prisma client instance
            document_id: Document ID to process
            deal_id: Deal ID
        
        Returns:
            Dict with extraction results
        """
        # Get document from database
        document = await prisma.document.find_unique(
            where={"id": document_id},
            include={"deal": True},
        )
        
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        logger.info(f"Processing document {document_id}: {document.filename}")
        
        # Update document status to PROCESSING
        await prisma.document.update(
            where={"id": document_id},
            data={
                "processingStatus": "PROCESSING",
                "processingStartedAt": datetime.utcnow(),
            }
        )
        
        try:
            # Step 1: Download file from storage
            file_content = await self._download_document(document)
            
            # Step 2: Classify document type
            classification_result = await self._classify_document(
                file_content=file_content,
                filename=document.filename,
                mime_type=document.mimeType,
            )
            
            document_type = classification_result["document_type"]
            classification_confidence = classification_result["confidence"]
            
            logger.info(f"Document {document_id} classified as {document_type} ({classification_confidence}% confidence)")
            
            # Step 3: Route to appropriate extraction service
            extraction_result = await self._extract_document_data(
                document_type=document_type,
                file_content=file_content,
                filename=document.filename,
                mime_type=document.mimeType,
                deal_id=deal_id,
                document=document,
            )
            
            # Step 4: Store extraction data in cache
            extraction_data_cache = await prisma.extractiondatacache.create(
                data={
                    "documentId": document_id,
                    "extractedData": extraction_result["extracted_data"],
                    "extractionModel": extraction_result["model_used"],
                    "extractionConfidence": extraction_result["overall_confidence"],
                }
            )
            
            # Step 5: Update document record
            await prisma.document.update(
                where={"id": document_id},
                data={
                    "documentType": document_type,
                    "classificationConfidence": classification_confidence,
                    "classificationModel": classification_result.get("model", "gemini-1.5-flash"),
                    "processingStatus": "COMPLETED",
                    "processingCompletedAt": datetime.utcnow(),
                    "extractionDataId": extraction_data_cache.id,
                    "extractionConfidence": extraction_result["overall_confidence"],
                }
            )
            
            logger.info(f"Document {document_id} extraction completed successfully")
            
            return {
                "document_id": document_id,
                "document_type": document_type,
                "extracted_data": extraction_result["extracted_data"],
                "overall_confidence": extraction_result["overall_confidence"],
                "fields_requiring_review": extraction_result["fields_requiring_review"],
                "cost_dollars": extraction_result["cost_dollars"],
                "model_used": extraction_result["model_used"],
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing document {document_id}: {error_msg}", exc_info=True)
            
            # Update document status to FAILED
            await prisma.document.update(
                where={"id": document_id},
                data={
                    "processingStatus": "FAILED",
                    "processingError": error_msg[:2000],
                    "processingCompletedAt": datetime.utcnow(),
                }
            )
            
            raise
    
    async def _download_document(self, document: Any) -> bytes:
        """
        Download document from storage.
        
        Args:
            document: Document record from database
        
        Returns:
            Document content as bytes
        """
        try:
            file_content = await asyncio.to_thread(
                self.storage_service.download,
                document.storagePath,
            )
            return file_content
        except Exception as e:
            raise ValueError(f"Failed to download document from storage: {str(e)}")
    
    async def _classify_document(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str,
    ) -> Dict[str, Any]:
        """
        Classify document type.
        
        Args:
            file_content: Document content as bytes
            filename: Document filename
            mime_type: MIME type
        
        Returns:
            Classification result dict
        """
        try:
            result = await asyncio.to_thread(
                self.classification_service.classify,
                file_content=file_content,
                filename=filename,
                mime_type=mime_type,
                use_cache=True,
            )
            return result
        except Exception as e:
            raise ValueError(f"Document classification failed: {str(e)}")
    
    async def _extract_document_data(
        self,
        document_type: str,
        file_content: bytes,
        filename: str,
        mime_type: str,
        deal_id: str,
        document: Any,
    ) -> Dict[str, Any]:
        """
        Route to appropriate extraction service and extract data.
        
        Args:
            document_type: Classified document type
            file_content: Document content as bytes
            filename: Document filename
            mime_type: MIME type
            deal_id: Deal ID
            document: Document record (for additional context)
        
        Returns:
            Extraction result dict
        """
        # Route to appropriate extraction service
        if document_type == "OFFERING_MEMORANDUM":
            result = await self.om_service.extract(
                file_content=file_content,
                filename=filename,
                mime_type=mime_type,
            )
        elif document_type == "T12_STATEMENT":
            # Get number of units from deal if available
            number_of_units = document.deal.units if document.deal else None
            result = await self.t12_service.extract(
                file_content=file_content,
                filename=filename,
                mime_type=mime_type,
                number_of_units=number_of_units,
            )
        elif document_type == "RENT_ROLL":
            result = await self.rent_roll_service.extract(
                file_content=file_content,
                filename=filename,
                mime_type=mime_type,
            )
        else:
            # For other document types, return empty extraction
            logger.warning(f"No extraction service for document type: {document_type}")
            result = {
                "extracted_data": {},
                "model_used": "none",
                "cost_dollars": 0.0,
                "overall_confidence": 0,
                "fields_requiring_review": [],
            }
        
        return result


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_extraction_processor_instance: Optional[ExtractionProcessor] = None


def get_extraction_processor() -> ExtractionProcessor:
    """Get or create global extraction processor instance"""
    global _extraction_processor_instance
    if _extraction_processor_instance is None:
        _extraction_processor_instance = ExtractionProcessor()
    return _extraction_processor_instance


# ============================================================================
# CELERY TASK (Optional - for async processing)
# ============================================================================

# Uncomment when Celery is configured:
# from celery import Celery
# 
# app = Celery('dream_ai')
# 
# @app.task(name='process_extraction_job')
# def process_extraction_job_task(job_id: str, deal_id: str, document_ids: List[str]):
#     """Celery task wrapper for extraction job processing"""
#     processor = get_extraction_processor()
#     return asyncio.run(processor.process_extraction_job(job_id, deal_id, document_ids))

