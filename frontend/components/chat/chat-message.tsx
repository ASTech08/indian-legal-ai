'use client'

import { useState } from 'react'
import { Bot, User, Copy, Check, ThumbsUp, ThumbsDown, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { cn } from '@/lib/utils'
import type { Message } from '@/lib/types'

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null)

  const isUser = message.role === 'user'

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleFeedback = (type: 'up' | 'down') => {
    setFeedback(type)
    // TODO: Send feedback to backend
  }

  return (
    <div className={cn(
      "flex gap-4 message-appear",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <div className="flex-shrink-0">
          <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
            <Bot className="h-5 w-5 text-primary" />
          </div>
        </div>
      )}

      <div className={cn(
        "flex flex-col space-y-2 max-w-[80%]",
        isUser && "items-end"
      )}>
        <Card className={cn(
          "p-4",
          isUser 
            ? "bg-primary text-primary-foreground" 
            : "bg-card"
        )}>
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="markdown-content prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '')
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={vscDarkPlus}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    )
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}

          {/* Sources/Citations */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border/50">
              <p className="text-xs font-semibold mb-2">Sources:</p>
              <div className="space-y-2">
                {message.sources.map((source, index) => (
                  <div key={index} className="text-xs">
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline"
                    >
                      [{index + 1}] {source.title}
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Attachments */}
          {message.attachments && message.attachments.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border/50 space-y-2">
              {message.attachments.map((attachment, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <Download className="h-4 w-4" />
                  <a
                    href={attachment.url}
                    download
                    className="text-primary hover:underline"
                  >
                    {attachment.name}
                  </a>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Actions */}
        {!isUser && (
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={handleCopy}
              className="h-7 px-2"
            >
              {copied ? (
                <Check className="h-3 w-3 text-green-500" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleFeedback('up')}
              className={cn(
                "h-7 px-2",
                feedback === 'up' && "text-green-500"
              )}
            >
              <ThumbsUp className="h-3 w-3" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleFeedback('down')}
              className={cn(
                "h-7 px-2",
                feedback === 'down' && "text-destructive"
              )}
            >
              <ThumbsDown className="h-3 w-3" />
            </Button>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0">
          <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
            <User className="h-5 w-5" />
          </div>
        </div>
      )}
    </div>
  )
}
