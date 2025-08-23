import React from 'react'

interface InputProps {
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  placeholder?: string
  className?: string
  [key: string]: unknown
}

export const Input = ({ value, onChange, placeholder, className = '', ...rest }: InputProps) => (
  <input
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className={`w-full rounded-xl bg-zinc-900/60 border border-zinc-800 px-4 py-2 text-sm text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-600 ${className}`}
    {...rest}
  />
)
