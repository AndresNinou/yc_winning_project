import React from 'react'
import { Rocket, Github, BookOpen } from 'lucide-react'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'

interface TopNavProps {
  onDocs: () => void
}

export function TopNav({ onDocs }: TopNavProps) {
  return (
    <div className="sticky top-0 z-30 w-full border-b border-zinc-900/80 bg-[#0b0b0c]/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-black">
            <Rocket className="h-4 w-4" />
          </div>
          <span className="text-sm font-semibold tracking-wide text-white/90">MCP Tool Builder</span>
          <Badge className="ml-2" tone="info">beta</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" onClick={onDocs}>
            <BookOpen className="h-4 w-4" /> Docs
          </Button>
          <a href="#" className="hidden md:inline-flex">
            <Button variant="ghost">
              <Github className="h-4 w-4" /> GitHub
            </Button>
          </a>
        </div>
      </div>
    </div>
  )
}
