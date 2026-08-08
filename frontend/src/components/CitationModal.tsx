import React from 'react';
import { Citation } from '../types';
import { FileText, X, ExternalLink, ShieldCheck, Tag } from 'lucide-react';

interface CitationModalProps {
  citation: Citation | null;
  onClose: () => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-surface-100 border border-slate-700/80 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50 bg-surface-200/50">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white tracking-tight">{citation.title}</h3>
              <p className="text-xs text-slate-400 font-mono">{citation.document}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          {/* Metadata Badges */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-brand-500/15 text-brand-400 border border-brand-500/30">
              <Tag className="w-3 h-3 mr-1" /> Category: {citation.category}
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
              Version {citation.version}
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-3 h-3 mr-1" /> Verified Grounding
            </span>
          </div>

          {/* Excerpt */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Retrieved Knowledge Chunk
            </label>
            <div className="p-4 rounded-xl bg-surface-300/80 border border-slate-700/60 text-slate-200 text-sm leading-relaxed font-sans max-h-60 overflow-y-auto">
              "{citation.snippet}"
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
            <span>Last Updated: {citation.updated_at}</span>
            {citation.score !== undefined && citation.score !== null && (
              <span className="font-mono text-brand-400">Similarity Match: {(citation.score * 100).toFixed(1)}%</span>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-surface-200/50 border-t border-slate-700/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-white bg-brand-600 hover:bg-brand-500 rounded-lg transition-colors shadow-sm"
          >
            Close Citation
          </button>
        </div>
      </div>
    </div>
  );
};
