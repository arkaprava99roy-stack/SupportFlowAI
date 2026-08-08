import React from 'react';
import { useChat } from '../context/ChatContext';
import { useAuth } from '../context/AuthContext';
import {
  MessageSquarePlus,
  MessageSquare,
  Package,
  ShieldCheck,
  LogOut,
  Trash2,
  Sparkles,
  ChevronRight,
  Bot,
} from 'lucide-react';

interface SidebarProps {
  onOpenOrders: () => void;
  onOpenAdmin: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onOpenOrders, onOpenAdmin, isOpen, onClose }) => {
  const { conversations, activeConversationId, selectConversation, startNewConversation, deleteConversation } = useChat();
  const { user, logout } = useAuth();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-30 bg-black/70 backdrop-blur-sm lg:hidden animate-fade-in"
        />
      )}

      {/* Sidebar Panel */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-40 w-72 bg-surface-300 border-r border-slate-800/80 flex flex-col justify-between transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Top Header & Brand */}
        <div className="p-4 space-y-4">
          <div className="flex items-center justify-between px-2">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-brand-500/25">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-sm font-bold text-white tracking-tight leading-none">SupportFlow AI</h1>
                <span className="text-[10px] text-brand-400 font-mono">Agentic Support Core</span>
              </div>
            </div>
          </div>

          {/* New Chat Action */}
          <button
            onClick={() => {
              startNewConversation();
              onClose();
            }}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all group"
          >
            <MessageSquarePlus className="w-4 h-4 transition-transform group-hover:scale-110" />
            <span>New Chat Session</span>
          </button>
        </div>

        {/* Conversation Thread List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <div className="px-3 pb-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Recent Conversations
          </div>

          {conversations.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-slate-500">
              No previous threads. Ask a question to start!
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeConversationId;
              return (
                <div
                  key={conv.id}
                  onClick={() => {
                    selectConversation(conv.id);
                    onClose();
                  }}
                  className={`group flex items-center justify-between px-3 py-2.5 rounded-xl text-xs cursor-pointer transition-all ${
                    isActive
                      ? 'bg-surface-100 text-white border border-slate-700/80 font-medium shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-surface-200/50'
                  }`}
                >
                  <div className="flex items-center space-x-2.5 truncate">
                    <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-brand-400' : 'text-slate-400'}`} />
                    <span className="truncate">{conv.title}</span>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-400 rounded transition-opacity"
                    title="Delete thread"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Action Drawers & User Profile */}
        <div className="p-3 space-y-2 border-t border-slate-800/80 bg-surface-400/50">
          {/* Quick Drawer Buttons */}
          <button
            onClick={() => {
              onOpenOrders();
              onClose();
            }}
            className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white hover:bg-surface-200 transition-colors"
          >
            <div className="flex items-center space-x-2">
              <Package className="w-4 h-4 text-emerald-400" />
              <span>My Orders & Tracking</span>
            </div>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          </button>

          <button
            onClick={() => {
              onOpenAdmin();
              onClose();
            }}
            className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white hover:bg-surface-200 transition-colors"
          >
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-purple-400" />
              <span>HITL Review Queue</span>
            </div>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {/* User Profile Card */}
          <div className="pt-2 border-t border-slate-800 flex items-center justify-between px-2">
            <div className="flex items-center space-x-2.5 truncate">
              <div className="w-7 h-7 rounded-full bg-brand-500/20 border border-brand-500/40 flex items-center justify-center text-brand-300 font-bold text-xs">
                {user?.name?.charAt(0) || 'U'}
              </div>
              <div className="truncate">
                <p className="text-xs font-semibold text-white truncate">{user?.name || 'Customer'}</p>
                <p className="text-[10px] text-slate-400 truncate">{user?.email}</p>
              </div>
            </div>

            <button
              onClick={logout}
              className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
