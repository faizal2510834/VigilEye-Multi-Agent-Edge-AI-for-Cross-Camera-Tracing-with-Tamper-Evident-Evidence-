"use client";

import { useState, useEffect } from 'react';
import { fetchQuery, fetchTrace } from '../../lib/api';

export default function TracePage() {
  const [query, setQuery] = useState('');
  const [justification, setJustification] = useState('');
  const [mode, setMode] = useState('handoff');
  const [loading, setLoading] = useState(false);
  const [parsed, setParsed] = useState<any>(null);
  const [traceResult, setTraceResult] = useState<any>(null);
  const [error, setError] = useState('');
  
  const [tracks, setTracks] = useState<any[]>([]);
  const [selectedTrack, setSelectedTrack] = useState<any>(null);

  useEffect(() => {
    // Load track gallery
    fetch('http://localhost:8000/api/tracks')
      .then(r => r.json())
      .then(d => setTracks(d.tracks || []))
      .catch(e => console.error(e));
  }, []);

  const handleTrace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!justification.trim()) {
      setError('Audit justification is required.');
      return;
    }
    setError('');
    setLoading(true);
    setTraceResult(null);
    setParsed(null);

    try {
      let tRes;
      if (selectedTrack) {
        // Tracing a selected track directly
        const res = await fetch('http://localhost:8000/api/trace', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
             track_id: selectedTrack.track_id, 
             start_camera: selectedTrack.camera_id, 
             mode 
          })
        });
        if (!res.ok) throw new Error('API Error');
        tRes = await res.json();
      } else {
        // Text-based query tracing
        const qRes = await fetchQuery(query, justification);
        setParsed(qRes.parsed);
        const qEmb = qRes.query_embedding;
        if (!qEmb) throw new Error("No query embedding returned from Intent parser");
        tRes = await fetchTrace(qEmb, 'cam_1', mode);
      }
      setTraceResult(tRes);
    } catch (err: any) {
      setError(err.message || 'Error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ marginBottom: '20px' }}>
        <h2>Target Trace</h2>
        <form onSubmit={handleTrace} style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '20px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px' }}>Track Selection (Gallery)</label>
            <div style={{ display: 'flex', gap: '10px', overflowX: 'auto', padding: '10px', border: '1px solid var(--border)', borderRadius: '4px' }}>
              {tracks.map((t, i) => (
                <div 
                  key={i} 
                  onClick={() => { setSelectedTrack(t); setQuery(`Selected Track: ${t.track_id}`); }}
                  style={{ 
                    padding: '10px', 
                    cursor: 'pointer',
                    border: selectedTrack?.track_id === t.track_id ? '2px solid var(--accent)' : '1px solid var(--border)',
                    backgroundColor: 'rgba(255,255,255,0.02)',
                    borderRadius: '4px',
                    minWidth: '100px',
                    textAlign: 'center'
                  }}
                >
                  <div style={{ fontSize: '12px' }}>{t.track_id}</div>
                  <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>{t.dominant_color}</div>
                </div>
              ))}
              {tracks.length === 0 && <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Loading tracks...</div>}
            </div>
            <div style={{ marginTop: '5px', fontSize: '12px', color: 'var(--text-secondary)' }}>
               Click a track above to select it, or clear the selection to type a text query.
               {selectedTrack && <button type="button" onClick={() => { setSelectedTrack(null); setQuery(''); }} style={{ marginLeft: '10px', padding: '2px 8px', fontSize: '10px' }}>Clear Selection</button>}
            </div>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px' }}>Natural Language Query</label>
            <input 
              type="text" 
              value={query} 
              onChange={(e) => { setQuery(e.target.value); setSelectedTrack(null); }} 
              placeholder="e.g. Find the blue shirt guy near gate 2" 
              required
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px' }}>Audit Justification (Required)</label>
            <input 
              type="text" 
              value={justification} 
              onChange={(e) => setJustification(e.target.value)} 
              placeholder="Reason for query" 
              required
            />
          </div>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <label>
              <input type="radio" value="handoff" checked={mode === 'handoff'} onChange={() => setMode('handoff')} /> Predictive Handoff
            </label>
            <label>
              <input type="radio" value="brute_force" checked={mode === 'brute_force'} onChange={() => setMode('brute_force')} /> Brute Force
            </label>
            <button type="submit" disabled={loading} style={{ marginLeft: 'auto' }}>
              {loading ? 'Searching...' : 'Trace Target'}
            </button>
          </div>
        </form>
        {error && <div style={{ color: 'var(--danger)', marginTop: '10px' }}>{error}</div>}
      </div>

      {parsed && (
        <div className="card" style={{ marginBottom: '20px', backgroundColor: 'rgba(59, 130, 246, 0.1)', borderColor: 'var(--accent)' }}>
          <h3 style={{ color: 'var(--accent)', marginBottom: '10px' }}>LLM Intent Parser Output</h3>
          <pre style={{ margin: 0, fontSize: '14px' }}>
            {JSON.stringify(parsed, null, 2)}
          </pre>
        </div>
      )}

      {traceResult && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '20px' }}>
          <div className="card">
            <h3>Camera Graph & Trail</h3>
            <div style={{ height: '300px', border: '1px solid var(--border)', marginTop: '15px', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#000' }}>
               <div style={{ display: 'flex', gap: '20px', overflowX: 'auto', padding: '20px' }}>
                 {traceResult.trail.map((t: any, i: number) => (
                   <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
                     <div style={{ padding: '10px 20px', backgroundColor: 'var(--accent)', borderRadius: '20px', color: '#fff', fontWeight: 'bold' }}>
                       {t.camera_id}
                     </div>
                     {i < traceResult.trail.length - 1 && <div style={{ width: '40px', height: '2px', backgroundColor: 'var(--accent)' }} />}
                   </div>
                 ))}
               </div>
            </div>
            
            <h4 style={{ marginTop: '20px', color: 'var(--text-secondary)' }}>Savings vs Brute Force</h4>
            <div style={{ display: 'flex', gap: '20px', marginTop: '10px' }}>
               <div style={{ padding: '15px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '4px', flex: 1 }}>
                 <div style={{ fontSize: '24px', color: 'var(--success)', fontWeight: 'bold' }}>{traceResult.metrics.inference_calls}</div>
                 <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Inference Calls</div>
               </div>
               <div style={{ padding: '15px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '4px', flex: 1 }}>
                 <div style={{ fontSize: '24px', color: 'var(--success)', fontWeight: 'bold' }}>{traceResult.metrics.comparisons}</div>
                 <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Vector Comparisons</div>
               </div>
            </div>
          </div>
          
          <div className="card" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <h3>Timeline</h3>
            <div style={{ marginTop: '15px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {traceResult.trail.map((t: any, i: number) => (
                <div key={i} style={{ padding: '10px', borderLeft: '2px solid var(--accent)', backgroundColor: 'rgba(255,255,255,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <strong style={{ color: 'var(--accent)' }}>{t.camera_id}</strong>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t.timestamp.toFixed(1)}s</span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--success)', marginBottom: '5px' }}>{t.confidence.toFixed(1)}% Match</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t.explanation}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
