'use client'

import { useState } from 'react'
import { ChatInterface } from '@/components/chat/chat-interface'
import { ChatSidebar } from '@/components/chat/chat-sidebar'
import { ChatHeader } from '@/components/chat/chat-header'
import { useAuth } from '@clerk/nextjs'
import { redirect } from 'next/navigation'

export default function ChatPage() {
  const { isSignedIn, isLoaded } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  if (isLoaded && !isSignedIn) {
    redirect('/sign-in')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <ChatSidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatHeader onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        <ChatInterface />
      </div>
    </div>
  )
}
