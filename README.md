# TrustLens - Fairness AI Recruitment Platform

An AI-powered recruitment platform that promotes fair and unbiased hiring decisions through resume screening, bias analysis, and candidate evaluation.

## 🌟 Features

- **Resume Upload**: Single and batch resume upload with automatic parsing
- **AI-Powered Screening**: Intelligent candidate evaluation based on job requirements
- **Bias Analysis**: Detect and mitigate unconscious bias in hiring decisions
- **Candidate Dashboard**: View and manage all candidates with detailed analytics
- **Reports & Analytics**: Comprehensive reporting on hiring metrics and fairness scores

## 🏗️ Architecture

### Frontend (trustlens-frontend/)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query + Zustand
- **UI Components**: Custom component library

### Backend
- **API**: RESTful API running on Google Cloud Run
- **URL**: `https://resume-backend-948277799081.us-central1.run.app`
- **Storage**: Supabase for resume storage
- **Authentication**: Firebase Auth

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd TrustLens
```

2. **Install dependencies**:
```bash
cd trustlens-frontend
npm install
```

3. **Set up environment variables**:
Create a `.env` file in the `trustlens-frontend` directory:
```env
VITE_API_BASE_URL=https://resume-backend-948277799081.us-central1.run.app
```

4. **Start the development server**:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 📡 API Configuration

The frontend is configured to connect to the deployed backend:

**Development**: Uses Vite proxy (`/api`) to avoid CORS issues
**Production**: Direct connection to backend URL

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload single resume |
| `/api/upload/batch` | POST | Upload multiple resumes |
| `/api/candidates` | GET | Get all candidates |
| `/api/candidates/:id` | GET | Get candidate details |
| `/api/candidates/:id/status` | GET | Get candidate screening status |
| `/api/screen` | POST | Start screening session |
| `/api/bias/metrics` | GET | Get bias analysis metrics |

## 🔧 Configuration

### Backend Connection

The API client (`src/services/api.ts`) is configured to:
- Use proxy in development (`/api`)
- Use direct backend URL in production
- Handle CORS with `withCredentials: false`
- Support FormData for file uploads

### Vite Proxy Configuration

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'https://resume-backend-948277799081.us-central1.run.app',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
    secure: false,
  },
}
```

## 📂 Project Structure

```
TrustLens/
├── trustlens-frontend/     # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services and utilities
│   │   ├── hooks/          # Custom React hooks
│   │   ├── types/          # TypeScript type definitions
│   │   └── styles/         # Global styles
│   ├── public/             # Static assets
│   └── dist/               # Production build
├── backend/                # Backend API (deployed on Cloud Run)
└── README.md               # This file
```

## 🧪 Development

### Running in Development Mode
```bash
npm run dev
```

### Building for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 🔒 Authentication

The application uses Firebase Authentication:
- Users must be authenticated to access the platform
- Auth tokens are automatically included in API requests
- Fallback to mock authentication in development (if Firebase config is missing)

## 📊 Upload Flow

1. **User uploads resume(s)** via Upload page
2. **Frontend sends FormData** to `/api/upload` endpoint
3. **Backend processes resume** and extracts information
4. **Resume stored in Supabase** storage bucket
5. **Candidate record created** in database
6. **AI screening initiated** (if configured)

## 🐛 Troubleshooting

### Port 5173 Already in Use
```bash
# Find process using port 5173
netstat -ano | findstr :5173

# Kill the process
taskkill /F /PID <PID>
```

### CORS Errors
- Ensure backend CORS configuration includes `http://localhost:5173`
- Check that `withCredentials: false` is set in API client
- Verify Vite proxy is working in development

### Backend Connection Issues
- Check `VITE_API_BASE_URL` environment variable
- Verify backend URL is accessible: `https://resume-backend-948277799081.us-central1.run.app`
- Check browser console for detailed error messages

## 📞 Support

For issues or questions:
1. Check the browser console for error messages
2. Verify API configuration in `src/services/api.ts`
3. Ensure all environment variables are set correctly
4. Check backend status at the health endpoint

## 📝 License

[Your License Here]

---

**Note**: This is a development version. For production deployment, ensure all environment variables are properly configured and Firebase authentication is set up.