# Jimat Frontend - AI Features Integration

## Overview

The frontend has been enhanced with AI-powered features from the jimat-ai service to provide intelligent expense tracking and analytics.

## New Features

### 1. **Smart Receipt Scanning** 📷
- **Location**: Quick Add Modal → Receipt Scan tab
- **How it works**: 
  - Upload a receipt/document photo
  - AI automatically extracts text using OCR
  - Suggested amount and description pre-filled
  - User can review and adjust before submitting
- **Benefits**: 
  - Faster expense entry
  - Reduced manual typing
  - Better accuracy

### 2. **AI Category Suggestions** ✨
- **Location**: Both manual entry and receipt scan modes
- **How it works**:
  - Type expense description
  - Click "Get AI Category Suggestion" button
  - AI analyzes text and suggests the best category
  - Shows confidence score (0-100%)
  - Shows explanation of why category was chosen
  - Offers alternative category suggestions
- **Benefits**:
  - Consistent categorization
  - Reduces decision fatigue
  - Learn spending patterns

### 3. **AI Insights Panel** 📊
- **Location**: Dashboard
- **What it shows**:
  - Total spending summary
  - Transaction statistics
  - Top spending category
  - Detected spending patterns
  - Severity and confidence scores for patterns
- **Benefits**:
  - Quick overview of spending health
  - Early detection of unusual patterns
  - Pattern-based insights

### 4. **Detailed Insights Page** 🔍
- **Location**: Navigation → AI Insights
- **What it shows**:
  - Comprehensive spending summary (daily/weekly/monthly/yearly)
  - Category breakdown with percentages and charts
  - All detected spending patterns
  - Pattern severity and confidence levels
  - Time period selector for custom analysis
- **Benefits**:
  - In-depth spending analysis
  - Identifies trends and anomalies
  - Customizable time periods

## New Components

### Core Components

1. **AICategorySuggestion** (`components/ai/AICategorySuggestion.tsx`)
   - Displays AI-powered category suggestions
   - Shows confidence scores and alternatives
   - Accept/reject UI for user control

2. **AIDocumentUpload** (`components/ai/AIDocumentUpload.tsx`)
   - Drag-and-drop document upload
   - OCR processing and text extraction
   - Preview and error handling
   - Automatic amount detection

3. **AIInsightsPanel** (`components/ai/AIInsightsPanel.tsx`)
   - Compact insights display for dashboard
   - Shows summary and patterns
   - Real-time loading and error states

## New Files Created

### API & Hooks
- `lib/aiApi.ts` - AI service API client and interfaces
- `hooks/useAI.ts` - Custom React hooks for AI features
- `components/ui/tabs.tsx` - Tab component for modal

### Pages
- `app/insights/page.tsx` - Dedicated insights analysis page

### Components
- `components/ai/index.ts` - AI components exports
- `components/ai/AICategorySuggestion.tsx` - Category suggestion component
- `components/ai/AIDocumentUpload.tsx` - Document upload component
- `components/ai/AIInsightsPanel.tsx` - Insights panel component

## Modified Files

- `app/page.tsx` - Added AI Insights section to dashboard
- `components/modals/AddExpenseModal.tsx` - Added receipt scan tab with AI features
- `components/layouts/Sidebar.tsx` - Added AI Insights navigation link
- `components/ui/tabs.tsx` - Created new tab component

## Configuration

### Environment Variables
Make sure your `.env.local` has:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000    # Jimat main API
NEXT_PUBLIC_AI_API_URL=http://localhost:8001 # Jimat AI service
```

### Prerequisites
- Jimat main service running on port 8000
- Jimat AI service running on port 8001

## Usage Guide

### Adding an Expense with Receipt

1. Click "Quick Add" button
2. Switch to "📷 Receipt Scan" tab
3. Drag and drop receipt image or click to select
4. Wait for OCR processing
5. Review extracted text and suggested amount
6. AI will suggest category - review confidence and explanation
7. Adjust category if needed
8. Click "Create Expense"

### Adding an Expense Manually

1. Click "Quick Add" button
2. Use "Manual Entry" tab
3. Type description (expense will be analyzed for AI suggestions)
4. Enter amount
5. AI suggests category automatically
6. Confirm or select different category
7. Select date
8. Click "Create Expense"

### Viewing Insights

1. Click "AI Insights" in navigation
2. Select time period (Daily/Weekly/Monthly/Yearly)
3. Review:
   - Spending summary statistics
   - Category breakdown chart
   - Detected patterns with severity scores
   - Pattern explanations

## AI Service Integration

The frontend communicates with jimat-ai service endpoints:

- **POST** `/api/v1/documents/analyze` - OCR and text extraction
- **POST** `/api/v1/categorization/categorize` - Category suggestion with confidence
- **POST** `/api/v1/insights/summary` - Spending summary analysis
- **POST** `/api/v1/insights/patterns` - Spending pattern detection

## Error Handling

All AI features include:
- Loading states with spinners
- Error messages with helpful context
- Fallback options (manual category selection if AI fails)
- Network error handling and retry prompts

## Design Principles

1. **User-Friendly** - Simple, intuitive interfaces with clear guidance
2. **Non-Intrusive** - AI suggestions don't require adoption, users can override
3. **Transparent** - Confidence scores and explanations shown
4. **Accessible** - Works with keyboard navigation, clear visual hierarchy
5. **Responsive** - Mobile-friendly design across all screen sizes

## Future Enhancements

Potential features for future releases:
- Budget recommendations based on patterns
- Spending alerts for anomalies
- Category-wise trend charts
- Export insights as reports
- Multi-user expense splitting with AI analysis
- Receipt image library with search
- Scheduled insights reports via email
