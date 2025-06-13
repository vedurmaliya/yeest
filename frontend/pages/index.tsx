import React, { useState } from 'react'
import Head from 'next/head'
import axios from 'axios'
import ChatWindow from '../components/ChatWindow'
import ChatInput from '../components/ChatInput'
import { ChatMessage } from '../components/ChatMessage'
import styled from 'styled-components'

const StyledYeestText = styled.h1`
  padding: 0;
  margin: 0;
  cursor: default;
  --primary-color: #111;
  --hovered-color: #c84747;
  position: relative;
  display: inline-block;
  font-weight: 600;
  font-size: 20px;
  color: var(--primary-color);

  &::after {
    position: absolute;
    content: "";
    width: 0;
    left: 0;
    bottom: -7px;
    background: var(--hovered-color);
    height: 2px;
    transition: 0.3s ease-out;
  }

  &::before {
    position: absolute;
    content: "yeest";
    width: 0%;
    inset: 0;
    color: var(--hovered-color);
    overflow: hidden;
    transition: 0.3s ease-out;
  }

  &:hover::after {
    width: 100%;
  }

  &:hover::before {
    width: 100%;
  }
`;

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = async (content: string) => {
    const userMessage: ChatMessage = {
      role: 'user',
      content
    }

    // Add user message to chat
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      const response = await axios.post('/api/chat', {
        question: content,
        history: messages
      })

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('Error sending message:', error)
      
      let errorMessage = 'Sorry, I encountered an error while processing your request.'
      
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.message) {
        errorMessage = error.message
      }

      const errorResponse: ChatMessage = {
        role: 'assistant',
        content: `❌ ${errorMessage}`
      }

      setMessages(prev => [...prev, errorResponse])
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = async () => {
    try {
      // Clear frontend state
      setMessages([])
      setError(null)

      // Clear backend memory
      await axios.post('/api/clear-memory')

      // Clear vector store to remove old documents
      await axios.post('/api/clear-vector-store')

      console.log('Chat and vector store cleared successfully')
    } catch (error) {
      console.error('Error clearing chat:', error)
      setError('Failed to clear chat completely')
    }
  }

  return (
    <>
      <Head>
        <title>yeest.xyz - AI Chat Assistant</title>
        <meta name="description" content="RAG-powered chat assistant with real-time information from Wikipedia, news, and Reddit" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="flex flex-col h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between max-w-4xl mx-auto">
            <div className="flex items-center space-x-3">
              <StyledYeestText>yeest</StyledYeestText>
              <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                AI Assistant
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              {messages.length > 0 && (
                <button
                  onClick={clearChat}
                  className="btn-secondary text-sm"
                  disabled={isLoading}
                >
                  Clear Chat
                </button>
              )}
              
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Online</span>
              </div>
            </div>
          </div>
        </header>

        {/* Main chat area */}
        <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
          <ChatWindow messages={messages} isLoading={isLoading} />
          
          {/* Error banner */}
          {error && (
            <div className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">
                <span className="font-medium">Error:</span> {error}
              </p>
            </div>
          )}
          
          <ChatInput 
            onSendMessage={sendMessage} 
            disabled={isLoading}
            placeholder="Ask me anything about current events, general knowledge, or any topic..."
          />
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 px-4 py-2">
          <div className="max-w-4xl mx-auto">
            <p className="text-xs text-gray-500 text-center">
              Powered by GROQ, LangChain, and real-time data sources • 
              <span className="ml-1">Built with Next.js and FastAPI</span>
            </p>
          </div>
        </footer>
      </div>
    </>
  )
}
