import React from 'react';
import { motion } from 'framer-motion';
import { Layers, Network, Database, Cpu, Sparkles, Shield } from 'lucide-react';

const architectureLayers = [
  {
    title: '感知交互层',
    description: '多模态交互接口',
    icon: Cpu,
    features: ['语音交互（ASR/TTS）', '视觉交互（图像/视频）', '文本对话', '实时协作界面'],
    color: 'primary',
  },
  {
    title: '核心功能层',
    description: '多智能体协作中枢',
    icon: Network,
    features: ['主持人调度', '专家辩论', '知识检索', '质量评估'],
    color: 'accent',
  },
  {
    title: '数据支撑层',
    description: '知识图谱与RAG',
    icon: Database,
    features: ['知识图谱', 'RAG检索', '向量索引', '版本管理'],
    color: 'secondary',
  },
];

const coreCapabilities = [
  {
    title: '多智能体协作',
    description: '7大智能体角色协同工作，实现高质量知识生产',
    icon: Network,
  },
  {
    title: '知识自净化',
    description: '通过证据强制、事实核查实现知识质量自我提升',
    icon: Shield,
  },
  {
    title: '多模态交互',
    description: '语音、视觉、文本三位一体的交互体验',
    icon: Cpu,
  },
  {
    title: '知识图谱',
    description: '三维知识图谱（时间、逻辑、资源）可视化追溯',
    icon: Layers,
  },
  {
    title: '实时沙龙',
    description: '端到端标准化流程，从主题到成果的完整闭环',
    icon: Sparkles,
  },
  {
    title: '成果沉淀',
    description: '结构化知识沉淀与版本化管理，可复用可追溯',
    icon: Database,
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export const ArchitectureSection: React.FC = () => {
  return (
    <section id="architecture" className="py-20 bg-neutral-50">
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
            系统架构概览
          </h2>
          <p className="text-lg text-neutral-600 max-w-3xl mx-auto">
            三层架构设计，多智能体协作，知识图谱支撑，打造可验证、可演化的知识生产系统
          </p>
        </motion.div>

        {/* 架构层级 */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20"
        >
          {architectureLayers.map((layer, index) => {
            const Icon = layer.icon;
            const colorClass = {
              primary: 'from-primary-600 to-primary-500',
              accent: 'from-accent-600 to-accent-500',
              secondary: 'from-secondary-600 to-secondary-500',
            }[layer.color];

            return (
              <motion.div
                key={layer.title}
                variants={itemVariants}
                whileHover={{ scale: 1.03, y: -5 }}
                className="bg-neutral-25 rounded-xl p-8 shadow-sm hover:shadow-md transition-all duration-300 border border-neutral-200"
              >
                <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${colorClass} flex items-center justify-center mb-6`}>
                  <Icon className="w-8 h-8 text-neutral-25" />
                </div>
                <h3 className="text-2xl font-semibold text-neutral-900 mb-2">{layer.title}</h3>
                <p className="text-neutral-600 mb-6">{layer.description}</p>
                <ul className="space-y-2">
                  {layer.features.map((feature) => (
                    <li key={feature} className="flex items-start space-x-2 text-sm text-neutral-700">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary-500 mt-1.5 flex-shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            );
          })}
        </motion.div>

        {/* 核心能力 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h3 className="text-3xl font-bold text-primary-900 mb-4">核心能力</h3>
          <p className="text-neutral-600">六大核心能力，构建完整的知识生产与演化生态</p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {coreCapabilities.map((capability) => {
            const Icon = capability.icon;
            return (
              <motion.div
                key={capability.title}
                variants={itemVariants}
                whileHover={{ scale: 1.05 }}
                className="bg-gradient-card rounded-lg p-6 border border-primary-200 hover:border-primary-400 hover:shadow-glow-primary transition-all duration-300"
              >
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                    <Icon className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-neutral-900 mb-2">{capability.title}</h4>
                    <p className="text-sm text-neutral-600">{capability.description}</p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
};
