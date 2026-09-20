"use client";

import { useState } from 'react';
import { fetchQuery, fetchTrace } from '../../lib/api';

export default function TracePage() {
  const [query, setQuery] = useState('');
  const [justification, setJustification] = useState('');
  const [mode, setMode] = useState('handoff');
  const [loading, setLoading] = useState(false);
  const [parsed, setParsed] = useState<any>(null);
  const [traceResult, setTraceResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleTrace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!justification.trim()) {
      setError('Audit justification is required.');
      return;
    }
    setError('');
    setLoading(true);
    setTraceResult(null);

    try {
      // 1. Parse intent
      const qRes = await fetchQuery(query, justification);
      setParsed(qRes.parsed);
      
      // 2. Perform trace using a mock embedding for now (since UI doesn't have it)
      // We pass query_embedding as a dummy 512 array to trigger search
      const dummyEmbedding = Array(512).fill(0.1); 
      const tRes = await fetchTrace(dummyEmbedding, 'cam_1', mode);
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
            <label style={{ display: 'block', marginBottom: '5px' }}>Natural Language Query</label>
            <input 
              type="text" 
              value={query} 
              onChange={(e) => setQuery(e.target.value)} 
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
               {/* Simple visualization of camera hops */}
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
