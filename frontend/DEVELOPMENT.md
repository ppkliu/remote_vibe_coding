# Frontend Development Guide

## Quick Start with Vite Dev Server

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

Using the npm script (recommended):
```bash
npm run dev
```

Or using npx directly:
```bash
npx vite dev
```

Or specifying the port:
```bash
npx vite dev --port 5173
```

### Expected Output

```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

Visit: **http://localhost:5173** in your browser

## Development Workflow

### File Structure

```
frontend/
├── src/
│   ├── components/          # Vue components
│   ├── views/              # Page components
│   ├── stores/             # Pinia state management
│   ├── api/                # API service calls
│   ├── App.vue             # Root component
│   └── main.ts             # Entry point
├── tests/                  # Unit and integration tests
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
└── tailwind.config.js      # TailwindCSS configuration
```

### Hot Module Replacement (HMR)

Vite automatically updates your browser when you modify:
- Vue components (`.vue`)
- TypeScript/JavaScript files (`.ts`, `.js`)
- Stylesheets (`.css`)
- Template changes

**No need to manually refresh!** Changes appear instantly.

### Common Tasks

#### Code Style & Linting

```bash
# Fix code style issues
npm run lint

# Check TypeScript types (no emit)
npm run type-check
```

#### Run Tests

```bash
# Run all tests
npm run test

# Run tests in UI mode (interactive)
npm run test:ui

# Run tests in watch mode
npm run test -- --watch
```

#### Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build locally
npm run preview
```

## Backend Integration

### API Proxy Configuration

Vite is configured to proxy API calls to the backend:

- **REST API**: `http://localhost:8000/api/v1`
- **WebSocket**: `ws://localhost:8000/ws`

This is configured in `vite.config.ts`:

```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
    '/ws': {
      target: 'ws://localhost:8000',
      ws: true,
    }
  }
}
```

### Environment Variables

Create a `.env` file in the frontend directory (copy from `.env.example`):

```bash
# Backend API endpoint
VITE_API_URL=http://localhost:8000/api/v1

# WebSocket endpoint
VITE_WS_URL=ws://localhost:8000/ws
```

Access in components:

```typescript
const apiUrl = import.meta.env.VITE_API_URL
const wsUrl = import.meta.env.VITE_WS_URL
```

## Development Tips

### 1. Using Vue DevTools

Install the Vue.js DevTools browser extension for better debugging:
- Chrome: https://chrome.google.com/webstore
- Firefox: https://addons.mozilla.org/firefox/
- Search for "Vue.js devtools"

### 2. Debug API Calls

Open DevTools (F12) → Network tab:
- Check all requests to `/api/v1/...`
- Verify request/response payloads
- Check CORS headers

### 3. State Management (Pinia)

The app uses Pinia for state management. Debug stores:
- Vue DevTools → Pinia tab
- Monitor state changes in real-time
- Time-travel debugging available

### 4. Component Structure

Vue 3 Composition API example:

```vue
<template>
  <div class="container">
    <h1>{{ message }}</h1>
    <button @click="increment">Count: {{ count }}</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const message = ref('Hello Vue 3')
const count = ref(0)

const increment = () => {
  count.value++
}
</script>

<style scoped>
.container {
  padding: 2rem;
}
</style>
```

## Troubleshooting

### Port Already in Use

If port 5173 is already in use:

```bash
# Use a different port
npx vite dev --port 5174

# Or find and kill the process on port 5173
lsof -i :5173
kill -9 <PID>
```

### CORS Errors

If you see CORS errors:
1. Ensure backend is running on `http://localhost:8000`
2. Check `CORS_ORIGINS` in `backend/.env` includes `http://localhost:5173`
3. Clear browser cache and restart dev server

### WebSocket Connection Fails

WebSocket errors when connecting to backend:
1. Ensure backend WebSocket is available
2. Check `VITE_WS_URL` in `.env` is correct
3. Backend must be running before creating a session

### Module Not Found

If you see "Module not found" errors:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Restart dev server
npm run dev
```

## Complete Development Setup

### Terminal 1: Backend

```bash
cd backend
uvicorn src.main:app --reload
```

Backend runs on: **http://localhost:8000**

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
# or
npx vite dev
```

Frontend runs on: **http://localhost:5173**

### Terminal 3: Optional - Run Tests

```bash
cd frontend
npm run test:ui
```

Then visit: **http://localhost:51204** (Vitest UI)

## Further Reading

- **Vite Docs**: https://vitejs.dev/
- **Vue 3 Docs**: https://vuejs.org/
- **Pinia Docs**: https://pinia.vuejs.org/
- **TailwindCSS Docs**: https://tailwindcss.com/
- **TypeScript Docs**: https://www.typescriptlang.org/
