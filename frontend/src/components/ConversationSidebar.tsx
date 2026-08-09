import React, { useState } from "react";
import { useChat } from "../context/ChatContext";
import {
  MessageSquare,
  Plus,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Clock,
  Loader2,
} from "lucide-react";

interface ConversationSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

export const ConversationSidebar: React.FC<ConversationSidebarProps> = ({ isOpen, onToggle }) => {
  const { conversations, activeConversationId, selectConversation, startNewConversation, deleteConversation } = useChat();
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const handleSelect = async (id: string) => {
    if (id === activeConversationId) return;
    setLoadingId(id);
    await selectConversation(id);
    setLoadingId(null);
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setDeletingId(id);
    await deleteConversation(id);
    setDeletingId(null);
  };

  const formatTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffHrs = diffMs / (1000 * 60 * 60);
      if (diffHrs < 1) return `${Math.round(diffMs / 60000)}m ago`;
      if (diffHrs < 24) return `${Math.round(diffHrs)}h ago`;
      if (diffHrs < 168) return `${Math.round(diffHrs / 24)}d ago`;
      return date.toLocaleDateString([], { month: "short", day: "numeric" });
    } catch {
      return dateStr;
    }
  };

  return (
    <>
      {/* Toggle Tab */}
      <button
        onClick={onToggle}
        title={isOpen ? "Collapse history" : "View conversation history"}
        className={`fixed top-1/2 -translate-y-1/2 z-40 w-5 h-16 flex items-center justify-center bg-[#0d121c] border border-white/10 rounded-r-xl text-slate-400 hover:text-teal-300 hover:border-teal-500/40 transition-all duration-300 shadow-lg ${isOpen ? "left-[280px]" : "left-0"}`}
      >
        {isOpen ? <ChevronLeft className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
      </button>

      {/* Sidebar Panel */}
      <aside
        className={`fixed top-0 left-0 h-full z-30 flex flex-col bg-[#0a0e18] border-r border-white/08 transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? "w-[280px] opacity-100" : "w-0 opacity-0"}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 pt-16 pb-3 border-b border-white/08 shrink-0">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-teal-400" />
            <span className="text-xs font-mono tracking-wider uppercase text-slate-400">History</span>
            {conversations.length > 0 && (
              <span className="px-1.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[0.6rem] font-mono text-slate-400">
                {conversations.length}
              </span>
            )}
          </div>
          <button
            onClick={startNewConversation}
            title="New conversation"
            className="p-1.5 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/30 text-teal-400 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto py-2 space-y-1 px-2">
          {conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center text-center py-16 space-y-2 px-4">
              <MessageSquare className="w-8 h-8 text-slate-700" />
              <p className="text-xs text-slate-500 font-mono leading-relaxed">No past conversations yet.</p>
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeConversationId;
              const isLoading = loadingId === conv.id;
              const isDeleting = deletingId === conv.id;
              return (
                <button
                  key={conv.id}
                  onClick={() => handleSelect(conv.id)}
                  disabled={isDeleting}
                  className={`w-full text-left group rounded-xl px-3 py-2.5 transition-all duration-150 relative ${isActive ? "bg-teal-500/10 border border-teal-500/30 text-white" : "hover:bg-white/[0.04] border border-transparent hover:border-white/10 text-slate-300"} ${isDeleting ? "opacity-40 pointer-events-none" : ""}`}
                >
                  {isActive && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-teal-400 rounded-r-full" />
                  )}
                  <div className="flex items-start gap-2.5">
                    <div className={`mt-0.5 shrink-0 ${isActive ? "text-teal-400" : "text-slate-500"}`}>
                      {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <MessageSquare className="w-3.5 h-3.5" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium truncate leading-snug">{conv.title || "Support conversation"}</p>
                      {conv.last_message && (
                        <p className="text-[0.65rem] text-slate-500 truncate mt-0.5 font-mono">{conv.last_message}</p>
                      )}
                      <div className="flex items-center gap-1 mt-1">
                        <Clock className="w-2.5 h-2.5 text-slate-600" />
                        <span className="text-[0.6rem] text-slate-600 font-mono">{formatTime(conv.updated_at)}</span>
                        {conv.message_count != null && (
                          <span className="ml-auto text-[0.6rem] text-slate-600 font-mono">{conv.message_count} msgs</span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleDelete(e, conv.id)}
                      title="Delete"
                      className="shrink-0 opacity-0 group-hover:opacity-100 p-1 rounded-md hover:bg-rose-500/20 hover:text-rose-400 text-slate-600 transition-all"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-white/05 shrink-0">
          <p className="text-[0.6rem] text-slate-600 font-mono text-center">Conversations auto-persist to database</p>
        </div>
      </aside>
    </>
  );
};
