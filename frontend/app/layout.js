import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Puja AI Assistant - Hindu Puja & Ritual Guidance',
  description: 'AI-powered guidance for Hindu puja and ritual practices based on authentic texts',
  keywords: 'puja, hindu, rituals, ganesh, durga, lakshmi, ai assistant, shopify',
  author: 'Puja AI Team',
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <meta name="theme-color" content="#FF6B35" />
        
        {/* Shopify App Bridge */}
        <script 
          src="https://unpkg.com/@shopify/app-bridge@3/umd/index.js"
          defer
        />
        
        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content="Puja AI Assistant" />
        <meta property="og:description" content="AI-powered guidance for Hindu puja and ritual practices" />
        <meta property="og:image" content="/og-image.jpg" />
        
        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Puja AI Assistant" />
        <meta name="twitter:description" content="AI-powered guidance for Hindu puja and ritual practices" />
        <meta name="twitter:image" content="/og-image.jpg" />
      </head>
      <body className={inter.className}>
        <div id="puja-ai-root">
          {children}
        </div>
        

      </body>
    </html>
  )
}
