import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import { Toaster } from '@/components/ui/sonner'
import { Providers } from '@/components/providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Indian Legal AI - AI-Powered Legal Research Platform',
  description: 'Interactive AI platform for Indian legal research, document analysis, and legal drafting. Powered by case law and government bare acts.',
  keywords: ['legal AI', 'Indian law', 'case law', 'legal research', 'legal drafting', 'Indian judiciary'],
  authors: [{ name: 'Indian Legal AI Team' }],
  openGraph: {
    title: 'Indian Legal AI Platform',
    description: 'AI-powered legal research and drafting for Indian laws',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body className={inter.className}>
          <Providers>
            {children}
            <Toaster />
          </Providers>
        </body>
      </html>
    </ClerkProvider>
  )
}
