// 极简聊天页面模板
// 适用于快速原型开发

"use client"

import { useState } from "react"
import { useLangGraphStream } from "./hooks/useLangGraphStream"

export default function MinimalChat() {
  const { messages, isLoading, submit } = useLangGraphStream()
  const [input, setInput] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = {
      id: Date.now().toString(),
      type: "human" as const,
      content: input.trim(),
    }

    setInput("")
    await submit({ messages: [...messages, userMessage] })
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Chat</h1>

      <div className="border rounded-lg p-4 h-96 overflow-y-auto mb-4">
        {messages.map((msg: any) => (
          <div key={msg.id} className={`mb-2 ${msg.type === 'human' ? 'text-right' : ''}`}>
            <span className={`inline-block px-3 py-1 rounded ${
              msg.type === 'human'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-800'
            }`}>
              {msg.content}
            </span>
          </div>
        ))}
        {isLoading && <div className="text-gray-500">AI is thinking...</div>}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 border rounded px-3 py-2"
          placeholder="Type a message..."
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          Send
        </button>
      </form>
    </div>
  )
}