import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Coffee, Users, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { supabase, Salon } from '../lib/supabase';

export const SalonDashboard: React.FC = () => {
  const [salons, setSalons] = useState<Salon[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSalons();
  }, []);

  const fetchSalons = async () => {
    try {
      const { data, error } = await supabase.functions.invoke('salon-manager', {
        body: { action: 'list', salon_data: { status: 'active' } }
      });

      if (error) throw error;

      if (data?.data?.salons) {
        setSalons(data.data.salons);
      }
    } catch (error) {
      console.error('Error fetching salons:', error);
    } finally {
      setLoading(false);
    }
  };

  const protocolNames = {
    tea: '茶协议',
    xiaolongbao: '小笼包协议',
    coffee: '咖啡协议'
  };

  const protocolColors = {
    tea: 'from-primary-600 to-primary-500',
    xiaolongbao: 'from-accent-600 to-accent-500',
    coffee: 'from-secondary-600 to-secondary-500'
  };

  return (
    <section id="salons" className="py-20 bg-neutral-50 min-h-screen">
      <div className="container mx-auto px-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-12">
          <div>
            <h2 className="text-4xl font-bold text-primary-900 mb-2">知识沙龙</h2>
            <p className="text-neutral-600">参与或创建AI驱动的知识讨论</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowCreateForm(true)}
            className="px-6 py-3 bg-accent-500 text-neutral-950 font-semibold rounded-md shadow-md hover:shadow-lg transition-all flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>创建沙龙</span>
          </motion.button>
        </div>

        {/* Salons Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
            <p className="mt-4 text-neutral-600">加载中...</p>
          </div>
        ) : salons.length === 0 ? (
          <div className="text-center py-12">
            <Coffee className="w-16 h-16 mx-auto text-neutral-400 mb-4" />
            <p className="text-neutral-600">暂无活跃沙龙，创建一个开始吧！</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {salons.map((salon) => (
              <motion.div
                key={salon.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ y: -5 }}
                className="bg-neutral-25 rounded-xl p-6 shadow-sm hover:shadow-md border-2 border-neutral-200 hover:border-primary-400 transition-all cursor-pointer"
                onClick={() => navigate(`/salon/${salon.id}`)}
              >
                {/* Protocol Badge */}
                <div className={`inline-block px-3 py-1 rounded-full bg-gradient-to-r ${protocolColors[salon.protocol_type]} text-neutral-25 text-xs font-medium mb-4`}>
                  {protocolNames[salon.protocol_type]}
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-neutral-900 mb-2">
                  {salon.title}
                </h3>

                {/* Description */}
                {salon.description && (
                  <p className="text-sm text-neutral-600 mb-4 line-clamp-2">
                    {salon.description}
                  </p>
                )}

                {/* Topic */}
                {salon.topic && (
                  <div className="mb-4">
                    <span className="text-xs text-neutral-500">主题：</span>
                    <span className="text-sm text-neutral-700">{salon.topic}</span>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between text-xs text-neutral-500 pt-4 border-t border-neutral-200">
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4" />
                    <span>最多 {salon.max_participants} 人</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(salon.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Create Form Modal */}
        {showCreateForm && (
          <CreateSalonModal
            onClose={() => setShowCreateForm(false)}
            onSuccess={() => {
              setShowCreateForm(false);
              fetchSalons();
            }}
          />
        )}
      </div>
    </section>
  );
};

// Create Salon Modal Component
const CreateSalonModal: React.FC<{ onClose: () => void; onSuccess: () => void }> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    protocol_type: 'coffee' as 'tea' | 'xiaolongbao' | 'coffee',
    topic: '',
    target_audience: ''
  });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError('');

    try {
      // Check if user is logged in
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        setError('请先登录后再创建沙龙');
        setCreating(false);
        return;
      }

      const { data, error: invokeError } = await supabase.functions.invoke('salon-manager', {
        body: {
          action: 'create',
          salon_data: formData
        }
      });

      if (invokeError) throw invokeError;

      if (data?.data?.salon) {
        onSuccess();
      } else {
        throw new Error('创建失败');
      }
    } catch (err: any) {
      setError(err.message || '创建沙龙失败');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-neutral-950/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-neutral-25 rounded-xl p-8 max-w-md w-full shadow-xl"
      >
        <h3 className="text-2xl font-bold text-primary-900 mb-6">创建知识沙龙</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              沙龙标题 *
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2 border-2 border-neutral-200 rounded-md focus:border-primary-500 focus:outline-none"
              placeholder="例：AI与咖啡文化的碰撞"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              描述
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border-2 border-neutral-200 rounded-md focus:border-primary-500 focus:outline-none"
              rows={3}
              placeholder="简要描述沙龙内容..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              协议类型 *
            </label>
            <select
              required
              value={formData.protocol_type}
              onChange={(e) => setFormData({ ...formData, protocol_type: e.target.value as any })}
              className="w-full px-4 py-2 border-2 border-neutral-200 rounded-md focus:border-primary-500 focus:outline-none"
            >
              <option value="coffee">咖啡协议（创新探索）</option>
              <option value="tea">茶协议（深度传承）</option>
              <option value="xiaolongbao">小笼包协议（结构化装配）</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              主题
            </label>
            <input
              type="text"
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
              className="w-full px-4 py-2 border-2 border-neutral-200 rounded-md focus:border-primary-500 focus:outline-none"
              placeholder="沙龙讨论主题"
            />
          </div>

          {error && (
            <div className="p-3 bg-error-100 border border-error-500 rounded-md text-error-700 text-sm">
              {error}
            </div>
          )}

          <div className="flex items-center space-x-3 pt-4">
            <button
              type="submit"
              disabled={creating}
              className="flex-1 px-6 py-3 bg-accent-500 text-neutral-950 font-semibold rounded-md hover:bg-accent-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {creating ? '创建中...' : '创建沙龙'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 bg-neutral-200 text-neutral-700 font-semibold rounded-md hover:bg-neutral-300 transition-colors"
            >
              取消
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};
