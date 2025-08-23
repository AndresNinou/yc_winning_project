"use client";

import { useEffect, useState, use } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Chat } from "./Chat";
import { MessageType, Tool } from "./types";
import { Button, Input } from "@/components/ui";
import { Textarea } from "@/components/ui/textarea";
import { sendMessage, parseStreamingResponse } from "./utils";
import { TopNav } from "@/components/layout";
import { FileText, Download, Copy, RotateCcw, MessageSquare, ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";

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
  const router = useRouter();

  const params = use(searchParams);
  const q = params.q || "";
  const name = params.name || "";

  useEffect(() => {
    if (q) {
      (async () => {
        setInputValue(q);
        console.log(q);
        await handleSend(q);
      })();
    }
  }, [q]);

  const handleSend = async (messageText?: string) => {
    try {
      const textToSend = messageText || inputValue;
      const userMessage: MessageType = {
        role: "user",
        text: textToSend,
        ts: Date.now(),
      };

      const loadingMessage: MessageType = {
        role: "loading",
        text: "",
        ts: Date.now(),
      };

      setMessages([...messages, userMessage, loadingMessage]);
      setInputValue("");

      const response = await sendMessage(q, textToSend);

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
    <div className="min-h-screen w-full bg-[#0b0b0c] text-white overflow-x-hidden">
      <TopNav onDocs={() => alert("Docs coming soon")} />

      {/* Back Button */}
      <div className="pt-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Button
              variant="ghost"
              onClick={() => router.push("/")}
              className="mb-6 text-white/70 hover:text-white hover:bg-white/10 flex items-center gap-2 px-4 py-2 rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm transition-all duration-300"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Home
            </Button>
          </motion.div>
        </div>
      </div>

      <main className="relative">
        {/* Hero Section with Project Title */}
        {/* <section className="pt-20 pb-8 px-4">
          <div className="max-w-6xl mx-auto text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent leading-tight"
            >
              {name || "Building your MCP"}
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-lg md:text-xl text-white/80 mb-8 max-w-3xl mx-auto leading-relaxed"
            >
              {q || "Your MCP tool is being built with AI assistance"}
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-wrap justify-center gap-3 mb-8"
            >
              <span className="inline-flex items-center px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm text-white/70">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2" />
                Live building
              </span>
              <span className="inline-flex items-center px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm text-white/70">
                Real-time chat
              </span>
              <span className="inline-flex items-center px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm text-white/70">
                AI-powered iteration
              </span>
            </motion.div>
          </div>
        </section> */}

        {/* Main Content */}
        <section className="px-4 pb-16">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              
              {/* File Output Sidebar */}
              <AnimatePresence>
                {fileOutput.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.6 }}
                    className="lg:col-span-1 space-y-4"
                  >
                    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 via-white/[0.02] to-white/5 backdrop-blur-xl p-6">
                      <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 via-transparent to-blue-500/10 opacity-50" />
                      
                      <div className="relative z-10">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                          <FileText className="w-5 h-5 mr-2 text-green-400" />
                          Generated Files
                        </h3>
                        <div className="space-y-3">
                          {fileOutput.map((file, index) => (
                            <motion.div
                              key={index}
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: index * 0.1, duration: 0.3 }}
                              className="bg-white/5 border border-white/10 rounded-xl p-3 font-mono text-sm text-white/90 hover:bg-white/10 transition-colors cursor-pointer"
                            >
                              {file}
                            </motion.div>
                          ))}
                        </div>
                        
                        {/* Action Buttons */}
                        <div className="mt-6 space-y-2">
                          <Button
                            variant="ghost"
                            className="w-full justify-start text-white/70 hover:text-white hover:bg-white/10"
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Download Project
                          </Button>
                          <Button
                            variant="ghost"
                            className="w-full justify-start text-white/70 hover:text-white hover:bg-white/10"
                          >
                            <Copy className="h-4 w-4 mr-2" />
                            Copy Repository URL
                          </Button>
                          <Button
                            variant="ghost"
                            className="w-full justify-start text-white/70 hover:text-white hover:bg-white/10"
                          >
                            <RotateCcw className="h-4 w-4 mr-2" />
                            Start Over
                          </Button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Chat Area */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className={`${fileOutput.length > 0 ? 'lg:col-span-3' : 'lg:col-span-4'} space-y-6`}
              >
                <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/5 via-white/[0.02] to-white/5 backdrop-blur-xl p-6">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-transparent to-purple-500/10 opacity-50" />
                  
                  <div className="relative z-10">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-semibold text-white flex items-center">
                        <MessageSquare className="w-5 h-5 mr-2 text-blue-400" />
                        AI Assistant
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-white/60">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                        Online
                      </div>
                    </div>
                    
                    {/* Chat Container */}
                    <div className="min-h-[400px] max-h-[600px] overflow-y-auto mb-6">
                      {messages.length === 0 && (
                        <div className="flex items-center justify-center h-32 text-white/40 text-sm">
                          Start a conversation to see messages here...
                        </div>
                      )}
                      <Chat messages={messages} tools={sampleTools} />
                    </div>
                    
                    {/* Input Area */}
                    <div className="flex items-end gap-4 pt-4 border-t border-white/10">
                      <div className="flex-1">
                        <Textarea
                          placeholder="Ask questions, request changes, or iterate on your MCP..."
                          className="min-h-[80px] bg-white/5 border border-white/10 rounded-2xl text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-300 resize-none"
                          value={inputValue}
                          onChange={(e) => setInputValue(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter" && e.shiftKey) {
                              e.preventDefault();
                              handleSend();
                            }
                          }}
                        />
                      </div>
                      
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-12 w-12 rounded-xl bg-white/5 border border-white/10 text-white/70 hover:text-white hover:bg-white/10"
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
                        
                        <Button
                          onClick={() => handleSend()}
                          disabled={!inputValue.trim()}
                          className="h-12 px-6 text-base font-semibold bg-white text-black hover:bg-white/90 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Send
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-white/10 py-8">
        <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-sm text-white/60">Building your MCP with AI assistance</div>
          <div className="flex items-center gap-6 text-sm">
            <a href="#" className="text-white/60 hover:text-white transition-colors">
              Privacy
            </a>
            <a href="#" className="text-white/60 hover:text-white transition-colors">
              Terms
            </a>
            <a href="#" className="text-white/60 hover:text-white transition-colors">
              Contact
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
