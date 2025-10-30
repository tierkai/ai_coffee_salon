import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, Lock, User } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (mode === 'register') {
        // Register new user
        const { data, error: signUpError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              username: username || email.split('@')[0]
            }
          }
        });

        if (signUpError) throw signUpError;

        if (data.user) {
          // Create profile
          const { error: profileError } = await supabase
            .from('profiles')
            .insert({
              id: data.user.id,
              username: username || email.split('@')[0],
              full_name: username || email.split('@')[0]
            });

          if (profileError) console.error('Profile creation error:', profileError);
          
          alert('注册成功!请检查邮箱验证链接(演示环境可直接登录)');
          setMode('login');
        }
      } else {
        // Login existing user
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password
        });

        if (signInError) throw signInError;

        onSuccess();
        onClose();
      }
    } catch (err: any) {
      setError(err.message || '操作失败,请重试');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-neutral-950/50 flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="bg-neutral-25 rounded-xl p-8 max-w-md w-full shadow-xl relative"
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 text-neutral-600 hover:text-neutral-900 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <h2 className="text-2xl font-bold text-primary-900 mb-6">
            {mode === 'login' ? '登录' : '注册'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  <User className="w-4 h-4 inline mr-1" />
                  用户名
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-2 border-2 border-neutral-200 rounded-md focus:border-primary-500 focus:outline-none"
                  placeholder="输入用户名"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                <Mail className="w-4 h-4 inline mr-1" />
                邮箱 *
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border-2 border-neutral-200 rounded-md focus:border-primary-500 focus:outline-none"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                <Lock className="w-4 h-4 inline mr-1" />
                密码 *
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border-2 border-neutral-200 rounded-md focus:border-primary-500 focus:outline-none"
                placeholder="至少6位字符"
                minLength={6}
              />
            </div>

            {error && (
              <div className="p-3 bg-error-100 border border-error-500 rounded-md text-error-700 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-accent-500 text-neutral-950 font-semibold rounded-md hover:bg-accent-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? '处理中...' : mode === 'login' ? '登录' : '注册'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setMode(mode === 'login' ? 'register' : 'login');
                setError('');
              }}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              {mode === 'login' ? '没有账号? 立即注册' : '已有账号? 立即登录'}
            </button>
          </div>

          <div className="mt-4 p-3 bg-info-100 border border-info-500 rounded-md">
            <p className="text-xs text-info-700">
              <strong>演示提示:</strong> 注册后可能需要邮箱验证。如果无法接收邮件,请使用演示账号或联系管理员。
            </p>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
