import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import StepNavbar from '../components/StepNavbar';
import api from '../api';

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    if (!f.name.endsWith('.pdf')) { setError('Only PDF files accepted'); return; }
    setFile(f); setError('');
  };

  const upload = async () => {
    if (!file) return;
    setLoading(true); setError('');
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await api.post('/resume/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      localStorage.setItem('session_id', String(res.data.session_id));
      navigate('/careers');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-[#0f1117]">
      <StepNavbar current={0} />
      <div className="max-w-2xl mx-auto px-6 py-16">
        <h1 className="text-2xl font-bold text-white mb-2">Upload your resume</h1>
        <p className="text-slate-400 mb-8">We'll extract your skills and recommend the best career paths for you.</p>

        {/* Drop zone */}
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={e => { e.preventDefault(); setDrag(true); }}
          onDragLeave={() => setDrag(false)}
          onDrop={e => { e.preventDefault(); setDrag(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
          className={`border-2 border-dashed rounded-xl p-14 text-center cursor-pointer transition
            ${drag ? 'border-blue-400 bg-blue-900/10' : 'border-[#2d3148] hover:border-blue-500 bg-[#1a1d27]'}
            ${file ? 'border-green-500 bg-green-900/10' : ''}`}
        >
          <input ref={inputRef} type="file" accept=".pdf" className="hidden"
            onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />

          {file ? (
            <>
              <div className="text-4xl mb-3">📄</div>
              <p className="text-green-400 font-medium">{file.name}</p>
              <p className="text-slate-400 text-sm mt-1">{(file.size / 1024).toFixed(0)} KB · Click to change</p>
            </>
          ) : (
            <>
              <div className="text-4xl mb-3">☁️</div>
              <p className="text-white font-medium">Drop your PDF here</p>
              <p className="text-slate-400 text-sm mt-1">or click to browse</p>
            </>
          )}
        </div>

        {error && <p className="text-red-400 text-sm mt-3">{error}</p>}

        <button
          onClick={upload}
          disabled={!file || loading}
          className="mt-6 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-medium py-3 rounded-xl transition"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin">⏳</span> Analysing resume... (this takes ~15 seconds)
            </span>
          ) : 'Analyse Resume →'}
        </button>

        {loading && (
          <p className="text-slate-400 text-sm text-center mt-3">
            AI is reading your resume and preparing career recommendations...
          </p>
        )}
      </div>
    </div>
  );
}