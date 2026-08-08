import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Loader2, Package, RefreshCw, XCircle, ShieldCheck } from 'lucide-react';
import { useChat } from '../context/ChatContext';

const QUICK_PROMPTS = [
  { label: '📦 Track Order ORD-1001', text: 'What is the current status and tracking number for my order ORD-1001?' },
  { label: '💰 Refund Guarantee', text: 'What is your 30-day refund policy and process for returned items?' },
  { label: '❌ Cancel Order ORD-1001', text: 'Please cancel my order ORD-1001' },
  { label: '🔒 Two-Factor Auth', text: 'How do I enable two-factor authentication and reset my password?' },
];

export const ChatInput: React.FC = () => {
  const { sendMessage, isStreaming } = useChat();
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleQuickPrompt = (promptText: string) => {
    if (isStreaming) return;
    sendMessage(promptText);
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-5 pt-2">
      {/* Quick Prompts Carousel */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-3 no-scrollbar">
        {QUICK_PROMPTS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleQuickPrompt(q.text)}
            disabled={isStreaming}
            className="inline-flex items-center px-3 py-1.5 rounded-xl text-xs font-medium bg-surface-100/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/60 hover:border-brand-500/50 whitespace-nowrap transition-all shadow-sm shrink-0 disabled:opacity-50"
          >
            {q.label}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={handleSubmit}
        className="relative flex items-end bg-surface-100/90 border border-slate-700/80 focus-within:border-brand-500/80 focus-within:ring-2 focus-within:ring-brand-500/20 rounded-2xl p-2 shadow-2xl transition-all"
      >
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your order, return policies, or account..."
          disabled={isStreaming}
          className="w-full bg-transparent text-slate-100 placeholder-slate-400 text-sm px-3 py-2 resize-none focus:outline-none max-h-36 disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={!input.trim() || isStreaming}
          className="p-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white disabled:bg-slate-800 disabled:text-slate-500 transition-all shrink-0 ml-2 shadow-md shadow-brand-500/20"
        >
          {isStreaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </form>

      <p className="text-center text-[11px] text-slate-400 mt-2">
        SupportFlow AI Agentic Platform • Verified Knowledge Grounding & Smart Escalation
      </p>
    </div>
  );
};
