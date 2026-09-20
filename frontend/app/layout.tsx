import type { Metadata } from 'next'
import './globals.css'
import styles from './layout.module.css'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'VigilEye Demo',
  description: 'Autonomous Multi-Agent AI & Edge Inference Systems',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className={styles.appContainer}>
          <nav className={styles.sidebar}>
            <div className={styles.logo}>
              <h2>VigilEye</h2>
            </div>
            <ul className={styles.navLinks}>
              <li><Link href="/">Home</Link></li>
              <li><Link href="/trace">Trace</Link></li>
              <li><Link href="/agents">Agents</Link></li>
              <li><Link href="/metrics">Metrics</Link></li>
              <li><Link href="/evidence">Evidence</Link></li>
            </ul>
          </nav>
          <main className={styles.mainContent}>
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
