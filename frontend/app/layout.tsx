import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'PDF RAG Application',
  description: 'Chat and generate MCQ from your PDF documents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
