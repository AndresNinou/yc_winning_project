import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  tone?: 'default' | 'success' | 'warn' | 'info' | 'danger'
  className?: string
}

export const Badge = ({ children, tone = 'default', className = '' }: BadgeProps) => {
  const tones: Record<string, string> = {
    default: 'bg-zinc-800 text-zinc-200',
    success: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40',
    warn: 'bg-amber-500/20 text-amber-300 border border-amber-500/40',
    info: 'bg-sky-500/20 text-sky-300 border border-sky-500/40',
    danger: 'bg-red-500/20 text-red-300 border border-red-500/40',
  }
  return <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs ${tones[tone]} ${className}`}>{children}</span>
}
