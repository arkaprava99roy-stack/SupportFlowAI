import React, { useState } from 'react';
import { Message, Citation } from '../types';
import { CitationModal } from './CitationModal';
import {
  Bot,
  User as UserIcon,
  ThumbsUp,
  ThumbsDown,
  FileText,
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Ticket,
} from 'lucide-react';
import { useChat } from '../context/ChatContext';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const { rateMessage } = useChat();
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [feedbackSent, setFeedbackSent] = useState<'thumbs_up' | 'thumbs_down' | null>(message.feedback || null);

  const isUser = message.sender === 'user';

  const handleRate = (rating: 'thumbs_up' | 'thumbs_down') => {
    setFeedbackSent(rating);
    rateMessage(message.id, rating);
  };

  const getIntentColor = (intent?: string) => {
    switch (intent) {
      case 'SECURITY':
        return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      case 'BILLING':
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      case 'REFUND':
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      case 'SHIPPING':
        return 'bg-sky-500/15 text-sky-400 border-sky-500/30';
      case 'ACCOUNT':
        return 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30';
      default:
        return 'bg-slate-700/50 text-slate-300 border-slate-600';
    }
  };

  return (
    <>
      <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in group`}>
        <div className={`flex items-start max-w-2xl space-x-3.5 ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'}`}>
          {/* Avatar Icon */}
          <div
            className={`w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 shadow-lg ${
              isUser
                ? 'bg-gradient-to-tr from-brand-600 to-indigo-500 text-white shadow-brand-500/20'
                : 'bg-surface-100 border border-slate-700/60 text-brand-400 shadow-black/40'
            }`}
          >
            {isUser ? <UserIcon className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
          </div>

          {/* Bubble Container */}
          <div className="flex flex-col space-y-2">
            {/* Meta header (for AI responses) */}
            {!isUser && (
              <div className="flex items-center space-x-2 text-xs">
                <span className="font-semibold text-slate-300 tracking-tight">SupportFlow AI</span>
                {message.intent && (
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${getIntentColor(message.intent)}`}>
                    {message.intent}
                  </span>
                )}
                {message.risk_level === 'HIGH' && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse">
                    <ShieldAlert className="w-3 h-3 mr-1" /> High Risk Safety
                  </span>
                )}
                {message.ticket_id && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-purple-500/15 text-purple-300 border border-purple-500/30">
                    <Ticket className="w-3 h-3 mr-1" /> {message.ticket_id}
                  </span>
                )}
                <span className="text-slate-400 text-[11px] ml-auto">{message.created_at}</span>
              </div>
            )}

            {/* Message Bubble Body */}
            <div
              className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap transition-all ${
                isUser
                  ? 'bg-brand-600 text-white rounded-tr-sm shadow-md'
                  : 'bg-surface-100/90 border border-slate-700/60 text-slate-200 rounded-tl-sm shadow-xl'
              }`}
            >
              {message.content}
            </div>

            {/* Citations Chips Section (AI responses) */}
            {!isUser && message.citations && message.citations.length > 0 && !message.is_escalated && (
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                <span className="text-[11px] text-slate-400 font-medium mr-1 flex items-center">
                  <FileText className="w-3 h-3 mr-1" /> Sources:
                </span>
                {message.citations.map((cit, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedCitation(cit)}
                    className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-mono bg-surface-200 hover:bg-slate-800 text-brand-300 hover:text-white border border-slate-700/70 hover:border-brand-500/50 transition-all shadow-sm group/cit"
                    title={`Click to view verified knowledge excerpt from ${cit.document}`}
                  >
                    <span>📄 {cit.document}</span>
                    <span className="text-[10px] text-slate-400 ml-1.5 group-hover/cit:text-brand-300 font-sans">v{cit.version}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Feedback Actions (AI responses) */}
            {!isUser && (
              <div className="flex items-center justify-between pt-1">
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleRate('thumbs_up')}
                    className={`p-1.5 rounded-lg text-xs transition-colors flex items-center space-x-1 ${
                      feedbackSent === 'thumbs_up'
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-surface-200'
                    }`}
                    title="Helpful response"
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleRate('thumbs_down')}
                    className={`p-1.5 rounded-lg text-xs transition-colors flex items-center space-x-1 ${
                      feedbackSent === 'thumbs_down'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-surface-200'
                    }`}
                    title="Unhelpful response"
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                  </button>
                  {feedbackSent && (
                    <span className="text-[11px] text-emerald-400 font-medium pl-1 flex items-center">
                      <CheckCircle2 className="w-3 h-3 mr-1" /> Feedback saved
                    </span>
                  )}
                </div>

                {isUser && <span className="text-slate-400 text-[11px]">{message.created_at}</span>}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Citation Detail Modal */}
      <CitationModal citation={selectedCitation} onClose={() => setSelectedCitation(null)} />
    </>
  );
};
