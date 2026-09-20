import Link from 'next/link';

export default function Home() {
  return (
    <div className="container">
      <div className="card" style={{ padding: '40px', textAlign: 'center', marginTop: '40px' }}>
        <h1 style={{ color: 'var(--accent)', fontSize: '48px', marginBottom: '20px' }}>VigilEye</h1>
        <p style={{ fontSize: '20px', color: 'var(--text-secondary)', marginBottom: '40px' }}>
          Autonomous Multi-Agent AI & Edge Inference Systems
        </p>
        
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
          <Link href="/trace">
            <button style={{ padding: '12px 24px', fontSize: '18px' }}>Start Tracing</button>
          </Link>
          <Link href="/agents">
            <button style={{ padding: '12px 24px', fontSize: '18px', backgroundColor: 'var(--border)' }}>View Agents</button>
          </Link>
        </div>
        
        <div style={{ marginTop: '60px', textAlign: 'left', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '8px' }}>
            <h3 style={{ color: 'var(--text-primary)', marginBottom: '10px' }}>Predictive Handoff</h3>
            <p style={{ color: 'var(--text-secondary)' }}>
              Edge perception agents intelligently wake up adjacent cameras only during predicted transit windows, saving massive amounts of compute and bandwidth.
            </p>
          </div>
          <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '8px' }}>
            <h3 style={{ color: 'var(--text-primary)', marginBottom: '10px' }}>Blockchain Evidence</h3>
            <p style={{ color: 'var(--text-secondary)' }}>
              A complete chronological trail is hashed into a Merkle root and anchored to a smart contract, providing tamper-evident forensic timelines.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
