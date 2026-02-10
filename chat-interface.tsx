'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Paperclip, Mic, StopCircle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ChatMessage } from './chat-message'
import { FileUpload } from './file-upload'
import { SuggestedQueries } from './suggested-queries'
import { useChatStore } from '@/lib/stores/chat-store'
import { cn } from '@/lib/utils'

export function ChatInterface() {
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [showFileUpload, setShowFileUpload] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const { messages, isLoading, sendMessage, uploadFile } = useChatStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    await sendMessage(input)
    setInput('')
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleFileUpload = async (file: File) => {
    await uploadFile(file)
    setShowFileUpload(false)
  }

  const handleSuggestedQuery = (query: string) => {
    setInput(query)
    textareaRef.current?.focus()
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-gradient-to-b from-background to-muted/10">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/60">
                  How can I help you today?
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl">
                  Ask me anything about Indian law, upload documents for analysis, or draft legal documents.
                </p>
              </div>
              
              <SuggestedQueries onSelect={handleSuggestedQuery} />
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Analyzing legal context...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            {showFileUpload && (
              <FileUpload
                onUpload={handleFileUpload}
                onClose={() => setShowFileUpload(false)}
              />
            )}
            
            <div className="relative">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value)
                  // Auto-resize textarea
                  e.target.style.height = 'auto'
                  e.target.style.height = e.target.scrollHeight + 'px'
                }}
                onKeyDown={handleKeyDown}
                placeholder="Ask a legal question, upload a document, or request a draft..."
                className="min-h-[60px] max-h-[200px] resize-none pr-24 text-base"
                disabled={isLoading}
              />
              
              <div className="absolute right-2 bottom-2 flex items-center space-x-2">
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  onClick={() => setShowFileUpload(!showFileUpload)}
                  className="h-8 w-8"
                  disabled={isLoading}
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
                
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  onClick={() => setIsRecording(!isRecording)}
                  className={cn(
                    "h-8 w-8",
                    isRecording && "text-destructive"
                  )}
                  disabled={isLoading}
                >
                  {isRecording ? (
                    <StopCircle className="h-4 w-4" />
                  ) : (
                    <Mic className="h-4 w-4" />
                  )}
                </Button>
                
                <Button
                  type="submit"
                  size="icon"
                  disabled={!input.trim() || isLoading}
                  className="h-8 w-8"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </form>
          
          <p className="text-xs text-muted-foreground text-center mt-2">
            AI can make mistakes. Verify important legal information with a qualified lawyer.
          </p>
        </div>
      </div>
    </div>
  )
}
