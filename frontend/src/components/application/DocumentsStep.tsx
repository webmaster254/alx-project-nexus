import React, { useState, useRef } from 'react';
import { ApplicationFormData } from './ApplicationForm';

interface DocumentsStepProps {
  formData: ApplicationFormData;
  updateFormData: (updates: Partial<ApplicationFormData>) => void;
  onNext: () => void;
  onBack: () => void;
}

interface DocumentUpload {
  document_type: 'resume' | 'cover_letter' | 'portfolio';
  title: string;
  file: File;
}

const DocumentsStep: React.FC<DocumentsStepProps> = ({
  formData,
  updateFormData,
  onNext,
  onBack
}) => {
  const [documents, setDocuments] = useState<DocumentUpload[]>(formData.documents);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [dragOver, setDragOver] = useState<string | null>(null);
  const fileInputRefs = {
    resume: useRef<HTMLInputElement>(null),
    cover_letter: useRef<HTMLInputElement>(null),
    portfolio: useRef<HTMLInputElement>(null)
  };

  const documentTypes = [
    {
      key: 'resume' as const,
      label: 'Resume/CV',
      description: 'Upload your resume or CV (PDF, DOC, DOCX)',
      required: true,
      accept: '.pdf,.doc,.docx'
    },
    {
      key: 'cover_letter' as const,
      label: 'Cover Letter',
      description: 'Upload a cover letter document (PDF, DOC, DOCX)',
      required: false,
      accept: '.pdf,.doc,.docx'
    },
    {
      key: 'portfolio' as const,
      label: 'Portfolio',
      description: 'Upload portfolio or work samples (PDF, DOC, DOCX)',
      required: false,
      accept: '.pdf,.doc,.docx'
    }
  ];

  const validateFile = (file: File): string | null => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (file.size > maxSize) {
      return 'File size must be less than 10MB';
    }

    if (!allowedTypes.includes(file.type)) {
      return 'Only PDF, DOC, and DOCX files are allowed';
    }

    return null;
  };

  const handleFileSelect = (documentType: 'resume' | 'cover_letter' | 'portfolio', file: File) => {
    const error = validateFile(file);
    if (error) {
      setErrors(prev => ({ ...prev, [documentType]: error }));
      return;
    }

    // Clear any existing error
    setErrors(prev => ({ ...prev, [documentType]: '' }));

    // Remove existing document of the same type
    const filteredDocs = documents.filter(doc => doc.document_type !== documentType);
    
    // Add new document
    const newDocument: DocumentUpload = {
      document_type: documentType,
      title: file.name,
      file
    };

    const updatedDocuments = [...filteredDocs, newDocument];
    setDocuments(updatedDocuments);
    updateFormData({ documents: updatedDocuments });
  };

  const handleFileInputChange = (documentType: 'resume' | 'cover_letter' | 'portfolio') => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(documentType, file);
    }
  };

  const handleDragOver = (e: React.DragEvent, documentType: string) => {
    e.preventDefault();
    setDragOver(documentType);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(null);
  };

  const handleDrop = (e: React.DragEvent, documentType: 'resume' | 'cover_letter' | 'portfolio') => {
    e.preventDefault();
    setDragOver(null);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(documentType, file);
    }
  };

  const removeDocument = (documentType: 'resume' | 'cover_letter' | 'portfolio') => {
    const filteredDocs = documents.filter(doc => doc.document_type !== documentType);
    setDocuments(filteredDocs);
    updateFormData({ documents: filteredDocs });
    
    // Clear any errors
    setErrors(prev => ({ ...prev, [documentType]: '' }));
    
    // Reset file input
    if (fileInputRefs[documentType].current) {
      fileInputRefs[documentType].current!.value = '';
    }
  };

  const getDocumentByType = (type: 'resume' | 'cover_letter' | 'portfolio') => {
    return documents.find(doc => doc.document_type === type);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Check if resume is uploaded (required)
    if (!getDocumentByType('resume')) {
      newErrors.resume = 'Resume is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateForm()) {
      onNext();
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="p-6">
      <div className="space-y-6">
        <div className="text-sm text-gray-600">
          <p>Upload your documents to complete your application. All files must be in PDF, DOC, or DOCX format and under 10MB.</p>
        </div>

        {documentTypes.map((docType) => {
          const existingDoc = getDocumentByType(docType.key);
          const hasError = errors[docType.key];

          return (
            <div key={docType.key} className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                {docType.label}
                {docType.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              <p className="text-xs text-gray-500">{docType.description}</p>

              {!existingDoc ? (
                <div
                  className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                    dragOver === docType.key
                      ? 'border-blue-400 bg-blue-50'
                      : hasError
                      ? 'border-red-300 bg-red-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragOver={(e) => handleDragOver(e, docType.key)}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, docType.key)}
                >
                  <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <div className="mt-4">
                    <button
                      type="button"
                      onClick={() => fileInputRefs[docType.key].current?.click()}
                      className="text-blue-600 hover:text-blue-500 font-medium"
                    >
                      Click to upload
                    </button>
                    <span className="text-gray-500"> or drag and drop</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    PDF, DOC, DOCX up to 10MB
                  </p>
                  <input
                    ref={fileInputRefs[docType.key]}
                    type="file"
                    accept={docType.accept}
                    onChange={handleFileInputChange(docType.key)}
                    className="hidden"
                    aria-label={`Upload ${docType.label}`}
                  />
                </div>
              ) : (
                <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {existingDoc.title}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(existingDoc.file.size)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        type="button"
                        onClick={() => fileInputRefs[docType.key].current?.click()}
                        className="text-blue-600 hover:text-blue-500 text-sm font-medium"
                      >
                        Replace
                      </button>
                      <button
                        type="button"
                        onClick={() => removeDocument(docType.key)}
                        className="text-red-600 hover:text-red-500 text-sm font-medium"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                  <input
                    ref={fileInputRefs[docType.key]}
                    type="file"
                    accept={docType.accept}
                    onChange={handleFileInputChange(docType.key)}
                    className="hidden"
                    aria-label={`Replace ${docType.label}`}
                  />
                </div>
              )}

              {hasError && (
                <p className="text-sm text-red-600" role="alert">
                  {hasError}
                </p>
              )}
            </div>
          );
        })}

        {/* Upload Guidelines */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-yellow-800">Upload Guidelines</h4>
              <div className="mt-1 text-sm text-yellow-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>Resume/CV is required for all applications</li>
                  <li>Files must be in PDF, DOC, or DOCX format</li>
                  <li>Maximum file size is 10MB per document</li>
                  <li>Use clear, descriptive filenames</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between pt-6 mt-6 border-t border-gray-200">
        <button
          onClick={onBack}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Back
        </button>
        <button
          onClick={handleNext}
          className="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Next: Review Application
        </button>
      </div>
    </div>
  );
};

export default DocumentsStep;