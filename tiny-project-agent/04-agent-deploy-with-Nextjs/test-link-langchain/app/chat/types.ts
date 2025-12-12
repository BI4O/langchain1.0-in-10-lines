export interface Message {
  id: string
  type: "human" | "ai" | "tool" | "system"
  content: string | any
  name?: string | null
  tool_calls?: any[]
  additional_kwargs?: any
  response_metadata?: any
}