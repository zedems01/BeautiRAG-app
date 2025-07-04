'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Bot } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  isLoading?: boolean; 
}

interface ChatInterfaceProps {
  selectedModel: string;
  apiKey: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ selectedModel, apiKey }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState<string>('');
  const [isBotLoading, setIsBotLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (inputValue.trim() === '' || isBotLoading) return;

    const userMessageText = inputValue;
    const newUserMessage: Message = {
      id: Date.now(),
      text: userMessageText,
      sender: 'user',
    };

    // Add messages
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setInputValue('');
    setIsBotLoading(true);

    const loadingBotMessage: Message = {
      id: Date.now() + 1,
      text: '...',
      sender: 'bot',
      isLoading: true,
    };
    setMessages(prevMessages => [...prevMessages, loadingBotMessage]);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/query/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessageText,
          model_name: selectedModel,
          api_key: apiKey || null,
        }),
      });

      const result = await response.json();

      let botResponseText: string;
      if (!response.ok) {
        console.error('Query error:', result.detail);
        botResponseText = `Error: ${result.detail || 'Failed to get response'}`;
      } else {
        botResponseText = result.response;
      }

      const finalBotMessage: Message = {
        id: loadingBotMessage.id,
        text: botResponseText,
        sender: 'bot',
      };

      setMessages(prevMessages =>
        prevMessages.map(msg => (msg.id === finalBotMessage.id ? finalBotMessage : msg))
      );

    } catch (error) {
      console.error('Failed to fetch query response:', error);
      const errorBotMessage: Message = {
        id: loadingBotMessage.id,
        text: `Error: ${error instanceof Error ? error.message : 'Network error'}`,
        sender: 'bot',
      };
      setMessages(prevMessages =>
        prevMessages.map(msg => (msg.id === errorBotMessage.id ? errorBotMessage : msg))
      );
    } finally {
      setIsBotLoading(false);
    }
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(event.target.value);
    event.target.style.height = 'inherit';
    event.target.style.height = `${event.target.scrollHeight}px`;
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[76vh] bg-gray-850 border border-gray-700 p-4 rounded-lg shadow-md text-gray-200">
      <h2 className="text-xl font-semi-bold mb-4 text-white">Chat with BeautiRAG</h2>

      {/* Message Display Area */}
      <div className={`flex-grow mb-4 pr-3 space-y-4 ${messages.length > 0 ? 'overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800' : 'overflow-hidden'}`}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Bot className="h-12 w-12 text-gray-500 mb-2" />
            <p className="text-lg font-semi-bold text-gray-400">No messages yet</p>
            <p className="text-sm text-gray-500">Upload some documents and start asking questions.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-sm lg:max-w-lg px-4 py-2 rounded-xl shadow ${msg.sender === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-gray-700 text-gray-200 rounded-bl-none'} ${msg.isLoading ? 'animate-pulse' : ''}`
              }
              >
                {msg.text}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex items-end border-t border-gray-700 pt-4 mt-2">
        <textarea
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="Ask BeautiRAG anything..."
          rows={1}
          className="flex-grow px-3 py-2 mr-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-white placeholder-gray-500 resize-none scrollbar-thin scrollbar-thumb-gray-500 scrollbar-track-gray-700"
          style={{ maxHeight: '100px' }}
          disabled={isBotLoading}
        />
        <button
          onClick={handleSendMessage}
          className="flex-shrink-0 px-5 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-850 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150"
          disabled={!inputValue.trim() || isBotLoading}
        >
          {isBotLoading ? (
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.886l4.108 4.108a1 1 0 010 1.414l-4.108 4.108A1 1 0 119.48 11.104l1.886-1.887H4a1 1 0 110-2h7.365l-1.886-1.886a1 1 0 111.414-1.415z"/>
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface; 