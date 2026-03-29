# Frontend Implementation Guide

**For:** Email Marketing Dashboard
**Backend:** FastAPI Email Marketing System
**Recommended Tech Stack:** React, TypeScript, Tailwind CSS, Axios

---

## Table of Contents

1. [Project Setup](#project-setup)
2. [API Service Layer](#api-service-layer)
3. [Authentication Flow](#authentication-flow)
4. [Component Architecture](#component-architecture)
5. [Pages & Features](#pages--features)
6. [State Management](#state-management)
7. [Form Handling](#form-handling)
8. [Error Handling](#error-handling)

---

## Project Setup

### Create React App with TypeScript

```bash
npx create-react-app email-marketing-frontend --template typescript
cd email-marketing-frontend
npm install axios react-router-dom zustand react-hot-toast
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Project Structure

```
src/
├── components/
│   ├── Auth/
│   │   ├── LoginForm.tsx
│   │   ├── SignupForm.tsx
│   │   └── ForgotPassword.tsx
│   ├── Dashboard/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Stats.tsx
│   ├── Email/
│   │   ├── EmailList.tsx
│   │   ├── SendEmail.tsx
│   │   ├── BulkSendEmail.tsx
│   │   └── TemplateManager.tsx
│   ├── Scrape/
│   │   ├── ScrapeForm.tsx
│   │   └── ScrapeProgress.tsx
│   └── Profile/
│       ├── UserProfile.tsx
│       └── ProfileForm.tsx
├── pages/
│   ├── LoginPage.tsx
│   ├── SignupPage.tsx
│   ├── DashboardPage.tsx
│   ├── EmailManagementPage.tsx
│   ├── ScrapePage.tsx
│   ├── ProfilePage.tsx
│   └── NotFoundPage.tsx
├── services/
│   ├── api.ts
│   ├── authService.ts
│   ├── emailService.ts
│   ├── scrapeService.ts
│   └── profileService.ts
├── store/
│   ├── authStore.ts
│   └── uiStore.ts
├── hooks/
│   ├── useAuth.ts
│   ├── useFetch.ts
│   └── useFormValidation.ts
├── types/
│   ├── api.ts
│   ├── auth.ts
│   └── email.ts
├── utils/
│   ├── localStorage.ts
│   ├── tokenUtils.ts
│   └── validators.ts
└── App.tsx
```

---

## API Service Layer

### 1. Base API Configuration

**`src/services/api.ts`**

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';
import { useAuthStore } from '../store/authStore';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

let api: AxiosInstance;

export const initializeAPI = () => {
  api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor
  api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      // Handle 401 - token expired or invalid
      if (error.response?.status === 401) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return api;
};

export const getAPI = () => api || initializeAPI();
```

### 2. Authentication Service

**`src/services/authService.ts`**

```typescript
import { getAPI } from './api';
import {
  SignUpRequest,
  LoginRequest,
  TokenResponse,
  ResetPasswordRequest,
  ForgotPasswordRequest,
} from '../types/auth';

export const authService = {
  signup: async (data: SignUpRequest): Promise<TokenResponse> => {
    const response = await getAPI().post('/auth/signup', data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await getAPI().post('/auth/login', data);
    return response.data;
  },

  resetPassword: async (data: ResetPasswordRequest): Promise<{ success: boolean; message: string }> => {
    const response = await getAPI().post('/auth/reset-password', data);
    return response.data;
  },

  forgotPassword: async (data: ForgotPasswordRequest): Promise<{ success: boolean; message: string }> => {
    const response = await getAPI().post('/auth/forgot-password', data);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await getAPI().get('/auth/me');
    return response.data;
  },
};
```

### 3. Email Service

**`src/services/emailService.ts`**

```typescript
import { getAPI } from './api';
import {
  EmailListResponse,
  EmailTemplate,
  SendEmailRequest,
  BulkSendEmailRequest,
  BulkSendResponse,
} from '../types/email';

export const emailService = {
  getAllEmails: async (): Promise<EmailListResponse> => {
    const response = await getAPI().get('/emails/all');
    return response.data;
  },

  getTemplates: async (): Promise<EmailTemplate[]> => {
    const response = await getAPI().get('/emails/templates');
    return response.data;
  },

  getTemplate: async (templateId: string): Promise<EmailTemplate> => {
    const response = await getAPI().get(`/emails/templates/${templateId}`);
    return response.data;
  },

  createTemplate: async (data: Omit<EmailTemplate, 'id' | 'is_active' | 'created_at' | 'updated_at'>) => {
    const response = await getAPI().post('/emails/templates', data);
    return response.data;
  },

  updateTemplate: async (templateId: string, data: Partial<EmailTemplate>) => {
    const response = await getAPI().patch(`/emails/templates/${templateId}`, data);
    return response.data;
  },

  deleteTemplate: async (templateId: string) => {
    const response = await getAPI().delete(`/emails/templates/${templateId}`);
    return response.data;
  },

  sendEmail: async (data: SendEmailRequest) => {
    const response = await getAPI().post('/emails/send', data);
    return response.data;
  },

  sendBulkEmails: async (data: BulkSendEmailRequest): Promise<BulkSendResponse> => {
    const response = await getAPI().post('/emails/send-bulk', data);
    return response.data;
  },
};
```

### 4. Scrape Service

**`src/services/scrapeService.ts`**

```typescript
import { getAPI } from './api';

export interface ScrapeRequest {
  email_limit: number;
  domain_limit: number;
  category: string;
}

export interface ScrapeResponse {
  total_processed: number;
  successful_leads: number;
  total_emails_found: number;
  total_emails_saved: number;
  duplicates_skipped: number;
  errors: number;
  results: any[];
}

export const scrapeService = {
  scrapeToDatabase: async (data: ScrapeRequest): Promise<ScrapeResponse> => {
    const response = await getAPI().post('/scrape/scrape-to-db', data);
    return response.data;
  },
};
```

### 5. Profile Service

**`src/services/profileService.ts`**

```typescript
import { getAPI } from './api';

export interface ProfileRequest {
  business_name: string;
  company_id: string;
  phone?: string;
  website?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  industry?: string;
  company_size?: string;
  description?: string;
  logo_url?: string;
}

export const profileService = {
  createOrUpdateProfile: async (data: ProfileRequest) => {
    const response = await getAPI().post('/auth/profile', data);
    return response.data;
  },

  getProfile: async () => {
    const response = await getAPI().get('/auth/profile');
    return response.data;
  },

  getUserWithProfile: async () => {
    const response = await getAPI().get('/auth/profile/full');
    return response.data;
  },
};
```

---

## Authentication Flow

### Authentication Store (Zustand)

**`src/store/authStore.ts`**

```typescript
import { create } from 'zustand';
import { authService } from '../services/authService';
import { SignUpRequest, LoginRequest } from '../types/auth';

interface User {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  signup: (data: SignUpRequest) => Promise<void>;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  loadUserFromStorage: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  isLoading: false,
  error: null,

  signup: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await authService.signup(data);
      localStorage.setItem('access_token', result.access_token);
      set({ user: result.user, token: result.access_token, isLoading: false });
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Signup failed', isLoading: false });
      throw error;
    }
  },

  login: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await authService.login(data);
      localStorage.setItem('access_token', result.access_token);
      set({ user: result.user, token: result.access_token, isLoading: false });
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Login failed', isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, token: null });
  },

  clearError: () => set({ error: null }),

  loadUserFromStorage: () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      set({ token });
    }
  },

  setUser: (user) => set({ user }),
}));
```

### useAuth Hook

**`src/hooks/useAuth.ts`**

```typescript
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

export const useAuth = () => {
  const { user, token, isLoading, error, signup, login, logout, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleSignup = async (name: string, email: string, password: string) => {
    try {
      await signup({ name, email, password });
      navigate('/dashboard');
    } catch {
      // Error handled in store
    }
  };

  const handleLogin = async (email: string, password: string) => {
    try {
      await login({ email, password });
      navigate('/dashboard');
    } catch {
      // Error handled in store
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated: !!token,
    handleSignup,
    handleLogin,
    handleLogout,
    clearError,
  };
};
```

---

## Component Architecture

### 1. Protected Route Component

**`src/components/ProtectedRoute.tsx`**

```typescript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface ProtectedRouteProps {
  element: React.ReactElement;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ element }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? element : <Navigate to="/login" />;
};
```

### 2. Login Form Component

**`src/components/Auth/LoginForm.tsx`**

```typescript
import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import toast from 'react-hot-toast';

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { handleLogin, isLoading, error } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await handleLogin(email, password);
      toast.success('Login successful!');
    } catch {
      toast.error(error || 'Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg"
          required
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? 'Logging in...' : 'Login'}
      </button>

      {error && <p className="text-red-600">{error}</p>}
    </form>
  );
};
```

### 3. Email List Component

**`src/components/Email/EmailList.tsx`**

```typescript
import React, { useEffect, useState } from 'react';
import { emailService } from '../../services/emailService';
import toast from 'react-hot-toast';

export const EmailList: React.FC = () => {
  const [emails, setEmails] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchEmails();
  }, []);

  const fetchEmails = async () => {
    try {
      const result = await emailService.getAllEmails();
      setEmails(result.emails);
      setTotal(result.total);
    } catch (error) {
      toast.error('Failed to fetch emails');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const csv = emails.join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'emails.csv';
    a.click();
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Emails ({total})</h2>
        <button
          onClick={handleExport}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
        >
          Export CSV
        </button>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {emails.map((email, idx) => (
          <div key={idx} className="p-2 bg-gray-50 rounded">
            {email}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 4. Send Bulk Email Component

**`src/components/Email/BulkSendEmail.tsx`**

```typescript
import React, { useState, useEffect } from 'react';
import { emailService } from '../../services/emailService';
import { scrapeService } from '../../services/scrapeService';
import toast from 'react-hot-toast';

export const BulkSendEmail: React.FC = () => {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [emails, setEmails] = useState<string[]>([]);
  const [variables, setVariables] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    fetchTemplates();
    fetchEmails();
  }, []);

  const fetchTemplates = async () => {
    try {
      const data = await emailService.getTemplates();
      setTemplates(data);
      if (data.length > 0) setSelectedTemplate(data[0].id);
    } catch (error) {
      toast.error('Failed to fetch templates');
    }
  };

  const fetchEmails = async () => {
    try {
      const { emails: emailList } = await emailService.getAllEmails();
      setEmails(emailList);
    } catch (error) {
      toast.error('Failed to fetch emails');
    }
  };

  const handleSend = async () => {
    if (!selectedTemplate || emails.length === 0) {
      toast.error('Please select a template and have emails available');
      return;
    }

    setLoading(true);
    try {
      const response = await emailService.sendBulkEmails({
        recipient_emails: emails,
        template_id: selectedTemplate,
        variables: Object.keys(variables).length > 0 ? variables : undefined,
      });

      setResult(response);
      toast.success(`Sent to ${response.successful} recipients`);
    } catch (error) {
      toast.error('Failed to send emails');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow space-y-4">
      <h2 className="text-2xl font-bold">Send Bulk Email</h2>

      {/* Template Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">Template</label>
        <select
          value={selectedTemplate}
          onChange={(e) => setSelectedTemplate(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg"
        >
          {templates.map((t: any) => (
            <option key={t.id} value={t.id}>
              {t.name} ({t.template_type})
            </option>
          ))}
        </select>
      </div>

      {/* Recipients Summary */}
      <div className="bg-blue-50 p-4 rounded">
        <p className="font-semibold">Recipients: {emails.length} emails</p>
      </div>

      {/* Variables Input */}
      <div>
        <label className="block text-sm font-medium mb-2">Variables (JSON)</label>
        <textarea
          value={JSON.stringify(variables, null, 2)}
          onChange={(e) => setVariables(JSON.parse(e.target.value || '{}'))}
          className="w-full px-4 py-2 border rounded-lg font-mono"
          rows={4}
        />
      </div>

      {/* Send Button */}
      <button
        onClick={handleSend}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Sending...' : 'Send Emails'}
      </button>

      {/* Results */}
      {result && (
        <div className="bg-green-50 p-4 rounded">
          <p>✓ Successful: {result.successful}/{result.total_recipients}</p>
          <p>✗ Failed: {result.failed}</p>
        </div>
      )}
    </div>
  );
};
```

### 5. Scrape Form Component

**`src/components/Scrape/ScrapeForm.tsx`**

```typescript
import React, { useState } from 'react';
import { scrapeService } from '../../services/scrapeService';
import toast from 'react-hot-toast';

export const ScrapeForm: React.FC = () => {
  const [emailLimit, setEmailLimit] = useState(1000);
  const [domainLimit, setDomainLimit] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState(0);

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setProgress(0);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + Math.random() * 30, 90));
      }, 1000);

      const response = await scrapeService.scrapeToDatabase({
        email_limit: emailLimit,
        domain_limit: domainLimit,
        category: 'WEB',
      });

      clearInterval(progressInterval);
      setProgress(100);
      setResult(response);
      toast.success('Scraping completed!');
    } catch (error) {
      toast.error('Scraping failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow space-y-4">
      <h2 className="text-2xl font-bold">Scrape UK Domains</h2>

      <form onSubmit={handleScrape} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Email Limit: {emailLimit}
          </label>
          <input
            type="range"
            min="100"
            max="10000"
            step="100"
            value={emailLimit}
            onChange={(e) => setEmailLimit(parseInt(e.target.value))}
            className="w-full"
            disabled={loading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Domain Limit: {domainLimit}
          </label>
          <input
            type="range"
            min="10"
            max="1000"
            step="10"
            value={domainLimit}
            onChange={(e) => setDomainLimit(parseInt(e.target.value))}
            className="w-full"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? `Scraping... ${Math.round(progress)}%` : 'Start Scraping'}
        </button>
      </form>

      {/* Progress Bar */}
      {loading && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-green-50 p-4 rounded space-y-2">
          <h3 className="font-bold">Results</h3>
          <p>Domains Processed: {result.total_processed}</p>
          <p>Emails Found: {result.total_emails_found}</p>
          <p>Emails Saved: {result.total_emails_saved}</p>
          <p>Duplicates: {result.duplicates_skipped}</p>
        </div>
      )}
    </div>
  );
};
```

---

## Pages & Features

### Dashboard Page Structure

```typescript
// src/pages/DashboardPage.tsx
import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { Stats } from '../components/Dashboard/Stats';
import { EmailList } from '../components/Email/EmailList';
import { BulkSendEmail } from '../components/Email/BulkSendEmail';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Welcome, {user?.name}!</h1>
      <Stats />
      <div className="grid grid-cols-2 gap-6">
        <EmailList />
        <BulkSendEmail />
      </div>
    </div>
  );
};
```

---

## State Management

### UI Store (Theme, Sidebar, Modals)

**`src/store/uiStore.ts`**

```typescript
import { create } from 'zustand';

interface UIStore {
  sidebarOpen: boolean;
  darkMode: boolean;
  activeModal: string | null;

  toggleSidebar: () => void;
  toggleDarkMode: () => void;
  openModal: (modal: string) => void;
  closeModal: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  darkMode: false,
  activeModal: null,

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
  openModal: (modal) => set({ activeModal: modal }),
  closeModal: () => set({ activeModal: null }),
}));
```

---

## Form Handling

### useFormValidation Hook

**`src/hooks/useFormValidation.ts`**

```typescript
import { useState } from 'react';

interface FormErrors {
  [key: string]: string;
}

export const useFormValidation = <T extends Record<string, any>>(
  initialValues: T,
  onSubmit: (values: T) => Promise<void>
) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await onSubmit(values);
    } catch (error: any) {
      if (error.response?.data?.detail) {
        setErrors({ submit: error.response.data.detail });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setValues(initialValues);
    setErrors({});
  };

  return {
    values,
    errors,
    isSubmitting,
    handleChange,
    handleSubmit,
    resetForm,
    setValues,
  };
};
```

---

## Error Handling

### Global Error Boundary

**`src/components/ErrorBoundary.tsx`**

```typescript
import React, { ReactNode, ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 bg-red-50 rounded-lg">
          <h1 className="text-2xl font-bold text-red-600">Something went wrong</h1>
          <p className="text-red-500">{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## Environment Variables

Create `.env.local`:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

---

## Building & Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm install -g netlify-cli
netlify deploy
```

---

## Testing Components

```typescript
// Example with React Testing Library
import { render, screen } from '@testing-library/react';
import { LoginForm } from './LoginForm';

test('renders login form', () => {
  render(<LoginForm />);
  expect(screen.getByText(/login/i)).toBeInTheDocument();
});
```

---

## Performance Optimization

1. **Code Splitting**: Use `React.lazy()` for route-based code splitting
2. **Memoization**: Use `React.memo()` for expensive components
3. **Virtualization**: Use `react-virtual` for long email lists
4. **Image Optimization**: Use optimized images and lazy loading
5. **Caching**: Implement cache-first strategy with service workers

---

## Security Best Practices

1. ✅ Store JWT in localStorage (or sessionStorage for better security)
2. ✅ Validate all user inputs
3. ✅ Use HTTPS in production
4. ✅ Implement CSRF protection
5. ✅ Sanitize HTML content with DOMPurify
6. ✅ Never log sensitive data
7. ✅ Implement rate limiting on client side

---

**Last Updated:** March 28, 2026
**Recommended Node Version:** 16+
**Recommended React Version:** 18+
