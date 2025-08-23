# MCP Tool Builder Frontend

A Next.js frontend for building MCP (Model Context Protocol) tools with AI assistance from Claude.

## 🚀 **Features**

### **AI-Powered MCP Tool Builder**
- **Interactive Chat Interface**: Chat with Claude to refine requirements and build MCP tools
- **Cursor-like Build Progress**: Visually distinct tool calls and progress indicators that flow through the chat conversation
- **Tool Usage Tracking**: See exactly which tools are being used with distinct styling and status indicators
- **Live File Generation**: Watch as code files are created in real-time
- **Backend Health Monitoring**: Real-time status of the Claude backend service

### **Build Progress System**
- **Integrated Progress**: Build progress appears naturally in the chat flow, not as a separate section
- **Visual Distinction**: Tool calls, content generation, and step completion are visually distinct from regular chat messages
- **Step-by-Step Updates**: Each build step (planning, scaffolding, generating, testing, deploying) updates with clear visual indicators
- **Progress Timeline**: Compact timeline showing current build status above chat messages
- **Status Icons**: Different icons and colors for running, completed, and pending steps
- **Completion Messages**: Clear indicators when each step completes and the next begins

### **Three-Panel Layout**
- **Left Panel**: Planning document with chat history and requirements
- **Middle Panel**: Generated code files with syntax highlighting
- **Right Panel**: AI chat with integrated build progress

## Backend Integration

This frontend integrates with the Claude Code SDK backend service at:
`https://integral-mozilla-ref-db.trycloudflare.com`

The backend provides:
- Claude AI chat functionality
- MCP tool generation capabilities
- File system operations
- Code analysis and generation

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or pnpm

### Installation

1. Install dependencies:
```bash
npm install
# or
pnpm install
```

2. Set environment variables (optional):
```bash
# Override backend URL if needed
CLAUDE_BACKEND_URL=https://your-backend-url.com
```

3. Run the development server:
```bash
npm run dev
# or
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### 1. Landing Page
- Enter your MCP tool requirements in the prompt field
- Use example prompts or write your own
- Click "Build an MCP" to start

### 2. Builder Workspace
The builder has three main panels:

#### Left Panel - Planner.md
- Shows conversation history with Claude
- Displays implementation plan
- Shows backend health status

#### Middle Panel - Generated Code
- Displays generated MCP tool files
- Switch between different file types
- View and edit generated code

#### Right Panel - AI Chat
- Chat with Claude to refine requirements
- Ask clarifying questions
- Get implementation guidance

### 3. Building Process
1. **Requirements Gathering**: Claude asks questions to understand your needs
2. **Planning**: Once satisfied, Claude creates an implementation plan
3. **Code Generation**: Claude generates all necessary MCP tool files
4. **Review**: Review and modify generated code as needed

## API Endpoints

- `/api/claude` - Main Claude chat endpoint
- `/api/claude/health` - Backend health check
- `/api/stream` - Legacy streaming endpoint (for demo purposes)

## Backend Health

The system continuously monitors backend health:
- **Green**: Backend is healthy and ready
- **Yellow**: Checking backend status
- **Red**: Backend is unavailable

Use the refresh button to manually check status.

## Troubleshooting

### Backend Unavailable
- Check if the backend service is running
- Verify network connectivity
- Check the health endpoint for detailed error information

### Chat Not Working
- Ensure backend health shows "Healthy"
- Check browser console for error messages
- Verify the Claude API endpoint is accessible

### Code Generation Issues
- Make sure requirements are clearly specified
- Check that Claude has enough context
- Review the conversation history for clarity

## Development

### Project Structure
```
src/
├── app/                    # Next.js app router
│   ├── api/               # API routes
│   ├── build/             # Builder workspace
│   └── page.tsx           # Landing page
├── components/             # React components
└── lib/                   # Utility functions
```

### Key Components
- `BuilderScreen`: Main builder interface
- `ChatMessage`: Chat message handling
- `GeneratedFile`: File management
- Health monitoring system

### Adding New Features
1. Update the appropriate component
2. Add any new API endpoints
3. Update types and interfaces
4. Test with the backend service

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the YC Hack MCP initiative.
