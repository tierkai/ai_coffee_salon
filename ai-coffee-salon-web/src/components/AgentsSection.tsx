import React from 'react';
import { motion } from 'framer-motion';
import { Users, Lightbulb, Search, BarChart, FileText, CheckCircle, Database } from 'lucide-react';

const agents = [
  {
    name: '主持人',
    role: 'Host',
    icon: Users,
    description: '流程控制、节奏管理、冲突仲裁',
    capabilities: ['议程控制', '回合管理', '人类在环触发', '路由决策'],
    color: 'primary',
  },
  {
    name: '专家',
    role: 'Expert',
    icon: Lightbulb,
    description: '深度见解、最佳实践、技术诊断',
    capabilities: ['RAG检索', '论证生成', '领域知识', '案例分析'],
    color: 'accent',
  },
  {
    name: '研究员',
    role: 'Researcher',
    icon: Search,
    description: '多源检索、证据收集、资料整理',
    capabilities: ['跨源检索', '证据标注', '知识发现', '文献分析'],
    color: 'secondary',
  },
  {
    name: '分析员',
    role: 'Analyst',
    icon: BarChart,
    description: '事实核验、逻辑一致性、趋势识别',
    capabilities: ['事实核查', '模式识别', '冲突检测', '逻辑验证'],
    color: 'info',
  },
  {
    name: '记录员',
    role: 'Recorder',
    icon: FileText,
    description: '结构化记录、观点提取、关联维护',
    capabilities: ['实时记录', '关键点提取', '知识关联', '格式化输出'],
    color: 'success',
  },
  {
    name: '总结员',
    role: 'Summarizer',
    icon: CheckCircle,
    description: '综合观点、结构化报告、行动建议',
    capabilities: ['观点融合', '报告生成', '建议提炼', '结论输出'],
    color: 'warning',
  },
  {
    name: '知识管理专家',
    role: 'Knowledge Manager',
    icon: Database,
    description: '知识图谱维护、质量监控、版本治理',
    capabilities: ['图谱更新', '质量评估', '版本控制', '审计追溯'],
    color: 'primary',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export const AgentsSection: React.FC = () => {
  return (
    <section id="agents" className="py-20 bg-neutral-50">
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
            智能体角色体系
          </h2>
          <p className="text-lg text-neutral-600 max-w-3xl mx-auto">
            7大智能体角色分工协作，形成完整的知识生产与质量保障体系
          </p>
        </motion.div>

        {/* 角色卡片网格 */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12"
        >
          {agents.map((agent) => {
            const Icon = agent.icon;
            
            return (
              <motion.div
                key={agent.role}
                variants={itemVariants}
                whileHover={{ scale: 1.05, y: -5 }}
                className="bg-neutral-25 rounded-xl p-8 shadow-sm hover:shadow-md border-2 border-neutral-200 hover:border-primary-400 transition-all duration-300"
              >
                {/* 图标 */}
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center mb-6">
                  <Icon className="w-8 h-8 text-primary-700" />
                </div>

                {/* 角色名称 */}
                <div className="mb-4">
                  <h3 className="text-2xl font-bold text-neutral-900 mb-1">{agent.name}</h3>
                  <p className="text-sm text-neutral-500 font-mono">{agent.role}</p>
                </div>

                {/* 描述 */}
                <p className="text-neutral-700 mb-6 leading-relaxed">{agent.description}</p>

                {/* 能力列表 */}
                <div>
                  <h4 className="text-sm font-semibold text-neutral-900 mb-3">核心能力</h4>
                  <div className="space-y-2">
                    {agent.capabilities.map((capability) => (
                      <div key={capability} className="flex items-center space-x-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary-500 flex-shrink-0" />
                        <span className="text-sm text-neutral-600">{capability}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* 协作流程说明 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="bg-gradient-card rounded-xl p-8 border-2 border-primary-200 max-w-4xl mx-auto"
        >
          <h3 className="text-2xl font-bold text-primary-900 mb-6 text-center">协作机制</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-primary-500 text-neutral-25 flex items-center justify-center mx-auto mb-3 font-bold text-lg">
                1
              </div>
              <h4 className="font-semibold text-neutral-900 mb-2">任务分解</h4>
              <p className="text-sm text-neutral-600">主持人拆解任务，分配给各专业智能体</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-accent-500 text-neutral-950 flex items-center justify-center mx-auto mb-3 font-bold text-lg">
                2
              </div>
              <h4 className="font-semibold text-neutral-900 mb-2">并行执行</h4>
              <p className="text-sm text-neutral-600">各智能体并行工作，实时共享知识</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-secondary-500 text-neutral-25 flex items-center justify-center mx-auto mb-3 font-bold text-lg">
                3
              </div>
              <h4 className="font-semibold text-neutral-900 mb-2">质量保障</h4>
              <p className="text-sm text-neutral-600">多轮验证、冲突解决、结果沉淀</p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
