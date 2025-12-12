# 故障排除指南

## 常见问题

### 1. 连接问题

#### 错误：`Failed to connect to LangGraph server`

**可能原因：**
- LangGraph 服务器未启动
- 端口 2024 被占用
- 防火墙阻止连接

**解决方案：**
```bash
# 检查端口是否被占用
lsof -i :2024

# 启动 LangGraph 服务器
langgraph serve --port 2024

# 或使用不同端口
# 更新 .env.local: NEXT_PUBLIC_API_URL=http://localhost:8080
```

#### 错误：`CORS error`

**解决方案：**
在 LangGraph 服务器配置中添加 CORS 支持：
```python
# langgraph.json
{
  "cors": {
    "allow_origins": ["http://localhost:3000"],
    "allow_methods": ["GET", "POST"],
    "allow_headers": ["*"]
  }
}
```

### 2. 流式问题

#### 问题：看不到流式效果，消息一次性出现

**可能原因：**
- 使用了错误的 `streamMode`
- API 路由代理问题

**解决方案：**
```typescript
// 确保使用正确的 streamMode
await streamValue.submit(input, {
  streamMode: ["values"], // 不是 ["messages"]
})
```

#### 问题：出现双气泡（loading + 消息同时显示）

**解决方案：**
```typescript
// 确保 firstTokenReceived 逻辑正确
{isLoading && !firstTokenReceived && (
  <LoadingComponent />
)}
```

### 3. TypeScript 错误

#### 错误：`找不到模块"@/lib/utils"`

**解决方案：**
```typescript
// 确保路径别名配置正确
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

#### 错误：`interrupt 不是函数`

**解决方案：**
```typescript
// 移除或注释掉 interrupt 调用
const stop = () => {
  // SDK 的 interrupt 不是函数，暂时留空
}
```

### 4. 性能问题

#### 问题：消息加载缓慢

**优化方案：**
```typescript
// 使用虚拟滚动
import { FixedSizeList as List } from 'react-window'

// 实现消息分页
const loadMoreMessages = async () => {
  const more = await fetch(`/api/messages?offset=${messages.length}`)
  // ...
}
```

#### 问题：内存占用过高

**解决方案：**
```typescript
// 限制消息历史长度
const MAX_MESSAGES = 100
const messages = allMessages.slice(-MAX_MESSAGES)

// 清理旧线程
const cleanupOldThreads = () => {
  // 实现清理逻辑
}
```

### 5. 认证问题

#### 错误：`401 Unauthorized`

**解决方案：**
```bash
# 检查 API key 配置
echo $NEXT_PUBLIC_API_KEY

# 更新 .env.local
NEXT_PUBLIC_API_KEY=your_actual_api_key
```

#### 错误：`API key not found`

**解决方案：**
```typescript
// 确保 API key 正确传递
const client = new Client({
  apiUrl,
  apiKey: apiKey || undefined, // 即使是 undefined 也要传递
})
```

## 调试技巧

### 1. 启用详细日志

```typescript
// 在开发环境启用调试
if (process.env.NODE_ENV === 'development') {
  console.log('Stream value:', streamValue)
  console.log('Messages:', messages)
}
```

### 2. 网络请求调试

```typescript
// 拦截和日志请求
const originalFetch = window.fetch
window.fetch = async (...args) => {
  console.log('Fetch:', args[0], args[1])
  const response = await originalFetch(...args)
  console.log('Response:', response.status, response.statusText)
  return response
}
```

### 3. 组件状态调试

```typescript
// 使用 React DevTools
// 或添加状态显示
<div style={{ position: 'fixed', top: 10, right: 10, background: 'white', padding: 10 }}>
  <div>Messages: {messages.length}</div>
  <div>Loading: {isLoading ? 'Yes' : 'No'}</div>
  <div>First Token: {firstTokenReceived ? 'Yes' : 'No'}</div>
</div>
```

## 测试清单

### 基础功能测试
- [ ] 页面正常加载
- [ ] 可以发送消息
- [ ] 收到 AI 回复
- [ ] 流式显示正常
- [ ] 没有"双气泡"

### 错误处理测试
- [ ] 网络断开时的处理
- [ ] 空消息提交
- [ ] 超长消息处理
- [ ] 特殊字符处理

### 性能测试
- [ ] 100+ 消息滚动流畅
- [ ] 内存使用稳定
- [ ] 快速连续发送不会出错

### 兼容性测试
- [ ] Chrome/Edge 正常
- [ ] Firefox 正常
- [ ] Safari 正常
- [ ] 移动端响应式

## 获取帮助

### 1. 查看日志
```bash
# Next.js 开发日志
pnpm dev

# LangGraph 服务器日志
langgraph serve --port 2024 --log-level DEBUG
```

### 2. 社区资源
- [LangGraph Discord](https://discord.gg/langchain)
- [GitHub Issues](https://github.com/langchain-ai/langgraphjs/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/langgraph)

### 3. 官方文档
- [LangGraph SDK 文档](https://api.js.langchain.com/)
- [Next.js 文档](https://nextjs.org/docs)
- [React 文档](https://react.dev/)