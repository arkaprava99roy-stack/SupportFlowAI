import React, { useEffect, useState } from 'react';
import { PendingReviewItem, AuditLogItem } from '../types';
import { api } from '../services/api';
import { ShieldCheck, X, Activity, ClipboardList, Clock, UserCheck, RefreshCw } from 'lucide-react';

interface AdminModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AdminModal: React.FC<AdminModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'reviews' | 'audit'>('reviews');
  const [reviews, setReviews] = useState<PendingReviewItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [revs, logs] = await Promise.all([api.getPendingReviews(), api.getAuditLogs()]);
      setReviews(revs);
      setAuditLogs(logs);
    } catch (e) {
      console.error('Failed to load admin logs:', e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="bg-surface-100 border border-slate-700/80 rounded-2xl w-full max-w-4xl shadow-2xl overflow-hidden animate-slide-up flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50 bg-surface-200/50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white tracking-tight">Admin & Human-in-the-Loop Inspector</h3>
              <p className="text-xs text-slate-400">Escalated review queue and compliance audit trail</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center px-6 border-b border-slate-700/40 bg-surface-300/40">
          <button
            onClick={() => setActiveTab('reviews')}
            className={`py-3 px-4 text-xs font-semibold border-b-2 transition-all flex items-center space-x-2 ${
              activeTab === 'reviews'
                ? 'border-brand-500 text-brand-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <ClipboardList className="w-4 h-4" />
            <span>Pending Review Queue ({reviews.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`py-3 px-4 text-xs font-semibold border-b-2 transition-all flex items-center space-x-2 ${
              activeTab === 'audit'
                ? 'border-brand-500 text-brand-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Tool Audit Logs ({auditLogs.length})</span>
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto space-y-4">
          {loading && (
            <div className="py-12 flex justify-center text-slate-400">
              <RefreshCw className="w-6 h-6 animate-spin text-purple-400" />
            </div>
          )}

          {/* Pending Reviews Tab */}
          {!loading && activeTab === 'reviews' && (
            <div className="space-y-3">
              {reviews.length === 0 ? (
                <div className="py-12 text-center text-slate-400 text-sm">
                  ✔ All customer interactions are resolved. No pending reviews in queue.
                </div>
              ) : (
                reviews.map((r) => (
                  <div
                    key={r.id}
                    className="p-4 rounded-xl bg-surface-200/70 border border-slate-700/60 hover:border-purple-500/40 transition-all space-y-2.5"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono font-bold text-white text-xs">{r.id}</span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                            r.risk_level === 'HIGH'
                              ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                              : 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                          }`}
                        >
                          {r.risk_level} Risk • {r.intent}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400">{r.created_at}</span>
                    </div>

                    <div className="text-xs text-slate-300">
                      <strong className="text-slate-400 font-normal">Customer Query:</strong> "{r.user_message}"
                    </div>

                    <div className="p-2.5 rounded-lg bg-surface-300/80 border border-slate-700/50 text-xs text-purple-300">
                      <strong>AI Recommendation:</strong> {r.ai_recommended_action}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Audit Logs Tab */}
          {!loading && activeTab === 'audit' && (
            <div className="space-y-3">
              {auditLogs.length === 0 ? (
                <div className="py-12 text-center text-slate-400 text-sm">No tool audit records found.</div>
              ) : (
                auditLogs.map((log) => (
                  <div
                    key={log.id}
                    className="p-3.5 rounded-xl bg-surface-200/60 border border-slate-700/60 flex items-start justify-between space-x-4 text-xs font-mono"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-brand-400 font-bold">{log.tool_name}()</span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] ${
                            log.result_status === 'SUCCESS'
                              ? 'bg-emerald-500/15 text-emerald-400'
                              : log.result_status === 'CONFIRMATION_REQUIRED'
                              ? 'bg-amber-500/15 text-amber-400'
                              : 'bg-rose-500/15 text-rose-400'
                          }`}
                        >
                          {log.result_status}
                        </span>
                        <span className="text-slate-400 font-sans">User: {log.user_id}</span>
                      </div>
                      <p className="text-slate-300 font-sans text-xs">{log.result_summary}</p>
                    </div>
                    <span className="text-slate-500 text-[10px] shrink-0 font-sans">{log.created_at}</span>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
