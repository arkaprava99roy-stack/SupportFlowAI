import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import { useChat } from './context/ChatContext';
import { Sidebar } from './components/Sidebar';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { OrdersModal } from './components/OrdersModal';
import { AdminModal } from './components/AdminModal';
import { AuthScreen } from './components/AuthScreen';
import { Menu, Bot, Sparkles, Shield, AlertCircle, RefreshCw, MessageSquare } from 'lucide-react';

const MainLayout: React.FC = () => {
  const { messages, isStreaming, streamingContent, error, activeConversationId } = useChat();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isOrdersOpen, setIsOrdersOpen] = useState(false);
  const [isAdminOpen, setIsAdminOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      {/* Sidebar Navigation */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onOpenOrders={() => setIsOrdersOpen(true)}
        onOpenAdmin={() => setIsAdminOpen(true)}
      />

      {/* Main Chat Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-surface-400/40 relative">
        {/* Top Navbar */}
        <header className="h-14 border-b border-slate-800/80 bg-surface-300/80 backdrop-blur-md px-4 flex items-center justify-between z-10 shrink-0">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="lg:hidden p-2 text-slate-400 hover:text-white rounded-lg hover:bg-surface-200 transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <h2 className="text-xs font-semibold text-white tracking-tight">
                {activeConversationId ? `Session Thread (${activeConversationId})` : 'Active Support Assistant'}
              </h2>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsOrdersOpen(true)}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-surface-200/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/60 transition-colors"
            >
              📦 My Orders
            </button>
            <button
              onClick={() => setIsAdminOpen(true)}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 border border-purple-500/30 transition-colors"
            >
              🛡️ Admin HITL
            </button>
          </div>
        </header>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 max-w-4xl w-full mx-auto">
          {messages.length === 0 && !isStreaming && (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 py-16 animate-fade-in">
              <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-2xl shadow-brand-500/30">
                <Bot className="w-9 h-9" />
              </div>
              <div className="max-w-md space-y-1.5">
                <h3 className="text-lg font-bold text-white tracking-tight">Welcome to SupportFlow AI</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Ask about your orders, package tracking, return policies, or account security. All answers are verified against grounded knowledge documents.
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2.5 shadow-lg">
              <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {/* Streaming Bubble */}
          {isStreaming && (
            <div className="flex justify-start animate-fade-in">
              <div className="flex items-start max-w-2xl space-x-3.5">
                <div className="w-9 h-9 rounded-2xl bg-surface-100 border border-slate-700/60 text-brand-400 flex items-center justify-center shrink-0 shadow-lg">
                  <Bot className="w-5 h-5 animate-pulse" />
                </div>
                <div className="p-4 rounded-2xl bg-surface-100/90 border border-slate-700/60 text-slate-200 text-sm leading-relaxed rounded-tl-sm shadow-xl space-y-2">
                  <div className="whitespace-pre-wrap">{streamingContent || 'SupportFlow AI is evaluating your inquiry...'}</div>
                  <div className="flex items-center space-x-1.5 text-xs text-brand-400 font-medium pt-1">
                    <span className="w-2 h-2 rounded-full bg-brand-400 animate-ping" />
                    <span>Streaming response...</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <ChatInput />
      </main>

      {/* Modals */}
      <OrdersModal isOpen={isOrdersOpen} onClose={() => setIsOrdersOpen(false)} />
      <AdminModal isOpen={isAdminOpen} onClose={() => setIsAdminOpen(false)} />
    </div>
  );
};

export const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center text-slate-400 space-y-3">
        <RefreshCw className="w-7 h-7 animate-spin text-brand-400" />
        <p className="text-xs">Loading SupportFlow AI Platform...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthScreen />;
  }

  return <MainLayout />;
};
