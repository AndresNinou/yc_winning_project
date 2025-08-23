'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Rocket,
  Github,
  BookOpen,
  ChevronRight,
} from 'lucide-react'

/*************************
 * Types
 *************************/
interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'ghost' | 'subtle' | 'danger'
  className?: string
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

interface TextareaProps {
  value: string
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
  placeholder?: string
  rows?: number
  className?: string
}

interface BadgeProps {
  children: React.ReactNode
  tone?: 'default' | 'success' | 'warn' | 'info'
  className?: string
}

interface CardProps {
  children: React.ReactNode
  className?: string
}

/*************************
 * Minimal UI atoms
 *************************/
const Button = ({ children, onClick, variant = 'primary', className = '', disabled, type }: ButtonProps) => {
  const base = 'inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-sm font-medium transition active:scale-[.98]'
  const variants: Record<string, string> = {
    primary: 'bg-white text-black shadow-sm hover:shadow disabled:opacity-60 disabled:cursor-not-allowed',
    ghost: 'bg-transparent text-white/90 hover:text-white border border-white/10 hover:border-white/20',
    subtle: 'bg-zinc-900/50 border border-zinc-800 text-white/90 hover:bg-zinc-900',
    danger: 'bg-red-500 text-white hover:bg-red-600 disabled:opacity-60 disabled:cursor-not-allowed',
  }
  return (
    <button type={type} disabled={disabled} onClick={onClick} className={`${base} ${variants[variant]} ${className}`}>
      {children}
    </button>
  )
}

const Textarea = ({ value, onChange, placeholder, rows = 6, className = '' }: TextareaProps) => (
  <textarea
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    rows={rows}
    className={`w-full rounded-xl bg-zinc-900/60 border border-zinc-800 px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-600 ${className}`}
  />
)

const Badge = ({ children, tone = 'default', className = '' }: BadgeProps) => {
  const tones: Record<string, string> = {
    default: 'bg-zinc-800 text-zinc-200',
    success: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40',
    warn: 'bg-amber-500/20 text-amber-300 border border-amber-500/40',
    info: 'bg-sky-500/20 text-sky-300 border border-sky-500/40',
  }
  return <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs ${tones[tone]} ${className}`}>{children}</span>
}

const Card = ({ children, className = '' }: CardProps) => (
  <div className={`rounded-2xl border border-zinc-800 bg-zinc-900/60 p-4 ${className}`}>{children}</div>
)

/*************************
 * Layout bits
 *************************/
function TopNav({ onDocs }: { onDocs: () => void }) {
  return (
    <div className="sticky top-0 z-30 w-full border-b border-zinc-900/80 bg-[#0b0b0c]/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-black"><Rocket className="h-4 w-4" /></div>
          <span className="text-sm font-semibold tracking-wide text-white/90">MCP Tool Builder</span>
          <Badge className="ml-2" tone="info">beta</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" onClick={onDocs}><BookOpen className="h-4 w-4" /> Docs</Button>
          <a href="#" className="hidden md:inline-flex"><Button variant="ghost"><Github className="h-4 w-4" /> GitHub</Button></a>
        </div>
      </div>
    </div>
  )
}

function Footer() {
  return (
    <div className="mt-20 border-t border-zinc-900/80 py-8 text-center text-xs text-zinc-500">© {new Date().getFullYear()} MCP Tool Builder • YC-style demo</div>
  )
}

/*************************
 * Landing
 *************************/
function Landing({ prompt, setPrompt, onExample, onStart }: { prompt: string; setPrompt: (s: string) => void; onExample: (s: string) => void; onStart: () => void }) {
  const EX = [
    'Build an MCP that monitors GitHub issues for a repo and exposes search_issues(owner, repo, query).',
    'Make a Notion MCP that fetches a page by URL and returns markdown.',
    'Create a Postgres MCP with list_tables, describe_table, select(query, limit).',
  ]
  const canStart = prompt.trim().length > 8
  return (
    <section className="mx-auto max-w-6xl px-4">
      <div className="mx-auto mt-20 max-w-3xl text-center">
        <Badge tone="success" className="mb-3">FastMCP mock builder</Badge>
        <h1 className="text-3xl md:text-5xl font-semibold tracking-tight leading-tight">Ship <span className="text-white">MCP tools</span> in minutes</h1>
        <p className="mt-3 text-white/70">Type what you want. We open a planning workspace, ask clarifying questions, stream code + build status via SSE, then let you iterate.</p>
      </div>
      <Card className="mx-auto mt-10 max-w-3xl">
        <form onSubmit={(e) => { e.preventDefault(); if (canStart) onStart() }}>
          <label className="text-sm text-zinc-400">Your prompt</label>
          <Textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder={EX[0]} />
          <div className="mt-3 flex flex-col items-start gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap gap-2">
              {EX.map((ex, i) => (
                <button key={i} type="button" onClick={() => onExample(ex)} className="rounded-full border border-zinc-800 px-3 py-1 text-xs text-zinc-300 hover:bg-zinc-900">Use example {i + 1}</button>
              ))}
            </div>
            <div className="flex items-center gap-2 self-end">
              <Button type="submit" disabled={!canStart}>Build an MCP <ChevronRight className="h-4 w-4" /></Button>
            </div>
          </div>
        </form>
      </Card>
    </section>
  )
}

/*************************
 * Root component (includes landing + builder for preview)
 *************************/
export default function App() {
  const [prompt, setPrompt] = useState('')
  const router = useRouter()

  const handleStart = () => {
    const projectName = suggestName(prompt)
    router.push(`/build?${new URLSearchParams({ q: prompt, name: projectName })}`)
  }

  return (
    <div className="min-h-screen w-full bg-[#0b0b0c] text-white">
      <TopNav onDocs={() => alert('Docs coming soon')} />
      <Landing
        prompt={prompt}
        setPrompt={setPrompt}
        onExample={(e) => setPrompt(e)}
        onStart={handleStart}
      />
      <Footer />
    </div>
  )
}

/*************************
 * Helpers
 *************************/
function suggestName(prompt: string) {
  if (!prompt) return 'Untitled MCP Tool'
  const noun = prompt.replace(/[^a-zA-Z0-9\s]/g, ' ').split(/\s+/).filter(Boolean).slice(0,2).map(w=>w[0].toUpperCase()+w.slice(1).toLowerCase()).join('')
  return noun ? `${noun}MCP` : 'Untitled MCP Tool'
}
