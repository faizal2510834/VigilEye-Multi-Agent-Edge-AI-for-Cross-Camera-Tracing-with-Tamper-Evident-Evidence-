"use client";

import { useEffect, useState, useRef } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const isDemo = process.env.NEXT_PUBLIC_DEMO_MODE === 'static';

export default function AgentsPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isDemo) {
      // Load static feed
      fetch('/demo-data/agents.json')
        .then(res => res.json())
        .then(data => setMessages(data.history))
        .catch(console.error);
      return;
    }

    let sse: EventSource | null = null;
    let cancelled = false;

    // Backfill any agent activity that already happened before this page was
    // opened, then open the live stream for anything new.
    fetch(`${API_URL}/api/agents/feed`)
      .then(res => res.json())
      .then(data => {
        if (cancelled) return;
        if (Array.isArray(data?.history)) {
          setMessages(data.history.slice(-100));
        }
      })
      .catch(console.error)
      .finally(() => {
        if (cancelled) return;

        sse = new EventSource(`${API_URL}/api/agents/ws`);

        sse.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);
            setMessages(prev => [...prev, data].slice(-100));
          } catch (err) {}
        };

        sse.onerror = (e) => {
          console.error("SSE Error", e);
        };
      });

    return () => {
      cancelled = true;
      sse?.close();
    };
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="container">
      <h2>Autonomous Agent Logs</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
        Live feed of communications between the four independent agents.
      </p>

      <div className="card" style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
        <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {messages.length === 0 ? (
            <div style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '20px' }}>
              Waiting for agent activity...
            </div>
          ) : (
            messages.map((msg, i) => (
              <div key={i} style={{ 
                padding: '12px', 
                backgroundColor: 'rgba(255,255,255,0.02)', 
                borderLeft: `4px solid ${getColor(msg?.message?.agent)}`,
                borderRadius: '4px',
                fontFamily: 'monospace'
              }}>
                <strong style={{ color: getColor(msg?.message?.agent) }}>[{msg?.message?.agent || 'System'}]</strong>
                <span style={{ marginLeft: '10px', color: 'var(--text-primary)' }}>{msg?.message?.msg}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function getColor(agentName: string) {
  if (!agentName) return 'var(--text-secondary)';
  if (agentName.startsWith('Edge')) return '#38bdf8'; // light blue
  if (agentName === 'Spatial') return '#a78bfa'; // purple
  if (agentName === 'Intent') return '#f472b6'; // pink
  if (agentName === 'CryptoAudit') return '#fbbf24'; // amber
  return 'var(--text-primary)';
}
