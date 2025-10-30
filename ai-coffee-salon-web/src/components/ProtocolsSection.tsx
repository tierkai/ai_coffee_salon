import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Coffee, Package, Droplet } from 'lucide-react';

type Protocol = 'tea' | 'xiaolongbao' | 'coffee';

const protocols = [
  {
    id: 'tea' as Protocol,
    name: '茶协议',
    subtitle: '深度传承与共识',
    icon: Droplet,
    color: 'primary',
    description: '多轮萃取与回甘，逐轮逼近高质量共识',
    steps: [
      { name: '温杯', desc: '上下文清理与偏见重置' },
      { name: '投茶量', desc: '知识种子注入与密度控制' },
      { name: '洗茶', desc: '预过滤、去重、去噪、事实纠偏' },
      { name: '分杯品饮', desc: '多轮分析与综合，逐轮逼近共识' },
      { name: '回甘', desc: '反馈迭代与知识沉淀' },
    ],
    适用场景: '高复杂、高分歧、需要深度共识的讨论',
    特点: ['多轮迭代', '证据强制', '逐轮逼近', '深度共识'],
  },
  {
    id: 'xiaolongbao' as Protocol,
    name: '小笼包协议',
    subtitle: '结构化知识装配',
    icon: Package,
    color: 'accent',
    description: 'Schema驱动，模块化组装，一致性校验',
    steps: [
      { name: '和面团', desc: 'Schema/框架设计' },
      { name: '调馅料', desc: '核心知识填充' },
      { name: '捏褶子', desc: '关系映射与依赖梳理' },
      { name: '蒸制', desc: '集成测试与一致性校验' },
    ],
    适用场景: '结构化装配、模块清晰、接口可验证的任务',
    特点: ['结构清晰', '模块化', '可验证', '一致性'],
  },
  {
    id: 'coffee' as Protocol,
    name: '咖啡协议',
    subtitle: '参数化创新探索',
    icon: Coffee,
    color: 'secondary',
    description: '可调参数萃取，多维评估，快速迭代创新',
    steps: [
      { name: '研磨度', desc: 'Recall/Precision参数控制' },
      { name: '水温压力', desc: '萃取强度与深度平衡' },
      { name: '萃取时间', desc: '知识提炼速度控制' },
      { name: '风味评估', desc: '多维质量向量（酸度/醇厚/余韵）' },
    ],
    适用场景: '创新探索、快速迭代、多目标优化',
    特点: ['参数可调', '多维评估', '快速迭代', '创新涌现'],
  },
];

export const ProtocolsSection: React.FC = () => {
  const [activeProtocol, setActiveProtocol] = useState<Protocol>('coffee');

  const active = protocols.find(p => p.id === activeProtocol)!;
  const Icon = active.icon;

  const colorClasses = {
    primary: {
      bg: 'from-primary-600 to-primary-500',
      text: 'text-primary-600',
      border: 'border-primary-400',
      activeBg: 'bg-primary-100',
    },
    accent: {
      bg: 'from-accent-600 to-accent-500',
      text: 'text-accent-600',
      border: 'border-accent-400',
      activeBg: 'bg-accent-100',
    },
    secondary: {
      bg: 'from-secondary-600 to-secondary-500',
      text: 'text-secondary-600',
      border: 'border-secondary-400',
      activeBg: 'bg-secondary-100',
    },
  };

  const currentColor = colorClasses[active.color];

  return (
    <section id="protocols" className="py-20 bg-neutral-25">
      <div className="container mx-auto px-6">
        {/* 标题 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-primary-900 mb-4">
            三种架构协议
          </h2>
          <p className="text-lg text-neutral-600 max-w-3xl mx-auto">
            以咖啡文化隐喻知识协作，不同协议适配不同场景，实现最优知识生产
          </p>
        </motion.div>

        {/* 协议选择器 */}
        <div className="flex flex-col lg:flex-row items-stretch gap-8 max-w-6xl mx-auto">
          {/* Tab导航 */}
          <div className="lg:w-1/3 space-y-3">
            {protocols.map((protocol) => {
              const ProtocolIcon = protocol.icon;
              const isActive = activeProtocol === protocol.id;
              const color = colorClasses[protocol.color];

              return (
                <motion.button
                  key={protocol.id}
                  onClick={() => setActiveProtocol(protocol.id)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full text-left p-6 rounded-xl transition-all duration-300 ${
                    isActive
                      ? `bg-gradient-to-br ${color.bg} text-neutral-25 shadow-md`
                      : 'bg-neutral-50 hover:bg-neutral-100 border-2 border-transparent hover:border-neutral-200'
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      isActive ? 'bg-neutral-25/20' : `${color.activeBg}`
                    }`}>
                      <ProtocolIcon className={`w-6 h-6 ${isActive ? 'text-neutral-25' : color.text}`} />
                    </div>
                    <div>
                      <h3 className={`text-xl font-semibold ${isActive ? 'text-neutral-25' : 'text-neutral-900'}`}>
                        {protocol.name}
                      </h3>
                      <p className={`text-sm ${isActive ? 'text-neutral-200' : 'text-neutral-600'}`}>
                        {protocol.subtitle}
                      </p>
                    </div>
                  </div>
                </motion.button>
              );
            })}
          </div>

          {/* 内容展示 */}
          <div className="lg:w-2/3">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeProtocol}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="bg-neutral-25 rounded-xl p-8 shadow-md border-2 border-neutral-200"
              >
                {/* 图标和标题 */}
                <div className="flex items-center space-x-4 mb-6">
                  <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${currentColor.bg} flex items-center justify-center`}>
                    <Icon className="w-8 h-8 text-neutral-25" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-neutral-900">{active.name}</h3>
                    <p className="text-neutral-600">{active.subtitle}</p>
                  </div>
                </div>

                {/* 描述 */}
                <p className="text-lg text-neutral-700 mb-6 leading-relaxed">{active.description}</p>

                {/* 流程步骤 */}
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-neutral-900 mb-4">流程步骤</h4>
                  <div className="space-y-3">
                    {active.steps.map((step, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${currentColor.bg} flex items-center justify-center flex-shrink-0 text-neutral-25 font-semibold text-sm`}>
                          {index + 1}
                        </div>
                        <div>
                          <h5 className="font-semibold text-neutral-900">{step.name}</h5>
                          <p className="text-sm text-neutral-600">{step.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 适用场景 */}
                <div className={`p-4 rounded-lg ${currentColor.activeBg} border ${currentColor.border} mb-4`}>
                  <h4 className="font-semibold text-neutral-900 mb-2">适用场景</h4>
                  <p className="text-sm text-neutral-700">{active.适用场景}</p>
                </div>

                {/* 特点标签 */}
                <div>
                  <h4 className="font-semibold text-neutral-900 mb-3">核心特点</h4>
                  <div className="flex flex-wrap gap-2">
                    {active.特点.map((feature) => (
                      <span
                        key={feature}
                        className={`px-3 py-1 rounded-full ${currentColor.activeBg} ${currentColor.text} text-sm font-medium`}
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
};
