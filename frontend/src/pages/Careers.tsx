import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StepNavbar from '../components/StepNavbar';
import api from '../api';

interface Career {
  title: string;
  fit_score: number;
  salary_range: string;
  demand: string;
  fit_rationale?: string;
  matched_skills?: string[];
  skill_gaps?: string[];
}

export default function Careers() {
  const navigate = useNavigate();
  const sessionId = localStorage.getItem('session_id');
  const [careers, setCareers] = useState<Career[]>([]);
  const [loading, setLoading] = useState(true);
  const [selecting, setSelecting] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) { navigate('/upload'); return; }
    api.post(`/careers/recommend/${sessionId}`)
      .then(r => setCareers(r.data.careers || []))
      .catch(e => setError(e.response?.data?.detail || 'Failed to get recommendations'))
      .finally(() => setLoading(false));
  }, [navigate, sessionId]);

  const select = async (title: string) => {
    setSelecting(title);
    try {
      await api.post(`/careers/select/${sessionId}`, { target_role: title });
      localStorage.setItem('target_role', title);
      navigate('/gaps');
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to select career');
      setSelecting('');
    }
  };

  const demandColor = (d: string) => {
    if (!d) return 'text-slate-400';
    const l = d.toLowerCase();
    if (l === 'high') return 'text-green-400';
    if (l === 'medium') return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-[#0f1117]">
      <StepNavbar current={1} />
      <div className="max-w-5xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-white mb-2">Career Recommendations</h1>
        <p className="text-slate-400 mb-8">Based on your resume, here are the best matches. Click one to continue.</p>

        {error && (
          <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg mb-6 text-sm">{error}</div>
        )}

        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin text-4xl mb-4">⚙️</div>
            <p className="text-slate-400">AI is analysing your resume... (~15 seconds)</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {careers.map(c => (
              <div
                key={c.title}
                className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-6 hover:border-blue-500 transition cursor-pointer"
                onClick={() => !selecting && select(c.title)}
              >
                {/* Score */}
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-white font-semibold text-lg leading-tight">{c.title}</h3>
                  <div className="text-right ml-2 shrink-0">
                    <div className={`text-2xl font-bold ${c.fit_score >= 75 ? 'text-green-400' : c.fit_score >= 55 ? 'text-yellow-400' : 'text-red-400'}`}>
                      {c.fit_score}%
                    </div>
                    <div className="text-slate-500 text-xs">fit score</div>
                  </div>
                </div>

                {/* Score bar */}
                <div className="h-1.5 bg-[#2d3148] rounded-full mb-4">
                  <div
                    className={`h-full rounded-full ${c.fit_score >= 75 ? 'bg-green-500' : c.fit_score >= 55 ? 'bg-yellow-500' : 'bg-red-500'}`}
                    style={{ width: `${c.fit_score}%` }}
                  />
                </div>

                <div className="space-y-2 text-sm text-slate-400 mb-4">
                  <div>💰 {c.salary_range}</div>
                  <div>📈 Demand: <span className={demandColor(c.demand)}>{c.demand}</span></div>
                </div>

                {c.fit_rationale && (
                  <p className="text-slate-400 text-xs mb-4 border-t border-[#2d3148] pt-3 leading-relaxed">
                    {c.fit_rationale}
                  </p>
                )}

                {c.matched_skills && c.matched_skills.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {c.matched_skills.slice(0, 3).map(s => (
                      <span key={s} className="bg-green-900/30 text-green-400 text-xs px-2 py-0.5 rounded-full">{s}</span>
                    ))}
                  </div>
                )}

                <button
                  disabled={!!selecting}
                  className="w-full mt-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white text-sm font-medium py-2 rounded-lg transition"
                >
                  {selecting === c.title ? 'Selecting...' : 'Select this career →'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}