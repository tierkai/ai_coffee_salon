import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Bot, 
  User as UserIcon, 
  ArrowLeft,
  Sparkles,
  Brain,
  Search,
  BarChart,
  FileText,
  BookOpen,
  Archive
} from 'lucide-react';
import { supabase, Salon, AgentMessage, UserMessage } from '../lib/supabase';

interface Message {
  id: string;
  type: 'agent' | 'user';
  role?: string;
  content: string;
  created_at: string;
  metadata?: any;
}

interface SalonDetailViewProps {
  salonId: string;
  onBack: () => void;
}

export const SalonDetailView: React.FC<SalonDetailViewProps> = ({ salonId, onBack }) => {
  const [salon, setSalon] = useState<Salon | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [userInput, setUserInput] = useState('');
  const [sending, setSending] = useState(false);
  const [agentProcessing, setAgentProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Agent role mapping
  const agentInfo = {
    host: { name: '主持人', icon: Sparkles, color: 'text-accent-600' },
    expert: { name: '专家', icon: Brain, color: 'text-primary-600' },
    researcher: { name: '研究员', icon: Search, color: 'text-secondary-600' },
    analyst: { name: '分析师', icon: BarChart, color: 'text-primary-700' },
    recorder: { name: '记录员', icon: FileText, color: 'text-neutral-600' },
    summarizer: { name: '总结员', icon: BookOpen, color: 'text-accent-700' },
    knowledge_manager: { name: '知识管理员', icon: Archive, color: 'text-primary-800' }
  };

  // Fetch salon details
  useEffect(() => {
    fetchSalonDetails();
    fetchMessages();
    
    // Set up real-time subscription for new messages
    const agentChannel = supabase
      .channel(`salon-${salonId}-agents`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'agent_messages',
          filter: `salon_id=eq.${salonId}`
        },
        (payload) => {
          const newMsg = payload.new as AgentMessage;
          setMessages(prev => [...prev, {
            id: newMsg.id,
            type: 'agent',
            role: newMsg.agent_role,
            content: newMsg.content,
            created_at: newMsg.created_at,
            metadata: newMsg.metadata
          }]);
          setAgentProcessing(false);
        }
      )
      .subscribe();

    const userChannel = supabase
      .channel(`salon-${salonId}-users`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'user_messages',
          filter: `salon_id=eq.${salonId}`
        },
        (payload) => {
          const newMsg = payload.new as UserMessage;
          setMessages(prev => [...prev, {
            id: newMsg.id,
            type: 'user',
            content: newMsg.content,
            created_at: newMsg.created_at
          }]);
        }
      )
      .subscribe();

    return () => {
      agentChannel.unsubscribe();
      userChannel.unsubscribe();
    };
  }, [salonId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchSalonDetails = async () => {
    try {
      const { data, error } = await supabase
        .from('salons')
        .select('*')
        .eq('id', salonId)
        .single();

      if (error) throw error;
      setSalon(data);
    } catch (error) {
      console.error('Error fetching salon:', error);
    }
  };

  const fetchMessages = async () => {
    try {
      setLoading(true);

      // Fetch agent messages
      const { data: agentMsgs, error: agentError } = await supabase
        .from('agent_messages')
        .select('*')
        .eq('salon_id', salonId)
        .order('created_at', { ascending: true });

      if (agentError) throw agentError;

      // Fetch user messages
      const { data: userMsgs, error: userError } = await supabase
        .from('user_messages')
        .select('*')
        .eq('salon_id', salonId)
        .order('created_at', { ascending: true });

      if (userError) throw userError;

      // Combine and sort all messages
      const allMessages: Message[] = [
        ...(agentMsgs || []).map(msg => ({
          id: msg.id,
          type: 'agent' as const,
          role: msg.agent_role,
          content: msg.content,
          created_at: msg.created_at,
          metadata: msg.metadata
        })),
        ...(userMsgs || []).map(msg => ({
          id: msg.id,
          type: 'user' as const,
          content: msg.content,
          created_at: msg.created_at
        }))
      ].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());

      setMessages(allMessages);
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || sending) return;

    const messageContent = userInput.trim();
    setUserInput('');
    setSending(true);

    try {
      // Get current user
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        alert('请先登录后再发送消息');
        setSending(false);
        return;
      }

      // Insert user message
      const { error: insertError } = await supabase
        .from('user_messages')
        .insert({
          salon_id: salonId,
          user_id: user.id,
          content: messageContent
        });

      if (insertError) throw insertError;

      // Trigger agent discussion
      await startAgentDiscussion(messageContent);

    } catch (error) {
      console.error('Error sending message:', error);
      alert('发送消息失败，请重试');
    } finally {
      setSending(false);
    }
  };

  const startAgentDiscussion = async (userMessage: string) => {
    setAgentProcessing(true);

    try {
      // Invoke agent-scheduler edge function
      const { data, error } = await supabase.functions.invoke('agent-scheduler', {
        body: {
          salon_id: salonId,
          user_message: userMessage,
          protocol_type: salon?.protocol_type || 'coffee'
        }
      });

      if (error) throw error;

      // The real-time subscription will handle displaying new agent messages
      console.log('Agent discussion initiated:', data);
    } catch (error) {
      console.error('Error starting agent discussion:', error);
      setAgentProcessing(false);
    }
  };

  const handleQuickAction = async (action: string) => {
    setAgentProcessing(true);
    
    const actionMessages = {
      start: '大家好，欢迎来到本次知识沙龙。让我们开始今天的讨论吧！',
      analyze: '请各位专家对当前讨论进行深入分析，提供你们的专业见解。',
      summarize: '请总结员对本次讨论的要点进行总结。',
      research: '请研究员提供相关的背景资料和研究数据。'
    };

    const message = actionMessages[action as keyof typeof actionMessages];
    if (message) {
      await startAgentDiscussion(message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="inline-block w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!salon) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-neutral-600">沙龙不存在</p>
      </div>
    );
  }

  const protocolColors = {
    tea: 'bg-gradient-to-r from-primary-600 to-primary-500',
    xiaolongbao: 'bg-gradient-to-r from-accent-600 to-accent-500',
    coffee: 'bg-gradient-to-r from-secondary-600 to-secondary-500'
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col">
      {/* Header */}
      <div className="bg-neutral-25 border-b-2 border-neutral-200 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="p-2 hover:bg-neutral-100 rounded-md transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-neutral-700" />
              </button>
              <div>
                <div className="flex items-center space-x-3">
                  <h1 className="text-2xl font-bold text-primary-900">{salon.title}</h1>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium text-neutral-25 ${protocolColors[salon.protocol_type]}`}>
                    {salon.protocol_type === 'tea' ? '茶协议' : salon.protocol_type === 'xiaolongbao' ? '小笼包协议' : '咖啡协议'}
                  </span>
                </div>
                {salon.description && (
                  <p className="text-sm text-neutral-600 mt-1">{salon.description}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-neutral-25 border-b border-neutral-200 py-3">
        <div className="container mx-auto px-6">
          <div className="flex items-center space-x-3">
            <span className="text-sm text-neutral-600">快捷操作：</span>
            <button
              onClick={() => handleQuickAction('start')}
              disabled={agentProcessing}
              className="px-4 py-1.5 bg-accent-100 text-accent-700 text-sm font-medium rounded-md hover:bg-accent-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              启动讨论
            </button>
            <button
              onClick={() => handleQuickAction('analyze')}
              disabled={agentProcessing}
              className="px-4 py-1.5 bg-primary-100 text-primary-700 text-sm font-medium rounded-md hover:bg-primary-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              深入分析
            </button>
            <button
              onClick={() => handleQuickAction('summarize')}
              disabled={agentProcessing}
              className="px-4 py-1.5 bg-secondary-100 text-secondary-700 text-sm font-medium rounded-md hover:bg-secondary-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              总结要点
            </button>
            <button
              onClick={() => handleQuickAction('research')}
              disabled={agentProcessing}
              className="px-4 py-1.5 bg-neutral-200 text-neutral-700 text-sm font-medium rounded-md hover:bg-neutral-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              提供资料
            </button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="container mx-auto px-6 py-6 max-w-4xl">
          <AnimatePresence>
            {messages.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
              >
                <Bot className="w-16 h-16 mx-auto text-neutral-400 mb-4" />
                <p className="text-neutral-600">暂无消息，发送一条消息开始讨论吧！</p>
              </motion.div>
            ) : (
              messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`mb-4 flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.type === 'agent' ? (
                    <div className="flex items-start space-x-3 max-w-[80%]">
                      <div className="flex-shrink-0">
                        {message.role && React.createElement(
                          agentInfo[message.role as keyof typeof agentInfo]?.icon || Bot,
                          { className: `w-8 h-8 ${agentInfo[message.role as keyof typeof agentInfo]?.color || 'text-primary-600'}` }
                        )}
                      </div>
                      <div>
                        <div className="flex items-center space-x-2 mb-1">
                          <span className={`text-sm font-semibold ${agentInfo[message.role as keyof typeof agentInfo]?.color || 'text-primary-600'}`}>
                            {message.role ? agentInfo[message.role as keyof typeof agentInfo]?.name : 'AI智能体'}
                          </span>
                          <span className="text-xs text-neutral-500">
                            {new Date(message.created_at).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="bg-neutral-25 border-2 border-neutral-200 rounded-lg rounded-tl-none px-4 py-3">
                          <p className="text-neutral-800 whitespace-pre-wrap">{message.content}</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start space-x-3 max-w-[80%]">
                      <div>
                        <div className="flex items-center justify-end space-x-2 mb-1">
                          <span className="text-xs text-neutral-500">
                            {new Date(message.created_at).toLocaleTimeString()}
                          </span>
                          <span className="text-sm font-semibold text-accent-700">
                            您
                          </span>
                        </div>
                        <div className="bg-gradient-to-r from-accent-500 to-accent-400 rounded-lg rounded-tr-none px-4 py-3">
                          <p className="text-neutral-950 whitespace-pre-wrap">{message.content}</p>
                        </div>
                      </div>
                      <div className="flex-shrink-0">
                        <UserIcon className="w-8 h-8 text-accent-700" />
                      </div>
                    </div>
                  )}
                </motion.div>
              ))
            )}
          </AnimatePresence>

          {/* Agent Processing Indicator */}
          {agentProcessing && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center space-x-3 mb-4"
            >
              <Bot className="w-8 h-8 text-primary-600 animate-pulse" />
              <div className="bg-neutral-25 border-2 border-neutral-200 rounded-lg px-4 py-3">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <span className="ml-2 text-sm text-neutral-600">智能体正在思考中...</span>
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-neutral-25 border-t-2 border-neutral-200 sticky bottom-0">
        <div className="container mx-auto px-6 py-4 max-w-4xl">
          <form onSubmit={handleSendMessage} className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
                placeholder="输入您的想法... (Shift+Enter 换行)"
                rows={3}
                className="w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:border-primary-500 focus:outline-none resize-none"
                disabled={sending || agentProcessing}
              />
            </div>
            <button
              type="submit"
              disabled={sending || agentProcessing || !userInput.trim()}
              className="px-6 py-3 h-[88px] bg-accent-500 text-neutral-950 font-semibold rounded-lg hover:bg-accent-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              <Send className="w-5 h-5" />
              <span>{sending ? '发送中...' : '发送'}</span>
            </button>
          </form>
          <p className="text-xs text-neutral-500 mt-2">
            提示：使用快捷操作快速启动智能体讨论，或直接输入您的想法与AI进行交流
          </p>
        </div>
      </div>
    </div>
  );
};
