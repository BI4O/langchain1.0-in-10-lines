# LangGraph 高级模式

## 线程持久化

### 使用 localStorage 持久化线程

```typescript
// app/chat/hooks/useLangGraphStream.ts
export function useLangGraphStream(assistantId: string = "agent") {
  const [threadId, setThreadId] = useState<string | null>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('langgraph-thread-id') || null
    }
    return null
  })

  const streamValue = useStream({
    apiUrl,
    apiKey: apiKey || undefined,
    assistantId,
    threadId,
  })

  // 保存新的线程 ID
  useEffect(() => {
    if (streamValue.threadId && streamValue.threadId !== threadId) {
      setThreadId(streamValue.threadId)
      localStorage.setItem('langgraph-thread-id', streamValue.threadId)
    }
  }, [streamValue.threadId, threadId])

  // 重置线程
  const resetThread = () => {
    setThreadId(null)
    localStorage.removeItem('langgraph-thread-id')
  }

  return {
    ...,
    threadId,
    resetThread,
  }
}
```

### 使用数据库持久化线程

```typescript
// app/chat/hooks/useLangGraphStream.ts
export function useLangGraphStream(assistantId: string = "agent", userId?: string) {
  const [threadId, setThreadId] = useState<string | null>(null)

  // 加载用户的线程 ID
  useEffect(() => {
    if (userId) {
      fetch(`/api/threads/${userId}`)
        .then(res => res.json())
        .then(data => {
          if (data.threadId) {
            setThreadId(data.threadId)
          }
        })
    }
  }, [userId])

  // 保存线程 ID
  const saveThreadId = async (newThreadId: string) => {
    if (userId) {
      await fetch(`/api/threads/${userId}`, {
        method: 'POST',
        body: JSON.stringify({ threadId: newThreadId })
      })
    }
  }

  // ...
}
```

## 多助手支持

### 助手切换

```typescript
// app/chat/types.ts
export interface Assistant {
  id: string
  name: string
  description: string
  icon?: string
}

// app/chat/lib/assistants.ts
export const ASSISTANTS: Assistant[] = [
  {
    id: 'agent',
    name: '通用助手',
    description: '处理各种日常任务'
  },
  {
    id: 'coder',
    name: '编程助手',
    description: '专门处理编程相关任务'
  },
  {
    id: 'analyst',
    name: '分析助手',
    description: '进行数据分析和报告生成'
  }
]

// app/chat/page.tsx
export default function ChatPage() {
  const [selectedAssistant, setSelectedAssistant] = useState(ASSISTANTS[0])
  const { messages, isLoading, submit } = useLangGraphStream(selectedAssistant.id)

  return (
    <div>
      {/* 助手选择器 */}
      <div className="flex gap-2 p-4 bg-white border-b">
        {ASSISTANTS.map(assistant => (
          <button
            key={assistant.id}
            onClick={() => setSelectedAssistant(assistant)}
            className={cn(
              "px-4 py-2 rounded-lg transition-colors",
              selectedAssistant.id === assistant.id
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            )}
          >
            {assistant.name}
          </button>
        ))}
      </div>
      {/* ... */}
    </div>
  )
}
```

## 自定义流模式

### 多种流模式支持

```typescript
// app/chat/hooks/useLangGraphStream.ts
export function useLangGraphStream(
  assistantId: string = "agent",
  options: {
    streamMode?: ("values" | "messages" | "updates")[]
    onToken?: (token: string) => void
    onMessage?: (message: Message) => void
  } = {}
) {
  const { streamMode = ["values"], onToken, onMessage } = options

  const streamValue = useStream({
    apiUrl,
    apiKey: apiKey || undefined,
    assistantId,
    threadId: null,
    streamMode,
  })

  // 处理流数据
  useEffect(() => {
    if (streamValue.data) {
      // 处理 token 级别更新
      if (onToken && streamValue.data.token) {
        onToken(streamValue.data.token)
      }

      // 处理消息级别更新
      if (onMessage && streamValue.data.message) {
        onMessage(streamValue.data.message)
      }
    }
  }, [streamValue.data, onToken, onMessage])

  return {
    ...streamValue,
    submit: async (input: { messages: Message[] }) => {
      await streamValue.submit(input, {
        streamMode,
        optimisticValues: (prev: any) => ({
          ...prev,
          messages: [...(prev.messages || []), input.messages[input.messages.length - 1]],
        }),
      })
    },
  }
}
```

## 错误处理和重试

### 增强的错误处理

```typescript
// app/chat/hooks/useLangGraphStream.ts
export function useLangGraphStream(assistantId: string = "agent") {
  const [retryCount, setRetryCount] = useState(0)
  const maxRetries = 3

  const streamValue = useStream({
    apiUrl,
    apiKey: apiKey || undefined,
    assistantId,
    threadId: null,
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
      setRetryCount(0) // 成功后重置重试次数
    } catch (error: any) {
      console.error("Stream error:", error)

      // 自动重试逻辑
      if (retryCount < maxRetries) {
        setRetryCount(prev => prev + 1)
        setTimeout(() => {
          submit(input) // 递归重试
        }, 1000 * Math.pow(2, retryCount)) // 指数退避
      }
    }
  }

  return {
    ...streamValue,
    retryCount,
    maxRetries,
  }
}
```

## 消息历史管理

### 分页加载历史

```typescript
// app/chat/hooks/useMessageHistory.ts
export function useMessageHistory(threadId: string | null) {
  const [history, setHistory] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)

  const loadHistory = async (offset = 0, limit = 50) => {
    if (!threadId || loading || !hasMore) return

    setLoading(true)
    try {
      const response = await fetch(
        `/api/threads/${threadId}/messages?offset=${offset}&limit=${limit}`
      )
      const data = await response.json()

      if (data.messages.length < limit) {
        setHasMore(false)
      }

      setHistory(prev => [...prev, ...data.messages])
    } catch (error) {
      console.error("Failed to load history:", error)
    } finally {
      setLoading(false)
    }
  }

  return {
    history,
    loading,
    hasMore,
    loadHistory,
  }
}
```

## 性能优化

### 虚拟滚动

```typescript
// app/chat/components/VirtualMessageList.tsx
import { FixedSizeList as List } from 'react-window'

interface VirtualMessageListProps {
  messages: Message[]
  height: number
}

export function VirtualMessageList({ messages, height }: VirtualMessageListProps) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <MessageComponent message={messages[index]} />
    </div>
  )

  return (
    <List
      height={height}
      itemCount={messages.length}
      itemSize={100} // 估算的消息高度
      width="100%"
    >
      {Row}
    </List>
  )
}
```

### 消息缓存

```typescript
// app/chat/lib/messageCache.ts
class MessageCache {
  private cache = new Map<string, Message[]>()
  private maxSize = 100

  set(threadId: string, messages: Message[]) {
    if (this.cache.size >= this.maxSize) {
      // 删除最旧的条目
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }
    this.cache.set(threadId, messages)
  }

  get(threadId: string): Message[] | undefined {
    return this.cache.get(threadId)
  }

  clear() {
    this.cache.clear()
  }
}

export const messageCache = new MessageCache()
```

## 类型安全增强

### 严格的类型定义

```typescript
// app/chat/types.ts
import { z } from 'zod'

export const MessageSchema = z.object({
  id: z.string(),
  type: z.enum(['human', 'ai', 'tool', 'system']),
  content: z.union([z.string(), z.any()]),
  name: z.string().nullable().optional(),
  tool_calls: z.array(z.any()).optional(),
  additional_kwargs: z.any().optional(),
  response_metadata: z.any().optional(),
})

export type Message = z.infer<typeof MessageSchema>

export const StreamValueSchema = z.object({
  values: z.object({
    messages: z.array(MessageSchema),
  }),
  isLoading: z.boolean(),
  error: z.union([z.string(), z.any()]).nullable(),
})

export type StreamValue = z.infer<typeof StreamValueSchema>
```