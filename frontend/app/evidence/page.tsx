"use client";

import Link from 'next/link';

export default function EvidencePage() {
  return (
    <div className="container">
      <div className="card">
        <h2>Blockchain Evidence Anchoring</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '10px', lineHeight: '1.6' }}>
          Evidence anchoring is tied to real query traces. To generate and anchor a tamper-evident audit record to the smart contract, please visit the{' '}
          <Link href="/trace" style={{ color: 'var(--accent)', textDecoration: 'underline' }}>
            Trace page
          </Link>
          , run a target trace across cameras, and anchor the resulting timeline trail directly to the blockchain.
        </p>
      </div>
    </div>
  );
}
