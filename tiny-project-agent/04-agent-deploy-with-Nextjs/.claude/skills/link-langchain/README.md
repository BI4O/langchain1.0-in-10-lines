# Link LangChain 技能

## 概述

这个技能帮助你在新的 Next.js 项目中快速集成 LangGraph 后端，创建一个支持真正流式响应的聊天页面。

## 使用方法

### 方式 1：使用自动设置脚本

1. 在 Next.js 项目根目录运行：
```bash
./.claude/skills/link-langchain/scripts/setup_next_langchain.sh
```

2. 确保 LangGraph 后端运行在 http://localhost:2024

3. 启动开发服务器：
```bash
pnpm dev
```

4. 访问 http://localhost:3000/chat

### 方式 2：手动创建

参考 SKILL.md 中的详细步骤，手动创建所需的文件和配置。

## 文件结构

```
.claude/skills/link-langchain/
├── SKILL.md                    # 主要技能文档
├── README.md                   # 本文件
├── scripts/
│   └── setup_next_langchain.sh # 自动设置脚本
├── references/
│   ├── advanced-patterns.md    # 高级模式参考
│   └── troubleshooting.md      # 故障排除指南
└── assets/
    └── minimal-chat-template.tsx # 极简聊天模板
```

## 特性

- ✅ 真正的流式响应（使用 LangGraph SDK）
- ✅ 防双气泡 UI 优化
- ✅ 完整的错误处理
- ✅ TypeScript 类型安全
- ✅ 响应式设计
- ✅ 自动滚动
- ✅ 乐观更新

## 环境要求

- Node.js 18+
- Next.js 14+
- LangGraph Studio 运行在 localhost:2024

## 故障排除

如果遇到问题，请查看 `references/troubleshooting.md` 获取详细的故障排除指南。

## 高级用法

查看 `references/advanced-patterns.md` 了解：
- 线程持久化
- 多助手支持
- 自定义流模式
- 性能优化
- 错误处理和重试

## 贡献

欢迎提出改进建议！