import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StepNavbar from '../components/StepNavbar';
import api from '../api';

interface Question { id: number; question: string; options: string[]; }

export default function Quiz() {
  const navigate = useNavigate();
  const sessionId = localStorage.getItem('session_id');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [quizId, setQuizId] = useState<number | null>(null);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [selected, setSelected] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) { navigate('/upload'); return; }
    api.post(`/quiz/generate/${sessionId}`)
      .then(r => { setQuestions(r.data.questions); setQuizId(r.data.quiz_id); })
      .catch(e => setError(e.response?.data?.detail || 'Failed to generate quiz'))
      .finally(() => setLoading(false));
  }, [navigate, sessionId]);

  const next = () => {
    if (!selected) return;
    const q = questions[current];
    const newAnswers = { ...answers, [String(q.id)]: selected };
    setAnswers(newAnswers);
    setSelected('');

    if (current < questions.length - 1) {
      setCurrent(current + 1);
    } else {
      // Submit
      setSubmitting(true);
      api.post(`/quiz/submit/${quizId}`, { answers: newAnswers })
        .then(r => setResult(r.data))
        .catch(e => setError(e.response?.data?.detail || 'Submit failed'))
        .finally(() => setSubmitting(false));
    }
  };

  const q = questions[current];

  return (
    <div className="min-h-screen bg-[#0f1117]">
      <StepNavbar current={3} />
      <div className="max-w-2xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-white mb-2">Knowledge Quiz</h1>
        <p className="text-slate-400 mb-8">Score 6/10 or above to unlock the mock interview.</p>

        {error && <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg mb-6 text-sm">{error}</div>}

        {loading || submitting ? (
          <div className="text-center py-20">
            <div className="animate-spin text-4xl mb-4">📝</div>
            <p className="text-slate-400">{loading ? 'Generating questions...' : 'Submitting your answers...'}</p>
          </div>
        ) : result ? (
          /* Results screen */
          <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-8 text-center">
            <div className={`text-6xl font-bold mb-2 ${result.score >= 6 ? 'text-green-400' : 'text-red-400'}`}>
              {result.score}/10
            </div>
            <p className={`text-lg mb-6 ${result.score >= 6 ? 'text-green-300' : 'text-red-300'}`}>
              {result.passed ? '🎉 You passed! Ready for the interview.' : '❌ Score below 6. Review the gaps and try again.'}
            </p>

            {/* Show correct answers */}
            <div className="text-left space-y-3 mb-8">
              {(result.results || []).map((r: any, i: number) => (
                <div key={r.id} className={`px-4 py-3 rounded-lg border text-sm
                  ${r.your_answer === r.correct ? 'bg-green-900/20 border-green-700' : 'bg-red-900/20 border-red-700'}`}>
                  <div className="font-medium text-white mb-1">Q{i + 1}: {questions[i]?.question}</div>
                  <div className="text-slate-300">
                    Your answer: <span className={r.your_answer === r.correct ? 'text-green-400' : 'text-red-400'}>{r.your_answer || 'Not answered'}</span>
                    {r.your_answer !== r.correct && <span className="text-green-400 ml-2">· Correct: {r.correct}</span>}
                  </div>
                  {r.explanation && <div className="text-slate-400 text-xs mt-1">{r.explanation}</div>}
                </div>
              ))}
            </div>

            {result.passed ? (
              <button onClick={() => navigate('/interview')}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-xl transition">
                Start Mock Interview →
              </button>
            ) : (
              <div className="space-y-3">
                <button onClick={() => window.location.reload()}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition">
                  Retake Quiz
                </button>
                <button onClick={() => navigate('/gaps')}
                  className="w-full border border-[#2d3148] text-slate-300 hover:text-white font-medium py-3 rounded-xl transition">
                  ← Review Gap Analysis
                </button>
              </div>
            )}
          </div>
        ) : q ? (
          /* Question screen */
          <div className="bg-[#1a1d27] border border-[#2d3148] rounded-xl p-8">
            {/* Progress dots */}
            <div className="flex gap-1.5 mb-6">
              {questions.map((_, i) => (
                <div key={i} className={`h-1.5 flex-1 rounded-full
                  ${i < current ? 'bg-blue-500' : i === current ? 'bg-blue-400' : 'bg-[#2d3148]'}`} />
              ))}
            </div>

            <div className="text-slate-400 text-sm mb-2">Question {current + 1} of {questions.length}</div>
            <h2 className="text-white text-lg font-medium mb-6 leading-relaxed">{q.question}</h2>

            <div className="space-y-3 mb-8">
              {q.options.map(opt => (
                <button
                  key={opt}
                  onClick={() => setSelected(opt[0])} // "A. text" → take first char
                  className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition
                    ${selected === opt[0]
                      ? 'bg-blue-600 border-blue-500 text-white'
                      : 'border-[#2d3148] text-slate-300 hover:border-blue-500 hover:text-white bg-[#0f1117]'}`}
                >
                  {opt}
                </button>
              ))}
            </div>

            <button
              onClick={next}
              disabled={!selected}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-medium py-3 rounded-xl transition"
            >
              {current === questions.length - 1 ? 'Submit Quiz' : 'Next Question →'}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}