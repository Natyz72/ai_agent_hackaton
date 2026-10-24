import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { Stepper } from './Stepper';

interface AppShellProps {
  children: ReactNode;
  showStepper?: boolean;
}

export function AppShell({ children, showStepper = false }: AppShellProps) {
  const location = useLocation();
  
  // Determine current step
  const getCurrentStep = () => {
    if (location.pathname === '/') return 1;
    if (location.pathname === '/results') return 2;
    if (location.pathname === '/review') return 3;
    if (location.pathname === '/incidents' || location.pathname.startsWith('/incidents/')) return 4;
    return 0;
  };
  
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-semibold text-slate-900">Message Investigator</span>
              </div>
              <nav className="hidden sm:flex items-center gap-4">
                <Link
                  to="/"
                  className={`text-sm font-medium px-3 py-2 rounded-md min-h-[44px] flex items-center transition-colors ${
                    location.pathname === '/'
                      ? 'text-indigo-700 bg-indigo-50'
                      : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  New
                </Link>
                <Link
                  to="/incidents"
                  className={`text-sm font-medium px-3 py-2 rounded-md min-h-[44px] flex items-center transition-colors ${
                    location.pathname === '/incidents' || location.pathname.startsWith('/incidents/')
                      ? 'text-indigo-700 bg-indigo-50'
                      : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  Saved Incidents
                </Link>
              </nav>
            </div>
            <div className="text-xs text-slate-600 text-right hidden md:block">
              <div>Text-only analysis · Links are never opened · Demo, fictitious data only</div>
            </div>
          </div>
        </div>
      </header>
      
      {showStepper && (
        <div className="bg-white border-b border-slate-200">
          <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <Stepper currentStep={getCurrentStep()} />
          </div>
        </div>
      )}
      
      <main className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}
