import { useNavigate } from 'react-router-dom';

const steps = [
  { label: 'Upload', path: '/upload' },
  { label: 'Careers', path: '/careers' },
  { label: 'Gaps', path: '/gaps' },
  { label: 'Quiz', path: '/quiz' },
  { label: 'Interview', path: '/interview' },
];

export default function StepNavbar({ current }: { current: number }) {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('session_id');
    localStorage.removeItem('target_role');
    navigate('/login', { replace: true });
  };

  return (
    <nav className="bg-[#1a1d27] border-b border-[#2d3148] px-6 py-3 flex items-center justify-between">
      {/* Logo */}
      <span className="text-blue-400 font-bold text-lg tracking-wide">CareerLens</span>

      {/* Steps */}
      <div className="flex items-center gap-1">
        {steps.map((s, i) => {
          const done = i < current;
          const active = i === current;
          return (
            <div key={s.label} className="flex items-center">
              <button
                onClick={() => done && navigate(s.path)}
                className={`px-3 py-1 rounded text-sm font-medium transition
                  ${active ? 'bg-blue-600 text-white' : ''}
                  ${done ? 'text-green-400 cursor-pointer hover:text-green-300' : ''}
                  ${!active && !done ? 'text-slate-500 cursor-default' : ''}
                `}
              >
                {done ? '✓ ' : ''}{s.label}
              </button>
              {i < steps.length - 1 && (
                <span className="text-slate-600 mx-1">→</span>
              )}
            </div>
          );
        })}
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/dashboard')} className="text-slate-400 hover:text-white text-sm">
          Dashboard
        </button>
        <button onClick={logout} className="text-red-400 hover:text-red-300 text-sm">
          Logout
        </button>
      </div>
    </nav>
  );
}