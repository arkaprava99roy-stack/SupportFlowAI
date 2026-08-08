import React, { useEffect, useState } from 'react';
import { Order } from '../types';
import { api } from '../services/api';
import { Package, X, Truck, Calendar, MapPin, DollarSign, RefreshCw, AlertCircle } from 'lucide-react';
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
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      case 'SHIPPED':
        return 'bg-sky-500/15 text-sky-400 border-sky-500/30';
      case 'DELIVERED':
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      case 'CANCELLED':
        return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-700 text-slate-300 border-slate-600';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="bg-surface-100 border border-slate-700/80 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden animate-slide-up flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50 bg-surface-200/50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-brand-500/15 border border-brand-500/30 flex items-center justify-center text-brand-400">
              <Package className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white tracking-tight">My Active Orders</h3>
              <p className="text-xs text-slate-400">Registered purchases and live carrier tracking</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4">
          {loading && (
            <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-3">
              <RefreshCw className="w-6 h-6 animate-spin text-brand-400" />
              <p className="text-sm">Fetching verified customer orders...</p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!loading && orders.length === 0 && !error && (
            <div className="py-12 text-center text-slate-400 space-y-2">
              <p className="text-sm">No orders found for this profile.</p>
            </div>
          )}

          {!loading &&
            orders.map((order) => (
              <div
                key={order.id}
                className="p-4 rounded-xl bg-surface-200/60 border border-slate-700/60 hover:border-slate-600 transition-all space-y-3 shadow-md"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-white text-sm">{order.id}</span>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getStatusBadge(order.status)}`}>
                        {order.status}
                      </span>
                    </div>
                    <h4 className="text-sm font-medium text-slate-200 mt-1">{order.product_name}</h4>
                  </div>
                  <span className="text-base font-semibold text-emerald-400">${order.total_amount.toFixed(2)}</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-400 pt-2 border-t border-slate-700/50">
                  <div className="flex items-center space-x-1.5">
                    <Truck className="w-3.5 h-3.5 text-slate-400" />
                    <span>{order.carrier || 'Carrier'}: <strong className="text-slate-300 font-mono">{order.tracking_number || 'Pending'}</strong></span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">{order.shipping_address}</span>
                  </div>
                </div>

                <div className="flex items-center justify-end space-x-2 pt-2">
                  {order.status === 'PROCESSING' && (
                    <button
                      onClick={() => handleCancelOrder(order)}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 transition-colors"
                    >
                      Request Cancellation
                    </button>
                  )}
                  <button
                    onClick={() => handleAskAboutOrder(order)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-brand-600 hover:bg-brand-500 text-white transition-colors"
                  >
                    Ask AI Assistant
                  </button>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};
