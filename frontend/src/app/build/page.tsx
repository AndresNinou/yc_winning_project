'use client'

import React, { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import ReactMarkdown from 'react-markdown'
import {
  Rocket,
  Github,
  BookOpen,
  ChevronRight,
  Loader2,
  Play,
  FileCode,
  FileJson2,
  Send,
  Bot,
  FileText,
  ChevronLeft,
  ChevronRight as ChevronRightIcon,
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

interface InputProps {
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  placeholder?: string
  className?: string
  [key: string]: unknown
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

interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
  ts: number
}

interface GeneratedFile {
  name: string
  content: string
  type: 'json' | 'python' | 'markdown' | 'yaml'
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

const Input = ({ value, onChange, placeholder, className = '', ...rest }: InputProps) => (
  <input
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className={`w-full rounded-xl bg-zinc-900/60 border border-zinc-800 px-4 py-2 text-sm text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-600 ${className}`}
    {...rest}
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
 * Builder Screen (three panels with collapsible sides)
 * Left: planner.md (collapsible)
 * Middle: Generated code files (expands when sides collapsed)
 * Right: AI agent chat (collapsible)
 *************************/
function BuilderScreen({ prompt, projectName }: { prompt: string; projectName: string }) {
  // Panel collapse state
  const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false)
  const [rightPanelCollapsed, setRightPanelCollapsed] = useState(false)

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'user', text: prompt || 'Build an MCP', ts: Date.now() },
  ])
  const [chatInput, setChatInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [requirementsComplete, setRequirementsComplete] = useState(false)

  // Generated files
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFile[]>([])
  const [activeFile, setActiveFile] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState(false)

  // Planner content
  const [plannerContent, setPlannerContent] = useState(`# MCP Tool Planning Document

## Initial Requirements
- Build an MCP tool based on user prompt
- Generate necessary code files
- Ensure proper MCP protocol compliance

## Chat History
*Waiting for AI agent to ask clarifying questions...*

## Implementation Plan
*To be developed based on requirements...*

## Generated Files
- manifest.json
- server.py
- Additional files as needed

## Status
🔄 Planning in progress...
`)

  // Mock AI questions for demonstration
  const aiQuestions = [
    "What specific functionality should this Notion MCP provide?",
    "Do you need authentication with Notion API?",
    "Should it support both reading and writing to Notion?",
    "What format should the markdown output be in?",
    "Are there any specific error handling requirements?"
  ]

  // Send chat message
  function sendMessage() {
    if (!chatInput.trim() || isTyping) return
    
    const userMessage: ChatMessage = {
      role: 'user',
      text: chatInput,
      ts: Date.now()
    }
    
    setMessages(prev => [...prev, userMessage])
    setChatInput('')
    setIsTyping(true)
    
    // Simulate AI response
    setTimeout(() => {
      const currentQuestionIndex = Math.floor(messages.length / 2)
      let aiResponse = ''
      
      if (currentQuestionIndex < aiQuestions.length) {
        aiResponse = aiQuestions[currentQuestionIndex]
      } else if (chatInput.toLowerCase().includes('yes') || chatInput.toLowerCase().includes('build')) {
        aiResponse = "Perfect! I have all the requirements. Let me generate the planner.md and code files for you."
        setRequirementsComplete(true)
        generateFiles()
      } else {
        aiResponse = "Thank you for that information. Do you have any other requirements or shall I proceed with building the MCP tool? (Say 'Yes, build' to continue)"
      }
      
      const aiMessage: ChatMessage = {
        role: 'assistant',
        text: aiResponse,
        ts: Date.now()
      }
      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
      updatePlannerWithChat()
    }, 1000)
  }

  // Update planner with chat content
  function updatePlannerWithChat() {
    const chatContent = messages
      .map(m => `${m.role === 'user' ? '👤 User' : '🤖 AI Agent'}: ${m.text}`)
      .join('\n\n')
    
    const newPlannerContent = `# MCP Tool Planning Document

## Initial Requirements
- Build an MCP tool based on user prompt: "${prompt}"
- Generate necessary code files
- Ensure proper MCP protocol compliance

## Chat History
${chatContent}

## Implementation Plan
${requirementsComplete ? '✅ Requirements gathered, proceeding with code generation...' : '*To be developed based on requirements...*'}

## Generated Files
${generatedFiles.length > 0 ? generatedFiles.map(f => `- ${f.name}`).join('\n') : '- manifest.json\n- server.py\n- Additional files as needed'}

## Status
${requirementsComplete ? '🚀 Generating code files...' : '🔄 Gathering requirements...'}
`

    setPlannerContent(newPlannerContent)
  }

  // Generate files when requirements are complete
  function generateFiles() {
    setIsGenerating(true)
    
    // Simulate file generation
    setTimeout(() => {
      const files: GeneratedFile[] = [
        {
          name: 'manifest.json',
          content: `{
  "$schema": "https://schema.mcp.alignment.dev/manifest-1.json",
  "name": "notion-mcp-server",
  "version": "0.1.0",
  "description": "Notion MCP server that fetches pages by URL and returns markdown",
  "server": { 
    "command": "python", 
    "args": ["server.py"], 
    "env": ["NOTION_API_KEY"] 
  },
  "tools": [
    {
      "name": "fetch_page",
      "description": "Fetch a Notion page by URL and return markdown",
      "input_schema": { 
        "type": "object", 
        "properties": { 
          "url": {"type": "string", "description": "Notion page URL"} 
        }, 
        "required": ["url"] 
      }
    }
  ],
  "resources": [ 
    { "name": "notion_pages", "uri": "mcp://notion/pages" } 
  ]
}`,
          type: 'json'
        },
        {
          name: 'server.py',
          content: `import os
import requests
from typing import Dict, Any

class NotionMCP:
    def __init__(self):
        self.api_key = os.getenv('NOTION_API_KEY')
        self.base_url = 'https://api.notion.com/v1'
        
    def fetch_page_markdown(self, url: str) -> str:
        """Fetch a Notion page and convert to markdown"""
        try:
            # Extract page ID from URL
            page_id = self._extract_page_id(url)
            
            # Fetch page content
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Notion-Version': '2022-06-28'
            }
            
            response = requests.get(
                f"{self.base_url}/pages/{page_id}",
                headers=headers
            )
            response.raise_for_status()
            
            page_data = response.json()
            return self._convert_to_markdown(page_data)
            
        except Exception as e:
            return f"Error fetching page: {str(e)}"
    
    def _extract_page_id(self, url: str) -> str:
        """Extract page ID from Notion URL"""
        # Implementation for extracting page ID
        return url.split('/')[-1].split('?')[0]
    
    def _convert_to_markdown(self, page_data: Dict[str, Any]) -> str:
        """Convert Notion page data to markdown"""
        # Implementation for converting to markdown
        title = page_data.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Untitled')
        return f"# {title}\\n\\n*Markdown content would be generated here*"

# Initialize MCP server
mcp = NotionMCP()

if __name__ == "__main__":
    print("Notion MCP Server running...")
    # MCP protocol implementation would go here`,
          type: 'python'
        },
        {
          name: 'requirements.txt',
          content: `requests>=2.28.0
python-dotenv>=0.19.0
markdown>=3.4.0`,
          type: 'yaml'
        },
        {
          name: 'README.md',
          content: `# Notion MCP Server

A Model Context Protocol (MCP) server that integrates with Notion API to fetch pages and return markdown content.

## Setup

1. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. Set environment variables:
   \`\`\`bash
   export NOTION_API_KEY="your_notion_api_key"
   \`\`\`

3. Run the server:
   \`\`\`bash
   python server.py
   \`\`\`

## Usage

The server provides a \`fetch_page\` tool that takes a Notion page URL and returns the content in markdown format.

## Features

- Fetch Notion pages by URL
- Convert page content to markdown
- MCP protocol compliance
- Error handling and logging`,
          type: 'markdown'
        }
      ]
      
      setGeneratedFiles(files)
      setActiveFile(files[0].name)
      setIsGenerating(false)
    }, 3000)
  }

  // Update planner when messages change
  useEffect(() => {
    updatePlannerWithChat()
  }, [messages, generatedFiles, requirementsComplete, prompt])

  // Get file icon based on type
  function getFileIcon(type: string) {
    switch (type) {
      case 'json': return <FileJson2 className="h-4 w-4" />
      case 'python': return <FileCode className="h-4 w-4" />
      case 'markdown': return <FileText className="h-4 w-4" />
      case 'yaml': return <FileText className="h-4 w-4" />
      default: return <FileCode className="h-4 w-4" />
    }
  }

  // Calculate grid columns based on collapsed state
  const getGridCols = () => {
    if (leftPanelCollapsed && rightPanelCollapsed) return 'lg:grid-cols-12'
    if (leftPanelCollapsed || rightPanelCollapsed) return 'lg:grid-cols-12'
    return 'lg:grid-cols-12'
  }

  const getLeftPanelCols = () => {
    if (leftPanelCollapsed) return 'lg:col-span-1'
    return 'lg:col-span-3'
  }

  const getMiddlePanelCols = () => {
    if (leftPanelCollapsed && rightPanelCollapsed) return 'lg:col-span-10'
    if (leftPanelCollapsed || rightPanelCollapsed) return 'lg:col-span-8'
    return 'lg:col-span-6'
  }

  const getRightPanelCols = () => {
    if (rightPanelCollapsed) return 'lg:col-span-1'
    return 'lg:col-span-3'
  }

  return (
    <div className="min-h-screen w-full bg-[#0b0b0c] text-white">
      <TopNav onDocs={() => alert('Docs coming soon')} />
      <section className="mx-auto max-w-7xl px-4">
        {/* Header controls */}
        <div className="mt-10 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-2 text-zinc-400 text-xs">
              <span>Project</span>
              <ChevronRight className="h-3 w-3" />
              <span className="text-white/80">{projectName}</span>
            </div>
            <h2 className="mt-1 text-xl font-semibold tracking-tight">AI-Powered MCP Builder</h2>
            <p className="mt-1 text-sm text-zinc-400 max-w-2xl">
              Initial Prompt: <span className="text-zinc-300">{prompt || '(Build an MCP)'}</span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Badge tone="info">SSE Enabled</Badge>
          </div>
        </div>

        {/* Three panels with collapsible functionality */}
        <div className={`mt-6 grid grid-cols-1 gap-6 ${getGridCols()}`}>
          {/* LEFT: Planner.md (Collapsible) */}
          <Card className={getLeftPanelCols()}>
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-white/90">
                <FileText className="h-4 w-4" /> 
                {!leftPanelCollapsed && 'Planner.md'}
              </div>
              <Button
                variant="ghost"
                onClick={() => setLeftPanelCollapsed(!leftPanelCollapsed)}
                className="p-1 h-6 w-6"
              >
                {leftPanelCollapsed ? <ChevronRightIcon className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
              </Button>
            </div>
            
                         {!leftPanelCollapsed && (
               <div className="rounded-xl border border-zinc-800 bg-black/60 p-3">
                 <div className="max-h-[500px] overflow-auto text-xs leading-relaxed prose prose-invert prose-sm max-w-none">
                   <ReactMarkdown>{plannerContent}</ReactMarkdown>
                 </div>
               </div>
             )}
          </Card>

          {/* MIDDLE: Generated Code Files (Expands when sides collapsed) */}
          <Card className={getMiddlePanelCols()}>
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-white/90">
                <FileCode className="h-4 w-4" /> Generated Code Files
              </div>
              {requirementsComplete && (
                <Button 
                  onClick={generateFiles} 
                  disabled={isGenerating}
                  className="px-3 py-1 text-xs"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-3 w-3 animate-spin" /> Generating...
                    </>
                  ) : (
                    <>
                      <Play className="h-3 w-3" /> Generate
                    </>
                  )}
                </Button>
              )}
            </div>
            
            {generatedFiles.length > 0 ? (
              <>
                                 <div className="mb-3 flex gap-2 flex-wrap">
                  {generatedFiles.map((file, index) => (
                    <button
                      key={`${file.name}-${index}`}
                      onClick={() => setActiveFile(file.name)}
                      className={`rounded-xl border px-3 py-1 text-xs flex items-center gap-2 whitespace-nowrap ${
                        activeFile === file.name 
                          ? 'border-zinc-600 bg-zinc-900' 
                          : 'border-zinc-800 hover:bg-zinc-900'
                      }`}
                    >
                      {getFileIcon(file.type)}
                      {file.name}
                    </button>
                  ))}
                </div>
                <div className="rounded-xl border border-zinc-800 bg-black/60 p-3">
                  <pre className="max-h-[500px] overflow-auto text-xs leading-relaxed break-words">
                    <code className="whitespace-pre-wrap break-words">{generatedFiles.find(f => f.name === activeFile)?.content}</code>
                  </pre>
                </div>
              </>
            ) : (
              <div className="rounded-xl border border-zinc-800 bg-black/60 p-8 text-center">
                <div className="text-zinc-400 text-sm">
                  Generated code files will appear here.
                  <br />
                  Can have multiple files too.
                </div>
              </div>
            )}
          </Card>

          {/* RIGHT: AI Agent Chat (Collapsible) */}
          <Card className={getRightPanelCols()}>
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-white/90">
                <Bot className="h-4 w-4" /> 
                {!rightPanelCollapsed && 'AI Agent Chat'}
              </div>
              <Button
                variant="ghost"
                onClick={() => setRightPanelCollapsed(!rightPanelCollapsed)}
                className="p-1 h-6 w-6"
              >
                {rightPanelCollapsed ? <ChevronLeft className="h-3 w-3" /> : <ChevronRightIcon className="h-3 w-3" />}
              </Button>
            </div>
            
            {!rightPanelCollapsed && (
              <>
                                 {/* Chat messages */}
                 <div className="max-h-96 space-y-3 overflow-auto rounded-xl bg-black/30 p-3 mb-3">
                   {messages.map((m, i) => (
                     <div key={`message-${i}`} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                       <div className={`max-w-[80%]`}>
                         <div className={`rounded-xl px-3 py-2 text-sm ${
                           m.role === 'user' ? 'bg-zinc-800 text-zinc-100' : 'bg-zinc-900 text-zinc-300'
                         }`}>
                           {m.text}
                         </div>
                       </div>
                     </div>
                   ))}
                                     {isTyping && (
                     <div className="flex justify-start">
                       <div className="max-w-[80%]">
                         <div className="rounded-xl bg-zinc-900 px-3 py-2 text-sm text-zinc-300">
                           <Loader2 className="h-4 w-4 animate-spin" /> AI is typing...
                         </div>
                       </div>
                     </div>
                   )}
                </div>

                {/* Chat input */}
                <div className="flex gap-2">
                  <Input 
                    value={chatInput} 
                    onChange={(e) => setChatInput(e.target.value)} 
                    placeholder="Ask questions or provide more details..." 
                    onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && sendMessage()}
                  />
                  <Button 
                    onClick={sendMessage} 
                    disabled={!chatInput.trim() || isTyping}
                    className="px-4"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="mt-3 text-xs text-zinc-500 text-center">
                  Asks questions until user is satisfied, mock it for now. Only until user says &quot;Yes. Build&quot;. 
                  After that, planner.md is generated.
                </div>
              </>
            )}
          </Card>
        </div>
      </section>
      <Footer />
    </div>
  )
}

function BuildPageContent() {
  const searchParams = useSearchParams()
  const prompt = searchParams.get('q') || 'Build an MCP'
  const projectName = searchParams.get('name') || 'Untitled MCP Tool'

  return <BuilderScreen prompt={prompt} projectName={projectName} />
}

export default function BuildPage() {
  return (
    <Suspense fallback={<div className="min-h-screen w-full bg-[#0b0b0c] text-white flex items-center justify-center">Loading...</div>}>
      <BuildPageContent />
    </Suspense>
  )
}
