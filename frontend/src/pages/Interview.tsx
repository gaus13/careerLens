import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StepNavbar from '../components/StepNavbar';
import api from '../api';

const QUESTIONS = [
  'Tell me about yourself and your background.',
  'Why do you want to work in this role?',
  'What is your strongest technical skill and give an example of using it?',
  'Describe a challenging project you worked on.',
  'How do you handle tight deadlines?',
  'Where do you see yourself in 3 years?',
  'What do you know about current trends in this field?',
  'Do you have any questions for us?',
];

interface Message {
  role: 'ai' | 'user';
  content: string;
  feedback?: any;
}

export default function Interview() {
  const navigate = useNavigate();
  const sessionId = localStorage.getItem('session_id');
  const role = localStorage.getItem('target_role') || 'the role';
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', content: `Welcome to your mock interview for ${role}. I'll ask you ${QUESTIONS.length} questions. Take your time and answer clearly. Let's begin:\n\n${QUESTIONS[0]}` }
  ]);
  const [answer, setAnswer] = useState('');
  const [qIndex, setQIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [scores, setScores] = useState<number[]>([]);

  const submit = async () => {
    if (!answer.trim() || loading) return;
    const userAnswer = answer.trim();
    setAnswer('');
    setMessages(prev => [...prev, { role: 'user', content: userAnswer }]);
    setLoading(true);

    try {
      const res = await api.post('/interview/evaluate', {
        question: QUESTIONS[qIndex],
        answer: userAnswer,
        session_id: Number(sessionId),
      });
      const fb = res.data;
      setScores(prev => [...prev, fb.score || 0]);

      const nextQ = qIndex + 1;
      const feedbackMsg = `Score: ${fb.score}/10\n✅ ${fb.what_was_good}\n⚠️ ${fb.what_was_missing}`;

      if (nextQ < QUESTIONS.length) {
        setMessages(prev => [
          ...prev,
          { role: 'ai', content: feedbackMsg, feedback: fb },
          { role: 'ai', content: `Next question:\n\n${QUESTIONS[nextQ]}` }
        ]);
        setQIndex(nextQ);
      } else {
        setMessages(prev => [
          ...prev,
          { role: 'ai', content: feedbackMsg, feedback: fb },
          { role: 'ai', content: "Interview complete! Click 'Get Final Report' to see your results." }
        ]);
        setDone(true);
      }
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Error evaluating answer. Please try again.' }]);
    } finally { setLoading(false); }
  };

  const avg = scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : '—';

  return (
    <div className="min-h-screen bg-[#0f1117] flex flex-col">
      <StepNavbar current={4} />

      <div className="flex flex-1 max-w-5xl mx-auto w-full px-6 py-6 gap-6">
        {/* Chat */}
        <div className="flex-1 flex flex-col bg-[#1a1d27] border border-[#2d3148] rounded-xl overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] px-4 py-3 rounded-xl text-sm leading-relaxed whitespace-pre-line
                  ${m.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : m.feedback
                      ? 'bg-[#1f2538] border border-[#3d4268] text-slate-300'
                      : 'bg-[#0f1117] text-slate-200'}`}>
                  {m.content}
                  {m.feedback?.model_answer_hint && (
                    <div className="mt-2 pt-2 border-t border-[#3d4268] text-blue-300 text-xs">
                      💡 Hint: {m.feedback.model_answer_hint}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-[#0f1117] text-slate-400 px-4 py-3 rounded-xl text-sm animate-pulse">
                  Evaluating your answer...
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          {!done ? (
            <div className="border-t border-[#2d3148] p-4 flex gap-3">
              <textarea
                value={answer}
                onChange={e => setAnswer(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); } }}
                placeholder="Type your answer... (Enter to send, Shift+Enter for new line)"
                className="flex-1 bg-[#0f1117] border border-[#2d3148] rounded-lg px-4 py-2.5 text-white text-sm resize-none focus:outline-none focus:border-blue-500"
                rows={3}
              />
              <button
                onClick={submit}
                disabled={!answer.trim() || loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white px-5 rounded-lg font-medium transition"
              >
                Send
              </button>
            </div>
          ) : (
            <div className="border-t border-[#2d3148] p-4">
              <button
                onClick={() => navigate('/report')}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-xl transition"
              >
                Get Final Report →
              </button>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="w-56 space-y-4">
          <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-4">
            <div className="text-slate-400 text-xs mb-1">Target Role</div>
            <div className="text-white text-sm font-medium">{role}</div>
          </div>
          <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-4">
            <div className="text-slate-400 text-xs mb-1">Avg Score</div>
            <div className="text-blue-400 text-2xl font-bold">{avg}</div>
            <div className="text-slate-500 text-xs">out of 10</div>
          </div>
          <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-4">
            <div className="text-slate-400 text-xs mb-2">Progress</div>
            <div className="flex flex-wrap gap-1.5">
              {QUESTIONS.map((_, i) => (
                <div key={i} className={`w-5 h-5 rounded text-xs flex items-center justify-center font-medium
                  ${i < scores.length
                    ? scores[i] >= 6 ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                    : i === qIndex ? 'bg-blue-600 text-white' : 'bg-[#2d3148] text-slate-500'}`}>
                  {i + 1}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}