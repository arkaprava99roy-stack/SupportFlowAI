import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Bot, Sparkles, Shield, ArrowRight, Loader2, Lock, Mail, User } from 'lucide-react';

export const AuthScreen: React.FC = () => {
  const { login, register, loginDemo, isLoading } = useAuth();
  const [isLoginTab, setIsLoginTab] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      if (isLoginTab) {
        await login(email, password);
      } else {
        await register(name, email, password);
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-background relative overflow-hidden">
      {/* Background ambient lighting effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-surface-100/90 border border-slate-700/80 rounded-3xl shadow-2xl overflow-hidden backdrop-blur-xl animate-slide-up z-10">
        {/* Top Branding Banner */}
        <div className="px-8 pt-8 pb-6 text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 mx-auto flex items-center justify-center text-white shadow-xl shadow-brand-500/30">
            <Bot className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">SupportFlow AI</h2>
            <p className="text-xs text-slate-400 mt-1">Portfolio-grade Agentic Customer Support Platform</p>
          </div>
        </div>

        {/* 1-Click Demo Login Highlight */}
        <div className="px-8 pb-4">
          <button
            onClick={loginDemo}
            disabled={isLoading}
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-600 hover:from-brand-500 hover:to-purple-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/25 flex items-center justify-center space-x-2 transition-all group border border-brand-400/30"
          >
            <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
            <span>1-Click Demo Login (Alex Mercer)</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
        </div>

        <div className="flex items-center my-2 px-8">
          <div className="flex-1 border-t border-slate-700/60" />
          <span className="px-3 text-[11px] text-slate-400 font-mono uppercase">or sign in with email</span>
          <div className="flex-1 border-t border-slate-700/60" />
        </div>

        {/* Tab Switcher */}
        <div className="flex px-8 pt-2 pb-4">
          <div className="flex w-full p-1 bg-surface-200 rounded-xl border border-slate-700/60 text-xs font-medium">
            <button
              type="button"
              onClick={() => {
                setIsLoginTab(true);
                setError(null);
              }}
              className={`flex-1 py-2 rounded-lg transition-all ${
                isLoginTab ? 'bg-brand-600 text-white font-semibold shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setIsLoginTab(false);
                setError(null);
              }}
              className={`flex-1 py-2 rounded-lg transition-all ${
                !isLoginTab ? 'bg-brand-600 text-white font-semibold shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              Create Account
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-8 pb-8 space-y-4">
          {error && (
            <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs">
              {error}
            </div>
          )}

          {!isLoginTab && (
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-300">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Sarah Miller"
                  className="w-full bg-surface-200/80 border border-slate-700 rounded-xl px-10 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
                />
              </div>
            </div>
          )}

          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-300">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="customer@example.com"
                className="w-full bg-surface-200/80 border border-slate-700 rounded-xl px-10 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-300">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-surface-200/80 border border-slate-700 rounded-xl px-10 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all flex items-center justify-center space-x-2"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>{isLoginTab ? 'Sign In' : 'Create Account'}</span>}
          </button>
        </form>
      </div>
    </div>
  );
};
