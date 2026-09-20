"use client";

import { useState } from 'react';
import { anchorEvidence } from '../../lib/api';

export default function EvidencePage() {
  const [caseId, setCaseId] = useState('case_001');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [tampered, setTampered] = useState(false);
  const [error, setError] = useState('');

  const mockTrail = [
    { camera_id: 'cam_1', track_id: 'cam_1_1', timestamp: 2.5 },
    { camera_id: 'cam_2', track_id: 'cam_2_1', timestamp: 14.1 },
    { camera_id: 'cam_3', track_id: 'cam_3_2', timestamp: 28.5 }
  ];

  const handleAnchor = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await anchorEvidence(caseId, mockTrail);
      setResult(res);
      setTampered(false);
    } catch (err: any) {
      setError(err.message || 'Error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleTamper = () => {
    setTampered(true);
  };

  return (
    <div className="container">
      <div className="card">
        <h2>Blockchain Evidence Anchoring</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '10px' }}>
          Anchor a timeline hash to the smart contract to guarantee tamper-evident records.
        </p>

        <div style={{ marginTop: '20px', display: 'flex', gap: '15px' }}>
          <input 
            type="text" 
            value={caseId} 
            onChange={(e) => setCaseId(e.target.value)} 
            placeholder="Case ID"
            style={{ width: '200px' }}
          />
          <button onClick={handleAnchor} disabled={loading}>
            {loading ? 'Anchoring...' : 'Anchor to Blockchain'}
          </button>
        </div>

        {error && <div style={{ color: 'var(--danger)', marginTop: '10px' }}>{error}</div>}

        {result && (
          <div style={{ marginTop: '30px', padding: '20px', backgroundColor: 'rgba(255,255,255,0.02)', border: `1px solid ${tampered ? 'var(--danger)' : 'var(--success)'}`, borderRadius: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ color: tampered ? 'var(--danger)' : 'var(--success)' }}>
                {tampered ? 'Verification Failed: Tampering Detected' : 'Evidence Verified on Chain'}
              </h3>
              {!tampered && (
                <button onClick={handleTamper} style={{ backgroundColor: 'var(--warning)' }}>Simulate Tamper</button>
              )}
            </div>
            
            <div style={{ marginTop: '20px', display: 'grid', gap: '10px', fontSize: '14px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Tx Hash:</span>
                <span style={{ fontFamily: 'monospace' }}>{result.tx_hash}</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Block Number:</span>
                <span style={{ fontFamily: 'monospace' }}>{result.block_number}</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Merkle Root:</span>
                <span style={{ fontFamily: 'monospace', color: tampered ? 'var(--danger)' : 'inherit' }}>
                  {tampered ? '0xBADHASH999999999999999999999999999999999999999999999999999999999' : result.merkle_root}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
