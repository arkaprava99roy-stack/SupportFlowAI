import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import { useChat } from './context/ChatContext';
import { LandingPage } from './components/LandingPage';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { AgentCanvas3D, AgentStateMode } from './components/AgentCanvas3D';
import { OrdersModal } from './components/OrdersModal';
import { AdminModal } from './components/AdminModal';
import { ConversationSidebar } from './components/ConversationSidebar';
import { AuthScreen } from './components/AuthScreen';
import {
  ArrowLeft,
  Shield,
  Bot,
  RefreshCw,
  AlertCircle,
  Package,
  Layers,
  Sparkles
} from 'lucide-react';

const STARTER_PROMPTS = [
  'Where is my order #4821?',
  'Cancel my order — I found it cheaper',
  'Someone accessed my account last night',
];

export const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const { messages, isStreaming, streamingContent, error, activeConversationId, sendMessage } = useChat();

  const [viewMode, setViewMode] = useState<'landing' | 'console'>('landing');
  const [isOrdersOpen, setIsOrdersOpen] = useState(false);
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll message stream to bottom smoothly
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  // Determine Agent 3D visual state mode
  const lastMessage = messages[messages.length - 1];
  let agentMode: AgentStateMode = 'idle';
  if (isStreaming) {
    agentMode = 'thinking';
  } else if (lastMessage?.risk_level === 'HIGH' || lastMessage?.is_escalated) {
    agentMode = 'escalated';
  }

  // Calculate resolution mix metrics
  const autoResolvedCount = Math.max(1, messages.filter(m => m.sender === 'assistant' && (!m.risk_level || m.risk_level === 'LOW')).length);
  const reviewCount = Math.max(2, messages.filter(m => m.sender === 'assistant' && m.risk_level === 'MEDIUM').length);
  const escalatedCount = Math.max(1, messages.filter(m => m.sender === 'assistant' && (m.risk_level === 'HIGH' || m.is_escalated)).length);
  const totalCount = autoResolvedCount + reviewCount + escalatedCount;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#07090e] flex flex-col items-center justify-center text-slate-400 space-y-4">
        <div className="w-10 h-10 rounded-full bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-teal-400 shadow-glow-teal animate-spin">
          🪐
        </div>
        <p className="text-xs font-mono tracking-wider uppercase text-slate-400">Loading SupportFlow AI Platform...</p>
      </div>
    );
  }

  // If user is on the Landing Page showcase view
  if (viewMode === 'landing') {
    return (
      <>
        <LandingPage
          onEnterConsole={() => setViewMode('console')}
          onOpenOrders={() => setIsOrdersOpen(true)}
          onOpenAdmin={() => setIsAdminOpen(true)}
        />
        <OrdersModal isOpen={isOrdersOpen} onClose={() => setIsOrdersOpen(false)} />
        <AdminModal isOpen={isAdminOpen} onClose={() => setIsAdminOpen(false)} />
      </>
    );
  }

  // Console Mode Layout
  return (
    <div className="min-h-screen bg-[#07090e] text-slate-200 flex flex-col justify-between overflow-x-hidden relative selection:bg-teal-500/30 selection:text-teal-200">
      {/* Conversation History Sidebar */}
      <ConversationSidebar isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen((p) => !p)} />

      {/* Background Glow */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-5%] right-[15%] w-[550px] h-[550px] rounded-full bg-teal-500/08 blur-[140px]" />
        <div className="absolute bottom-[5%] left-[10%] w-[500px] h-[500px] rounded-full bg-blue-600/06 blur-[150px]" />
      </div>

      {/* Top Floating Console Bar — shifts right when sidebar is open */}
      <header className={`relative z-30 pt-4 px-4 sm:px-8 max-w-7xl w-full mx-auto transition-all duration-300 ${isSidebarOpen ? 'pl-[300px] sm:pl-[308px]' : ''}`}>
        <div className="flex items-center justify-between">
          {/* Back Button */}
          <button
            onClick={() => setViewMode('landing')}
            className="glass rounded-full px-4 py-2 text-xs font-medium text-slate-300 hover:text-white border border-white/10 hover:border-teal-500/40 transition-all flex items-center gap-2 hover:scale-105 active:scale-95"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to overview</span>
          </button>

          {/* Center Logo */}
          <div className="hidden sm:flex items-center gap-2 cursor-pointer" onClick={() => setViewMode('landing')}>
            <span className="text-base">🪐</span>
            <span className="font-serif text-lg tracking-tight font-semibold text-white">
              Support<span className="text-teal-400">Flow</span><span className="font-mono text-xs text-slate-400 ml-1">AI</span>
            </span>
          </div>

          {/* Right Status Indicators & Drawers */}
          <div className="flex items-center gap-2.5">
            <div className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[0.68rem] font-mono text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
              <span>SESSION #{activeConversationId ? activeConversationId.slice(-6).toUpperCase() : 'SF-2041'}</span>
            </div>

            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[0.68rem] font-mono text-teal-300">
              <span className={`w-1.5 h-1.5 rounded-full ${agentMode === 'thinking' ? 'bg-amber-400 animate-ping' : agentMode === 'escalated' ? 'bg-rose-400 animate-pulse' : 'bg-teal-400'}`} />
              <span className="uppercase">{agentMode === 'thinking' ? 'THINKING PULSE' : agentMode === 'escalated' ? 'ALERT FLARE' : 'AGENT IDLE'}</span>
            </div>

            <button
              onClick={() => setIsOrdersOpen(true)}
              className="glass rounded-full px-3.5 py-1.5 text-xs font-mono text-slate-300 hover:text-white border border-white/10 hover:border-teal-500/40 transition-all"
            >
              📦 Orders
            </button>

            <button
              onClick={() => setIsAdminOpen(true)}
              className="glass rounded-full px-3.5 py-1.5 text-xs font-mono text-purple-300 hover:text-white border border-purple-500/30 hover:border-purple-500/60 transition-all"
            >
              🛡️ Admin
            </button>
          </div>
        </div>
      </header>

      {/* Main Console Split View — shifts right when sidebar open */}
      <main className={`relative z-10 max-w-7xl w-full mx-auto px-4 sm:px-8 py-5 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch transition-all duration-300 ${isSidebarOpen ? 'pl-[300px] sm:pl-[308px]' : ''}`}>
        {/* ======================================================== */}
        {/* LEFT COLUMN: CHAT CONSOLE & PIEPLINE TRACER (7 COLS) */}
        {/* ======================================================== */}
        <div className="lg:col-span-7 glass rounded-3xl border border-white/10 flex flex-col h-[82vh] overflow-hidden shadow-2xl relative">
          {/* Header */}
          <div className="px-5 py-3.5 border-b border-white/08 flex items-center justify-between bg-white/[0.02]">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-teal-500/15 border border-teal-500/30 flex items-center justify-center text-teal-400">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white tracking-tight">SupportFlow Agent</h2>
                <div className="text-[0.68rem] font-mono text-slate-400">
                  supervisor · intent · rag · memory · risk-gate
                </div>
              </div>
            </div>

            <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-teal-500/10 border border-teal-500/30 text-[0.65rem] font-mono text-teal-300">
              <Shield className="w-3 h-3 text-teal-400" />
              <span>GUARDRAILS ON</span>
            </div>
          </div>

          {/* Messages Stream Body */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
            {/* Empty State Showcase */}
            {messages.length === 0 && !isStreaming && (
              <div className="h-full flex flex-col items-center justify-center text-center space-y-5 py-8 animate-fade-in">
                <div className="w-12 h-12 rounded-full bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-2xl shadow-glow-teal">
                  🪐
                </div>

                <div className="max-w-sm space-y-2">
                  <h3 className="font-serif text-3xl text-white font-normal">Watch the agent think.</h3>
                  <p className="text-xs text-slate-400 leading-relaxed font-light">
                    Every message routes through intent, risk, retrieval and tools. Try one of these — each shows a different escalation path.
                  </p>
                </div>

                {/* Quick Starter Prompts */}
                <div className="flex flex-col gap-2 w-full max-w-md pt-2">
                  {STARTER_PROMPTS.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => sendMessage(prompt)}
                      className="glass-card rounded-2xl px-4 py-2.5 text-xs text-slate-300 hover:text-white border border-white/10 hover:border-teal-500/50 text-left transition-all hover:scale-[1.02] active:scale-[0.98]"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Error Message Alert */}
            {error && (
              <div className="p-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2.5 shadow-lg">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            {/* Rendered Messages */}
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}

            {/* Active Streaming Node Pulse */}
            {isStreaming && (
              <div className="flex flex-col space-y-3 w-full max-w-2xl animate-fade-in">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-xs shadow-glow-amber animate-spin">
                    🪐
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[0.68rem] font-mono font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    ● EVALUATING INTENT & RISKS
                  </span>
                </div>
                <div className="glass-card rounded-2xl p-4 sm:p-5 border border-white/10 text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {streamingContent || 'SupportFlow agent is executing graph nodes...'}
                </div>
                <div className="px-2 flex items-center gap-2 text-xs font-mono text-amber-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
                  <span>Processing LangGraph state transitions...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Bottom Chat Input */}
          <ChatInput />
        </div>

        {/* ======================================================== */}
        {/* RIGHT COLUMN: 3D CANVAS & HUD METRICS (5 COLS) */}
        {/* ======================================================== */}
        <div className="lg:col-span-5 hidden lg:flex flex-col space-y-4 h-[82vh]">
          {/* 3D Wireframe HUD Card */}
          <div className="glass rounded-3xl border border-white/10 p-6 flex flex-col items-center justify-center relative overflow-hidden flex-1 shadow-2xl">
            {/* Top State Badge */}
            <div className="absolute top-4 right-4">
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[0.68rem] font-mono font-medium ${agentMode === 'thinking' ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30' : agentMode === 'escalated' ? 'bg-rose-500/15 text-rose-300 border border-rose-500/30' : 'bg-teal-500/15 text-teal-300 border border-teal-500/30'}`}>
                <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                {agentMode === 'thinking' ? 'THINKING PULSE' : agentMode === 'escalated' ? 'ALERT FLARE' : 'CALM DRIFT'}
              </span>
            </div>

            {/* 3D Canvas Geometry */}
            <AgentCanvas3D mode={agentMode} size={280} />
          </div>

          {/* Resolution Mix Widget */}
          <div className="glass-card rounded-3xl p-5 border border-white/10 space-y-3 shadow-xl">
            <div className="text-[0.68rem] font-mono tracking-wider uppercase text-slate-400">
              👥 RESOLUTION MIX · DEMO SET
            </div>

            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <div className="font-serif text-2xl text-teal-300 font-semibold">{autoResolvedCount}</div>
                <div className="text-[0.65rem] text-slate-400 font-mono">auto-resolved</div>
              </div>
              <div>
                <div className="font-serif text-2xl text-amber-300 font-semibold">{reviewCount}</div>
                <div className="text-[0.65rem] text-slate-400 font-mono">AI + review</div>
              </div>
              <div>
                <div className="font-serif text-2xl text-rose-400 font-semibold">{escalatedCount}</div>
                <div className="text-[0.65rem] text-slate-400 font-mono">escalated</div>
              </div>
            </div>

            {/* Multi-segment Colored Bar */}
            <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden flex gap-0.5">
              <div
                className="bg-teal-400 rounded-l-full transition-all duration-500"
                style={{ width: `${(autoResolvedCount / totalCount) * 100}%` }}
              />
              <div
                className="bg-amber-400 transition-all duration-500"
                style={{ width: `${(reviewCount / totalCount) * 100}%` }}
              />
              <div
                className="bg-rose-400 rounded-r-full transition-all duration-500"
                style={{ width: `${(escalatedCount / totalCount) * 100}%` }}
              />
            </div>
          </div>

          {/* Escalation Policy Quick HUD */}
          <div className="glass-card rounded-3xl p-5 border border-white/10 space-y-2.5 text-xs text-slate-300 font-light shadow-xl">
            <div className="text-[0.68rem] font-mono tracking-wider uppercase text-slate-400">
              🛡️ ESCALATION POLICY
            </div>
            <div className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 mt-1.5 shrink-0" />
              <span><strong className="text-slate-100 font-medium">LOW</strong> — auto-resolve with citations</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
              <span><strong className="text-slate-100 font-medium">MEDIUM</strong> — confirmation step, audit-logged, flagged for review</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
              <span><strong className="text-slate-100 font-medium">HIGH</strong> — ticket created, human handoff, no silent DB writes</span>
            </div>
          </div>
        </div>
      </main>

      {/* Modals */}
      <OrdersModal isOpen={isOrdersOpen} onClose={() => setIsOrdersOpen(false)} />
      <AdminModal isOpen={isAdminOpen} onClose={() => setIsAdminOpen(false)} />
    </div>
  );
};
