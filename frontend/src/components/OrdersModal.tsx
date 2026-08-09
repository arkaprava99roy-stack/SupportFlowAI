import React, { useEffect, useState } from 'react';
import { Order } from '../types';
import { api } from '../services/api';
import { Package, X, RefreshCw, AlertCircle } from 'lucide-react';
import { useChat } from '../context/ChatContext';

interface OrdersModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OrdersModal: React.FC<OrdersModalProps> = ({ isOpen, onClose }) => {
  const { sendMessage } = useChat();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchOrders();
    }
  }, [isOpen]);

  const fetchOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getOrders();
      setOrders(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load orders.');
    } finally {
      setLoading(false);
    }
  };

  const handleAskAboutOrder = (order: Order) => {
    onClose();
    sendMessage(`What is the current tracking status and delivery update for my order ${order.id}?`);
  };

  const handleCancelOrder = (order: Order) => {
    onClose();
    sendMessage(`Please cancel my order ${order.id}`);
  };

  if (!isOpen) return null;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PROCESSING':
        return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
      case 'SHIPPED':
        return 'bg-sky-500/15 text-sky-300 border-sky-500/30';
      case 'DELIVERED':
        return 'bg-teal-500/15 text-teal-300 border-teal-500/30';
      case 'CANCELLED':
        return 'bg-rose-500/15 text-rose-300 border-rose-500/30';
      default:
        return 'bg-slate-700 text-slate-300 border-slate-600';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="glass rounded-3xl border border-white/10 w-full max-w-2xl shadow-2xl overflow-hidden animate-slide-up flex flex-col max-h-[85vh] bg-[#0d121c]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/[0.02]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-teal-500/15 border border-teal-500/30 flex items-center justify-center text-teal-400">
              <Package className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white tracking-tight">My Active Orders</h3>
              <p className="text-xs text-slate-400 font-mono">Registered purchases and live carrier tracking</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4">
          {loading && (
            <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-3 font-mono text-xs">
              <RefreshCw className="w-6 h-6 animate-spin text-teal-400" />
              <p>Fetching customer orders from PostgreSQL...</p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!loading && !error && orders.length === 0 && (
            <div className="text-center py-12 text-slate-400 space-y-2">
              <Package className="w-8 h-8 mx-auto text-slate-600" />
              <p className="text-sm">No orders found for this customer profile.</p>
            </div>
          )}

          {!loading && !error && orders.map((order) => (
            <div
              key={order.id}
              className="glass-card rounded-2xl p-4 sm:p-5 border border-white/10 hover:border-teal-500/40 transition-all space-y-3"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/08 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-semibold font-mono text-white tracking-wide">{order.id}</span>
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono border ${getStatusBadge(order.status)}`}>
                    {order.status}
                  </span>
                </div>
                <div className="text-sm font-semibold font-mono text-teal-400">
                  ${order.total_amount.toFixed(2)}
                </div>
              </div>

              <div className="text-sm font-medium text-slate-200">{order.product_name}</div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono text-slate-400 pt-1">
                {order.tracking_number && (
                  <div>
                    <span className="text-slate-400">Tracking: </span>
                    <span className="text-slate-200">{order.tracking_number}</span>
                    {order.carrier && <span className="text-slate-400 ml-1">({order.carrier})</span>}
                  </div>
                )}
                <div>
                  <span className="text-slate-400">Address: </span>
                  <span className="text-slate-200">{order.shipping_address}</span>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-white/08">
                <button
                  onClick={() => handleAskAboutOrder(order)}
                  className="px-3 py-1.5 rounded-full text-xs font-mono font-medium bg-teal-500/10 hover:bg-teal-500/20 text-teal-300 border border-teal-500/30 transition-colors"
                >
                  🔍 Track with AI
                </button>
                {order.status === 'PROCESSING' && (
                  <button
                    onClick={() => handleCancelOrder(order)}
                    className="px-3 py-1.5 rounded-full text-xs font-mono font-medium bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 transition-colors"
                  >
                    ❌ Cancel Order
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-white/[0.02] border-t border-white/10 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-white/5 hover:bg-white/10 rounded-full transition-colors border border-white/10"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
