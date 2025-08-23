'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { TopNav } from '@/components/layout'
import { Button } from '@/components/ui'

/*************************
 * Home Page
 *************************/
export default function Home() {
  const [prompt, setPrompt] = useState('Build an MCP that monitors GitHub issues for a repo and exposes search_issues(owner, repo, query).')
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prompt.trim()) {
      const encodedPrompt = encodeURIComponent(prompt.trim())
      const projectName = prompt.trim().substring(0, 50)
      const encodedName = encodeURIComponent(projectName)
      router.push(`/build?q=${encodedPrompt}&name=${encodedName}`)
    }
  }

  const useExample = (example: string) => {
    setPrompt(example)
  }

  const examples = [
    'Build an MCP that monitors GitHub issues for a repo and exposes search_issues(owner, repo, query).',
    'Make a Notion MCP that fetches a page by URL and returns markdown.',
    'Create a Postgres MCP with list_tables, describe_table, select(query, limit).'
  ]

  return (
    <div className="min-h-screen w-full bg-[#0b0b0c] text-white">
      <TopNav onDocs={() => alert('Docs coming soon')} />
      <main className="flex min-h-[calc(100vh-80px)] items-center justify-center px-4">
        <div className="w-full max-w-4xl">
          <div className="relative overflow-hidden rounded-3xl border border-zinc-800 bg-gradient-to-br from-blue-950/20 via-zinc-900/40 to-purple-950/20 p-8 md:p-12">
            {/* Background pattern */}
            <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%239C92AC%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%221%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40"></div>
            
            <div className="relative z-10 text-center">
              <h1 className="text-4xl font-bold tracking-tight text-white md:text-6xl">
                Ship MCP tools in minutes
              </h1>
              <p className="mt-6 text-lg text-zinc-300 md:text-xl max-w-3xl mx-auto">
                Type what you want. We open a planning workspace, ask clarifying questions, stream code + build status via SSE, then let you iterate.
              </p>
              
              <div className="mt-12 max-w-2xl mx-auto">
                <form onSubmit={handleSubmit} className="rounded-2xl border border-zinc-700 bg-zinc-900/60 p-6 backdrop-blur-sm">
                  <div className="text-left">
                    <h3 className="text-lg font-semibold text-white mb-2">MCP Tool Builder</h3>
                    <p className="text-sm text-zinc-400 mb-4">Ship MCP tools in minutes with AI-powered planning and code generation</p>
                    
                    <div className="space-y-3">
                      <label className="block text-sm font-medium text-zinc-300">Your prompt</label>
                      <textarea 
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        className="w-full h-24 rounded-xl bg-zinc-800/60 border border-zinc-700 px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                        placeholder="Describe your MCP tool requirements..."
                      />
                      
                      <div className="flex items-center justify-between">
                        <div className="flex gap-2">
                          {examples.map((example, index) => (
                            <button
                              key={index}
                              type="button"
                              onClick={() => useExample(example)}
                              className="px-3 py-1.5 rounded-lg bg-zinc-800 text-zinc-300 text-xs hover:bg-zinc-700 transition-colors"
                            >
                              Use example {index + 1}
                            </button>
                          ))}
                        </div>
                        <Button type="submit" disabled={!prompt.trim()}>
                          Build an MCP →
                        </Button>
                      </div>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
