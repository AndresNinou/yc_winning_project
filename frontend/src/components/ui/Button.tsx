import React from 'react'

interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'ghost' | 'subtle' | 'danger'
  className?: string
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

export const Button = ({ children, onClick, variant = 'primary', className = '', disabled, type }: ButtonProps) => {
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
