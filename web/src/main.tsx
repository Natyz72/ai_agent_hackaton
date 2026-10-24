import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './styles/index.css'
import { InvestigationProvider } from './state/InvestigationContext.tsx'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <InvestigationProvider>
      <App />
    </InvestigationProvider>
  </React.StrictMode>,
)
