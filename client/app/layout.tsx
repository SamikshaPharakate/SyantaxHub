import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SyntaxHub — Version-aware code analysis',
  description: 'Analyze code against version-specific framework documentation and migrate with confidence.',
  generator: 'SyntaxHub',
}

export const viewport: Viewport = {
  colorScheme: 'dark',
  themeColor: '#0b0d10',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" className="dark bg-background"><body className="antialiased">{children}{process.env.NODE_ENV === 'production' && <Analytics />}</body></html>
}
