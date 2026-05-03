import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

interface Session {
  id: number;
  target_role: string | null;
  status: string;
  created_at: string;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/resume/sessions')
      .then(r => setSessions(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const startNew = () => navigate('/upload');

  const continueSession = (s: Session) => {
    localStorage.setItem('session_id', String(s.id));
    if (!s.target_role) navigate('/careers');
    else navigate('/gaps');
  };

  const viewReport = (id: number) => {
    localStorage.setItem('session_id', String(id));
    navigate('/report');
  };

  const completed = sessions.filter(s => s.status === 'completed');
  const inProgress = sessions.filter(s => s.status !== 'completed');

  return (
    <div className="min-h-screen bg-[#0f1117]">
      {/* Top bar */}
      <nav className="bg-[#1a1d27] border-b border-[#2d3148] px-6 py-4 flex items-center justify-between">
        <span className="text-blue-400 font-bold text-lg">CareerLens</span>
        <div className="flex gap-3">
          <button
            onClick={startNew}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
          >
            + New Session
          </button>
          <button
            onClick={() => {
              localStorage.removeItem('token');
              localStorage.removeItem('session_id');
              localStorage.removeItem('target_role');
              navigate('/login', { replace: true });
            }}
            className="text-slate-400 hover:text-white text-sm px-3 py-2"
          >
            Logout
          </button>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400 mb-8">Your career preparation history</p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-10">
          {[
            { label: 'Total Sessions', value: sessions.length },
            { label: 'Completed', value: completed.length },
            { label: 'In Progress', value: inProgress.length },
          ].map(stat => (
            <div key={stat.label} className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-5 text-center">
              <div className="text-3xl font-bold text-blue-400">{stat.value}</div>
              <div className="text-slate-400 text-sm mt-1">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* In Progress */}
        {inProgress.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-3">Continue where you left off</h2>
            <div className="space-y-3">
              {inProgress.map(s => (
                <div key={s.id} className="bg-[#1a1d27] border border-yellow-700/40 rounded-xl p-5 flex items-center justify-between">
                  <div>
                    <div className="text-white font-medium">{s.target_role || 'Role not selected yet'}</div>
                    <div className="text-slate-400 text-sm mt-0.5">
                      Started {new Date(s.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <button
                    onClick={() => continueSession(s)}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
                  >
                    Continue →
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Session history */}
        <div>
          <h2 className="text-lg font-semibold text-white mb-3">Session History</h2>
          {loading ? (
            <div className="text-slate-400 text-center py-10">Loading...</div>
          ) : sessions.length === 0 ? (
            <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-10 text-center">
              <p className="text-slate-400 mb-4">No sessions yet. Upload your resume to get started.</p>
              <button
                onClick={startNew}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium transition"
              >
                Start Now
              </button>
            </div>
          ) : (
            <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#2d3148] text-left">
                    <th className="px-5 py-3 text-slate-400 text-sm font-medium">Role</th>
                    <th className="px-5 py-3 text-slate-400 text-sm font-medium">Status</th>
                    <th className="px-5 py-3 text-slate-400 text-sm font-medium">Date</th>
                    <th className="px-5 py-3 text-slate-400 text-sm font-medium">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map(s => (
                    <tr key={s.id} className="border-b border-[#2d3148] last:border-0 hover:bg-[#1f2235] transition">
                      <td className="px-5 py-4 text-white">{s.target_role || '—'}</td>
                      <td className="px-5 py-4">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium
                          ${s.status === 'completed' ? 'bg-green-900/40 text-green-400' : 'bg-yellow-900/40 text-yellow-400'}`}>
                          {s.status === 'completed' ? 'Completed' : 'In Progress'}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-slate-400 text-sm">
                        {new Date(s.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-5 py-4">
                        {s.status === 'completed' ? (
                          <button onClick={() => viewReport(s.id)} className="text-blue-400 hover:text-blue-300 text-sm">
                            View Report →
                          </button>
                        ) : (
                          <button onClick={() => continueSession(s)} className="text-yellow-400 hover:text-yellow-300 text-sm">
                            Continue →
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}