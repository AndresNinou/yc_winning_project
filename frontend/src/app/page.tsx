"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Rocket,
  Github,
  BookOpen,
  ChevronRight,
  Play,
  Download,
  Copy,
  RotateCcw,
  MessageSquare,
  FileText,
  Code,
  CheckCircle,
  Clock,
  AlertCircle,
  X,
  Plus,
} from "lucide-react";
import { TopNav } from "@/components/layout";
import { Button } from "@/components/ui";

// Types
interface BuildStep {
  id: string;
  title: string;
  status: "queued" | "running" | "success" | "needs_input" | "error";
  description: string;
}

interface SSEEvent {
  type: "log" | "code" | "status";
  content: string;
  timestamp: number;
}

// SSE Demo Data (no network required)
const demoSSEEvents: SSEEvent[] = [
  {
    type: "log",
    content: "🔍 Analyzing requirements...",
    timestamp: Date.now(),
  },
  {
    type: "log",
    content: "📋 Creating project structure...",
    timestamp: Date.now() + 1000,
  },
  { type: "code", content: "manifest.json", timestamp: Date.now() + 2000 },
  {
    type: "log",
    content: "⚡ Generating server code...",
    timestamp: Date.now() + 3000,
  },
  { type: "code", content: "server.py", timestamp: Date.now() + 4000 },
  { type: "log", content: "🧪 Running tests...", timestamp: Date.now() + 5000 },
  {
    type: "log",
    content: "✅ All tests passed!",
    timestamp: Date.now() + 6000,
  },
];

const buildSteps: BuildStep[] = [
  {
    id: "scope",
    title: "Scope & Clarify",
    status: "queued",
    description: "Understanding requirements",
  },
  {
    id: "design",
    title: "Design & Scaffolding",
    status: "queued",
    description: "Planning architecture",
  },
  {
    id: "code",
    title: "Code Generation",
    status: "queued",
    description: "Writing implementation",
  },
  {
    id: "build",
    title: "Build & Test",
    status: "queued",
    description: "Testing and validation",
  },
  {
    id: "ship",
    title: "Ship",
    status: "queued",
    description: "Ready for deployment",
  },
];

const examplePrompts = [
  "Stripe MCP that lists recent charges and refunds charges by ID",
  "Notion MCP to search pages by tag and return page content",
  "Jira MCP to create, assign, and comment on issues",
  "Postgres MCP with list_tables, describe_table, select(query, limit)",
  "GitHub MCP that searches issues across org repos and exposes search_issues(owner, repo, query)",
  "Slack MCP to send messages and list channels",
  "Discord MCP to create webhooks and send messages",
  "Linear MCP to manage projects and create issues",
];

const exampleNames = [
  "Stripe Payments",
  "Notion Pages",
  "Jira Issues",
  "Postgres Database",
  "GitHub Issues",
  "Slack Messages",
  "Discord Webhooks",
  "Linear Projects",
];

// Components
function TrustChip({ children }: { children: React.ReactNode }) {
  return (
    <motion.span
      whileHover={{ scale: 1.02 }}
      className="inline-flex items-center px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm text-white/70 hover:text-white/90 transition-colors"
    >
      {children}
    </motion.span>
  );
}

function ExamplePromptChip({
  prompt,
  onClick,
  variant = "default",
}: {
  prompt: string;
  onClick: () => void;
  variant?: "default" | "primary";
}) {
  return (
    <motion.button
      type="button"
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
        variant === "primary"
          ? "bg-white/10 border border-white/20 text-white hover:bg-white/20"
          : "bg-white/5 border border-white/10 text-white/70 hover:bg-white/10 hover:text-white"
      }`}
    >
      {prompt}
    </motion.button>
  );
}

function PromptCard({
  onPromptSubmit,
}: {
  onPromptSubmit: (prompt: string) => void;
}) {
  const [prompt, setPrompt] = useState("");
  const [showMoreExamples, setShowMoreExamples] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "/" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      onPromptSubmit(prompt.trim());
    }
  };

  const useExample = (example: string) => {
    setPrompt(example);
    inputRef.current?.focus();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
      className="w-full max-w-4xl mx-auto"
    >
      <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/5 via-white/[0.02] to-white/5 backdrop-blur-xl p-8">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-transparent to-purple-500/10 opacity-50" />

        <div className="relative z-10">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-2">
              Describe what you want to build
            </h2>
            <p className="text-sm text-white/60 max-w-2xl mx-auto">
              Tip: Tell us the source APIs, the commands you want, and any
              config you need.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <textarea
                ref={inputRef}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="E.g., Monitor GitHub issues and expose search_issues(owner, repo, query)"
                className="w-full h-32 rounded-2xl bg-white/5 border border-white/10 p-4 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-300 resize-none backdrop-blur-sm"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex gap-3">
                <ExamplePromptChip
                  prompt={exampleNames[0]}
                  onClick={() => useExample(examplePrompts[0])}
                />
                <ExamplePromptChip
                  prompt={exampleNames[1]}
                  onClick={() => useExample(examplePrompts[1])}
                />
                <ExamplePromptChip
                  prompt={exampleNames[2]}
                  onClick={() => useExample(examplePrompts[2])}
                />
                <button
                  type="button"
                  onClick={() => setShowMoreExamples(true)}
                  className="px-4 py-2 rounded-xl text-sm font-medium text-white/60 hover:text-white transition-colors"
                >
                  More examples
                </button>
              </div>

              <Button
                type="submit"
                disabled={!prompt.trim()}
                className="px-8 py-3 text-base font-semibold"
              >
                Build my MCP →
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* More Examples Drawer */}
      <AnimatePresence>
        {showMoreExamples && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowMoreExamples(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-zinc-900 border border-white/10 rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">
                  More Example Prompts
                </h3>
                <button
                  onClick={() => setShowMoreExamples(false)}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <X className="h-5 w-5 text-white/60" />
                </button>
              </div>

              <div className="grid gap-3">
                {examplePrompts.map((example, index) => (
                  <ExamplePromptChip
                    key={index}
                    prompt={exampleNames[index]}
                    onClick={() => {
                      useExample(example);
                      setShowMoreExamples(false);
                    }}
                    variant="primary"
                  />
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function PlannerTabs() {
  const [activeTab, setActiveTab] = useState<"planner" | "chat">("planner");

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.6 }}
      className="w-full max-w-6xl mx-auto mt-16"
    >
      <div className="flex items-center justify-center mb-8">
        <div className="flex bg-white/5 rounded-2xl p-1 border border-white/10">
          <button
            onClick={() => setActiveTab("planner")}
            className={`px-6 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
              activeTab === "planner"
                ? "bg-white text-black shadow-lg"
                : "text-white/60 hover:text-white"
            }`}
          >
            Planner
          </button>
          <button
            onClick={() => setActiveTab("chat")}
            className={`px-6 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
              activeTab === "chat"
                ? "bg-white text-black shadow-lg"
                : "text-white/60 hover:text-white"
            }`}
          >
            Chat history
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Planner Stepper */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white mb-4">Build Steps</h3>
          {buildSteps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: 0.1 * index }}
              className="flex items-start gap-3 p-4 rounded-xl border border-white/10 bg-white/5"
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-sm font-medium text-white/60">
                {index + 1}
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-white">{step.title}</h4>
                <p className="text-sm text-white/60">{step.description}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Middle: Live Build */}
        <div className="space-y-4">
          <div className="sticky top-4">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Live build
            </h3>
            <div className="h-64 rounded-xl border border-white/10 bg-black/20 p-4 overflow-hidden">
              <div className="h-full overflow-y-auto space-y-2">
                {demoSSEEvents.map((event, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="text-sm font-mono"
                  >
                    <span className="text-white/40">
                      [{new Date(event.timestamp).toLocaleTimeString()}]
                    </span>
                    <span className="text-white ml-2">{event.content}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right: Status */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white mb-4">Status</h3>
          <div className="space-y-3">
            {buildSteps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.1 * index }}
                className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/10"
              >
                <span className="text-sm text-white/80">{step.title}</span>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    step.status === "queued"
                      ? "bg-white/10 text-white/60"
                      : step.status === "running"
                      ? "bg-blue-500/20 text-blue-300"
                      : step.status === "success"
                      ? "bg-green-500/20 text-green-300"
                      : step.status === "needs_input"
                      ? "bg-yellow-500/20 text-yellow-300"
                      : "bg-red-500/20 text-red-300"
                  }`}
                >
                  {step.status}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ActionFooter() {
  const [showIterateDialog, setShowIterateDialog] = useState(false);
  const [iteratePrompt, setIteratePrompt] = useState("");

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.9 }}
        className="fixed bottom-0 left-0 right-0 bg-zinc-900/80 backdrop-blur-xl border-t border-white/10 p-4 z-40"
      >
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="text-sm text-white/60">Build in progress...</div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={() => setShowIterateDialog(true)}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Iterate
            </Button>
            <Button variant="ghost">
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button variant="ghost">
              <Copy className="h-4 w-4 mr-2" />
              Copy repo URL
            </Button>
            <Button variant="ghost">
              <RotateCcw className="h-4 w-4 mr-2" />
              Start over
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Iterate Dialog */}
      <AnimatePresence>
        {showIterateDialog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowIterateDialog(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-zinc-900 border border-white/10 rounded-2xl p-6 max-w-lg w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">
                  Iterate on your MCP
                </h3>
                <button
                  onClick={() => setShowIterateDialog(false)}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <X className="h-5 w-5 text-white/60" />
                </button>
              </div>

              <textarea
                value={iteratePrompt}
                onChange={(e) => setIteratePrompt(e.target.value)}
                placeholder="Tell us what to change (e.g., add auth, rename command, fix 401)."
                className="w-full h-24 rounded-xl bg-white/5 border border-white/10 p-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-300 resize-none mb-4"
              />

              <div className="flex justify-end gap-3">
                <Button
                  variant="ghost"
                  onClick={() => setShowIterateDialog(false)}
                >
                  Cancel
                </Button>
                <Button onClick={() => setShowIterateDialog(false)}>
                  Submit Iteration
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export function Footer() {
  return (
    <footer className="mt-32 border-t border-white/10 py-8">
      <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="text-sm text-white/60">Made for fast iteration.</div>
        <div className="flex items-center gap-6 text-sm">
          <a
            href="#"
            className="text-white/60 hover:text-white transition-colors"
          >
            Privacy
          </a>
          <a
            href="#"
            className="text-white/60 hover:text-white transition-colors"
          >
            Terms
          </a>
          <a
            href="#"
            className="text-white/60 hover:text-white transition-colors"
          >
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
}

// Main Home Page
export default function Home() {
  const router = useRouter();

  const handlePromptSubmit = (prompt: string) => {
    const encodedPrompt = encodeURIComponent(prompt);
    const projectName = prompt.substring(0, 50);
    const encodedName = encodeURIComponent(projectName);
    // Navigate to build page - don't start local build process here
    router.push(`/build?q=${encodedPrompt}&name=${encodedName}`);
  };

  return (
    <div className="min-h-screen w-full bg-[#0b0b0c] text-white overflow-x-hidden">
      <TopNav onDocs={() => alert("Docs coming soon")} />

      <main className="relative">
        {/* Hero Section */}
        <section className="pt-20 pb-16 px-4">
          <div className="max-w-6xl mx-auto text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent leading-tight"
            >
              From idea → MCP in minutes
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl md:text-2xl text-white/80 mb-8 max-w-4xl mx-auto leading-relaxed"
            >
              Describe your tool. We plan it, ask smart questions, stream code
              over SSE, and ship a working MCP you can iterate on.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-wrap justify-center gap-3 mb-12"
            >
              <TrustChip>AI-assisted planning</TrustChip>
              <TrustChip>SSE live logs</TrustChip>
              <TrustChip>One-click iterate</TrustChip>
            </motion.div>
          </div>
        </section>

        {/* Prompt Input Card */}
        <section className="px-4 pb-16">
          <PromptCard onPromptSubmit={handlePromptSubmit} />
        </section>
      </main>

      <Footer />
    </div>
  );
}
