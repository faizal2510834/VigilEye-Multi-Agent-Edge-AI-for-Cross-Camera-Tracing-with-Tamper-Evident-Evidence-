const isDemo = process.env.NEXT_PUBLIC_DEMO_MODE === 'static';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchQuery(query: string, justification: string) {
  if (isDemo) {
    return {
      parsed: {
        object_class: "person",
        attributes: { color: "blue" },
        time_range: null,
        camera_hints: [],
        raw_text: query
      }
    };
  }
  const res = await fetch(`${API_URL}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, justification, operator_id: "demo_admin" })
  });
  if (!res.ok) throw new Error('API Error');
  return res.json();
}

export async function fetchTrace(query_embedding: number[], start_camera: string, mode: string) {
  if (isDemo) {
    const res = await fetch('/demo-data/trace.json');
    return res.json();
  }
  const res = await fetch(`${API_URL}/api/trace`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query_embedding, start_camera, mode })
  });
  if (!res.ok) throw new Error('API Error');
  return res.json();
}

export async function fetchMetrics() {
  if (isDemo) {
    const res = await fetch('/demo-data/metrics.json');
    return res.json();
  }
  const res = await fetch(`${API_URL}/api/metrics`);
  if (!res.ok) throw new Error('API Error');
  return res.json();
}

export async function anchorEvidence(caseId: string, trail: any[]) {
  if (isDemo) {
    return {
      merkle_root: "0xsimulatedroot...",
      tx_hash: "0xsimulatedtxhash...",
      block_number: 12345
    };
  }
  const res = await fetch(`${API_URL}/api/evidence/anchor`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId, trail })
  });
  if (!res.ok) throw new Error('API Error');
  return res.json();
}
