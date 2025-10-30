import React from 'react';
import { Coffee, Github, Mail, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-primary-900 text-neutral-200 py-12">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* 品牌信息 */}
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-accent-500 rounded-full flex items-center justify-center">
                <Coffee className="w-6 h-6 text-neutral-950" />
              </div>
              <span className="text-xl font-bold text-neutral-25">
                AI咖啡知识沙龙
              </span>
            </div>
            <p className="text-neutral-300 text-sm leading-relaxed">
              万有引力，蒸蒸日上
              <br />
              多智能体驱动的知识进化系统
            </p>
          </div>

          {/* 快速链接 */}
          <div>
            <h3 className="text-neutral-25 font-semibold mb-4">快速链接</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#architecture" className="hover:text-accent-400 transition-colors">
                  系统架构
                </a>
              </li>
              <li>
                <a href="#protocols" className="hover:text-accent-400 transition-colors">
                  架构协议
                </a>
              </li>
              <li>
                <a href="#agents" className="hover:text-accent-400 transition-colors">
                  智能体角色
                </a>
              </li>
              <li>
                <a href="#about" className="hover:text-accent-400 transition-colors">
                  关于TIER
                </a>
              </li>
            </ul>
          </div>

          {/* 联系方式 */}
          <div>
            <h3 className="text-neutral-25 font-semibold mb-4">联系我们</h3>
            <div className="space-y-3 text-sm">
              <a
                href="mailto:contact@tier-coffee.com"
                className="flex items-center space-x-2 hover:text-accent-400 transition-colors"
              >
                <Mail className="w-4 h-4" />
                <span>contact@tier-coffee.com</span>
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 hover:text-accent-400 transition-colors"
              >
                <Github className="w-4 h-4" />
                <span>GitHub</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>

        {/* 版权信息 */}
        <div className="border-t border-primary-700 pt-8 text-center text-sm text-neutral-400">
          <p>
            © 2025 TIER咖啡知识沙龙. All rights reserved.
          </p>
          <p className="mt-2">
            北京师范大学附属中学 · Kai数字主理人项目
          </p>
        </div>
      </div>
    </footer>
  );
};
