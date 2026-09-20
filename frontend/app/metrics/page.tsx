"use client";

import React, { useEffect, useState } from 'react';
import { fetchMetrics } from '../../lib/api';

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics()
      .then(setMetrics)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="container">Loading metrics...</div>;

  const quant = metrics?.quantization || {};

  return (
    <div className="container">
      <h2>System Metrics & Benchmarks</h2>
      
      <div className="card" style={{ marginTop: '20px' }}>
        <h3 style={{ marginBottom: '15px' }}>INT8 Quantization Benchmarks (ONNX Runtime)</h3>
        {Object.keys(quant).length > 0 ? (
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '10px' }}>Model</th>
                <th style={{ padding: '10px' }}>Precision</th>
                <th style={{ padding: '10px' }}>Latency (ms)</th>
                <th style={{ padding: '10px' }}>FPS</th>
                <th style={{ padding: '10px' }}>RAM (MB)</th>
                <th style={{ padding: '10px' }}>Size (MB)</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(quant).map(([modelName, data]: any) => (
                <React.Fragment key={modelName}>
                  <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)' }}>
                    <td style={{ padding: '10px' }}>{modelName}</td>
                    <td style={{ padding: '10px' }}>FP32</td>
                    <td style={{ padding: '10px' }}>{data.FP32.Latency_ms}</td>
                    <td style={{ padding: '10px' }}>{data.FP32.FPS}</td>
                    <td style={{ padding: '10px' }}>{data.FP32.RAM_MB}</td>
                    <td style={{ padding: '10px' }}>{data.FP32.Size_MB}</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '10px', color: 'var(--accent)' }}>{modelName}</td>
                    <td style={{ padding: '10px', color: 'var(--accent)' }}>INT8</td>
                    <td style={{ padding: '10px', color: 'var(--success)' }}>{data.INT8.Latency_ms}</td>
                    <td style={{ padding: '10px', color: 'var(--success)' }}>{data.INT8.FPS}</td>
                    <td style={{ padding: '10px', color: 'var(--success)' }}>{data.INT8.RAM_MB}</td>
                    <td style={{ padding: '10px', color: 'var(--success)' }}>{data.INT8.Size_MB}</td>
                  </tr>
                </React.Fragment>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No quantization benchmarks found. Run `make benchmark`.</p>
        )}
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h3 style={{ marginBottom: '15px' }}>Learned Transit Priors</h3>
        <pre style={{ backgroundColor: 'rgba(0,0,0,0.5)', padding: '15px', borderRadius: '4px', overflowX: 'auto' }}>
          {JSON.stringify(metrics?.learned_priors, null, 2)}
        </pre>
      </div>
    </div>
  );
}
