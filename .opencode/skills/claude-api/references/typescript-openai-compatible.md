# TypeScript patterns for OpenAI-compatible APIs

Prefer the `openai` package when the endpoint is OpenAI-compatible. Fall back to `fetch` only when the SDK does not fit the target runtime.

## Install

```bash
npm install openai
```

## Minimal client setup

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY ?? "opencode",
  baseURL: process.env.OPENAI_BASE_URL || undefined,
});

const model = process.env.OPENAI_MODEL ?? "gpt-oss-120b";
```

## Single request

```ts
const response = await client.chat.completions.create({
  model,
  temperature: 0,
  messages: [
    { role: "system", content: "You are a concise assistant." },
    { role: "user", content: "Summarize this diff in three bullets." },
  ],
});

const text = response.choices[0]?.message?.content ?? "";
```

## Streaming

```ts
const stream = await client.chat.completions.create({
  model,
  messages: [{ role: "user", content: "Write a long answer." }],
  stream: true,
});

let fullText = "";
for await (const chunk of stream) {
  const delta = chunk.choices[0]?.delta?.content ?? "";
  if (delta) {
    process.stdout.write(delta);
    fullText += delta;
  }
}
```

## Structured JSON

```ts
const response = await client.chat.completions.create({
  model,
  temperature: 0,
  messages: [
    {
      role: "user",
      content: "Return JSON with keys title, priority, and tags.",
    },
  ],
});

const raw = response.choices[0]?.message?.content ?? "{}";
const data = JSON.parse(raw) as { title?: string; priority?: string; tags?: string[] };
if (!Array.isArray(data.tags)) {
  throw new Error("Expected tags to be an array");
}
```

## Tool calling

```ts
const tools = [
  {
    type: "function" as const,
    function: {
      name: "lookupTicket",
      description: "Fetch a ticket by ID",
      parameters: {
        type: "object",
        properties: {
          ticketId: { type: "string" },
        },
        required: ["ticketId"],
      },
    },
  },
];

const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
  { role: "user", content: "Check ticket OPS-1042." },
];

const first = await client.chat.completions.create({ model, messages, tools });
const assistant = first.choices[0]?.message;
if (assistant) {
  messages.push(assistant as OpenAI.Chat.Completions.ChatCompletionMessageParam);
}

for (const toolCall of assistant?.tool_calls ?? []) {
  const args = JSON.parse(toolCall.function.arguments || "{}");
  const result = JSON.stringify({ id: args.ticketId, status: "open" });
  messages.push({
    role: "tool",
    tool_call_id: toolCall.id,
    content: result,
  });
}

const final = await client.chat.completions.create({ model, messages, tools });
const answer = final.choices[0]?.message?.content ?? "";
```

## Raw `fetch` fallback

Use `fetch()` only when the SDK is unavailable in the runtime. Keep the same environment variables and payload contract so you can switch between SDK and raw HTTP without changing app config.
