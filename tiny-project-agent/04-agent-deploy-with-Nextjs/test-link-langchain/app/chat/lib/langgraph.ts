import { Client } from "@langchain/langgraph-sdk"

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2024"
const apiKey = process.env.NEXT_PUBLIC_API_KEY

export const client = new Client({
  apiUrl,
  apiKey,
})

export { apiUrl, apiKey }