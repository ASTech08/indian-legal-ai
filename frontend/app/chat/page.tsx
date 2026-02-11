'use client'

import { useState } from 'react'
import { ChatInterface } from '@/components/chat/chat-interface'
import { ChatHeader } from '@/components/chat/chat-header'

export default function ChatPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatHeader onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        <ChatInterface />
      </div>
    </div>
  )
}
