import { NextRequest, NextResponse } from "next/server"

const AGENT_URL = "http://localhost:2024"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { messages } = body

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: "Invalid messages format" },
        { status: 400 }
      )
    }

    // 直接调用 agent 的 stream 端点
    const runResponse = await fetch(`${AGENT_URL}/runs/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        assistant_id: "agent",
        input: { messages },
        streamMode: ["messages"],
      }),
    })

    if (!runResponse.ok) {
      console.error("Agent API error:", runResponse.statusText)
      return NextResponse.json(
        { error: "Failed to communicate with agent" },
        { status: 500 }
      )
    }

    // 直接使用响应体
    const reader = runResponse.body?.getReader() ?? null

    if (!reader) {
      return NextResponse.json(
        { error: "No response from agent" },
        { status: 500 }
      )
    }

    const stream = new ReadableStream({
      async start(controller) {
        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            // 转发数据
            controller.enqueue(value)
          }
        } catch (error) {
          console.error("Stream error:", error)
          controller.error(error)
        } finally {
          controller.close()
        }
      },
    })

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    })
  } catch (error) {
    console.error("API route error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}