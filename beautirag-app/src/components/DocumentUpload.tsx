'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 mx-auto mb-3 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
);

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

const DocumentUpload: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [message, setMessage] = useState<string>('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setUploadedFiles(prevFiles => [...prevFiles, ...acceptedFiles]);
    setStatus('uploading');
    setMessage('Uploading...');

    const formData = new FormData();
    acceptedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/upload/`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Upload failed');
      }

      setStatus('success');
      setMessage(result.message || 'Files uploaded successfully!');
      
      // setUploadedFiles([]);
      console.log('Upload successful:', result);

    } catch (error) {
      console.error('Upload error:', error);
      setStatus('error');
      setMessage(error instanceof Error ? error.message : 'An unknown error occurred');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpeg', '.jpg'],
      'audio/mpeg': ['.mp3'],
      'audio/wav': ['.wav'],
    }
  });

  return (
    <div className="bg-gray-850 border border-gray-700 p-6 rounded-lg shadow-md text-gray-200">
      <h2 className="text-xl font-semi-bold-serif mb-4 text-white">Upload Documents</h2>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed border-gray-600 rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ease-in-out ${isDragActive ? 'border-indigo-500 bg-gray-700/50' : 'hover:border-gray-500 hover:bg-gray-800'}`}
      >
        <input {...getInputProps()} />
        <UploadIcon />
        {
          isDragActive ?
            <p className="text-indigo-400 font-medium">Drop the files here ...</p> :
            <p className="text-gray-400">Drag 'n' drop files here, or <span className="text-indigo-400 font-medium">click to select</span></p>
        }
        <p className="text-xs mt-3 text-gray-500">Supported: TXT, PDF, DOCX, PNG, JPEG, MP3, WAV</p>
      </div>

      {status !== 'idle' && (
        <div className={`mt-4 p-3 rounded text-center text-sm ${status === 'uploading' ? 'bg-blue-900/50 text-blue-300' : status === 'success' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}`}>
          {message}
        </div>
      )}

      {/* Keep file list even after status message for clarity */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-md font-medium text-gray-300 mb-3">Files Queued/Uploaded:</h3>
          <ul className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <li key={index} className="text-sm bg-gray-700/50 px-3 py-2 rounded flex justify-between items-center">
                <span>{file.name}</span>
                <span className="text-gray-400 text-xs">({Math.round(file.size / 1024)} KB)</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload; 