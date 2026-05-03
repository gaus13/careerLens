import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StepNavbar from '../components/StepNavbar';
import api from '../api';

export default function Gaps() {
  const navigate = useNavigate();
  const sessionId = localStorage.getItem('session_id');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) { navigate('/upload'); return; }
    api.post(`/gaps/analyse/${sessionId}`)
      .then(r => setData(r.data))
      .catch(e => setError(e.response?.data?.detail || 'Analysis failed'))
      .finally(() => setLoading(false));
  }, [navigate, sessionId]);

  const priorityColor = (p: string) => {
    if (!p) return 'text-slate-400 bg-slate-800';
    const l = p.toLowerCase();
    if (l === 'high') return 'text-red-400 bg-red-900/30';
    if (l === 'medium') return 'text-yellow-400 bg-yellow-900/30';
    return 'text-green-400 bg-green-900/30';
  };

  return (
    <div className="min-h-screen bg-[#0f1117]">
      <StepNavbar current={2} />
      <div className="max-w-5xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-white mb-2">Gap Analysis</h1>
        <p className="text-slate-400 mb-8">
          Target role: <span className="text-blue-400 font-medium">{localStorage.getItem('target_role') || '—'}</span>
        </p>

        {error && <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg mb-6 text-sm">{error}</div>}

        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin text-4xl mb-4">🔍</div>
            <p className="text-slate-400">Comparing your skills against the role... (~15 seconds)</p>
          </div>
        ) : data && (
          <>
            {/* Readiness score */}
            <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-6 mb-6 flex items-center gap-6">
              <div className="text-center">
                <div className={`text-5xl font-bold ${
                  data.readiness_percentage >= 70 ? 'text-green-400' :
                  data.readiness_percentage >= 45 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {data.readiness_percentage}%
                </div>
                <div className="text-slate-400 text-sm mt-1">Readiness</div>
              </div>
              <div className="flex-1">
                <div className="h-3 bg-[#2d3148] rounded-full">
                  <div className={`h-full rounded-full transition-all ${
                    data.readiness_percentage >= 70 ? 'bg-green-500' :
                    data.readiness_percentage >= 45 ? 'bg-yellow-500' : 'bg-red-500'}`}
                    style={{ width: `${data.readiness_percentage}%` }} />
                </div>
                <p className="text-slate-400 text-sm mt-2">{data.score_explanation || data.readiness_label}</p>
                <p className="text-slate-500 text-sm mt-1">
                  Estimated time to job-ready: <span className="text-white">{data.estimated_weeks_to_ready} weeks</span>
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Matched skills */}
              <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-6">
                <h3 className="text-white font-semibold mb-4">✅ Skills you have</h3>
                <div className="space-y-3">
                  {(data.matched_skills || []).map((s: any) => (
                    <div key={s.skill} className="flex items-center justify-between">
                      <span className="text-slate-300 text-sm">{s.skill}</span>
                      <span className="text-green-400 text-xs bg-green-900/30 px-2 py-0.5 rounded-full">{s.proficiency}</span>
                    </div>
                  ))}
                  {(!data.matched_skills || data.matched_skills.length === 0) && (
                    <p className="text-slate-500 text-sm">No strong matches found</p>
                  )}
                </div>
              </div>

              {/* Missing skills */}
              <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-6">
                <h3 className="text-white font-semibold mb-4">⚠️ Skills to learn</h3>
                <div className="space-y-3">
                  {(data.missing_skills || []).map((s: any) => (
                    <div key={s.skill} className="flex items-center justify-between">
                      <div>
                        <span className="text-slate-300 text-sm">{s.skill}</span>
                        {s.learn_weeks && <span className="text-slate-500 text-xs ml-2">~{s.learn_weeks}w</span>}
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${priorityColor(s.priority)}`}>{s.priority}</span>
                    </div>
                  ))}
                  {(!data.missing_skills || data.missing_skills.length === 0) && (
                    <p className="text-slate-500 text-sm">No major gaps found!</p>
                  )}
                </div>
              </div>
            </div>

            {/* Roadmap */}
            {data.roadmap && data.roadmap.length > 0 && (
              <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-6 mb-8">
                <h3 className="text-white font-semibold mb-4">📅 Learning Roadmap</h3>
                <div className="space-y-3">
                  {data.roadmap.map((r: any, i: number) => (
                    <div key={i} className="flex gap-4 items-start">
                      <div className="text-blue-400 font-medium text-sm w-16 shrink-0">
                        {r.week_range || `Week ${i + 1}`}
                      </div>
                      <div>
                        <div className="text-white text-sm font-medium">{r.focus}</div>
                        {r.goal && <div className="text-slate-400 text-xs mt-0.5">{r.goal}</div>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => navigate('/quiz')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition"
            >
              Test Your Knowledge →
            </button>
          </>
        )}
      </div>
    </div>
  );
}