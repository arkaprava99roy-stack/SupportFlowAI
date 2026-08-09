import React, { createContext, useContext, useState, useEffect } from 'react';
import { ConversationSummary, Message, Citation } from '../types';
import { api } from '../services/api';
import { useAuth } from './AuthContext';

interface ChatContextType {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  activeCitations: Citation[];
  activeNode: string | null;
  activeNodeLabel: string | null;
  error: string | null;
  loadConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  startNewConversation: () => void;
  sendMessage: (text: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  rateMessage: (messageId: string, rating: 'thumbs_up' | 'thumbs_down') => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [streamingContent, setStreamingContent] = useState<string>('');
  const [activeCitations, setActiveCitations] = useState<Citation[]>([]);
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [activeNodeLabel, setActiveNodeLabel] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadConversations = async () => {
    if (!isAuthenticated) return;
    try {
      const list = await api.getConversations();
      setConversations(list);
    } catch (e: any) {
      console.error('Error loading conversations:', e);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadConversations();
    } else {
      setConversations([]);
      setMessages([]);
      setActiveConversationId(null);
    }
  }, [isAuthenticated]);

  const selectConversation = async (id: string) => {
    setActiveConversationId(id);
    setError(null);
    try {
      const detail = await api.getConversation(id);
      setMessages(detail.messages);
    } catch (e: any) {
      setError(e.message || 'Failed to load conversation messages');
    }
  };

  const startNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
    setStreamingContent('');
    setActiveCitations([]);
    setActiveNode(null);
    setActiveNodeLabel(null);
    setError(null);
  };

  const deleteConversation = async (id: string) => {
    try {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        startNewConversation();
      }
    } catch (e: any) {
      setError(e.message || 'Failed to delete conversation');
    }
  };

  const sendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    setError(null);
    const userMsgId = `temp_user_${Date.now()}`;
    const userMsg: Message = {
      id: userMsgId,
      sender: 'user',
      content: text,
      created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);
    setStreamingContent('');
    setActiveCitations([]);
    setActiveNode(null);
    setActiveNodeLabel(null);

    let accumulatedTokens = '';

    await api.streamChatMessage(
      text,
      activeConversationId || undefined,
      (token) => {
        accumulatedTokens += token;
        setStreamingContent((prev) => prev + token);
        // Clear active node once tokens start flowing
        setActiveNode(null);
        setActiveNodeLabel(null);
      },
      (metadata) => {
        if (metadata.conversation_id && !activeConversationId) {
          setActiveConversationId(metadata.conversation_id);
        }

        const assistantMsg: Message = {
          id: metadata.message_id || `temp_asst_${Date.now()}`,
          sender: 'assistant',
          content: accumulatedTokens || metadata.response || '',
          intent: metadata.intent,
          risk_level: metadata.risk_level,
          citations: metadata.citations || [],
          is_escalated: metadata.is_escalated,
          ticket_id: metadata.ticket_id,
          created_at: metadata.created_at || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };

        setMessages((prev) => [...prev, assistantMsg]);
        setStreamingContent('');
        setIsStreaming(false);
        loadConversations();
      },
      async (err) => {
        // Fallback to batch chat endpoint if streaming encountered a network issue

        try {
          const batchRes = await api.sendChatMessage(text, activeConversationId || undefined);
          if (!activeConversationId) {
            setActiveConversationId(batchRes.conversation_id);
          }

          const assistantMsg: Message = {
            id: batchRes.message_id,
            sender: 'assistant',
            content: batchRes.response,
            intent: batchRes.intent,
            risk_level: batchRes.risk_level,
            citations: batchRes.citations,
            is_escalated: batchRes.is_escalated,
            ticket_id: batchRes.ticket_id,
            created_at: batchRes.created_at,
          };

          setMessages((prev) => [...prev, assistantMsg]);
          loadConversations();
        } catch (batchErr: any) {
          setError(batchErr.message || err);
        } finally {
          setIsStreaming(false);
          setStreamingContent('');
        }
      },
      // onProgress — handle live node execution events
      (node: string, label: string) => {
        setActiveNode(node);
        setActiveNodeLabel(label);
      }
    );
  };

  const rateMessage = async (messageId: string, rating: 'thumbs_up' | 'thumbs_down') => {
    if (!activeConversationId) return;

    setMessages((prev) =>
      prev.map((m) => (m.id === messageId ? { ...m, feedback: rating } : m))
    );

    try {
      await api.submitFeedback({
        conversation_id: activeConversationId,
        message_id: messageId,
        rating,
      });
    } catch (e: any) {
      console.error('Failed to submit feedback:', e);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeConversationId,
        messages,
        isStreaming,
        streamingContent,
        activeCitations,
        activeNode,
        activeNodeLabel,
        error,
        loadConversations,
        selectConversation,
        startNewConversation,
        sendMessage,
        deleteConversation,
        rateMessage,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
