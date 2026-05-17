# AI Features Development Guide

## Architecture Overview

### Layer Structure

```
Frontend (React/Next.js)
    ↓
AI Hooks Layer (useAI.ts)
    ↓
API Client Layer (aiApi.ts)
    ↓
Jimat-AI Service (FastAPI)
    ↓
LLM/ML Models
```

### Data Flow

```
User Action (e.g., upload receipt)
    ↓
Component (e.g., AIDocumentUpload)
    ↓
Hook (e.g., useDocumentAnalysis)
    ↓
API Client (analyzeDocument)
    ↓
Jimat-AI Endpoint
    ↓
Response → Component State → UI Update
```

---

## Extending AI Features

### Adding a New AI Feature (Step-by-Step)

#### Step 1: Define API Interface

Add to `lib/aiApi.ts`:

```typescript
// Define request interface
export interface MyNewFeatureRequest {
  input: string;
  metadata?: Record<string, any>;
}

// Define response interface
export interface MyNewFeatureResponse {
  success: boolean;
  result: string;
  confidence: number;
  processing_time_ms: number;
  timestamp: string;
}

// Create API function
export async function myNewFeature(
  request: MyNewFeatureRequest
): Promise<MyNewFeatureResponse> {
  const response = await aiClient.post('/api/v1/mynewfeature', request);
  return response.data;
}
```

#### Step 2: Create a Custom Hook

Add to `hooks/useAI.ts`:

```typescript
export function useMyNewFeature() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processFeature = useCallback(async (request: MyNewFeatureRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await myNewFeature(request);
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message;
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { processFeature, loading, error };
}
```

#### Step 3: Create a Component

Create `components/ai/MyNewFeature.tsx`:

```typescript
'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Loader } from 'lucide-react';
import { useMyNewFeature } from '@/hooks/useAI';

interface MyNewFeatureProps {
  onResult: (result: any) => void;
}

export function MyNewFeature({ onResult }: MyNewFeatureProps) {
  const { processFeature, loading, error } = useMyNewFeature();

  const handleProcess = async () => {
    try {
      const result = await processFeature({ input: 'your input' });
      onResult(result);
    } catch (err) {
      // Error handled in hook
    }
  };

  return (
    <div>
      <Button onClick={handleProcess} disabled={loading}>
        {loading ? <Loader className="animate-spin" /> : 'Process'}
      </Button>
      {error && <p className="text-red-600 text-sm">{error}</p>}
    </div>
  );
}
```

#### Step 4: Export from Index

Update `components/ai/index.ts`:

```typescript
export { MyNewFeature } from './MyNewFeature';
```

#### Step 5: Use in Page/Modal

```typescript
import { MyNewFeature } from '@/components/ai';

export default function MyPage() {
  return <MyNewFeature onResult={(result) => console.log(result)} />;
}
```

---

## Component Best Practices

### 1. State Management

Use React hooks for component state:

```typescript
const [data, setData] = useState<DataType | null>(null);
const [expanded, setExpanded] = useState(false);
const [cached, setCached] = useState<Map>(new Map());
```

### 2. Loading States

Always show loading indicators:

```typescript
{loading && (
  <div className="flex items-center gap-2">
    <Loader className="animate-spin" />
    <span>Processing...</span>
  </div>
)}
```

### 3. Error Handling

Graceful error display:

```typescript
{error && (
  <div className="bg-red-50 border border-red-200 rounded p-3">
    <p className="text-red-700 text-sm">{error}</p>
  </div>
)}
```

### 4. Empty States

Handle case when no data:

```typescript
{data?.length === 0 && (
  <div className="text-center text-gray-500">
    <p>No data available</p>
  </div>
)}
```

---

## API Client Patterns

### Handling Different Response Types

```typescript
// Success response
interface SuccessResponse<T> {
  success: true;
  data: T;
  timestamp: string;
}

// Error response
interface ErrorResponse {
  success: false;
  error: string;
  details?: Record<string, any>;
}

// Union type
type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;

// Usage
export async function apiCall<T>(
  endpoint: string,
  data: any
): Promise<T> {
  const response = await aiClient.post<ApiResponse<T>>(endpoint, data);
  if (!response.data.success) {
    throw new Error(response.data.error);
  }
  return response.data.data;
}
```

### Retry Logic

```typescript
export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  delay = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Max retries exceeded');
}
```

---

## Styling Guidelines

### Consistent Color Scheme

```typescript
const severityColors = {
  high: 'bg-red-50 border-l-red-500 text-red-700',
  medium: 'bg-amber-50 border-l-amber-500 text-amber-700',
  low: 'bg-green-50 border-l-green-500 text-green-700',
};

const statusColors = {
  loading: 'text-blue-600',
  success: 'text-green-600',
  error: 'text-red-600',
  warning: 'text-amber-600',
};
```

### Responsive Design

```typescript
// Mobile first
<div className="space-y-2 md:space-y-4">
  {/* Content */}
</div>

// Grid with responsive columns
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Items */}
</div>
```

---

## Performance Optimization

### 1. Memoization

```typescript
import { useMemo, useCallback } from 'react';

const MyComponent = ({ data }: Props) => {
  // Memoize expensive calculations
  const processedData = useMemo(() => {
    return data.map(item => expensiveOperation(item));
  }, [data]);

  // Memoize callbacks
  const handleClick = useCallback(() => {
    doSomething();
  }, [dependencies]);

  return <div>{processedData}</div>;
};
```

### 2. Lazy Loading

```typescript
import dynamic from 'next/dynamic';

// Load component only when needed
const ExpensiveComponent = dynamic(
  () => import('@/components/ExpensiveComponent'),
  { loading: () => <Skeleton /> }
);
```

### 3. Request Debouncing

```typescript
import { useEffect, useRef } from 'react';

function useDebounce(value: string, delay: number) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}
```

---

## Testing Patterns

### Component Testing

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

describe('AICategorySuggestion', () => {
  it('should display suggestion with confidence score', async () => {
    render(
      <AICategorySuggestion
        description="Lunch at restaurant"
        onSelectCategory={jest.fn()}
      />
    );

    const button = screen.getByRole('button', { name: /get ai category/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/confident/i)).toBeInTheDocument();
    });
  });
});
```

### Hook Testing

```typescript
import { renderHook, act } from '@testing-library/react';

describe('useCategorization', () => {
  it('should categorize expense', async () => {
    const { result } = renderHook(() => useCategorization());

    let response;
    await act(async () => {
      response = await result.current.categorize({
        description: 'Coffee',
      });
    });

    expect(response.confidence).toBeGreaterThan(0);
  });
});
```

---

## Future Enhancement Ideas

### 1. Caching
- Cache categorization results for common descriptions
- Store user's past category choices for suggestions

### 2. Bulk Operations
- Batch categorize multiple expenses
- Bulk pattern detection for large datasets

### 3. User Preferences
- Learn from user's accepted/rejected suggestions
- Personalized category recommendations

### 4. Advanced Analytics
- Budget forecasting based on patterns
- Seasonal spending analysis
- Category trend predictions

### 5. Notifications
- Alert for unusual spending patterns
- Budget milestone notifications
- Weekly/monthly spending summaries

---

## Debugging Tips

### 1. Network Requests
```typescript
// Enable logging in aiApi.ts
if (process.env.NODE_ENV === 'development') {
  console.log('Request:', request);
  console.log('Response:', response.data);
}
```

### 2. Component State
```typescript
// Use React DevTools to inspect component state
// Add console logs at key points
console.log('Processing...', { loading, error, data });
```

### 3. Performance
```typescript
// Use React Profiler to measure component performance
// Check for unnecessary re-renders
// Profile API response times
```

---

## Deployment Considerations

### Environment Setup
```env
# Production
NEXT_PUBLIC_AI_API_URL=https://ai-api.jimat.example.com

# Staging
NEXT_PUBLIC_AI_API_URL=https://ai-staging.jimat.example.com
```

### Error Tracking
- Integrate with Sentry/LogRocket for error monitoring
- Log AI service failures for debugging

### Rate Limiting
- Implement client-side rate limiting for API calls
- Cache responses to reduce API load

### Security
- Never expose API keys in frontend code
- Use environment variables for sensitive data
- Validate user input before sending to AI service

---

## Resources

- [React Hooks Documentation](https://react.dev/reference/react)
- [Next.js Documentation](https://nextjs.org/docs)
- [Base UI Documentation](https://base-ui.io/)
- [Axios Documentation](https://axios-http.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
