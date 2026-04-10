import { useCallback, useState, useRef } from 'react';
import { Upload } from 'lucide-react';

interface FileDropzoneProps {
  accept: string;            // e.g. ".csv" or ".yml,.yaml"
  label: string;             // e.g. "Drop CSV file here"
  onFile: (file: File) => void;
  disabled?: boolean;
  className?: string;
}

export function FileDropzone({ accept, label, onFile, disabled, className = '' }: FileDropzoneProps) {
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const exts = accept.split(',').map(e => e.trim().toLowerCase());

  const isValidFile = (file: File) => {
    const name = file.name.toLowerCase();
    return exts.some(ext => name.endsWith(ext));
  };

  const handleFile = useCallback((file: File) => {
    if (!isValidFile(file)) return;
    setFileName(file.name);
    onFile(file);
  }, [onFile, exts]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [disabled, handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setDragOver(true);
  }, [disabled]);

  const handleDragLeave = useCallback(() => setDragOver(false), []);

  const handleClick = useCallback(() => {
    if (!disabled) inputRef.current?.click();
  }, [disabled]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    // Reset so same file can be re-selected
    e.target.value = '';
  }, [handleFile]);

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={handleClick}
      className={`
        border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors
        ${dragOver ? 'border-blue-400 bg-blue-50' : 'border-slate-300 hover:border-slate-400'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleInputChange}
        className="hidden"
      />
      <Upload className="size-5 mx-auto mb-1.5 text-slate-400" />
      {fileName ? (
        <p className="text-sm font-medium text-slate-700">{fileName}</p>
      ) : (
        <p className="text-sm text-slate-500">{label}</p>
      )}
      <p className="text-xs text-slate-400 mt-0.5">
        {accept.replace(/\./g, '').toUpperCase()} only
      </p>
    </div>
  );
}
