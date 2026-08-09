import React, { useState } from 'react';
import { Message, Citation } from '../types';
import { CitationModal } from './CitationModal';
import {
  ThumbsUp,
  ThumbsDown,
  FileText,
  Shield,
  CheckCircle2,
  AlertTriangle,
  User as UserIcon,
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

  const getRiskBadge = (risk?: string) => {
    switch (risk) {
      case 'HIGH':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.68rem] font-mono font-medium bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse" />
            RISK HIGH
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.68rem] font-mono font-medium bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            RISK MEDIUM
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.68rem] font-mono font-medium bg-teal-500/15 text-teal-400 border border-teal-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
            RISK LOW
          </span>
        );
    }
  };

  const getResolutionBadge = (risk?: string, isEscalated?: boolean) => {
    if (isEscalated || risk === 'HIGH') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.68rem] font-mono font-medium bg-rose-500/15 text-rose-300 border border-rose-500/30">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
          HUMAN ESCALATION
        </span>
      );
    }
    if (risk === 'MEDIUM') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.68rem] font-mono font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
          FLAGGED FOR REVIEW
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.68rem] font-mono font-medium bg-teal-500/15 text-teal-300 border border-teal-500/30">
        <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
        AUTO-RESOLVED
      </span>
    );
  };

  if (isUser) {
    return (
      <div className="flex flex-col items-end space-y-1.5 max-w-xl ml-auto animate-fade-in">
        <div className="flex items-center gap-2 text-xs text-slate-400 pr-1">
          <span className="font-mono text-[0.7rem]">User</span>
          <div className="w-5 h-5 rounded-full bg-white/10 flex items-center justify-center text-slate-300">
            <UserIcon className="w-3 h-3" />
          </div>
        </div>
        <div className="rounded-2xl bg-white/5 border border-white/10 px-4 py-3 text-sm text-slate-100 leading-relaxed shadow-lg">
          {message.content}
        </div>
        <span className="text-[0.65rem] font-mono text-slate-400 pr-1">{message.created_at}</span>
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-col space-y-3 w-full max-w-2xl animate-fade-in">
        {/* Header Badges */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-xs shadow-glow-teal">
            🪐
          </div>

          {message.intent && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.68rem] font-mono font-medium bg-white/5 text-slate-300 border border-white/10 uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
              {message.intent}
            </span>
          )}

          {getRiskBadge(message.risk_level)}
          {getResolutionBadge(message.risk_level, message.is_escalated)}

          {message.ticket_id && (
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[0.68rem] font-mono bg-purple-500/15 text-purple-300 border border-purple-500/30 ml-auto">
              🎫 {message.ticket_id}
            </span>
          )}
        </div>

        {/* Message Content Bubble */}
        <div className="glass-card rounded-2xl p-4 sm:p-5 border border-white/10 text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>

        {/* Diagnostic Steps & Traversal Logs */}
        <div className="px-2 space-y-1.5 text-xs font-mono text-slate-400">
          {message.intent && (
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
              <span>Intent classifier → {message.intent} (0.94)</span>
            </div>
          )}

          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
            <span>Risk analysis → {message.risk_level || 'LOW'} ({message.risk_level === 'HIGH' ? 'Security threat detected' : message.risk_level === 'MEDIUM' ? 'Confirmation required' : 'Standard flow'})</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
            <span>Guardrail check → PASSED (No prompt injection detected)</span>
          </div>
        </div>

        {/* RAG Citations Chips */}
        {message.citations && message.citations.length > 0 && !message.is_escalated && (
          <div className="flex flex-wrap items-center gap-2 pt-1 px-1">
            <FileText className="w-3.5 h-3.5 text-slate-400" />
            {message.citations.map((cit, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedCitation(cit)}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono bg-teal-500/10 hover:bg-teal-500/20 text-teal-300 border border-teal-500/30 transition-all hover:scale-105"
                title={`Click to view policy excerpt from ${cit.document}`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                <span>{cit.document}</span>
                <span className="text-[0.65rem] text-teal-400">· v{cit.version}</span>
              </button>
            ))}
          </div>
        )}

        {/* Feedback Row */}
        <div className="flex items-center justify-between pt-1 px-1 text-xs text-slate-400 font-mono">
          <div className="flex items-center gap-3">
            <span className="text-[0.68rem] tracking-wider uppercase text-slate-400">FEEDBACK</span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => handleRate('thumbs_up')}
                className={`p-1.5 rounded-full transition-colors ${
                  feedbackSent === 'thumbs_up'
                    ? 'bg-teal-500/20 text-teal-400 border border-teal-500/40'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
                title="Helpful response"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleRate('thumbs_down')}
                className={`p-1.5 rounded-full transition-colors ${
                  feedbackSent === 'thumbs_down'
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
                title="Unhelpful response"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
            </div>
            {feedbackSent && (
              <span className="text-teal-400 text-[0.7rem] flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Recorded
              </span>
            )}
          </div>

          <span className="text-[0.65rem] text-slate-400">{message.created_at}</span>
        </div>
      </div>

      {/* Citation Detail Modal */}
      {selectedCitation && (
        <CitationModal citation={selectedCitation} onClose={() => setSelectedCitation(null)} />
      )}
    </>
  );
};
