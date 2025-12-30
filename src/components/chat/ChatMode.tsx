'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Paperclip, Send, Loader2, X, FileText, Image as ImageIcon } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

// Types
interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  timestamp: Date;
  attachments?: FileAttachment[];
  extractedData?: ExtractedData;
}

interface FileAttachment {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  uploadProgress?: number;
  uploadStatus?: 'uploading' | 'uploaded' | 'error';
}

interface ExtractedData {
  propertyName?: string;
  address?: string;
  units?: number;
  askingPrice?: number;
  yearBuilt?: number;
  status?: string;
}

interface ChatModeProps {
  dealId?: string;
  onSwitchToDashboard?: () => void;
}

export const ChatMode: React.FC<ChatModeProps> = ({ dealId, onSwitchToDashboard }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [extractedDeal, setExtractedDeal] = useState<ExtractedData | null>(null);
  const [showFileMenu, setShowFileMenu] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  // Load chat history from localStorage
  useEffect(() => {
    const savedMessages = localStorage.getItem(`chat-history-${dealId || 'new'}`);
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages);
        setMessages(
          parsed.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
          }))
        );
      } catch (e) {
        console.error('Failed to load chat history:', e);
      }
    }

    // Load extracted deal if dealId exists
    if (dealId) {
      loadDealSummary(dealId);
    }
  }, [dealId]);

  // Save chat history to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(
        `chat-history-${dealId || 'new'}`,
        JSON.stringify(messages)
      );
    }
  }, [messages, dealId]);

  const loadDealSummary = async (dealId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/deals/${dealId}`);
      if (response.ok) {
        const deal = await response.json();
        setExtractedDeal({
          propertyName: deal.property_name,
          address: `${deal.address_street}, ${deal.address_city}, ${deal.address_state} ${deal.address_zip}`,
          units: deal.units,
          askingPrice: deal.asking_price,
          yearBuilt: deal.year_built,
          status: deal.stage,
        });
      }
    } catch (error) {
      console.error('Failed to load deal summary:', error);
    }
  };

  const handleFileDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach((file) => {
      const attachment: FileAttachment = {
        id: Math.random().toString(36).substring(2, 11),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadStatus: 'uploading',
        uploadProgress: 0,
      };

      // Add message with attachment
      const newMessage: ChatMessage = {
        id: Math.random().toString(36).substring(2, 11),
        role: 'user',
        content: `Uploaded ${file.name}`,
        timestamp: new Date(),
        attachments: [attachment],
      };

      setMessages((prev) => [...prev, newMessage]);

      // Simulate file upload
      uploadFile(attachment, dealId);
    });
  }, [dealId]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleFileDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    noClick: true,
  });

  const uploadFile = async (attachment: FileAttachment, dealId?: string) => {
    try {
      const formData = new FormData();
      formData.append('files', attachment.file);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const url = dealId
        ? `${apiUrl}/api/v1/deals/${dealId}/documents`
        : `${apiUrl}/api/v1/documents/upload`;

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        
        // Update attachment status
        setMessages((prev) =>
          prev.map((msg) => ({
            ...msg,
            attachments: msg.attachments?.map((att) =>
              att.id === attachment.id
                ? { ...att, uploadStatus: 'uploaded' as const, uploadProgress: 100 }
                : att
            ),
          }))
        );

        // Add AI response about file processing
        setTimeout(() => {
          addAIMessage(
            `I've received ${attachment.name}. Processing it now...`,
            result.extraction_job_id ? { extractionJobId: result.extraction_job_id } : undefined
          );
        }, 500);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('File upload error:', error);
      setMessages((prev) =>
        prev.map((msg) => ({
          ...msg,
          attachments: msg.attachments?.map((att) =>
            att.id === attachment.id ? { ...att, uploadStatus: 'error' as const } : att
          ),
        }))
      );
    }
  };

  const addAIMessage = (content: string, extractedData?: any) => {
    const newMessage: ChatMessage = {
      id: Math.random().toString(36).substring(2, 11),
      role: 'ai',
      content,
      timestamp: new Date(),
      extractedData,
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() && messages.length === 0) return;

    const userMessage: ChatMessage = {
      id: Math.random().toString(36).substring(2, 11),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Simulate AI response (replace with actual API call)
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // For now, use simple pattern matching
      let aiResponse = '';
      const lowerInput = inputValue.toLowerCase();

      if (lowerInput.includes('property') || lowerInput.includes('deal')) {
        aiResponse =
          "Great! Let me help you evaluate this deal. What's the property name?";
      } else if (lowerInput.includes('upload') || lowerInput.includes('document')) {
        aiResponse =
          'You can drag and drop files here, or click the attach button to browse. I support PDF, Excel, and image files.';
      } else if (lowerInput.includes('create') || lowerInput.includes('new')) {
        aiResponse =
          "I can help you create a new deal. Let's start with the property name. What would you like to call it?";
      } else {
        aiResponse =
          "I understand. Can you provide more details? For example, you can tell me about the property, upload documents, or ask me to create a new deal.";
      }

      addAIMessage(aiResponse);
    } catch (error) {
      console.error('Error sending message:', error);
      addAIMessage(
        "I'm sorry, I encountered an error. Please try again or switch to Dashboard mode for manual entry."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatTime = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    }).format(date);
  };

  const hasMessages = messages.length > 0;

  return (
    <div
      {...getRootProps()}
      className={`flex flex-col h-screen bg-background-secondary ${
        isDragActive ? 'bg-yinmn-blue/5' : ''
      }`}
    >
      <input {...getInputProps()} />

      {/* Header */}
      <header className="sticky top-0 z-40 bg-background-primary border-b border-border shadow-sm">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <h1 className="text-2xl font-heading font-bold text-primary">DREAM AI</h1>
          <div className="flex items-center gap-4">
            {/* Mode Toggle */}
            <div
              className="flex items-center bg-background-tertiary rounded-lg p-1"
              role="group"
              aria-label="Mode selection"
            >
              <button
                type="button"
                onClick={onSwitchToDashboard}
                aria-label="Switch to Dashboard mode"
                className="px-4 py-2 text-sm font-medium text-secondary hover:text-primary rounded-md transition-colors min-h-[44px]"
              >
                Dashboard
              </button>
              <button
                type="button"
                aria-pressed="true"
                aria-label="Current mode: Chat"
                className="px-4 py-2 text-sm font-medium bg-background-primary text-primary rounded-md shadow-sm min-h-[44px]"
              >
                Chat
              </button>
            </div>
            <button
              type="button"
              aria-label="User menu"
              className="px-4 py-2 text-sm font-medium text-secondary hover:text-primary hover:bg-background-tertiary rounded-md transition-colors min-h-[44px]"
            >
              User Menu
            </button>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 overflow-hidden">
        {/* Empty State */}
        {!hasMessages && (
          <section className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-2xl">
              <h2 className="text-3xl font-heading font-bold text-primary mb-4">
                Welcome to Chat Mode
              </h2>
              <p className="text-lg text-secondary mb-8">
                I can help you create and evaluate deals. Try saying:
              </p>
              <ul className="space-y-3 mb-8">
                <li>
                  <button
                    type="button"
                    onClick={() => {
                      setInputValue("I have a 96-unit property in Austin asking $12.5M");
                      textareaRef.current?.focus();
                    }}
                    className="w-full px-6 py-4 bg-background-primary border border-border rounded-lg text-left hover:bg-background-tertiary hover:border-yinmn-blue transition-colors min-h-[44px]"
                  >
                    "I have a 96-unit property in Austin asking $12.5M"
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => {
                      setInputValue("Upload my OM and extract the key information");
                      textareaRef.current?.focus();
                    }}
                    className="w-full px-6 py-4 bg-background-primary border border-border rounded-lg text-left hover:bg-background-tertiary hover:border-yinmn-blue transition-colors min-h-[44px]"
                  >
                    "Upload my OM and extract the key information"
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => {
                      setInputValue("Create a new deal for Oak Creek Apartments");
                      textareaRef.current?.focus();
                    }}
                    className="w-full px-6 py-4 bg-background-primary border border-border rounded-lg text-left hover:bg-background-tertiary hover:border-yinmn-blue transition-colors min-h-[44px]"
                  >
                    "Create a new deal for Oak Creek Apartments"
                  </button>
                </li>
              </ul>
              <p className="text-sm text-secondary-muted">
                Or drag and drop documents here to get started.
              </p>
            </div>
          </section>
        )}

        {/* Populated State */}
        {hasMessages && (
          <>
            {/* Extracted Deal Summary Card */}
            {extractedDeal && (
              <article className="mb-6">
                <div className="bg-background-primary border border-border rounded-lg p-6">
                  <header className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-heading font-semibold text-primary">
                      {extractedDeal.propertyName || 'Deal Summary'}
                    </h2>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => dealId && navigate(`/deals/${dealId}`)}
                      >
                        View Full Details
                      </Button>
                      <Button variant="ghost" size="sm">
                        Edit
                      </Button>
                    </div>
                  </header>
                  <dl className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                    {extractedDeal.address && (
                      <div>
                        <dt className="text-xs font-medium text-secondary-muted mb-1">Address</dt>
                        <dd className="text-sm text-primary">{extractedDeal.address}</dd>
                      </div>
                    )}
                    {extractedDeal.units && (
                      <div>
                        <dt className="text-xs font-medium text-secondary-muted mb-1">Units</dt>
                        <dd className="text-sm text-primary tabular-nums">{extractedDeal.units}</dd>
                      </div>
                    )}
                    {extractedDeal.askingPrice && (
                      <div>
                        <dt className="text-xs font-medium text-secondary-muted mb-1">Asking Price</dt>
                        <dd className="text-sm text-primary tabular-nums">
                          ${extractedDeal.askingPrice.toLocaleString()}
                        </dd>
                      </div>
                    )}
                    {extractedDeal.yearBuilt && (
                      <div>
                        <dt className="text-xs font-medium text-secondary-muted mb-1">Year Built</dt>
                        <dd className="text-sm text-primary tabular-nums">{extractedDeal.yearBuilt}</dd>
                      </div>
                    )}
                    {extractedDeal.status && (
                      <div>
                        <dt className="text-xs font-medium text-secondary-muted mb-1">Status</dt>
                        <dd className="text-sm text-brand-success">{extractedDeal.status}</dd>
                      </div>
                    )}
                  </dl>
                </div>
              </article>
            )}

            {/* Chat Messages */}
            <section
              role="log"
              aria-live="polite"
              aria-relevant="additions"
              className="flex-1 overflow-y-auto space-y-4 mb-4"
            >
              {messages.map((message) => (
                <article
                  key={message.id}
                  className={`flex items-start gap-3 ${
                    message.role === 'user' ? 'justify-end' : ''
                  }`}
                >
                  {message.role === 'ai' && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background-tertiary flex items-center justify-center">
                      <span className="text-xs font-medium text-secondary">AI</span>
                    </div>
                  )}

                  <div className={`flex-1 max-w-[80%] ${message.role === 'user' ? 'order-2' : ''}`}>
                    <div
                      className={`rounded-2xl p-4 ${
                        message.role === 'user'
                          ? 'bg-yinmn-blue text-white ml-auto'
                          : 'bg-background-tertiary text-primary'
                      }`}
                    >
                      <p className="text-base whitespace-pre-wrap">{message.content}</p>

                      {/* File Attachments */}
                      {message.attachments && message.attachments.length > 0 && (
                        <div className="mt-3 space-y-2">
                          {message.attachments.map((attachment) => (
                            <div
                              key={attachment.id}
                              className={`rounded-lg p-3 ${
                                message.role === 'user' ? 'bg-white/10' : 'bg-background-primary'
                              }`}
                            >
                              <div className="flex items-center gap-3">
                                <FileText className="w-5 h-5" />
                                <div className="flex-1">
                                  <p className="text-sm font-medium">{attachment.name}</p>
                                  <p className="text-xs opacity-80">{formatFileSize(attachment.size)}</p>
                                </div>
                                {attachment.uploadStatus === 'uploading' && (
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                )}
                                {attachment.uploadStatus === 'uploaded' && (
                                  <span className="text-xs">✓</span>
                                )}
                                {attachment.uploadStatus === 'error' && (
                                  <span className="text-xs text-brand-danger">✗</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Extracted Data Display */}
                      {message.extractedData && (
                        <div className="mt-4 space-y-2">
                          {Object.entries(message.extractedData).map(([key, value]) => (
                            <div
                              key={key}
                              className="flex items-center justify-between border-b border-border/50 pb-2"
                            >
                              <dt className="text-sm font-medium capitalize">
                                {key.replace(/([A-Z])/g, ' $1').trim()}
                              </dt>
                              <dd className="text-sm tabular-nums">{String(value)}</dd>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    <time className="text-xs text-secondary-muted mt-1 block">
                      {formatTime(message.timestamp)}
                    </time>
                  </div>

                  {message.role === 'user' && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-yinmn-blue flex items-center justify-center order-3">
                      <span className="text-xs font-medium text-white">You</span>
                    </div>
                  )}
                </article>
              ))}

              {/* Typing Indicator */}
              {isLoading && (
                <article className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background-tertiary flex items-center justify-center">
                    <span className="text-xs font-medium text-secondary">AI</span>
                  </div>
                  <div className="flex-1 max-w-[80%]">
                    <div className="bg-background-tertiary rounded-2xl p-4">
                      <div className="flex items-center gap-1">
                        <span className="w-2 h-2 bg-secondary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="w-2 h-2 bg-secondary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="w-2 h-2 bg-secondary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                      </div>
                    </div>
                  </div>
                </article>
              )}

              <div ref={messagesEndRef} />
            </section>
          </>
        )}

        {/* Input Area */}
        <section className="border-t border-border bg-background-primary">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-end gap-2 p-4"
          >
            {/* File Upload Button */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowFileMenu(!showFileMenu)}
                aria-label="Attach file"
                className="px-4 py-3 text-secondary hover:text-primary hover:bg-background-tertiary rounded-md transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
              >
                <Paperclip className="w-5 h-5" />
              </button>

              {/* File Menu */}
              {showFileMenu && (
                <div className="absolute bottom-full left-0 mb-2 bg-background-primary border border-border rounded-lg shadow-lg p-2 min-w-[200px]">
                  <button
                    type="button"
                    onClick={() => {
                      document.querySelector('input[type="file"]')?.click();
                      setShowFileMenu(false);
                    }}
                    className="w-full px-4 py-3 text-left text-sm text-primary hover:bg-background-tertiary rounded-md transition-colors min-h-[44px] flex items-center gap-2"
                  >
                    <FileText className="w-4 h-4" />
                    Browse Files
                  </button>
                  <button
                    type="button"
                    className="w-full px-4 py-3 text-left text-sm text-primary hover:bg-background-tertiary rounded-md transition-colors min-h-[44px] flex items-center gap-2"
                  >
                    <ImageIcon className="w-4 h-4" />
                    Take Photo
                  </button>
                  <div className="border-t border-border my-1"></div>
                  <button
                    type="button"
                    className="w-full px-4 py-3 text-left text-sm text-primary hover:bg-background-tertiary rounded-md transition-colors min-h-[44px]"
                  >
                    ☁️ Google Drive
                  </button>
                  <button
                    type="button"
                    className="w-full px-4 py-3 text-left text-sm text-primary hover:bg-background-tertiary rounded-md transition-colors min-h-[44px]"
                  >
                    ☁️ OneDrive
                  </button>
                  <button
                    type="button"
                    className="w-full px-4 py-3 text-left text-sm text-primary hover:bg-background-tertiary rounded-md transition-colors min-h-[44px]"
                  >
                    ☁️ Dropbox
                  </button>
                </div>
              )}
            </div>

            {/* Text Input */}
            <Textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              rows={1}
              className="flex-1 resize-none min-h-[44px] max-h-32"
            />

            {/* Send Button */}
            <Button
              type="submit"
              disabled={!inputValue.trim() && !hasMessages}
              className="px-6 py-3 min-h-[44px]"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  Send
                  <Send className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </form>

          {/* Drag and Drop Overlay */}
          {isDragActive && (
            <div className="border-2 border-dashed border-yinmn-blue rounded-lg p-8 m-4 bg-yinmn-blue/5 text-center">
              <p className="text-base font-medium text-primary mb-2">Drop files here to upload</p>
              <p className="text-sm text-secondary-muted">
                Supported: PDF, XLSX, XLS, PNG, JPG, DOCX (max 50MB)
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default ChatMode;

