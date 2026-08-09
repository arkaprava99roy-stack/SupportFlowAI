import React from 'react';
import { AgentCanvas3D } from './AgentCanvas3D';
import {
  ArrowRight,
  Shield,
  FileText,
  Cpu,
  Layers,
  Sparkles,
  GitBranch,
  Terminal,
  Activity,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Boxes,
  Database,
  Lock
} from 'lucide-react';

interface LandingPageProps {
  onEnterConsole: () => void;
  onOpenOrders?: () => void;
  onOpenAdmin?: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onEnterConsole,
  onOpenOrders,
  onOpenAdmin,
}) => {
  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-200 overflow-x-hidden relative selection:bg-teal-500/30 selection:text-teal-200">
      {/* Background Ambient Glowing Orbs */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[20%] w-[600px] h-[600px] rounded-full bg-teal-500/10 blur-[130px]" />
        <div className="absolute top-[30%] right-[10%] w-[500px] h-[500px] rounded-full bg-amber-500/08 blur-[140px]" />
        <div className="absolute bottom-[15%] left-[10%] w-[550px] h-[550px] rounded-full bg-blue-600/08 blur-[150px]" />
      </div>

      {/* Floating Navigation Header */}
      <header className="fixed top-4 left-1/2 -translate-x-1/2 w-[92%] max-w-5xl z-50">
        <nav className="glass-nav rounded-full px-5 py-2.5 flex items-center justify-between shadow-2xl border border-white/10">
          {/* Logo */}
          <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-teal-500 to-indigo-600 flex items-center justify-center text-white text-base shadow-glow-teal">
              🪐
            </div>
            <span className="font-serif text-lg tracking-tight font-semibold text-white">
              Support<span className="text-teal-400">Flow</span><span className="font-mono text-xs text-slate-400 ml-1">AI</span>
            </span>
          </div>

          {/* Nav Links */}
          <div className="hidden md:flex items-center gap-7 text-xs font-medium text-slate-400">
            <button onClick={() => scrollToSection('architecture')} className="hover:text-teal-300 transition-colors">
              Architecture
            </button>
            <button onClick={() => scrollToSection('capabilities')} className="hover:text-teal-300 transition-colors">
              Capabilities
            </button>
            <button onClick={() => scrollToSection('escalation')} className="hover:text-teal-300 transition-colors">
              Escalation
            </button>
            <button onClick={() => scrollToSection('pipeline')} className="hover:text-teal-300 transition-colors">
              Pipeline
            </button>
          </div>

          {/* CTA Console Button */}
          <button
            onClick={onEnterConsole}
            className="rounded-full bg-teal-500 hover:bg-teal-400 px-4 py-1.5 text-xs font-semibold text-slate-950 transition-all shadow-glow-teal hover:scale-105 active:scale-95 flex items-center gap-1.5"
          >
            <span>Open the Console</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </nav>
      </header>

      {/* Main Content Sections */}
      <main className="relative z-10 pt-28 sm:pt-36">
        {/* ======================================================== */}
        {/* 1. HERO SECTION */}
        {/* ======================================================== */}
        <section className="px-4 sm:px-6 max-w-5xl mx-auto text-center flex flex-col items-center min-h-[85vh] justify-center relative">
          {/* Top Badges */}
          <div className="flex flex-wrap items-center justify-center gap-2.5 mb-6 animate-fade-in">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[0.7rem] font-mono tracking-wider uppercase text-teal-300">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
              <span>Agentic Support Platform</span>
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[0.7rem] font-mono tracking-wider uppercase text-amber-300">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>v1.0 · LangGraph Ready</span>
            </div>
          </div>

          {/* Hero Headline */}
          <h1 className="font-serif text-5xl sm:text-7xl md:text-8xl font-normal tracking-tight text-white max-w-4xl leading-[0.95] mb-6 animate-fade-in-up">
            Watch the agent <br />
            <span className="italic font-normal bg-gradient-to-r from-teal-200 via-white to-amber-200 bg-clip-text text-transparent">
              think.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-sm sm:text-base text-slate-400 max-w-2xl leading-relaxed mb-8 font-light">
            SupportFlow AI routes every message through intent, retrieval, and risk agents — then resolves it, reviews it, or hands it to a human. The whole decision is visible, cinematic, and cited.
          </p>

          {/* Call to Actions */}
          <div className="flex flex-wrap items-center justify-center gap-3.5 mb-14">
            <button
              onClick={onEnterConsole}
              className="px-6 py-3 rounded-full bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 text-slate-950 font-semibold text-sm transition-all shadow-glow-amber hover:scale-105 active:scale-95 flex items-center gap-2"
            >
              <span>Enter the console</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => scrollToSection('architecture')}
              className="px-5 py-3 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-slate-200 text-sm font-medium transition-all hover:border-teal-500/40 flex items-center gap-2"
            >
              <GitBranch className="w-4 h-4 text-teal-400" />
              <span>See the agent graph</span>
            </button>
          </div>

          {/* Tech Spec Badges */}
          <div className="flex flex-wrap items-center justify-center gap-4 text-xs font-mono text-slate-400 mb-8">
            <div className="flex items-center gap-1.5 text-teal-400">
              <span className="w-2 h-2 rounded-full bg-teal-400 animate-ping" />
              <span>AGENT ONLINE</span>
            </div>
            <span className="text-slate-600">·</span>
            <span>FASTAPI</span>
            <span className="text-slate-600">·</span>
            <span>LANGGRAPH</span>
            <span className="text-slate-600">·</span>
            <span>FAISS VECTOR</span>
          </div>

          {/* Floating Ambient Live Capsule */}
          <div className="w-full max-w-md glass rounded-2xl p-3.5 border border-white/10 flex items-center justify-between text-left shadow-2xl animate-float">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-teal-400">
                <Activity className="w-3.5 h-3.5 animate-spin" style={{ animationDuration: '6s' }} />
              </div>
              <div>
                <div className="text-[0.7rem] font-mono tracking-widest uppercase text-slate-300 font-semibold">
                  SUPERVISOR · IDLE DRIFT
                </div>
                <div className="text-xs text-slate-400">
                  agent online · streaming ready
                </div>
              </div>
            </div>
            <div className="w-2 h-2 rounded-full bg-teal-400 shadow-glow-teal animate-pulse" />
          </div>
        </section>

        {/* ======================================================== */}
        {/* 2. THE AGENT GRAPH SECTION */}
        {/* ======================================================== */}
        <section id="architecture" className="py-24 px-4 sm:px-6 max-w-5xl mx-auto">
          <div className="mb-12">
            <div className="text-[0.7rem] font-mono tracking-widest uppercase text-teal-400 mb-2">
              THE AGENT GRAPH
            </div>
            <h2 className="font-serif text-3xl sm:text-5xl font-normal text-white mb-4 leading-tight">
              One supervisor. Three agents. One risk gate.
            </h2>
            <p className="text-sm sm:text-base text-slate-400 max-w-2xl leading-relaxed">
              Every message flows through a readable LangGraph pipeline. Each node is its own module; the graph definition stays one file, one diagram, zero mystery.
            </p>
          </div>

          <div className="space-y-3.5">
            {/* Node 01 */}
            <div className="glass-card rounded-2xl p-4 sm:p-5 flex items-center justify-between border border-white/10 hover:border-teal-500/40 transition-all">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[0.68rem] font-mono text-slate-400 uppercase tracking-wider">NODE 01</div>
                  <div className="text-base font-semibold text-white">Intent Agent</div>
                </div>
              </div>
              <div className="hidden sm:block text-xs font-mono text-slate-400">
                BILLING · REFUND · SHIPPING · SECURITY...
              </div>
              <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
            </div>

            {/* Node 02 */}
            <div className="glass-card rounded-2xl p-4 sm:p-5 flex items-center justify-between border border-white/10 hover:border-teal-500/40 transition-all">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[0.68rem] font-mono text-slate-400 uppercase tracking-wider">NODE 02</div>
                  <div className="text-base font-semibold text-white">RAG Agent</div>
                </div>
              </div>
              <div className="hidden sm:block text-xs font-mono text-slate-400">
                FAISS retrieval + metadata chunks
              </div>
              <span className="w-2 h-2 rounded-full bg-blue-400" />
            </div>

            {/* Node 03 */}
            <div className="glass-card rounded-2xl p-4 sm:p-5 flex items-center justify-between border border-white/10 hover:border-teal-500/40 transition-all">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                  <Boxes className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[0.68rem] font-mono text-slate-400 uppercase tracking-wider">NODE 03</div>
                  <div className="text-base font-semibold text-white">Memory Agent</div>
                </div>
              </div>
              <div className="hidden sm:block text-xs font-mono text-slate-400">
                conversation context across sessions
              </div>
              <span className="w-2 h-2 rounded-full bg-purple-400" />
            </div>

            {/* Node 04 */}
            <div className="glass-card rounded-2xl p-4 sm:p-5 flex items-center justify-between border border-white/10 hover:border-amber-500/40 transition-all">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <Shield className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[0.68rem] font-mono text-slate-400 uppercase tracking-wider">NODE 04</div>
                  <div className="text-base font-semibold text-white">Risk Analysis</div>
                </div>
              </div>
              <div className="hidden sm:block text-xs font-mono text-amber-300/80">
                LOW / MEDIUM / HIGH scoring
              </div>
              <span className="w-2 h-2 rounded-full bg-amber-400" />
            </div>
          </div>
        </section>

        {/* ======================================================== */}
        {/* 3. CAPABILITIES SECTION */}
        {/* ======================================================== */}
        <section id="capabilities" className="py-24 px-4 sm:px-6 max-w-5xl mx-auto">
          <div className="mb-12">
            <div className="text-[0.7rem] font-mono tracking-widest uppercase text-teal-400 mb-2">
              PLATFORM CAPABILITIES
            </div>
            <h2 className="font-serif text-3xl sm:text-5xl font-normal text-white mb-4 leading-tight">
              Deterministic safety, grounded answers.
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="glass-card rounded-3xl p-6 sm:p-7 border border-white/10 flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-teal-300 mb-6">
                  <FileText className="w-6 h-6" />
                </div>
                <h3 className="font-serif text-2xl font-normal text-white mb-3">
                  Every answer, with its source
                </h3>
                <p className="text-xs sm:text-sm text-slate-400 leading-relaxed font-light">
                  RAG chunks carry document, category, and version metadata. Answers surface citations as light-edge chips — nothing the agent says floats without a source.
                </p>
              </div>
              <div className="pt-6 flex items-center gap-2 text-xs font-mono text-teal-400">
                <span>📄 Policy frontmatter chunks</span>
              </div>
            </div>

            {/* Card 2 */}
            <div className="glass-card rounded-3xl p-6 sm:p-7 border border-white/10 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-1.5 mb-6">
                  <span className="px-2 py-0.5 rounded-md bg-teal-500/10 border border-teal-500/30 text-[0.65rem] font-mono text-teal-300">Auto-resolve</span>
                  <span className="px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/30 text-[0.65rem] font-mono text-amber-300">AI + review</span>
                  <span className="px-2 py-0.5 rounded-md bg-rose-500/10 border border-rose-500/30 text-[0.65rem] font-mono text-rose-300">Human handoff</span>
                </div>
                <h3 className="font-serif text-2xl font-normal text-white mb-3">
                  Risk decides the room lighting
                </h3>
                <p className="text-xs sm:text-sm text-slate-400 leading-relaxed font-light">
                  LOW resolves instantly. MEDIUM attempts resolution and flags for review. HIGH cuts the automation and calls a human — escalation is a design decision, not a failure.
                </p>
              </div>
              <div className="pt-6 flex items-center gap-2 text-xs font-mono text-amber-400">
                <span>⚖️ 3-Tier safety taxonomy</span>
              </div>
            </div>

            {/* Card 3 */}
            <div className="glass-card rounded-3xl p-6 sm:p-7 border border-white/10 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-1.5 mb-6">
                  <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[0.65rem] font-mono text-slate-300">Authorization</span>
                  <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[0.65rem] font-mono text-slate-300">Guardrails</span>
                  <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[0.65rem] font-mono text-slate-300">Audit log</span>
                </div>
                <h3 className="font-serif text-2xl font-normal text-white mb-3">
                  Tool calling with guardrails
                </h3>
                <p className="text-xs sm:text-sm text-slate-400 leading-relaxed font-light">
                  Order lookups, cancellations, and tickets run through explicit authorization checks and a prompt-injection guardrail. Every tool call is logged for the audit trail.
                </p>
              </div>
              <div className="pt-6 flex items-center gap-2 text-xs font-mono text-teal-400">
                <span>🛡️ Non-repudiation logging</span>
              </div>
            </div>
          </div>
        </section>

        {/* ======================================================== */}
        {/* 4. ESCALATION & RISK LADDER */}
        {/* ======================================================== */}
        <section id="escalation" className="py-24 px-4 sm:px-6 max-w-5xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="text-[0.7rem] font-mono tracking-widest uppercase text-amber-400 mb-2">
                ESCALATION POLICY & RISK LADDER
              </div>
              <h2 className="font-serif text-3xl sm:text-5xl font-normal text-white mb-4 leading-tight">
                Every message has its severity.
              </h2>
              <p className="text-sm text-slate-400 leading-relaxed font-light mb-8">
                Low-risk requests resolve on sight. Medium ones get a confirmation step and a review flag. High-risk moments summon a human, instantly.
              </p>

              <div className="space-y-3">
                <div className="glass-card rounded-2xl p-4 border border-teal-500/30 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-200">LOW — auto-resolve</span>
                  <span className="px-2.5 py-1 rounded-full bg-teal-500/20 text-teal-300 text-xs font-mono">● RISK LOW</span>
                </div>
                <div className="glass-card rounded-2xl p-4 border border-amber-500/30 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-200">MEDIUM — AI resolves, team reviews</span>
                  <span className="px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-300 text-xs font-mono">● RISK MEDIUM</span>
                </div>
                <div className="glass-card rounded-2xl p-4 border border-rose-500/30 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-200">HIGH — human escalation</span>
                  <span className="px-2.5 py-1 rounded-full bg-rose-500/20 text-rose-300 text-xs font-mono">● RISK HIGH</span>
                </div>
              </div>
            </div>

            {/* 3D Visual in Hero Card */}
            <div className="glass rounded-3xl p-6 border border-white/10 flex flex-col items-center justify-center relative overflow-hidden">
              <div className="w-full flex items-center justify-between mb-4">
                <div className="text-xs font-mono text-slate-400">HUD TELEMETRY</div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
                  <span className="text-[0.7rem] font-mono text-teal-300">LIVE FEED</span>
                </div>
              </div>
              <AgentCanvas3D mode="idle" size={260} />
              <div className="text-center mt-4">
                <div className="text-xs font-mono text-slate-300">LangGraph State Visualizer</div>
                <div className="text-[0.7rem] text-slate-500 font-mono">Deterministic routing with memory checkpoints</div>
              </div>
            </div>
          </div>
        </section>

        {/* ======================================================== */}
        {/* 5. THE FLOW PIPELINE */}
        {/* ======================================================== */}
        <section id="pipeline" className="py-24 px-4 sm:px-6 max-w-5xl mx-auto text-center">
          <div className="mb-14">
            <div className="text-[0.7rem] font-mono tracking-widest uppercase text-teal-400 mb-2">
              THE FLOW
            </div>
            <h2 className="font-serif text-3xl sm:text-5xl font-normal text-white mb-4">
              Six steps. Zero black boxes.
            </h2>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5 relative">
            {[
              { num: '01', title: 'Message', desc: 'Customer message arrives over the API' },
              { num: '02', title: 'Intent', desc: 'Classifier labels request across 8 intents' },
              { num: '03', title: 'Risk', desc: 'Content + intent scored LOW / MEDIUM / HIGH' },
              { num: '04', title: 'Route', desc: 'Auto-resolve, AI+review, or human escalation' },
              { num: '05', title: 'Act', desc: 'Tools execute with auth checks + logging' },
              { num: '06', title: 'Respond', desc: 'Cited answer streams back to customer' },
            ].map((step, idx) => (
              <div
                key={step.num}
                className="glass-card rounded-2xl p-4 border border-white/10 hover:border-teal-500/40 text-left flex flex-col justify-between h-40 transition-all hover:scale-105"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-teal-400 font-bold">{step.num}</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                </div>
                <div>
                  <h4 className="font-serif text-base text-white mb-1 font-semibold">{step.title}</h4>
                  <p className="text-[0.7rem] text-slate-400 leading-snug font-light">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ======================================================== */}
        {/* 6. FOOTER CTA SECTION */}
        {/* ======================================================== */}
        <section className="py-28 px-4 sm:px-6 max-w-4xl mx-auto text-center">
          <div className="w-10 h-10 rounded-full bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-xl mx-auto mb-6 shadow-glow-teal">
            🪐
          </div>

          <h2 className="font-serif text-4xl sm:text-6xl font-normal text-white mb-4">
            Every risk, with a light on it.
          </h2>
          <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto leading-relaxed mb-8 font-light">
            Step into the live console — send a message and watch the agent reason, retrieve, and act in real time.
          </p>

          <button
            onClick={onEnterConsole}
            className="px-7 py-3.5 rounded-full bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 text-slate-950 font-semibold text-sm transition-all shadow-glow-amber hover:scale-105 active:scale-95 inline-flex items-center gap-2 mb-12"
          >
            <span>Open the console</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3 text-xs font-mono text-slate-400">
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10">● React + Vite</span>
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10">● FastAPI backend</span>
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10">● JWT auth</span>
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10">● Docker ready</span>
          </div>
        </section>
      </main>

      {/* Subtle Bottom Footer */}
      <footer className="border-t border-white/05 py-6 text-center text-xs font-mono text-slate-600">
        SupportFlow AI · Built with LangGraph, Vector RAG & FastAPI
      </footer>
    </div>
  );
};
