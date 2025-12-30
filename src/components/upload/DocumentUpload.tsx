'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { UploadCloud, FileText, Loader2, CheckCircle2, AlertCircle, Trash2, RefreshCw } from 'lucide-react';

// Document types matching backend schema
export type DocumentType =
  | 'OFFERING_MEMORANDUM'
  | 'T12_STATEMENT'
  | 'RENT_ROLL'
  | 'LEASING_REPORT'
  | 'CONCESSIONS_REPORT'
  | 'AGED_RECEIVABLES'
  | 'CAPITAL_EXPENDITURE_REPORT'
  | 'LOAN_DOCUMENTS'
  | 'PROPERTY_PHOTO'
  | 'SITE_PLAN'
  | 'FLOOR_PLAN'
  | 'INSPECTION_REPORT'
  | 'APPRAISAL'
  | 'PRIOR_APPRAISAL'
  | 'MARKET_STUDY'
  | 'ENVIRONMENTAL_REPORT'
  | 'TITLE_REPORT'
  | 'ORIGINAL_PLANS'
  | 'CONSTRUCTION_BUDGET'
  | 'PERMITS'
  | 'ENGINEERING_REPORT'
  | 'OTHER';

const DOCUMENT_TYPE_OPTIONS: { value: DocumentType; label: string }[] = [
  { value: 'OFFERING_MEMORANDUM', label: 'Offering Memorandum' },
  { value: 'T12_STATEMENT', label: 'T-12 Statement' },
  { value: 'RENT_ROLL', label: 'Rent Roll' },
  { value: 'LEASING_REPORT', label: 'Leasing Report' },
  { value: 'CONCESSIONS_REPORT', label: 'Concessions Report' },
  { value: 'AGED_RECEIVABLES', label: 'Aged Receivables' },
  { value: 'CAPITAL_EXPENDITURE_REPORT', label: 'Capital Expenditure Report' },
  { value: 'LOAN_DOCUMENTS', label: 'Loan Documents' },
  { value: 'PROPERTY_PHOTO', label: 'Property Photo' },
  { value: 'SITE_PLAN', label: 'Site Plan' },
  { value: 'FLOOR_PLAN', label: 'Floor Plan' },
  { value: 'INSPECTION_REPORT', label: 'Inspection Report' },
  { value: 'APPRAISAL', label: 'Appraisal' },
  { value: 'PRIOR_APPRAISAL', label: 'Prior Appraisal' },
  { value: 'MARKET_STUDY', label: 'Market Study' },
  { value: 'ENVIRONMENTAL_REPORT', label: 'Environmental Report' },
  { value: 'TITLE_REPORT', label: 'Title Report' },
  { value: 'ORIGINAL_PLANS', label: 'Original Plans' },
  { value: 'CONSTRUCTION_BUDGET', label: 'Construction Budget' },
  { value: 'PERMITS', label: 'Permits' },
  { value: 'ENGINEERING_REPORT', label: 'Engineering Report' },
  { value: 'OTHER', label: 'Other' },
];

// Supported file types
const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel': ['.xls'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
};

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB in bytes

interface UploadedFile {
  id: string;
  file: File;
  documentType: DocumentType | null;
  status: 'uploading' | 'uploaded' | 'error';
  progress: number;
  error?: string;
  documentId?: string; // From API response
}

interface DocumentUploadProps {
  dealId: string;
  onUploadComplete?: (uploadId: string, extractionJobId: string) => void;
  onCancel?: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  dealId,
  onUploadComplete,
  onCancel,
}) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionProgress, setExtractionProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Validate file
  const validateFile = (file: File): string | null => {
    // Check file type
    const isValidType = Object.values(ACCEPTED_FILE_TYPES).some((extensions) =>
      extensions.some((ext) => file.name.toLowerCase().endsWith(ext))
    );

    if (!isValidType) {
      return `File type not supported. Please upload PDF, XLSX, XLS, PNG, JPG, or DOCX files.`;
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds 50MB limit. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB.`;
    }

    return null;
  };

  // Handle file drop/selection
  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);

    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      const errorMessage =
        errors.find((e: any) => e.code === 'file-too-large')?.message ||
        errors.find((e: any) => e.code === 'file-invalid-type')?.message ||
        'File validation failed';

      const newFile: UploadedFile = {
        id: `${Date.now()}-${Math.random()}`,
        file,
        documentType: null,
        status: 'error',
        progress: 0,
        error: errorMessage,
      };

      setFiles((prev) => [...prev, newFile]);
    });

    // Handle accepted files
    acceptedFiles.forEach((file) => {
      const validationError = validateFile(file);
      if (validationError) {
        const newFile: UploadedFile = {
          id: `${Date.now()}-${Math.random()}`,
          file,
          documentType: null,
          status: 'error',
          progress: 0,
          error: validationError,
        };
        setFiles((prev) => [...prev, newFile]);
        return;
      }

      const newFile: UploadedFile = {
        id: `${Date.now()}-${Math.random()}`,
        file,
        documentType: null,
        status: 'uploading',
        progress: 0,
      };

      setFiles((prev) => [...prev, newFile]);
      uploadFile(newFile);
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: true,
  });

  // Upload file to backend
  const uploadFile = async (uploadedFile: UploadedFile) => {
    try {
      const formData = new FormData();
      formData.append('files[]', uploadedFile.file);
      if (uploadedFile.documentType) {
        formData.append('document_types[]', uploadedFile.documentType);
      }

      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uploadedFile.id ? { ...f, progress } : f
            )
          );
        }
      });

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status === 202) {
          const response = JSON.parse(xhr.responseText);
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uploadedFile.id
                ? {
                    ...f,
                    status: 'uploaded',
                    progress: 100,
                    documentId: response.documents?.[0]?.id,
                  }
                : f
            )
          );
        } else {
          throw new Error('Upload failed');
        }
      });

      // Handle errors
      xhr.addEventListener('error', () => {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadedFile.id
              ? {
                  ...f,
                  status: 'error',
                  error: 'Upload failed. Please try again.',
                }
              : f
          )
        );
      });

      xhr.open('POST', `${apiUrl}/api/v1/deals/${dealId}/documents`);
      xhr.send(formData);
    } catch (error) {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadedFile.id
            ? {
                ...f,
                status: 'error',
                error: error instanceof Error ? error.message : 'Upload failed',
              }
            : f
        )
      );
    }
  };

  // Update document type
  const handleDocumentTypeChange = (fileId: string, documentType: DocumentType) => {
    setFiles((prev) =>
      prev.map((f) =>
        f.id === fileId ? { ...f, documentType } : f
      )
    );
  };

  // Remove file
  const handleRemoveFile = (fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  // Retry upload for failed files
  const handleRetryUpload = (fileId: string) => {
    const fileToRetry = files.find((f) => f.id === fileId);
    if (fileToRetry) {
      // Reset file status and retry upload
      setFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? {
                ...f,
                status: 'uploading',
                progress: 0,
                error: undefined,
              }
            : f
        )
      );
      uploadFile({ ...fileToRetry, status: 'uploading', progress: 0, error: undefined });
    }
  };

  // Extract data
  const handleExtractData = async () => {
    const uploadedFiles = files.filter((f) => f.status === 'uploaded');
    if (uploadedFiles.length === 0) {
      setError('Please upload at least one file before extracting data.');
      return;
    }

    setIsExtracting(true);
    setExtractionProgress(0);
    setError(null);

    try {
      // Get extraction job ID from the first uploaded file's response
      // In a real implementation, this would come from the upload response
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

      // Simulate extraction progress (in real implementation, poll the extraction job status)
      const progressInterval = setInterval(() => {
        setExtractionProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 1000);

      // In production, this would poll GET /api/v1/extraction-jobs/{job_id}
      // For now, simulate completion
      setTimeout(() => {
        clearInterval(progressInterval);
        setExtractionProgress(100);
        setIsExtracting(false);

        if (onUploadComplete) {
          // Extract job ID from upload response (would be stored in state)
          onUploadComplete('upload_xyz789', 'job_ext123');
        }
      }, 5000);
    } catch (error) {
      setIsExtracting(false);
      setError(error instanceof Error ? error.message : 'Extraction failed');
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  // Get file icon
  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FileText className="w-6 h-6 text-destructive" />;
    if (['xlsx', 'xls'].includes(ext || '')) return <FileText className="w-6 h-6 text-chart-5" />;
    if (['png', 'jpg', 'jpeg'].includes(ext || '')) return <FileText className="w-6 h-6 text-chart-2" />;
    return <FileText className="w-6 h-6 text-foreground" />;
  };

  const uploadedFilesCount = files.filter((f) => f.status === 'uploaded').length;
  const hasUploadedFiles = uploadedFilesCount > 0;

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {/* Error Message */}
      {error && (
        <div className="bg-destructive/10 border border-destructive rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-destructive mb-1">Error</h3>
            <p className="text-sm text-foreground">{error}</p>
          </div>
        </div>
      )}

      {/* Drag-and-Drop Zone */}
      <section aria-label="File upload area">
        <div
          {...getRootProps()}
          className={`relative bg-background border-2 border-dashed rounded-lg p-8 sm:p-12 text-center transition-all duration-200 cursor-pointer ${
            isDragActive
              ? 'border-ring bg-ring/5'
              : 'border-border hover:border-ring/50 hover:bg-muted'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex justify-center mb-4">
            <UploadCloud className="w-12 h-12 text-foreground" />
          </div>
          <h2 className="text-2xl font-heading font-semibold text-primary mb-2">
            {isDragActive ? 'Drop files here' : 'Drag and drop files here, or click to browse'}
          </h2>
          <p className="text-base text-foreground mb-3">
            Supported formats: PDF, XLSX, XLS, PNG, JPG, DOCX
          </p>
          <p className="text-sm text-muted-foreground mb-6">Max file size: 50MB per file</p>
          <Button type="button" variant="outline" className="min-h-[44px]">
            Browse Files
          </Button>
        </div>
      </section>

      {/* Uploaded Files List */}
      <section aria-label="Uploaded files">
        <h2 className="text-2xl font-heading font-semibold text-primary mb-4">Uploaded Files</h2>

        {files.length === 0 ? (
          <div className="bg-background border border-border rounded-lg p-6 text-center text-foreground">
            <p className="text-base">
              No files uploaded yet. Drag and drop files above or click Browse Files.
            </p>
          </div>
        ) : (
          <ul className="space-y-3">
            {files.map((file) => (
              <li key={file.id}>
                <article className="bg-background border border-border rounded-lg p-4 hover:shadow-md transition-shadow">
                  {/* File Info */}
                  <div className="flex items-start gap-3 mb-4">
                    {getFileIcon(file.file.name)}
                    <div className="flex-1 min-w-0">
                      <h3 className="text-base font-medium text-primary truncate">
                        {file.file.name}
                      </h3>
                      <p className="text-sm text-muted-foreground">{formatFileSize(file.file.size)}</p>
                    </div>
                  </div>

                  {/* Document Type Dropdown */}
                  <div className="mb-4">
                    <label
                      htmlFor={`doc-type-${file.id}`}
                      className="block text-sm font-medium text-foreground mb-1"
                    >
                      Document Type
                    </label>
                    <Select
                      value={file.documentType || ''}
                      onValueChange={(value) =>
                        handleDocumentTypeChange(file.id, value as DocumentType)
                      }
                      disabled={file.status === 'error'}
                    >
                      <SelectTrigger id={`doc-type-${file.id}`} className="w-full">
                        <SelectValue placeholder="Select type..." />
                      </SelectTrigger>
                      <SelectContent>
                        {DOCUMENT_TYPE_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Upload Progress */}
                  {file.status === 'uploading' && (
                    <div className="mb-4">
                      <div className="bg-muted rounded-full h-2 mb-1 overflow-hidden">
                        <div
                          className="bg-chart-2 h-2 rounded-full transition-all"
                          style={{ width: `${file.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-muted-foreground">Uploading... {file.progress}%</p>
                    </div>
                  )}

                  {/* Status and Actions */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {file.status === 'uploading' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-chart-2/10 text-chart-2">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          Uploading
                        </span>
                      )}
                      {file.status === 'uploaded' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-chart-1/10 text-chart-1">
                          <CheckCircle2 className="w-3 h-3" />
                          Uploaded
                        </span>
                      )}
                      {file.status === 'error' && (
                        <div className="flex flex-col gap-2">
                          <div className="flex items-start gap-2">
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-destructive/10 text-destructive">
                              <AlertCircle className="w-3 h-3" />
                              Error
                            </span>
                            {file.error && (
                              <p className="text-xs text-destructive flex-1">{file.error}</p>
                            )}
                          </div>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => handleRetryUpload(file.id)}
                            className="w-full sm:w-auto min-h-[44px]"
                            aria-label={`Retry upload for ${file.file.name}`}
                          >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Retry Upload
                          </Button>
                        </div>
                      )}
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveFile(file.id)}
                      className="text-foreground hover:text-primary"
                      aria-label={`Remove ${file.file.name}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </article>
              </li>
            ))}
          </ul>
        )}

        {/* Files Ready Status */}
        {hasUploadedFiles && !isExtracting && (
          <div className="mt-4 text-sm text-foreground text-center">
            <p>{uploadedFilesCount} file{uploadedFilesCount !== 1 ? 's' : ''} ready for extraction</p>
          </div>
        )}
      </section>

      {/* Action Buttons */}
      <section aria-label="Form actions">
        <div className="flex flex-col sm:flex-row gap-4 justify-end">
          {onCancel && (
            <Button type="button" variant="outline" onClick={onCancel} disabled={isExtracting}>
              Cancel
            </Button>
          )}
          <Button
            type="button"
            onClick={handleExtractData}
            disabled={!hasUploadedFiles || isExtracting}
            className="min-w-[120px]"
          >
            {isExtracting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Extracting...
              </>
            ) : (
              'Extract Data →'
            )}
          </Button>
        </div>
      </section>

      {/* Extraction Progress */}
      {isExtracting && (
        <section aria-label="Extraction progress">
          <div className="bg-background border border-border rounded-lg p-6 text-center">
            <Loader2 className="w-8 h-8 text-chart-2 animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-heading font-semibold text-primary mb-2">
              Extracting Data...
            </h2>
            <p className="text-base text-foreground mb-4">
              Processing {uploadedFilesCount} document{uploadedFilesCount !== 1 ? 's' : ''}. This may
              take up to 45 seconds.
            </p>
            <div className="mb-4">
              <div className="bg-muted rounded-full h-2 mb-1 overflow-hidden">
                <div
                  className="bg-chart-2 h-2 rounded-full transition-all"
                  style={{ width: `${extractionProgress}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">{extractionProgress}% complete</p>
            </div>
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsExtracting(false)}
              disabled={extractionProgress >= 100}
            >
              Cancel Extraction
            </Button>
          </div>
        </section>
      )}
    </div>
  );
};

export default DocumentUpload;
