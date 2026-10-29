import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SyntaxHub — Ship confidently. Stay current.',
  description: 'AI-powered code analysis: Analyze your code against official documentation, detect outdated patterns, and get actionable refactoring suggestions.',
  generator: 'SyntaxHub',
}

export const viewport: Viewport = {
  colorScheme: 'dark',
  themeColor: '#080914',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark bg-background" suppressHydrationWarning>
      <body className="antialiased" suppressHydrationWarning>
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
