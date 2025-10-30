import React, { useState, useEffect } from 'react';
import { Menu, X, Coffee, User as UserIcon, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { AuthModal } from './AuthModal';

const navItems = [
  { id: 'hero', label: '首页' },
  { id: 'architecture', label: '系统架构' },
  { id: 'protocols', label: '架构协议' },
  { id: 'agents', label: '智能体角色' },
  { id: 'about', label: '关于TIER' },
];

export const Navigation: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('hero');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [user, setUser] = useState<any>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  useEffect(() => {
    // Check current user
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (!isHomePage) return;
    
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);

      // 检测当前活跃区块
      const sections = navItems.map(item => document.getElementById(item.id));
      const scrollPosition = window.scrollY + 100;

      for (let i = sections.length - 1; i >= 0; i--) {
        const section = sections[i];
        if (section && section.offsetTop <= scrollPosition) {
          setActiveSection(navItems[i].id);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isHomePage]);

  const scrollToSection = (sectionId: string) => {
    if (!isHomePage) {
      navigate('/');
      setTimeout(() => {
        const element = document.getElementById(sectionId);
        if (element) {
          const offset = 72;
          const elementPosition = element.offsetTop - offset;
          window.scrollTo({
            top: elementPosition,
            behavior: 'smooth'
          });
        }
      }, 100);
    } else {
      const element = document.getElementById(sectionId);
      if (element) {
        const offset = 72;
        const elementPosition = element.offsetTop - offset;
        window.scrollTo({
          top: elementPosition,
          behavior: 'smooth'
        });
      }
    }
    setIsMobileMenuOpen(false);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  return (
    <>
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled
            ? 'bg-primary-900/95 backdrop-blur-md shadow-md'
            : 'bg-transparent'
        }`}
      >
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-18">
            {/* Logo */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-3 cursor-pointer"
              onClick={() => scrollToSection('hero')}
            >
              <div className="w-10 h-10 bg-accent-500 rounded-full flex items-center justify-center">
                <Coffee className="w-6 h-6 text-neutral-950" />
              </div>
              <span className="text-xl font-bold text-neutral-25">
                AI咖啡知识沙龙
              </span>
            </motion.div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              {navItems.map((item, index) => (
                <motion.button
                  key={item.id}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  onClick={() => scrollToSection(item.id)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    activeSection === item.id && isHomePage
                      ? 'text-accent-400 bg-primary-800'
                      : 'text-neutral-200 hover:text-accent-400 hover:bg-primary-800/50'
                  }`}
                >
                  {item.label}
                </motion.button>
              ))}
              <motion.button
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: navItems.length * 0.1 }}
                onClick={() => navigate('/salons')}
                className="px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 bg-accent-500 text-neutral-950 hover:bg-accent-400"
              >
                知识沙龙
              </motion.button>

              {/* User Menu */}
              {user ? (
                <div className="flex items-center space-x-2 ml-2">
                  <div className="px-3 py-2 bg-primary-800 rounded-md flex items-center space-x-2">
                    <UserIcon className="w-4 h-4 text-accent-400" />
                    <span className="text-sm text-neutral-200">
                      {user.user_metadata?.username || user.email?.split('@')[0]}
                    </span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="p-2 text-neutral-200 hover:text-accent-400 hover:bg-primary-800 rounded-md transition-colors"
                    title="退出登录"
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <motion.button
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: (navItems.length + 1) * 0.1 }}
                  onClick={() => setShowAuthModal(true)}
                  className="px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 border-2 border-primary-400 text-primary-300 hover:bg-primary-400 hover:text-neutral-25 ml-2"
                >
                  登录
                </motion.button>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              className="lg:hidden p-2 text-neutral-200 hover:text-accent-400 transition-colors"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="lg:hidden bg-primary-900 border-t border-primary-700"
            >
              <div className="container mx-auto px-6 py-4 space-y-2">
                {navItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToSection(item.id)}
                    className={`block w-full text-left px-4 py-3 rounded-md text-sm font-medium transition-colors ${
                      activeSection === item.id && isHomePage
                        ? 'text-accent-400 bg-primary-800'
                        : 'text-neutral-200 hover:text-accent-400 hover:bg-primary-800/50'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
                <button
                  onClick={() => {
                    navigate('/salons');
                    setIsMobileMenuOpen(false);
                  }}
                  className="block w-full text-left px-4 py-3 rounded-md text-sm font-medium bg-accent-500 text-neutral-950 hover:bg-accent-400"
                >
                  知识沙龙
                </button>

                {/* Mobile User Menu */}
                {user ? (
                  <div className="pt-2 border-t border-primary-700 space-y-2">
                    <div className="px-4 py-2 text-sm text-neutral-200 flex items-center space-x-2">
                      <UserIcon className="w-4 h-4 text-accent-400" />
                      <span>{user.user_metadata?.username || user.email?.split('@')[0]}</span>
                    </div>
                    <button
                      onClick={() => {
                        handleLogout();
                        setIsMobileMenuOpen(false);
                      }}
                      className="block w-full text-left px-4 py-3 rounded-md text-sm font-medium text-neutral-200 hover:text-accent-400 hover:bg-primary-800/50 flex items-center space-x-2"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>退出登录</span>
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      setShowAuthModal(true);
                      setIsMobileMenuOpen(false);
                    }}
                    className="block w-full text-left px-4 py-3 rounded-md text-sm font-medium border-2 border-primary-400 text-primary-300 hover:bg-primary-400 hover:text-neutral-25"
                  >
                    登录
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={() => {
          setShowAuthModal(false);
        }}
      />
    </>
  );
};
