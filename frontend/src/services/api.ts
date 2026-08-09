import { User, ConversationSummary, Message, Order, PendingReviewItem, AuditLogItem, Citation } from '../types';

const API_BASE = '/api';

export function getAuthToken(): string | null {
  return localStorage.getItem('sf_auth_token');
}

export function setAuthToken(token: string) {
  localStorage.setItem('sf_auth_token', token);
}

export function removeAuthToken() {
  localStorage.removeItem('sf_auth_token');
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeAuthToken();
    window.dispatchEvent(new Event('auth:unauthorized'));
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unexpected error occurred.' }));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  async register(data: { email: string; password: string; name: string }) {
    return request<{ access_token: string; user_id: string; email: string; name: string; role: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async login(data: { email: string; password: string }) {
    return request<{ access_token: string; user_id: string; email: string; name: string; role: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getMe() {
    return request<User>('/auth/me');
  },

  async logout() {
    removeAuthToken();
    return request<{ success: boolean }>('/auth/logout', { method: 'POST' }).catch(() => ({ success: true }));
  },

  // Conversations & Chat
  async getConversations() {
    return request<ConversationSummary[]>('/conversations');
  },

  async getConversation(id: string) {
    return request<{ id: string; title: string; created_at: string; updated_at: string; messages: Message[] }>(`/conversations/${id}`);
  },

  async deleteConversation(id: string) {
    return request<{ success: boolean }>(`/conversations/${id}`, { method: 'DELETE' });
  },

  async sendChatMessage(message: string, conversationId?: string) {
    return request<{
      conversation_id: string;
      message_id: string;
      response: string;
      intent: string;
      intent_confidence: number;
      risk_level: string;
      citations: Citation[];
      is_escalated: boolean;
      ticket_id?: string;
      created_at: string;
    }>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  },

  // Streaming Chat via Server-Sent Events (SSE)
  async streamChatMessage(
    message: string,
    conversationId: string | undefined,
    onToken: (token: string) => void,
    onMetadata: (metadata: any) => void,
    onError: (err: string) => void,
    onProgress?: (node: string, label: string) => void,
  ) {
    const token = getAuthToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ message, conversation_id: conversationId }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Streaming failed' }));
        throw new Error(errorData.detail || 'Streaming failed');
      }

      if (!response.body) {
        throw new Error('ReadableStream not supported by response');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let currentEvent = 'message';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('event:')) {
            currentEvent = trimmed.replace('event:', '').trim();
          } else if (trimmed.startsWith('data:')) {
            const dataStr = trimmed.replace('data:', '').trim();
            if (dataStr === '[DONE]') {
              break;
            }
            try {
              const parsed = JSON.parse(dataStr);
              if (currentEvent === 'metadata') {
                onMetadata(parsed);
              } else if (currentEvent === 'progress' && onProgress) {
                onProgress(parsed.node, parsed.label);
              } else if (parsed.token) {
                onToken(parsed.token);
              }
            } catch (e) {
              if (dataStr) onToken(dataStr);
            }
          }
        }
      }
    } catch (e: any) {
      onError(e.message || 'Stream connection failed');
    }
  },

  // Orders
  async getOrders() {
    return request<Order[]>('/orders');
  },

  async cancelOrder(orderId: string, confirmation: boolean = false, reason?: string) {
    return request<{
      success: boolean;
      requires_confirmation?: boolean;
      order_id: string;
      status?: string;
      refund_amount?: string;
      message: string;
    }>(`/orders/${orderId}/cancel`, {
      method: 'POST',
      body: JSON.stringify({ confirmation, reason }),
    });
  },

  // Feedback
  async submitFeedback(data: { conversation_id: string; message_id?: string; rating: string; comment?: string }) {
    return request<{ success: boolean; feedback_id: string; message: string }>('/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Admin
  async getPendingReviews() {
    return request<PendingReviewItem[]>('/admin/pending-reviews');
  },

  async getAuditLogs() {
    return request<AuditLogItem[]>('/admin/audit-logs');
  },
};
