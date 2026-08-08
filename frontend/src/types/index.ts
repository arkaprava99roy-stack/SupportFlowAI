export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  status: string;
}

export interface Citation {
  document: string;
  title: string;
  category: string;
  version: string;
  updated_at: string;
  chunk_id?: string;
  snippet: string;
  score?: number;
}

export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  intent?: string;
  risk_level?: string;
  citations?: Citation[];
  is_escalated?: boolean;
  ticket_id?: string;
  created_at: string;
  feedback?: 'thumbs_up' | 'thumbs_down';
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message?: string;
  message_count: number;
}

export interface Order {
  id: string;
  order_number: string;
  product_id: string;
  product_name: string;
  status: 'PROCESSING' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED' | 'REFUNDED';
  total_amount: number;
  carrier?: string;
  tracking_number?: string;
  shipping_address: string;
  created_at: string;
}

export interface PendingReviewItem {
  id: string;
  conversation_id: string;
  user_id: string;
  ticket_id: string;
  risk_level: string;
  intent: string;
  user_message: string;
  ai_recommended_action: string;
  status: string;
  created_at: string;
}

export interface AuditLogItem {
  id: number;
  user_id: string;
  tool_name: string;
  arguments: string;
  result_status: string;
  result_summary: string;
  created_at: string;
}
