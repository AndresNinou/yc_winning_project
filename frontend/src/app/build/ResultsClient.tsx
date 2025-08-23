"use client";

import { useEffect, useState, use } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Chat } from "./Chat";
import { MessageType, Tool } from "./types";
import { Button, Input } from "@/components/ui";
import { Textarea } from "@/components/ui/textarea";
import { sendMessage, parseStreamingResponse } from "./utils";
import { TopNav } from "@/components/layout";

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

export default function ResultsClient({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; name?: string }>;
}) {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [fileOutput, setFileOutput] = useState<string[]>(["comeone.ts"]);

  const params = use(searchParams);
  const q = params.q || "";
  const name = params.name || "";

  useEffect(() => {
    if (q) {
      (async () => {
        setInputValue(q);
        console.log(q);
        await handleSend();
      })();
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
        tool: Math.random() > 0.5 ? "code-task-1" : "reasoning-task-1",
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
    <>
      <TopNav onDocs={() => alert("Docs coming soon")} />
      <div className="container mx-auto">
        <div className="flex gap-4 max-w-7xl mx-auto p-6 h-[calc(100vh-64px)]">
          <AnimatePresence>
            {fileOutput.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: -20, width: 0 }}
                animate={{ opacity: 1, x: 0, width: "auto" }}
                exit={{ opacity: 0, x: -20, width: 0 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="min-w-xs bg-background rounded-lg p-4 shadow-sm"
              >
                <h2 className="text-lg font-semibold text-foreground mb-3 flex items-center">
                  <svg
                    className="w-5 h-5 mr-2 text-primary"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  File Output
                </h2>
                <div className="space-y-2">
                  {fileOutput.map((file, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1, duration: 0.2 }}
                      className="bg-card p-3 rounded border border-border font-mono text-sm text-card-foreground shadow-sm"
                    >
                      {file}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex flex-col gap-4 flex-1">
            <Chat messages={messages} tools={sampleTools} />
            <div className="mt-auto flex flex-row space-x-4 items-center">
              <Button
                variant="outline"
                size="icon"
                className="h-14 w-14 shrink-0 rounded-full"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                  />
                </svg>
              </Button>
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
      </div>
    </>
  );
}
