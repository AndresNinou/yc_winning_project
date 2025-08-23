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
  CheckCircle,
  AlertCircle,
  Clock,
} from 'lucide-react'
import { TopNav } from '@/components/layout'
import { Button, Badge, Input, Card } from '@/components/ui'

/*************************
 * Types
 *************************/
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

interface StreamEvent {
  id: string
  type: 'planning' | 'scaffolding' | 'generating' | 'testing' | 'deploying' | 'tool_use' | 'content' | 'message_info'
  status: 'pending' | 'loading' | 'completed' | 'error'
  title: string
  description: string
  startTime?: number
  endTime?: number
  error?: string
  tool_name?: string
  content?: string
  message_type?: string
}

/*************************
 * Layout bits
 *************************/
function Footer() {
  return (
    <div className="mt-20 border-t border-zinc-900/80 py-8 text-center text-xs text-zinc-500">© {new Date().getFullYear()} MCP Tool Builder • YC-style demo</div>
  )
}

/*************************
 * Streaming Event Component
 *************************/
function StreamEventItem({ event }: { event: StreamEvent }) {
  const getStatusIcon = () => {
    switch (event.status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-emerald-400" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-400" />
      case 'loading':
        return <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />
      case 'pending':
        return <Clock className="h-4 w-4 text-zinc-400" />
      default:
        return <Clock className="h-4 w-4 text-zinc-400" />
    }
  }

  const getStatusColor = () => {
    switch (event.status) {
      case 'completed':
        return 'border-emerald-500/30 bg-emerald-500/10'
      case 'error':
        return 'border-red-500/30 bg-red-500/10'
      case 'loading':
        return 'border-blue-500/30 bg-blue-500/10'
      case 'pending':
        return 'border-zinc-500/30 bg-zinc-500/10'
      default:
        return 'border-zinc-500/30 bg-zinc-500/10'
    }
  }

  const getDuration = () => {
    if (event.startTime && event.endTime) {
      return `${((event.endTime - event.startTime) / 1000).toFixed(1)}s`
    }
    if (event.startTime && event.status === 'loading') {
      return `${((Date.now() - event.startTime) / 1000).toFixed(1)}s`
    }
    return null
  }

  // Special handling for tool usage events
  if (event.type === 'tool_use' && event.tool_name) {
    return (
      <div className="flex items-start gap-3 p-3 rounded-lg border border-blue-500/30 bg-blue-500/10">
        <div className="flex-shrink-0 mt-0.5">
          <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-white">Using Tool: {event.tool_name}</h4>
            {getDuration() && (
              <span className="text-xs text-zinc-400">{getDuration()}</span>
            )}
          </div>
          <p className="text-xs text-zinc-300 mt-1">Executing {event.tool_name} operation...</p>
        </div>
      </div>
    )
  }

  // Special handling for content events
  if (event.type === 'content' && event.content) {
  return (
      <div className="flex items-start gap-3 p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10">
        <div className="flex-shrink-0 mt-0.5">
          <CheckCircle className="h-4 w-4 text-emerald-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-white">Content Generated</h4>
            {getDuration() && (
              <span className="text-xs text-zinc-400">{getDuration()}</span>
            )}
        </div>
          <p className="text-xs text-zinc-300 mt-1">{event.content.substring(0, 100)}...</p>
      </div>
    </div>
  )
}

  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg border ${getStatusColor()}`}>
      <div className="flex-shrink-0 mt-0.5">
        {getStatusIcon()}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-white">{event.title}</h4>
          {getDuration() && (
            <span className="text-xs text-zinc-400">{getDuration()}</span>
          )}
        </div>
        <p className="text-xs text-zinc-300 mt-1">{event.description}</p>
        {event.error && (
          <p className="text-xs text-red-400 mt-1">{event.error}</p>
        )}
      </div>
    </div>
  )
}

/*************************
 * Build Progress Indicator Component
 *************************/
function BuildProgressIndicator({ events }: { events: StreamEvent[] }) {
  const currentStep = events.find(event => event.status === 'loading')
  const completedSteps = events.filter(event => event.status === 'completed')
  const totalSteps = events.length
  
  if (!currentStep && completedSteps.length === 0) return null
  
  return (
    <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 mb-3">
      <div className="flex items-center gap-2 mb-2">
        <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />
        <span className="text-sm font-medium text-white">Building MCP Tool</span>
        <span className="text-xs text-blue-400">
          {completedSteps.length}/{totalSteps} steps completed
        </span>
      </div>
      
      {currentStep && (
        <div className="text-xs text-blue-300">
          Current: {currentStep.title}
        </div>
      )}
      
      <div className="mt-2 flex gap-1">
        {events.map((event) => (
          <div
            key={event.id}
            className={`h-1 flex-1 rounded-full ${
              event.status === 'completed' 
                ? 'bg-emerald-500' 
                : event.status === 'loading' 
                ? 'bg-blue-500' 
                : 'bg-zinc-600'
            }`}
          />
        ))}
      </div>
    </div>
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

  // Chat state - Initialize with user prompt and Claude's greeting
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'user', text: prompt || 'Build an MCP', ts: Date.now() },
    { 
      role: 'assistant', 
      text: `Hi! I'm Claude, and I'm here to help you build an excellent MCP (Model Context Protocol) tool. I see you want to: "${prompt}"\n\nLet me ask a few questions to understand your requirements better so I can create exactly what you need. What specific functionality do you envision for this MCP tool?`, 
      ts: Date.now() + 100 
    }
  ])
  const [chatInput, setChatInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [requirementsComplete, setRequirementsComplete] = useState(false)

  // Generated files
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFile[]>([])
  const [activeFile, setActiveFile] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState(false)

  // Backend health status
  const [backendHealth, setBackendHealth] = useState<'healthy' | 'unhealthy' | 'checking'>('checking')

  // Streaming events state
  const [streamEvents, setStreamEvents] = useState<StreamEvent[]>([
    {
      id: 'planning',
      type: 'planning',
      status: 'pending',
      title: 'Planning & Requirements',
      description: 'Gathering requirements and planning the MCP tool architecture'
    },
    {
      id: 'scaffolding',
      type: 'scaffolding',
      status: 'pending',
      title: 'Project Scaffolding',
      description: 'Creating project structure and initial files'
    },
    {
      id: 'generating',
      type: 'generating',
      status: 'pending',
      title: 'Code Generation',
      description: 'Generating MCP tool implementation code'
    },
    {
      id: 'testing',
      type: 'testing',
      status: 'pending',
      title: 'Testing & Validation',
      description: 'Testing the generated MCP tool'
    },
    {
      id: 'deploying',
      type: 'deploying',
      status: 'pending',
      title: 'Deployment',
      description: 'Preparing for deployment and usage'
    }
  ])

  // Check backend health
  async function checkBackendHealth() {
    try {
      setBackendHealth('checking')
      const response = await fetch('/api/claude/health')
      if (response.ok) {
        const data = await response.json()
        setBackendHealth(data.status === 'healthy' ? 'healthy' : 'unhealthy')
      } else {
        setBackendHealth('unhealthy')
      }
    } catch (error) {
      console.error('Health check failed:', error)
      setBackendHealth('unhealthy')
    }
  }

  // Start streaming events
  function startStreamingEvents() {
    // Reset all events to pending status
    setStreamEvents(prev => prev.map(event => ({
      ...event,
      status: 'pending' as const,
      startTime: undefined,
      endTime: undefined,
      error: undefined
    })))

    // Start the first event (planning) - backend will control the rest
    setStreamEvents(prev => prev.map(event => 
      event.id === 'planning' 
        ? { ...event, status: 'loading', startTime: Date.now() }
        : event
    ))

    // Add build start message to chat
    const buildStartMessage: ChatMessage = {
      role: 'assistant',
      text: '🚀 **Starting MCP Tool Build Process**\n\nI\'ll now begin building your MCP tool step by step. Watch the progress as I use various tools to create your project.',
      ts: Date.now()
    }
    setMessages(prev => [...prev, buildStartMessage])

    // Start mock backend events (in real implementation, this would be real SSE)
    simulateBackendEvents()
  }

  // Handle backend events and update streaming events
  function handleBackendEvent(eventData: any) {
    const eventType = eventData.type
    const toolName = eventData.tool_name
    const content = eventData.content
    const error = eventData.error

    if (eventType === 'tool_use' && toolName) {
      // Add tool usage event to chat
      const toolMessage: ChatMessage = {
        role: 'assistant',
        text: `🛠️ **Using Tool: ${toolName}**\nExecuting ${toolName} operation...`,
        ts: Date.now()
      }
      setMessages(prev => [...prev, toolMessage])
      
      // Update the corresponding build step
      updateBuildStep(toolName)
    } else if (eventType === 'content' && content) {
      // Add content generation event to chat
      const contentMessage: ChatMessage = {
        role: 'assistant',
        text: `✅ **Content Generated**\n${content}`,
        ts: Date.now()
      }
      setMessages(prev => [...prev, contentMessage])
    } else if (eventType === 'done') {
      // Mark current step as completed and start next
      completeCurrentStep()
    } else if (eventType === 'error' && error) {
      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: 'assistant',
        text: `❌ **Error**\n${error}`,
        ts: Date.now()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  // Update build step based on tool usage
  function updateBuildStep(toolName: string) {
    // Map tools to build steps
    const toolToStep: Record<string, string> = {
      'ListDir': 'scaffolding',
      'CreateFile': 'scaffolding',
      'Write': 'generating',
      'Search': 'planning',
      'Read': 'planning'
    }
    
    const stepId = toolToStep[toolName]
    if (stepId) {
      setStreamEvents(prev => prev.map(event => 
        event.id === stepId 
          ? { ...event, status: 'loading', startTime: Date.now() }
          : event
      ))
    }
  }

  // Complete current step and start next
  function completeCurrentStep() {
    setStreamEvents(prev => {
      const currentLoading = prev.find(event => event.status === 'loading')
      if (!currentLoading) return prev
      
      // Mark current as completed
      const updated = prev.map(event => 
        event.id === currentLoading.id 
          ? { ...event, status: 'completed' as const, endTime: Date.now() }
          : event
      )
      
      // Add completion message to chat
      const completionMessage: ChatMessage = {
        role: 'assistant',
        text: `🎯 **Step Completed: ${currentLoading.title}**\nSuccessfully completed ${currentLoading.title.toLowerCase()}`,
        ts: Date.now()
      }
      setMessages(prev => [...prev, completionMessage])
      
      // Check if all steps are completed
      const allCompleted = updated.every(event => event.status === 'completed')
      if (allCompleted) {
        const finalMessage: ChatMessage = {
          role: 'assistant',
          text: `🎉 **Build Complete!**\nAll MCP tool build steps have been completed successfully. Your tool is ready for use!`,
          ts: Date.now()
        }
        setMessages(prev => [...prev, finalMessage])
        return updated
      }
      
      // Find next pending step
      const nextStep = updated.find(event => event.status === 'pending')
      if (nextStep) {
        // Add next step message to chat
        const nextStepMessage: ChatMessage = {
          role: 'assistant',
          text: `⏭️ **Next Step: ${nextStep.title}**\nStarting ${nextStep.title.toLowerCase()}...`,
          ts: Date.now()
        }
        setMessages(prev => [...prev, nextStepMessage])
        
        return updated.map(event => 
          event.id === nextStep.id 
            ? { ...event, status: 'loading' as const, startTime: Date.now() }
            : event
        )
      }
      
      return updated
    })
  }

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

  // Send chat message to real Claude
  async function sendMessage() {
    if (!chatInput.trim() || isTyping) return
    
    const userMessage: ChatMessage = {
      role: 'user',
      text: chatInput,
      ts: Date.now()
    }
    
    setMessages(prev => [...prev, userMessage])
    const currentInput = chatInput
    setChatInput('')
    setIsTyping(true)
    
    try {
      // Send to Claude via SSE
      const response = await fetch('/api/claude', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: `Context: You are helping the user build an MCP (Model Context Protocol) tool based on their initial prompt: "${prompt}". 

Current conversation history:
${messages.map(m => `${m.role}: ${m.text}`).join('\n')}

User's latest message: ${currentInput}

Your task:
1. Ask clarifying questions to understand requirements better
2. Once you have enough information and the user confirms (like saying "Yes, build"), help plan and generate the MCP tool
3. Be conversational and helpful

Please respond appropriately to continue the conversation.`,
          conversation_id: 'mcp-builder-session',
          system_prompt: 'You are Claude, an AI assistant specialized in helping developers build MCP (Model Context Protocol) tools. You ask clarifying questions, understand requirements, and help plan and generate code. Be conversational, helpful, and focused on practical implementation.',
          allowed_tools: ['Read', 'Write', 'CreateFile', 'ListDir', 'Search'],
          permission_mode: 'default'
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      // Handle SSE stream
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let assistantResponse = ''

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                if (data.type === 'content') {
                  assistantResponse += data.content
                  
                  // Update the typing indicator with partial response
                  setMessages(prev => {
                    const newMessages = [...prev]
                    const lastMessage = newMessages[newMessages.length - 1]
                    
                    if (lastMessage && lastMessage.role === 'assistant') {
                      // Update existing assistant message
                      lastMessage.text = assistantResponse
                    } else {
                      // Add new assistant message
                      newMessages.push({
                        role: 'assistant',
                        text: assistantResponse,
                        ts: Date.now()
                      })
                    }
                    return newMessages
                  })

                  // Handle backend event for streaming events
                  handleBackendEvent(data)
                }
                
                if (data.type === 'tool_use') {
                  // Handle tool usage event
                  handleBackendEvent(data)
                }
                
                if (data.type === 'done' || data.type === 'complete') {
                  setIsTyping(false)
                  updatePlannerWithChat()
                  
                  // Handle completion event
                  handleBackendEvent(data)
                  
                  // Check if user wants to build
                  if (currentInput.toLowerCase().includes('yes') && 
                      currentInput.toLowerCase().includes('build')) {
                    setRequirementsComplete(true)
                    setTimeout(() => {
                      startStreamingEvents()
                      generateFiles()
                    }, 1000)
                  }
                  break
                }
                
                if (data.type === 'error') {
                  // Handle error event
                  handleBackendEvent(data)
                  throw new Error(data.error || 'Claude API error')
                }
              } catch (e) {
                // Skip malformed JSON
                continue
              }
            }
          }
        }
      }

      // If no assistant response was captured, add a final message
      if (!assistantResponse) {
        const aiMessage: ChatMessage = {
          role: 'assistant',
          text: 'I received your message. How can I help you with your MCP tool?',
          ts: Date.now()
        }
        setMessages(prev => [...prev, aiMessage])
      }

    } catch (error) {
      console.error('Chat error:', error)
      let errorMessage = 'Sorry, I encountered an error. Please try again.'
      
      if (error instanceof Error) {
        if (error.message.includes('Failed to fetch')) {
          errorMessage = 'Unable to connect to Claude service. Please check your internet connection and try again.'
        } else if (error.message.includes('HTTP 500')) {
          errorMessage = 'Claude service is experiencing issues. Please try again later.'
        } else if (error.message.includes('HTTP 503')) {
          errorMessage = 'Claude service is temporarily unavailable. Please try again later.'
        } else {
          errorMessage = `Error: ${error.message}`
        }
      }
      
      const errorChatMessage: ChatMessage = {
        role: 'assistant',
        text: errorMessage,
        ts: Date.now()
      }
      setMessages(prev => [...prev, errorChatMessage])
    } finally {
      setIsTyping(false)
      updatePlannerWithChat()
    }
  }

  // Update planner with chat content
  function updatePlannerWithChat() {
    const chatContent = messages
      .map(m => `${m.role === 'user' ? '👤 User' : '🤖 AI Agent'}: ${m.text}`)
      .join('\n\n')
    
    const backendStatus = backendHealth === 'unhealthy' 
      ? '⚠️ **Backend Service Unavailable** - Claude AI service is not responding. Please check the health status above.'
      : backendHealth === 'checking' 
      ? '🔄 **Checking Backend Status** - Verifying connection to Claude AI service...'
      : '✅ **Backend Service Healthy** - Claude AI service is ready.'
    
    const newPlannerContent = `# MCP Tool Planning Document

## Backend Status
${backendStatus}

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

  // Mock SSE events for demonstration (simulates backend)
  function simulateBackendEvents() {
    const mockEvents = [
      { type: 'tool_use', tool_name: 'Search', delay: 1000 },
      { type: 'content', content: 'Found relevant documentation for MCP tool structure', delay: 2000 },
      { type: 'done', delay: 1000 }, // Complete planning step
      { type: 'tool_use', tool_name: 'ListDir', delay: 1000 },
      { type: 'content', content: 'Creating project directory structure', delay: 1500 },
      { type: 'done', delay: 1000 }, // Complete scaffolding step
      { type: 'tool_use', tool_name: 'CreateFile', delay: 1000 },
      { type: 'content', content: 'Generated manifest.json with MCP schema', delay: 2000 },
      { type: 'done', delay: 1000 }, // Complete generating step
      { type: 'tool_use', tool_name: 'Write', delay: 1000 },
      { type: 'content', content: 'Writing server.py with MCP protocol implementation', delay: 3000 },
      { type: 'done', delay: 1000 }, // Complete testing step
      { type: 'content', content: 'All tests passed successfully', delay: 2000 },
      { type: 'done', delay: 1000 } // Complete deployment step
    ]

    let currentIndex = 0
    
    function processNextEvent() {
      if (currentIndex >= mockEvents.length) return
      
      const event = mockEvents[currentIndex]
      setTimeout(() => {
        handleBackendEvent(event)
        currentIndex++
        if (currentIndex < mockEvents.length) {
          processNextEvent()
        }
      }, event.delay)
    }
    
    processNextEvent()
  }

  // Update planner when messages change
  useEffect(() => {
    updatePlannerWithChat()
  }, [messages, generatedFiles, requirementsComplete, prompt, backendHealth])

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth()
  }, [])

  // Auto-start agent when page loads with a prompt
  useEffect(() => {
    if (prompt && prompt !== 'Build an MCP' && backendHealth === 'healthy') {
      // Start the build process automatically
      setTimeout(() => {
        startStreamingEvents()
      }, 1000) // Small delay to ensure everything is loaded
    }
  }, [prompt, backendHealth])

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
              <button 
                onClick={() => window.location.href = '/'}
                className="hover:text-white transition-colors"
              >
                <ChevronLeft className="h-3 w-3" />
                <span>Home</span>
              </button>
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
            <Badge tone={backendHealth === 'healthy' ? 'success' : backendHealth === 'unhealthy' ? 'danger' : 'warn'}>
              {backendHealth === 'checking' ? 'Checking...' : backendHealth === 'healthy' ? 'Healthy' : 'Unhealthy'}
            </Badge>
            <Button 
              variant="ghost" 
              onClick={checkBackendHealth}
              disabled={backendHealth === 'checking'}
              className="px-2 py-1 text-xs"
            >
              <Loader2 className={`h-3 w-3 ${backendHealth === 'checking' ? 'animate-spin' : ''}`} />
            </Button>
            <Button 
              variant="subtle" 
              onClick={() => {
                setMessages(prev => [...prev, {
                  role: 'user',
                  text: 'Test message',
                  ts: Date.now()
                }])
                setChatInput('Hello Claude, can you help me build an MCP tool?')
              }}
              disabled={backendHealth !== 'healthy'}
              className="px-2 py-1 text-xs"
            >
              Test Chat
            </Button>
            <Button 
              variant="subtle" 
              onClick={() => {
                if (!requirementsComplete) {
                  setRequirementsComplete(true)
                }
                startStreamingEvents()
              }}
              disabled={backendHealth !== 'healthy'}
              className="px-2 py-1 text-xs"
            >
              Demo Build
            </Button>
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

          {/* RIGHT: AI Agent Chat & Streaming Events (Collapsible) */}
          <Card className={getRightPanelCols()}>
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-white/90">
                <Bot className="h-4 w-4" /> 
                {!rightPanelCollapsed && 'AI Agent & Build Progress'}
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
                <div className="max-h-80 space-y-3 overflow-auto rounded-xl bg-black/30 p-3 mb-3">
                  {/* Build Progress Timeline - Compact One-liner */}
                  {streamEvents.some(event => event.status !== 'pending') && (
                    <div className="bg-zinc-800/50 border border-zinc-700 rounded-lg p-2 mb-3">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                          <span className="text-xs font-medium text-white">Build Progress:</span>
                        </div>
                        <div className="flex items-center gap-2 flex-1">
                          {streamEvents.map((event, index) => (
                            <div key={event.id} className="flex items-center gap-1">
                              <div className={`w-1.5 h-1.5 rounded-full ${
                                event.status === 'completed' ? 'bg-emerald-400' :
                                event.status === 'loading' ? 'bg-blue-400 animate-pulse' :
                                'bg-zinc-600'
                              }`}></div>
                              <span className={`text-xs ${
                                event.status === 'completed' ? 'text-emerald-300' :
                                event.status === 'loading' ? 'text-blue-300' :
                                'text-zinc-500'
                              }`}>
                                {event.title.split(' ')[0]}
                              </span>
                            </div>
                          ))}
                        </div>
                        <div className="text-xs text-zinc-400">
                          {streamEvents.filter(e => e.status === 'completed').length}/{streamEvents.length}
                        </div>
                      </div>
                    </div>
                  )}
                  
                   {messages.map((m, i) => (
                     <div key={`message-${i}`} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                       <div className={`max-w-[80%]`}>
                        {/* Special styling for tool usage and progress messages */}
                        {m.text.includes('🛠️ **Using Tool:') ? (
                          <div className="flex items-start gap-3 p-3 rounded-lg border border-blue-500/30 bg-gradient-to-r from-blue-500/10 to-blue-600/10 mb-2">
                            <div className="flex-shrink-0 mt-0.5">
                              <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/40 flex items-center justify-center">
                                <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="text-sm font-medium text-white">Tool Execution</h4>
                                <div className="flex items-center gap-1">
                                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                                  <span className="text-xs text-blue-400">Running</span>
                                </div>
                              </div>
                              <p className="text-xs text-blue-300">{m.text.replace('🛠️ **Using Tool:', '').replace('**', '').trim()}</p>
                              <div className="mt-2 w-full bg-blue-500/20 rounded-full h-1">
                                <div className="bg-blue-400 h-1 rounded-full animate-pulse" style={{width: '60%'}}></div>
                              </div>
                            </div>
                          </div>
                        ) : m.text.includes('✅ **Content Generated**') ? (
                          <div className="flex items-start gap-3 p-3 rounded-lg border border-emerald-500/30 bg-gradient-to-r from-emerald-500/10 to-emerald-600/10 mb-2">
                            <div className="flex-shrink-0 mt-0.5">
                              <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center">
                                <CheckCircle className="h-4 w-4 text-emerald-400" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="text-sm font-medium text-white">Content Generated</h4>
                                <div className="flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3 text-emerald-400" />
                                  <span className="text-xs text-emerald-400">Complete</span>
                                </div>
                              </div>
                              <p className="text-xs text-emerald-300">{m.text.replace('✅ **Content Generated**', '').trim()}</p>
                            </div>
                          </div>
                        ) : m.text.includes('🚀 **Starting MCP Tool Build Process**') ? (
                          <div className="flex items-start gap-3 p-3 rounded-lg border border-purple-500/30 bg-gradient-to-r from-purple-500/10 to-purple-600/10 mb-2">
                            <div className="flex-shrink-0 mt-0.5">
                              <div className="w-8 h-8 rounded-full bg-purple-500/20 border border-purple-500/40 flex items-center justify-center">
                                <Rocket className="h-4 w-4 text-purple-400" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="text-sm font-medium text-white">Build Process Started</h4>
                                <div className="flex items-center gap-1">
                                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                                  <span className="text-xs text-purple-400">Initializing</span>
                                </div>
                              </div>
                              <p className="text-xs text-purple-300">MCP tool build process has begun</p>
                            </div>
                          </div>
                        ) : m.text.includes('🎯 **Step Completed:') ? (
                          <div className="flex items-start gap-3 p-3 rounded-lg border border-emerald-500/30 bg-gradient-to-r from-emerald-500/10 to-emerald-600/10 mb-2">
                            <div className="flex-shrink-0 mt-0.5">
                              <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center">
                                <CheckCircle className="h-4 w-4 text-emerald-400" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="text-sm font-medium text-white">Step Completed</h4>
                                <div className="flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3 text-emerald-400" />
                                  <span className="text-xs text-emerald-400">Complete</span>
                                </div>
                              </div>
                              <p className="text-xs text-emerald-300">{m.text.replace('🎯 **Step Completed:', '').replace('**', '').trim()}</p>
                            </div>
                          </div>
                        ) : m.text.includes('⏭️ **Next Step:') ? (
                          <div className="flex items-start gap-3 p-3 rounded-lg border border-amber-500/30 bg-gradient-to-r from-amber-500/10 to-amber-600/10 mb-2">
                            <div className="flex-shrink-0 mt-0.5">
                              <div className="w-8 h-8 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center">
                                <Play className="h-4 w-4 text-amber-400" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="text-sm font-medium text-white">Next Step</h4>
                                <div className="flex items-center gap-1">
                                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></div>
                                  <span className="text-xs text-amber-400">Starting</span>
                                </div>
                              </div>
                              <p className="text-xs text-amber-300">{m.text.replace('⏭️ **Next Step:', '').replace('**', '').trim()}</p>
                            </div>
                          </div>
                        ) : m.text.includes('🎉 **Build Complete!**') ? (
                          <div className="flex items-start gap-3 p-3 rounded-lg border border-emerald-500/30 bg-gradient-to-r from-emerald-500/20 to-emerald-600/20 mb-2">
                            <div className="flex-shrink-0 mt-0.5">
                              <div className="w-8 h-8 rounded-full bg-emerald-500/30 border border-emerald-500/50 flex items-center justify-center">
                                <CheckCircle className="h-4 w-4 text-emerald-400" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="text-sm font-medium text-white">Build Complete!</h4>
                                <div className="flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3 text-emerald-400" />
                                  <span className="text-xs text-emerald-400">Success</span>
                                </div>
                              </div>
                              <p className="text-xs text-emerald-300">All MCP tool build steps have been completed successfully. Your tool is ready for use!</p>
                              <div className="mt-2 w-full bg-emerald-500/30 rounded-full h-1">
                                <div className="bg-emerald-400 h-1 rounded-full" style={{width: '100%'}}></div>
                              </div>
                            </div>
                          </div>
                        ) : m.text.includes('❌ **Error**') ? (
                          <div className="flex items-start gap-3 p-3 rounded-lg border border-red-500/30 bg-gradient-to-r from-red-500/10 to-red-600/10 mb-2">
                            <div className="flex-shrink-0 mt-0.5">
                              <div className="w-8 h-8 rounded-full bg-red-500/20 border border-red-500/40 flex items-center justify-center">
                                <AlertCircle className="h-4 w-4 text-red-400" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="text-sm font-medium text-white">Error Occurred</h4>
                                <div className="flex items-center gap-1">
                                  <AlertCircle className="w-3 h-3 text-red-400" />
                                  <span className="text-xs text-red-400">Failed</span>
                                </div>
                              </div>
                              <p className="text-xs text-red-300">{m.text.replace('❌ **Error**', '').trim()}</p>
                            </div>
                          </div>
                        ) : (
                         <div className={`rounded-xl px-3 py-2 text-sm ${
                           m.role === 'user' ? 'bg-zinc-800 text-zinc-100' : 'bg-zinc-900 text-zinc-300'
                         }`}>
                           {m.text}
                         </div>
                        )}
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
                    placeholder={backendHealth === 'unhealthy' ? 'Backend unavailable - check health status' : "Ask questions or provide more details..."} 
                    onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && sendMessage()}
                    disabled={backendHealth === 'unhealthy'}
                  />
                  <Button 
                    onClick={sendMessage} 
                    disabled={!chatInput.trim() || isTyping || backendHealth === 'unhealthy'}
                    className="px-4"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="mt-3 text-xs text-zinc-500 text-center">
                  {backendHealth === 'unhealthy' ? (
                    <span className="text-red-400">⚠️ Backend service unavailable. Please check the health status above.</span>
                  ) : (
                    "Chat with Claude to refine requirements. Build progress will appear in the chat as tools are used."
                  )}
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