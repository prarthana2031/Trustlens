# TrustLens Frontend File Structure

## 📁 Root Directory
```
trustlens-frontend/
├── 📄 .env                    # Environment variables
├── 📄 .env.example           # Environment variables template
├── 📄 .eslintrc.json         # ESLint configuration
├── 📄 .stylelintrc.json      # Stylelint configuration
├── 📁 .vite/                 # Vite build cache
├── 📄 Dockerfile             # Docker container configuration
├── 📁 FRONT/                 # Frontend assets
├── 📄 index.html             # Main HTML entry point
├── 📄 nginx.conf             # Nginx configuration
├── 📄 package-lock.json      # Dependency lock file
├── 📄 package.json           # Project metadata and scripts
├── 📄 postcss.config.js      # PostCSS configuration
├── 📁 src/                   # Source code
├── 📄 tailwind.config.cjs    # Tailwind CSS config (CommonJS)
├── 📄 tailwind.config.js     # Tailwind CSS config (ES Module)
├── 📄 tailwind.config.ts     # Tailwind CSS config (TypeScript)
├── 📄 tsconfig.json          # TypeScript configuration
├── 📄 tsconfig.node.json     # TypeScript config for Node.js
└── 📄 vite.config.ts         # Vite build configuration
```

## 📁 Source Code Structure (`src/`)
```
src/
├── 📄 App.css                # Global application styles
├── 📄 App.tsx                # Main application component
├── 📁 assets/                # Static assets
│   ├── 🖼️ images/            # Image files
│   └── 🎨 icons/             # Icon files
├── 📁 components/            # Reusable UI components
│   ├── 📁 common/            # Common components
│   │   ├── 📄 CandidateStatusBadge.tsx
│   │   ├── 📄 EmptyState.tsx
│   │   ├── 📄 Header.tsx
│   │   ├── 📄 LoadingSpinner.tsx
│   │   ├── 📄 Sidebar.tsx
│   │   └── 📄 Skeleton.tsx
│   ├── 📁 bias/              # Bias analysis components
│   │   └── 📄 BiasMetricsCard.tsx
│   ├── 📁 enhancement/       # AI enhancement components
│   │   └── 📄 EnhancementPanel.tsx
│   ├── 📁 feedback/          # Feedback components
│   │   └── 📄 FeedbackForm.tsx
│   ├── 📁 screening/         # Screening components
│   │   └── 📄 FairnessReport.tsx
│   └── 📁 scoring/           # Scoring components
│       └── 📄 ScoreChart.tsx
├── 📁 hooks/                 # Custom React hooks
│   ├── 📄 useAuth.ts          # Authentication hook
│   ├── 📄 useBias.ts          # Bias analysis hooks
│   ├── 📄 useCandidates.ts    # Candidate management hooks
│   ├── 📄 useCompleteScreening.ts
│   ├── 📄 useFeedback.ts      # Feedback hooks
│   ├── 📄 useScores.ts        # Scoring hooks
│   ├── 📄 useScreening.ts     # Screening hooks
│   └── 📄 useAuth.ts          # Authentication hook
├── 📄 index.css              # Global styles
├── 📄 main.tsx               # Application entry point
├── 📁 pages/                 # Page components
│   ├── 📄 BiasAnalysisPage.tsx
│   ├── 📄 CandidateDetailPage.tsx
│   ├── 📄 CandidatesPage.tsx
│   ├── 📄 Dashboard.tsx
│   ├── 📄 ReportsPage.tsx
│   ├── 📄 ScreeningPage.tsx
│   ├── 📄 SettingsPage.tsx
│   └── 📄 UploadPage.tsx
├── 📁 services/              # API services
│   ├── 📄 api.ts              # Axios API client
│   ├── 📄 biasService.ts      # Bias analysis service
│   ├── 📄 candidateService.ts # Candidate management service
│   ├── 📄 completeMockBackend.ts
│   ├── 📄 firebaseConfig.ts   # Firebase configuration
│   ├── 📄 mockBackend.ts      # Mock backend for development
│   ├── 📄 scoringService.ts   # Scoring service
│   ├── 📄 screeningService.ts # Screening service
│   ├── 📄 tempMockEnhancement.ts
│   └── 📄 tempMockProcessing.ts
├── 📁 store/                 # State management
│   ├── 📄 authStore.ts        # Authentication state
│   ├── 📄 queryKeys.ts        # React Query keys
│   └── 📄 uiStore.ts          # UI state management
├── 📁 styles/                # Style files
│   ├── 📄 globals.css         # Global CSS styles
│   └── 📄 components.css      # Component-specific styles
├── 📁 types/                 # TypeScript type definitions
│   ├── 📄 api.ts              # API response types
│   ├── 📄 bias.ts             # Bias analysis types
│   ├── 📄 candidate.ts        # Candidate types
│   ├── 📄 feedback.ts         # Feedback types
│   ├── 📄 screening.ts        # Screening types
│   └── 📄 score.ts            # Scoring types
├── 📁 utils/                 # Utility functions
│   ├── 📄 cn.ts               # Class name utility
│   ├── 📄 debounce.ts         # Debounce function
│   ├── 📄 downloadFile.ts     # File download utility
│   ├── 📄 format.ts           # Formatting utilities
│   ├── 📄 validation.ts      # Form validation
│   └── 📄 constants.ts        # Application constants
└── 📄 vite-env.d.ts          # Vite environment types
```

## 🔧 Key Configuration Files

### 📄 `package.json` - Dependencies & Scripts
```json
{
  "name": "trustlens-frontend",
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "@tanstack/react-query": "^4.24.0",
    "react-hot-toast": "^2.4.0",
    "firebase": "^9.6.0",
    "recharts": "^2.5.0",
    "lucide-react": "^0.263.0"
  }
}
```

### 📄 `vite.config.ts` - Build Configuration
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'https://resume-backend-948277799081.us-central1.run.app',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
        secure: false,
      },
    },
  },
})
```

### 📄 `tsconfig.json` - TypeScript Configuration
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

## 🚀 Application Flow

### 📱 Pages & Routes
1. **`/` - Dashboard** - Main candidate overview
2. **`/upload` - Upload** - Resume upload interface
3. **`/candidate/:id` - Candidate Detail** - Individual candidate analysis
4. **`/reports` - Reports** - Analytics and exports
5. **`/bias-analysis` - Bias Analysis** - Fairness metrics
6. **`/settings` - Settings** - Configuration

### 🔄 Data Flow
```
Upload → Process → Enhance → Analyze → Report
   ↓        ↓         ↓         ↓        ↓
Candidate → Score → AI Bias → Metrics → Export
```

### 🛠️ Service Architecture
```
Components → Hooks → Services → API
    ↓         ↓        ↓       ↓
   UI     State    Logic   Backend
```

## 📊 Key Features

### ✅ **Implemented Features**
- 🔐 Firebase Authentication
- 📤 Resume Upload (Single & Batch)
- 🎯 Candidate Processing
- 🤖 AI Enhancement (Gemini)
- 📊 Score Visualization
- ⚖️ Bias Analysis
- 📈 Reports & Analytics
- 📱 Responsive Design

### 🔧 **Technical Stack**
- **Frontend**: React 18 + TypeScript
- **Routing**: React Router v6
- **State**: Zustand + React Query
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **API**: Axios
- **Auth**: Firebase
- **Build**: Vite

---

*Generated on: $(date)*
*Total Files: 94+ files across src/ directory*
