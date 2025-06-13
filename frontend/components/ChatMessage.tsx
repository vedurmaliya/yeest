import React from 'react'
import clsx from 'clsx'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{
    content: string
    metadata: Record<string, any>
  }>
}

interface ChatMessageProps {
  message: ChatMessage
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={clsx('flex w-full mb-4', isUser ? 'justify-end' : 'justify-start')}>
      <div className={clsx('flex max-w-[80%]', isUser ? 'flex-row-reverse' : 'flex-row')}>
        {/* Avatar */}
        <div className={clsx('flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium', 
          isUser ? 'bg-primary-500 text-white ml-2' : 'bg-gray-300 text-gray-700 mr-2'
        )}>
          {isUser ? 'U' : 'AI'}
        </div>
        
        {/* Message content */}
        <div className="flex flex-col">
          <div className={clsx('chat-bubble', 
            isUser ? 'chat-bubble-user' : 'chat-bubble-assistant'
          )}>
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
          
          {/* Sources (only for assistant messages) */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-2 space-y-1">
              <p className="text-xs text-gray-500 font-medium">Sources:</p>
              {message.sources.map((source, index) => (
                <div key={index} className="text-xs bg-gray-100 p-2 rounded border-l-2 border-primary-300">
                  <div className="font-medium text-gray-700 mb-1">
                    {source.metadata.source === 'wikipedia' && '📖 Wikipedia'}
                    {source.metadata.source === 'news' && '📰 News'}
                    {source.metadata.source === 'reddit' && '💬 Reddit'}
                    {source.metadata.title && `: ${source.metadata.title}`}
                  </div>
                  <div className="text-gray-600 line-clamp-2">
                    {source.content}
                  </div>
                  {source.metadata.url && (
                    <a 
                      href={source.metadata.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary-500 hover:text-primary-600 underline mt-1 inline-block"
                    >
                      View source
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
