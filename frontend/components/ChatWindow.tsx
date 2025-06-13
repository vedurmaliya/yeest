import React, { useEffect, useRef } from 'react'
import ChatMessage, { ChatMessage as ChatMessageType } from './ChatMessage'

interface ChatWindowProps {
  messages: ChatMessageType[]
  isLoading?: boolean
}

export default function ChatWindow({ messages, isLoading = false }: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="max-w-md">
            <h2 className="text-2xl font-bold text-gray-700 mb-4">
              Welcome to yeest.xyz
            </h2>
            <p className="text-gray-500 mb-6">
              I'm your AI assistant powered by real-time information from Wikipedia, news, and Reddit. 
              Ask me anything and I'll provide you with up-to-date, sourced answers.
            </p>
            <div className="grid grid-cols-1 gap-2 text-sm text-gray-400">
              <div className="flex items-center justify-center space-x-2">
                <span>📖</span>
                <span>Wikipedia knowledge</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <span>📰</span>
                <span>Latest news</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <span>💬</span>
                <span>Reddit discussions</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-sm font-medium text-gray-700">
                  AI
                </div>
                <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  )
}
