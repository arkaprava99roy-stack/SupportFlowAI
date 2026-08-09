import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Loader2 } from 'lucide-react';
import { useChat } from '../context/ChatContext';

export const ChatInput: React.FC = () => {
  const { sendMessage, isStreaming } = useChat();
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
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

  return (
    <div className="w-full max-w-2xl mx-auto px-2 pb-4 pt-1">
      {/* Input Container */}
      <form
        onSubmit={handleSubmit}
        className="glass rounded-2xl border border-white/10 focus-within:border-teal-500/50 focus-within:ring-2 focus-within:ring-teal-500/20 p-2 flex items-center transition-all shadow-2xl"
      >
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about an order, a refund, an account..."
          disabled={isStreaming}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-400 text-sm px-3 py-1.5 resize-none focus:outline-none max-h-32 disabled:opacity-50 font-normal"
        />

        <button
          type="submit"
          disabled={!input.trim() || isStreaming}
          className="w-9 h-9 rounded-xl bg-teal-500 hover:bg-teal-400 disabled:bg-white/5 text-slate-950 disabled:text-slate-600 flex items-center justify-center transition-all shrink-0 ml-1.5 shadow-glow-teal disabled:shadow-none hover:scale-105 active:scale-95"
          aria-label="Send message"
        >
          {isStreaming ? <Loader2 className="w-4 h-4 animate-spin text-teal-300" /> : <ArrowUp className="w-4 h-4 stroke-[2.5]" />}
        </button>
      </form>

      <div className="flex items-center justify-center gap-2 mt-2 text-[0.68rem] font-mono text-slate-400 tracking-wider uppercase">
        <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
        <span>CONNECTED TO FASTAPI /api/chat/stream · SSE STREAMING</span>
      </div>
    </div>
  );
};

