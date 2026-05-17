/**
 * AI Document Upload Component
 * 
 * Upload receipts/documents for OCR and expense extraction
 */

'use client';

import React, { useState, useRef } from 'react';
import { Upload, Image as ImageIcon, Loader, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useDocumentAnalysis } from '@/hooks/useAI';

interface AIDocumentUploadProps {
  onExtractedText: (text: string) => void;
  onExtractedData?: (data: {
    description: string;
    amount?: number;
  }) => void;
  disabled?: boolean;
}

export function AIDocumentUpload({
  onExtractedText,
  onExtractedData,
  disabled = false,
}: AIDocumentUploadProps) {
  const { analyze, loading, error } = useDocumentAnalysis();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState<string>('');

  const handleFileSelect = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file (receipt/document photo)');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64 = e.target?.result as string;
      setPreview(base64);

      // Analyze document
      try {
        const result = await analyze({
          content_type: 'image',
          content: base64.split(',')[1], // Remove data URL prefix
        });

        setExtractedText(result.extracted_text);
        onExtractedText(result.extracted_text);

        // Try to parse expense data from extracted text
        if (onExtractedData) {
          // Simple pattern matching for common receipt formats
          const amountMatch = result.extracted_text.match(/(?:total|amount|price|$)?\s*(\d+\.?\d*)/i);
          const amount = amountMatch ? parseFloat(amountMatch[1]) : undefined;

          onExtractedData({
            description: result.extracted_text.substring(0, 100),
            amount,
          });
        }
      } catch (err) {
        // Error is handled in hook
      }
    };
    reader.readAsDataURL(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-400 transition cursor-pointer bg-gray-50 hover:bg-blue-50"
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleInputChange}
          disabled={disabled || loading}
          className="hidden"
        />

        {preview ? (
          <div className="space-y-2">
            <img src={preview} alt="Receipt preview" className="max-h-40 mx-auto rounded" />
            {loading && (
              <div className="flex items-center justify-center gap-2 text-blue-600">
                <Loader className="w-4 h-4 animate-spin" />
                <span className="text-sm">Processing image...</span>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            {loading ? (
              <>
                <Loader className="w-6 h-6 text-blue-600 animate-spin" />
                <p className="text-sm text-gray-600">Processing...</p>
              </>
            ) : (
              <>
                <ImageIcon className="w-6 h-6 text-gray-400" />
                <p className="text-sm font-semibold text-gray-700">
                  Click to upload or drag receipt
                </p>
                <p className="text-xs text-gray-500">
                  JPG, PNG or GIF (max. 5MB)
                </p>
              </>
            )}
          </div>
        )}
      </div>

      {extractedText && (
        <div className="bg-gray-100 rounded-lg p-3 border border-gray-200">
          <p className="text-xs font-semibold text-gray-600 mb-1">Extracted Text:</p>
          <p className="text-sm text-gray-700 line-clamp-3">{extractedText}</p>
        </div>
      )}

      {error && (
        <div className="flex gap-2 items-start bg-red-50 border border-red-200 rounded-lg p-3">
          <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {preview && (
        <Button
          onClick={() => {
            setPreview(null);
            setExtractedText('');
            if (fileInputRef.current) fileInputRef.current.value = '';
          }}
          size="sm"
          variant="outline"
          className="w-full"
        >
          Clear
        </Button>
      )}
    </div>
  );
}
