import React, { useState } from 'react';
import { Card, Button } from '../components/UIComponents';
import { UploadCloud, FileText, Check, Loader2, ArrowRight } from 'lucide-react';

const DealIntake: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<{name: string, size: string, status: 'uploading' | 'parsing' | 'complete'}[]>([]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      simulateUpload(e.dataTransfer.files[0].name);
    }
  };

  const simulateUpload = (filename: string) => {
    setFiles(prev => [...prev, { name: filename, size: '2.4 MB', status: 'uploading' }]);
    
    setTimeout(() => {
       setFiles(prev => prev.map(f => f.name === filename ? { ...f, status: 'parsing' } : f));
       setTimeout(() => {
         setFiles(prev => prev.map(f => f.name === filename ? { ...f, status: 'complete' } : f));
       }, 2000);
    }, 1500);
  };

  return (
    <div className="max-w-3xl mx-auto py-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-heading font-bold text-primary mb-3">Analyze a New Deal</h1>
        <p className="text-secondary-muted max-w-lg mx-auto">Upload an Offering Memorandum (OM), Rent Roll, or T12. DreamVision will extract the data and build a financial model in seconds.</p>
      </div>

      <Card className={`p-10 border-2 border-dashed transition-all duration-200 text-center mb-8 ${dragActive ? 'border-accent bg-accent/5' : 'border-border hover:border-accent/50 bg-background-primary'}`}
        onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
      >
        <div className="w-16 h-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-4">
          <UploadCloud className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-semibold text-secondary mb-2">Drag and drop files here</h3>
        <p className="text-sm text-secondary-muted mb-6">Supported formats: PDF, XLSX, CSV</p>
        <Button variant="outline">Browse Files</Button>
      </Card>

      {files.length > 0 && (
        <div className="space-y-4 mb-8">
          <h4 className="text-sm font-semibold text-secondary-muted uppercase tracking-wider">Uploaded Files</h4>
          {files.map((file, idx) => (
            <Card key={idx} className="p-4 flex items-center justify-between">
               <div className="flex items-center space-x-3">
                 <div className="p-2 bg-background-tertiary rounded">
                   <FileText className="w-5 h-5 text-secondary" />
                 </div>
                 <div>
                   <p className="text-sm font-medium text-secondary">{file.name}</p>
                   <p className="text-xs text-secondary-muted">{file.size}</p>
                 </div>
               </div>
               <div className="flex items-center">
                 {file.status === 'uploading' && <span className="flex items-center text-xs text-blue-600 dark:text-blue-400"><Loader2 className="w-3 h-3 mr-1 animate-spin" /> Uploading...</span>}
                 {file.status === 'parsing' && <span className="flex items-center text-xs text-orange-600 dark:text-orange-400"><Loader2 className="w-3 h-3 mr-1 animate-spin" /> Extracting Data...</span>}
                 {file.status === 'complete' && <span className="flex items-center text-xs text-green-600 dark:text-green-400 font-medium"><Check className="w-4 h-4 mr-1" /> Ready</span>}
               </div>
            </Card>
          ))}
        </div>
      )}

      {files.some(f => f.status === 'complete') && (
        <div className="flex justify-end">
           <Button variant="primary" size="lg" icon={ArrowRight} onClick={onComplete}>Analyze Deal</Button>
        </div>
      )}
    </div>
  );
};

export default DealIntake;