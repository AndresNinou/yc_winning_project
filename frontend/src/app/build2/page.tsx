"use client";

import { useEffect, useState } from "react";
import { Chat } from "./Chat";
import { MessageType, Tool } from "./messages";
import { Button, Input } from "@/components/ui";
import { Textarea } from "@/components/ui/textarea";
import { sendMessage, parseStreamingResponse } from "./utils";

const sampleMessages: MessageType[] = [
  {
    role: "user",
    text: "Can you help me write a function to calculate fibonacci numbers?",
    ts: Date.now() - 300000,
  },
  {
    role: "assistant",
    text: "I'll help you create a fibonacci function. Let me write that code for you.",
    ts: Date.now() - 240000,
    tool: "code-task-1",
  },
  {
    role: "assistant",
    text: "Here's an efficient fibonacci function using memoization:\n\n```javascript\nfunction fibonacci(n, memo = {}) {\n  if (n in memo) return memo[n];\n  if (n <= 2) return 1;\n  memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo);\n  return memo[n];\n}\n```",
    ts: Date.now() - 180000,
  },
  {
    role: "user",
    text: "That's perfect! Can you explain how the memoization works?",
    ts: Date.now() - 120000,
  },
  {
    role: "assistant",
    text: "Let me break down how memoization optimizes the fibonacci calculation...",
    ts: Date.now() - 60000,
    tool: "reasoning-task-1",
  },
];

const sampleTools: Record<string, Tool> = {
  "code-task-1": {
    type: "code",
    status: "success",
  },
  "reasoning-task-1": {
    type: "reasoning",
    status: "done",
  },
  error: {
    type: "error",
    status: "error",
  },
};

export default function BuilderScreen({
  searchParams,
}: {
  searchParams: { q?: string; name?: string };
}) {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [inputValue, setInputValue] = useState("");

  const q = searchParams.q || "";
  const name = searchParams.name || "";

  useEffect(() => {
    if (q) {
      const userMessage: MessageType = {
        role: "user",
        text: q,
        ts: Date.now(),
      };
      const assistantMessage: MessageType = {
        role: "assistant",
        text: "I'll help you create a fibonacci function. Let me write that code for you.",
        ts: Date.now() - 240000,
        tool: "code-task-1",
      };
      setMessages([userMessage, assistantMessage]);
    }
  }, [q]);

  const handleSend = async () => {
    try {
      const userMessage: MessageType = {
        role: "user",
        text: inputValue,
        ts: Date.now(),
      };

      const loadingMessage: MessageType = {
        role: "loading",
        text: "",
        ts: Date.now(),
      };

      setMessages([...messages, userMessage, loadingMessage]);
      setInputValue("");

      const response = await sendMessage(q, inputValue);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const content = await parseStreamingResponse(response);

      await new Promise((resolve) => setTimeout(resolve, 1000));

      const assistantMessage: MessageType = {
        role: "assistant",
        text: content,
        ts: Date.now(),
      };

      // Remove loading message and add assistant response
      setMessages((prev) => prev.slice(0, -1).concat(assistantMessage));
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) =>
        prev.slice(0, -1).concat({
          role: "assistant",
          text: "I'm sorry, I couldn't process your message.",
          ts: Date.now(),
          tool: "error",
        })
      );
    }
  };

  return (
    <div className="container mx-auto h-screen">
      <div className="flex flex-col gap-4 max-w-4xl mx-auto h-screen p-6">
        <Chat messages={messages} tools={sampleTools} />
        <div className="mt-auto flex flex-row space-x-4">
          {/* <Input placeholder="Ask a question..." className="h-14" /> */}
          <Textarea
            placeholder="Ask a question..."
            className="h-14"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <Button className="h-full w-24" onClick={handleSend}>
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
