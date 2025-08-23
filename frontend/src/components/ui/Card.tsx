import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
}

export const Card = ({ children, className = '' }: CardProps) => (
  <div className={`rounded-2xl border border-zinc-800 bg-zinc-900/60 p-4 ${className}`}>{children}</div>
)
