"use client"

import { useStream } from "@langchain/langgraph-sdk/react"
import { apiUrl, apiKey } from "../lib/langgraph"
import type { Message } from "../types"

export function useLangGraphStream(assistantId: string = "agent") {
  const streamValue = useStream({
    apiUrl,
    apiKey: apiKey || undefined,
    assistantId,
    threadId: null, // 让 SDK 自动创建新线程
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

  const stop = () => {
    // SDK 的 interrupt 方法可能不是函数，暂时留空
    // 可以通过设置一个标志来停止
  }

  return {
    messages: (streamValue.values as any)?.messages || [],
    isLoading: streamValue.isLoading,
    error: (streamValue.error as any)?.message || (streamValue.error as any)?.toString(),
    submit,
    stop,
    values: streamValue.values,
  }
}