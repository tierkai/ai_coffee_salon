import React from 'react';
import { motion } from 'framer-motion';
import { ArrowDown, Sparkles, Coffee } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const coreValues = [
  {
    title: '真',
    subtitle: '自然科学与技术创新',
    description: '探索科技前沿，追求真理与创新',
    color: 'from-primary-600 to-primary-500',
  },
  {
    title: '善',
    subtitle: '社会科学与人文关怀',
    description: '关注社会价值，倡导人文精神',
    color: 'from-accent-600 to-accent-500',
  },
  {
    title: '美',
    subtitle: '艺术表达与审美体验',
    description: '追求艺术之美，提升审美境界',
    color: 'from-secondary-600 to-secondary-500',
  },
  {
    title: '灵',
    subtitle: '跨学科灵感与创新思维',
    description: '激发创新灵感，促进思想碰撞',
    color: 'from-info-500 to-primary-500',
  },
];

export const HeroSection: React.FC = () => {
  const navigate = useNavigate();
  
  const scrollToNext = () => {
    const element = document.getElementById('architecture');
    if (element) {
      const offset = 72;
      const elementPosition = element.offsetTop - offset;
      window.scrollTo({
        top: elementPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-hero">
      {/* 背景装饰 */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-10 w-72 h-72 bg-accent-500 rounded-full filter blur-3xl animate-pulse-glow" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-primary-400 rounded-full filter blur-3xl animate-pulse-glow" style={{ animationDelay: '1s' }} />
      </div>

      {/* 主要内容 */}
      <div className="container mx-auto px-6 py-20 relative z-10">
        <div className="max-w-5xl mx-auto text-center">
          {/* 标题区 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-12"
          >
            <div className="inline-flex items-center space-x-2 bg-accent-500/20 backdrop-blur-sm border border-accent-400/30 rounded-full px-6 py-2 mb-6">
              <Sparkles className="w-5 h-5 text-accent-400" />
              <span className="text-accent-300 font-medium">多智能体驱动的知识进化系统</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-neutral-25 mb-6 leading-tight">
              <span className="bg-gradient-to-r from-accent-400 via-primary-300 to-accent-400 bg-clip-text text-transparent">
                AI咖啡知识沙龙
              </span>
            </h1>

            <h2 className="text-2xl md:text-3xl lg:text-4xl font-semibold text-neutral-100 mb-6">
              万有引力，蒸蒸日上
            </h2>

            <p className="text-lg md:text-xl text-neutral-200 max-w-3xl mx-auto leading-relaxed">
              基于多智能体协作、知识自净化与涌现评估的纯AI知识沙龙系统
              <br />
              让知识在碰撞中升华，在对话中进化
            </p>
          </motion.div>

          {/* 核心价值卡片 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
          >
            {coreValues.map((value, index) => (
              <motion.div
                key={value.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="bg-neutral-25/10 backdrop-blur-sm border border-neutral-200/20 rounded-xl p-6 hover:shadow-glow-primary transition-all duration-300"
              >
                <div className={`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br ${value.color} flex items-center justify-center`}>
                  <span className="text-3xl font-bold text-neutral-25">{value.title}</span>
                </div>
                <h3 className="text-lg font-semibold text-neutral-100 mb-2">{value.subtitle}</h3>
                <p className="text-sm text-neutral-300">{value.description}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* CTA按钮 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <button
              onClick={() => navigate('/salons')}
              className="group px-8 py-4 bg-accent-500 text-neutral-950 font-semibold rounded-md shadow-glow-accent hover:bg-accent-400 hover:shadow-xl hover:scale-105 transition-all duration-300 flex items-center space-x-2"
            >
              <Coffee className="w-5 h-5" />
              <span>进入知识沙龙</span>
            </button>
            <button
              onClick={scrollToNext}
              className="group px-8 py-4 bg-transparent border-2 border-primary-400 text-primary-300 font-semibold rounded-md hover:bg-primary-400 hover:text-neutral-25 transition-all duration-300 flex items-center space-x-2"
            >
              <span>了解更多</span>
              <ArrowDown className="w-5 h-5 group-hover:translate-y-1 transition-transform" />
            </button>
          </motion.div>
        </div>
      </div>

      {/* 底部滚动提示 */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.5 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          className="text-neutral-300 text-sm flex flex-col items-center space-y-2"
        >
          <span>向下滚动探索更多</span>
          <ArrowDown className="w-5 h-5" />
        </motion.div>
      </motion.div>
    </section>
  );
};
