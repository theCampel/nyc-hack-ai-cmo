import React, { useCallback, useState } from 'react';
import { Upload, X, FileImage, FileText, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface UploadedFile {
  id: string;
  file: File;
  type: 'photo' | 'document';
  preview?: string;
}

interface FileUploadProps {
  onFilesChange: (files: UploadedFile[]) => void;
  hasPhoto: boolean;
}

export function FileUpload({ onFilesChange, hasPhoto }: FileUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    processFiles(selectedFiles);
  }, []);

  const processFiles = (newFiles: File[]) => {
    const processedFiles = newFiles.map(file => {
      const isImage = file.type.startsWith('image/');
      const hasExistingPhoto = files.some(f => f.type === 'photo');
      
      const uploadedFile: UploadedFile = {
        id: Math.random().toString(36).substr(2, 9),
        file,
        type: isImage && !hasExistingPhoto ? 'photo' : 'document',
      };

      if (isImage) {
        uploadedFile.preview = URL.createObjectURL(file);
      }

      return uploadedFile;
    });

    const updatedFiles = [...files, ...processedFiles];
    setFiles(updatedFiles);
    onFilesChange(updatedFiles);
  };

  const removeFile = (id: string) => {
    const updatedFiles = files.filter(f => f.id !== id);
    setFiles(updatedFiles);
    onFilesChange(updatedFiles);
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        className={cn(
          "relative border-4 border-dashed rounded-3xl p-12 text-center transition-all duration-300 cursor-pointer",
          "bg-white/60 backdrop-blur-sm shadow-md border-cmo-primary/40",
          "hover:border-cmo-primary/60",
          isDragOver && "border-cmo-primary bg-cmo-primary/10",
          !hasPhoto && "border-cmo-primary/60 bg-gradient-to-br from-white/70 to-transparent"
        )}
      >
        <input
          type="file"
          multiple
          accept="image/*,.pdf,.doc,.docx,.txt"
          onChange={handleFileSelect}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="flex flex-col items-center space-y-4">
          <div className={cn(
            "w-20 h-20 rounded-full border-4 border-dashed border-cmo-primary/40 flex items-center justify-center transition-all duration-300",
            !hasPhoto && "border-cmo-primary bg-cmo-primary/10"
          )}>
            {!hasPhoto ? (
              <User className="w-8 h-8 text-cmo-primary" />
            ) : (
              <Upload className="w-8 h-8 text-muted-foreground" />
            )}
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-medium">
              {!hasPhoto ? 'Upload your photo first' : 'Add supporting documents'}
            </h3>
            <p className="text-sm text-muted-foreground">
              {!hasPhoto 
                ? 'Drag and drop your photo here, or click to select'
                : 'Add brand guidelines, pitch decks, or other materials'
              }
            </p>
          </div>
        </div>
      </div>

      {/* File Previews */}
      {files.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {files.map((file) => (
            <div
              key={file.id}
              className="relative group bg-card border border-border rounded-xl p-4 hover:shadow-lg transition-all duration-300"
            >
              <button
                onClick={() => removeFile(file.id)}
                className="absolute -top-2 -right-2 w-6 h-6 bg-destructive text-destructive-foreground rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:scale-110"
              >
                <X className="w-3 h-3" />
              </button>

              <div className="flex flex-col items-center space-y-3">
                {file.preview ? (
                  <img
                    src={file.preview}
                    alt={file.file.name}
                    className="w-12 h-12 rounded-lg object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center">
                    {file.type === 'photo' ? (
                      <FileImage className="w-6 h-6 text-muted-foreground" />
                    ) : (
                      <FileText className="w-6 h-6 text-muted-foreground" />
                    )}
                  </div>
                )}

                <div className="text-center">
                  <p className="text-xs font-medium truncate w-full">
                    {file.file.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {file.type === 'photo' ? 'Profile Photo' : 'Document'}
                  </p>
                </div>

                {file.type === 'photo' && (
                  <div className="w-2 h-2 bg-cmo-primary rounded-full animate-pulse-glow" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}