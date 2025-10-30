import React from 'react';
import { motion } from 'framer-motion';
import { Coffee, Sparkles, Heart, Palette, Zap } from 'lucide-react';

const brandStory = {
  naming: {
    title: '品牌命名',
    content: '"TIER"源于"磨"字，象征咖啡豆研磨与中国传统制墨的共通性，寓意匠心沉淀与思考的积累。咖啡从单一饮品升华为文化与思维的载体。',
  },
  motto: {
    title: '品牌主张',
    content: '万有引力，蒸蒸日上',
    description: '知识的磁场汇聚优秀思想，咖啡桌前的交流拉近人际距离，不同观点的碰撞激发创新火花，蒸汽升腾象征持续进步与活力。',
  },
  values: [
    {
      title: '真',
      subtitle: '自然科学与技术创新',
      description: '探索科技前沿，追求真理与创新，通过理性思考和实证研究推动知识进步',
      icon: Sparkles,
      color: 'from-primary-600 to-primary-500',
    },
    {
      title: '善',
      subtitle: '社会科学与人文关怀',
      description: '关注社会价值，倡导人文精神，以同理心和责任感促进社会和谐发展',
      icon: Heart,
      color: 'from-accent-600 to-accent-500',
    },
    {
      title: '美',
      subtitle: '艺术表达与审美体验',
      description: '追求艺术之美，提升审美境界，在创作与欣赏中感受生活的诗意',
      icon: Palette,
      color: 'from-secondary-600 to-secondary-500',
    },
    {
      title: '灵',
      subtitle: '跨学科灵感与创新思维',
      description: '激发创新灵感，促进思想碰撞，在跨界交流中涌现新的认知与可能',
      icon: Zap,
      color: 'from-info-500 to-primary-500',
    },
  ],
  bases: [
    {
      name: '科',
      location: '由新书店',
      description: '科技创新基地，探索前沿技术与应用',
      color: 'primary',
    },
    {
      name: '教',
      location: '北师附中',
      description: '教育传承阵地，培养未来创新人才',
      color: 'accent',
    },
    {
      name: '文',
      location: '中央美院',
      description: '文化艺术中心，促进美学交流与创作',
      color: 'secondary',
    },
    {
      name: '卫',
      location: '柳叶刀烧烤店',
      description: '健康生活空间，倡导身心平衡发展',
      color: 'success',
    },
  ],
};

export const AboutSection: React.FC = () => {
  return (
    <section id="about" className="py-20 bg-neutral-25">
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
            关于TIER咖啡
          </h2>
          <p className="text-lg text-neutral-600 max-w-3xl mx-auto">
            以咖啡为载体，构建知识共生生态，传递"真善美灵"的核心价值
          </p>
        </motion.div>

        {/* 品牌命名 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto mb-16"
        >
          <div className="bg-gradient-to-br from-primary-50 to-accent-50 rounded-2xl p-8 md:p-12 border-2 border-primary-200">
            <div className="flex items-center space-x-4 mb-6">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-600 to-accent-600 flex items-center justify-center">
                <Coffee className="w-8 h-8 text-neutral-25" />
              </div>
              <h3 className="text-3xl font-bold text-primary-900">{brandStory.naming.title}</h3>
            </div>
            <p className="text-lg text-neutral-700 leading-relaxed">{brandStory.naming.content}</p>
          </div>
        </motion.div>

        {/* 品牌主张 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h3 className="text-sm uppercase tracking-wider text-neutral-600 mb-4">{brandStory.motto.title}</h3>
          <h2 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary-700 via-accent-600 to-secondary-600 bg-clip-text text-transparent">
            {brandStory.motto.content}
          </h2>
          <p className="text-lg text-neutral-600 max-w-3xl mx-auto leading-relaxed">{brandStory.motto.description}</p>
        </motion.div>

        {/* 真善美灵 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-20 max-w-6xl mx-auto"
        >
          {brandStory.values.map((value, index) => {
            const Icon = value.icon;
            return (
              <motion.div
                key={value.title}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.03 }}
                className="bg-neutral-25 rounded-xl p-8 border-2 border-neutral-200 hover:border-primary-400 hover:shadow-lg transition-all duration-300"
              >
                <div className={`w-20 h-20 rounded-full bg-gradient-to-br ${value.color} flex items-center justify-center mb-6`}>
                  <span className="text-4xl font-bold text-neutral-25">{value.title}</span>
                </div>
                <h4 className="text-xl font-bold text-neutral-900 mb-3">{value.subtitle}</h4>
                <p className="text-neutral-600 leading-relaxed">{value.description}</p>
              </motion.div>
            );
          })}
        </motion.div>

        {/* 四大阵地 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-6xl mx-auto"
        >
          <h3 className="text-3xl font-bold text-primary-900 mb-8 text-center">四大阵地</h3>
          <p className="text-center text-neutral-600 mb-12 max-w-2xl mx-auto">
            科教文卫四大阵地协同发展，构建全方位的知识交流与创新生态
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {brandStory.bases.map((base, index) => (
              <motion.div
                key={base.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="bg-gradient-card rounded-lg p-6 text-center border-2 border-primary-200 hover:border-primary-400 hover:shadow-md transition-all duration-300"
              >
                <div className="w-16 h-16 mx-auto rounded-full bg-primary-500 text-neutral-25 flex items-center justify-center mb-4 text-3xl font-bold">
                  {base.name}
                </div>
                <h4 className="text-lg font-semibold text-neutral-900 mb-2">{base.location}</h4>
                <p className="text-sm text-neutral-600">{base.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};
