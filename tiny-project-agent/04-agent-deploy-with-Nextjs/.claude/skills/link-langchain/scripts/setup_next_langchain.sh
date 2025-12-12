#!/bin/bash

# Next.js LangGraph 集成快速设置脚本
# 用于快速搭建新的 Next.js + LangGraph 聊天项目

set -e

echo "🚀 Next.js LangGraph 集成快速设置"
echo "================================="

# 检查是否在 Next.js 项目根目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误：请在 Next.js 项目根目录运行此脚本"
    exit 1
fi

# 检查是否使用 pnpm
if ! command -v pnpm &> /dev/null; then
    echo "⚠️  警告：建议使用 pnpm 作为包管理器"
    PKG_MANAGER="npm"
else
    PKG_MANAGER="pnpm"
fi

echo "📦 安装依赖..."

# 安装核心依赖
$PKG_MANAGER add @langchain/langgraph-sdk@1.2.0 @langchain/core lucide-react clsx tailwind-merge

# 安装开发依赖
$PKG_MANAGER add -D tailwindcss typescript

echo "📁 创建目录结构..."

# 创建目录
mkdir -p app/chat/hooks app/chat/lib

echo "🔧 创建文件..."

# 创建环境变量文件
if [ ! -f ".env.local" ]; then
    cat > .env.local << EOF
# LangGraph 配置
NEXT_PUBLIC_API_URL=http://localhost:2024
NEXT_PUBLIC_API_KEY=
EOF
    echo "✅ 创建 .env.local 文件"
else
    echo "⚠️  .env.local 已存在，跳过创建"
fi

# 创建类型定义
cat > app/chat/types.ts << 'EOF'
export interface Message {
  id: string
  type: "human" | "ai" | "tool" | "system"
  content: string | any
  name?: string | null
  tool_calls?: any[]
  additional_kwargs?: any
  response_metadata?: any
}
EOF

# 创建 LangGraph 客户端配置
cat > app/chat/lib/langgraph.ts << 'EOF'
import { Client } from "@langchain/langgraph-sdk"

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2024"
const apiKey = process.env.NEXT_PUBLIC_API_KEY

export const client = new Client({
  apiUrl,
  apiKey,
})

export { apiUrl, apiKey }
EOF

# 创建流式处理 Hook
cat > app/chat/hooks/useLangGraphStream.ts << 'EOF'
"use client"

import { useStream } from "@langchain/langgraph-sdk/react"
import { apiUrl, apiKey } from "../lib/langgraph"
import type { Message } from "../types"

export function useLangGraphStream(assistantId: string = "agent") {
  const streamValue = useStream({
    apiUrl,
    apiKey: apiKey || undefined,
    assistantId,
    threadId: null, // SDK 自动创建新线程
  })

  const submit = async (input: { messages: Message[] }) => {
    try {
      await streamValue.submit(
        { messages: input.messages },
        {
          streamMode: ["values"],
          optimisticValues: (prev: any) => ({
            ...prev,
            messages: [...(prev.messages || []), input.messages[input.messages.length - 1]],
          }),
        }
      )
    } catch (error: any) {
      console.error("Stream error:", error)
    }
  }

  return {
    messages: (streamValue.values as any)?.messages || [],
    isLoading: streamValue.isLoading,
    error: (streamValue.error as any)?.message || (streamValue.error as any)?.toString(),
    submit,
    values: streamValue.values,
  }
}
EOF

# 检查是否需要创建 lib 目录和 utils.ts
mkdir -p lib
if [ ! -f "lib/utils.ts" ]; then
    cat > lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF
fi

# 创建导出文件
cat > app/chat/index.ts << 'EOF'
export { default as ChatPage } from './page'
export { useLangGraphStream } from './hooks/useLangGraphStream'
export type { Message } from './types'
export { apiUrl, apiKey, client } from './lib/langgraph'
EOF

echo "🎯 创建聊天页面组件..."

# 创建完整的聊天页面
cat > app/chat/page.tsx << 'EOF'
"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Bot, User } from "lucide-react"
import { cn } from "@/lib/utils"
import { useLangGraphStream } from "./hooks/useLangGraphStream"

export default function ChatPage() {
  const { messages, isLoading, submit } = useLangGraphStream()
  const [input, setInput] = useState("")
  const [firstTokenReceived, setFirstTokenReceived] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const prevMessagesLengthRef = useRef(0)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  // 跟踪是否收到第一个 token - 防止双气泡
  useEffect(() => {
    const currentLength = messages.length
    const prevLength = prevMessagesLengthRef.current

    const hasNewAIMessage = currentLength > prevLength &&
                           messages[currentLength - 1]?.type === "ai"

    if (hasNewAIMessage && !firstTokenReceived) {
      setFirstTokenReceived(true)
    } else if (!isLoading && firstTokenReceived) {
      setFirstTokenReceived(false)
    }

    prevMessagesLengthRef.current = currentLength
  }, [messages.length, isLoading, firstTokenReceived])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = {
      id: Date.now().toString(),
      type: "human" as const,
      content: input.trim(),
    }

    setInput("")
    setFirstTokenReceived(false)
    await submit({ messages: [...messages, userMessage] })
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <Bot className="w-6 h-6 text-blue-600" />
          <h1 className="text-xl font-semibold text-gray-900">AI 聊天助手</h1>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-12">
              <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p>开始对话吧！我是你的 AI 助手。</p>
            </div>
          ) : (
            messages.map((message: any) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3",
                  message.type === "human" ? "justify-end" : "justify-start"
                )}
              >
                {message.type === "ai" && (
                  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[70%] rounded-2xl px-4 py-2",
                    message.type === "human"
                      ? "bg-blue-600 text-white"
                      : "bg-white border border-gray-200 text-gray-900"
                  )}
                >
                  <p className="whitespace-pre-wrap">
                    {typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
                  </p>
                </div>
                {message.type === "human" && (
                  <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center shrink-0">
                    <User className="w-5 h-5 text-white" />
                  </div>
                )}
              </div>
            ))
          )}
          {/* Loading 动画 - 只在未收到第一个 token 时显示 */}
          {isLoading && !firstTokenReceived && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入你的消息..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className={cn(
                "px-6 py-2 rounded-full font-medium transition-colors",
                "bg-blue-600 text-white hover:bg-blue-700",
                "disabled:bg-gray-300 disabled:cursor-not-allowed"
              )}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
EOF

echo ""
echo "✅ 设置完成！"
echo ""
echo "📋 下一步："
echo "1. 确保 LangGraph 后端运行在 http://localhost:2024"
echo "2. 如需 API key，请在 .env.local 中设置 NEXT_PUBLIC_API_KEY"
echo "3. 运行 '$PKG_MANAGER dev' 启动开发服务器"
echo "4. 访问 http://localhost:3000/chat"
echo ""
echo "💡 提示：此脚本已创建了完整的聊天功能，包括防双气泡优化"