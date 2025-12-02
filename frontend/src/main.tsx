import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Strict Mode disabled to prevent flickering in Chrome during development
// Re-enable for production builds if needed
ReactDOM.createRoot(document.getElementById('root')!).render(
  <App />
)
