import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StepNavbar from '../components/StepNavbar';
import api from '../api';

export default function Report() {
  const navigate = useNavigate();
  const sessionId = localStorage.getItem('session_id');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) { navigate('/upload'); return; }
    api.get(`/interview/report/${sessionId}`)
      .then(r => setData(r.data))
      .catch(e => setError(e.response?.data?.detail || 'Failed to load report'))
      .finally(() => setLoading(false));
  }, [navigate, sessionId]);

  const startOver = () => {
    localStorage.removeItem('session_id');
    localStorage.removeItem('target_role');
    navigate('/upload');
  };

  const scoreColor = (s: number) =>
    s >= 70 ? 'text-green-400' : s >= 50 ? 'text-yellow-400' : 'text-red-400';

  const scoreBg = (s: number) =>
    s >= 70 ? 'bg-green-500' : s >= 50 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="min-h-screen bg-[#0f1117]">
      <StepNavbar current={4} />
      <div className="max-w-3xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-white mb-2">Final Report</h1>
        <p className="text-slate-400 mb-8">Your career readiness summary</p>

        {error && <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg mb-6 text-sm">{error}</div>}

        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin text-4xl mb-4">📊</div>
            <p className="text-slate-400">Generating your report...</p>
          </div>
        ) : data && (
          <>
            {/* Readiness Score */}
            <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-8 mb-6 text-center">
              <div className="text-slate-400 text-sm mb-2">Overall Readiness Score</div>
              <div className={`text-7xl font-bold mb-2 ${scoreColor(data.readiness_score)}`}>
                {data.readiness_score}
              </div>
              <div className="text-slate-400 text-sm">out of 100</div>

              {/* Score bars */}
              <div className="mt-8 space-y-3 text-left">
                {[
                  { label: 'Quiz Score', value: data.quiz_score },
                  { label: 'Interview Average', value: (data.interview_avg || 0) * 10 },
                ].map(bar => (
                  <div key={bar.label}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-400">{bar.label}</span>
                      <span className="text-white">{Math.round(bar.value)}%</span>
                    </div>
                    <div className="h-2 bg-[#2d3148] rounded-full">
                      <div className={`h-full rounded-full ${scoreBg(bar.value)}`} style={{ width: `${bar.value}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Target role */}
            <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-5 mb-6">
              <span className="text-slate-400 text-sm">Target Role: </span>
              <span className="text-blue-400 font-medium">{data.target_role}</span>
            </div>

            {/* Strengths */}
            {data.strengths?.length > 0 && (
              <div className="bg-[#1a1d27] border border-green-700/40 rounded-xl p-6 mb-4">
                <h3 className="text-green-400 font-semibold mb-3">💪 Strengths</h3>
                <ul className="space-y-2">
                  {data.strengths.map((s: string, i: number) => (
                    <li key={i} className="text-slate-300 text-sm flex gap-2">
                      <span className="text-green-400 mt-0.5">✓</span>{s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improvements */}
            {data.improvements?.length > 0 && (
              <div className="bg-[#1a1d27] border border-yellow-700/40 rounded-xl p-6 mb-4">
                <h3 className="text-yellow-400 font-semibold mb-3">📈 Areas to Improve</h3>
                <ul className="space-y-2">
                  {data.improvements.map((s: string, i: number) => (
                    <li key={i} className="text-slate-300 text-sm flex gap-2">
                      <span className="text-yellow-400 mt-0.5">→</span>{s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Next steps */}
            {data.next_steps?.length > 0 && (
              <div className="bg-[#1a1d27] border border-blue-700/40 rounded-xl p-6 mb-8">
                <h3 className="text-blue-400 font-semibold mb-3">🚀 Next Steps</h3>
                <ul className="space-y-3">
                  {data.next_steps.map((step: any, i: number) => (
                    <li key={i} className="text-slate-300 text-sm">
                      <span className="text-blue-400 font-medium">{i + 1}. {step.action || step}</span>
                      {step.why && <div className="text-slate-500 text-xs mt-0.5">{step.why}</div>}
                      {step.resource && (
                        <div className="text-blue-300 text-xs mt-0.5">📚 {step.resource}</div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex gap-4">
              <button
                onClick={startOver}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition"
              >
                Start New Session
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="flex-1 border border-[#2d3148] text-slate-300 hover:text-white font-medium py-3 rounded-xl transition"
              >
                Dashboard
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}