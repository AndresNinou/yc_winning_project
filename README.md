# WINGMAN - AI AGENT FOR BUILDING MCP TOOLS

🥈 **Winner: Y Combinator's First Overnight Hackathon - Silver Medal**  
🏆 **Developer Tools and AI Agents Track**  
👥 **Team Wingman**

An Agentic AI Platform for building Model Context Protocol (MCP) tools with AI assistance from Claude. This project combines a FastAPI backend with a Next.js frontend to create an interactive development environment for MCP tool creation.

Features automated deployment to **Dedaluslabs.ai** - the MCP marketplace - using Browser-Use automation.

## 👥 Team Wingman

- [Andres Niño](https://www.linkedin.com/in/andres-ni%C3%B1o-593722187/)
- [Shubham Nair](https://www.linkedin.com/in/nair-shubh/)
- [Jaehoon Son](https://www.linkedin.com/in/jaehoon-son/)
- [James Lin](https://www.linkedin.com/in/linj3/)


## 🛠️ Built With Award-Winning Tools

This hackathon-winning project leverages cutting-edge tools and technologies:

- **Claude Code SDK** - Core AI integration for intelligent code generation
- **FastMCP** - Modern MCP server framework for protocol implementation
- **Model Context Protocol (MCP)** - Anthropic's protocol for AI-context integration
- **Claude Sonnet** - Advanced AI model powering the code generation
- **Server-Sent Events (SSE)** - Real-time streaming for live updates
- **Watchdog** - File system monitoring for instant feedback
- **Browser-Use** - Web automation capabilities
- **Groq** - High-performance AI inference
- **OpenAI API** - Additional AI capabilities
- **Next.js 15** - Latest React framework with Turbopack
- **FastAPI** - Modern Python web framework
- **Radix UI** - Accessible component system

## 🚀 Features

### AI-Powered Development
- **Interactive Chat Interface**: Chat with Claude to refine requirements and build MCP tools
- **Real-time Code Generation**: Watch as code files are created and modified in real-time
- **Intelligent Planning**: Claude creates implementation plans and breaks down complex tasks
- **Live File Monitoring**: Real-time file system monitoring with Server-Sent Events (SSE) streaming

### Advanced UI/UX
- **Three-Panel Layout**: Planning document, generated code files, and AI chat interface
- **Progress Tracking**: Visual build progress with Cursor-like indicators
- **Backend Health Monitoring**: Real-time status monitoring of services
- **Responsive Design**: Modern UI components with Tailwind CSS and Radix UI

### Backend Architecture
- **FastAPI Microservice**: Stateless HTTP API with async support
- **MCP Integration**: Built-in support for MCP server creation and deployment
- **File System Operations**: Workspace management with live file monitoring
- **Claude Integration**: Direct integration with Claude Code SDK

## 🏗️ Architecture

```mermaid
flowchart LR
    A[Next.js Frontend] -- HTTP/SSE --> B[FastAPI Backend]
    B -- Integration --> C[Claude Code SDK]
    B -- File Operations --> D[Workspace Manager]
    B -- MCP --> E[MCP Servers]
    B -- Monitoring --> F[File Stream Service]
    
    subgraph "Frontend Components"
        A1[Landing Page]
        A2[Builder Interface]
        A3[Chat System]
        A --> A1 & A2 & A3
    end
    
    subgraph "Backend Services"
        B1[Claude API Routes]
        B2[File Stream API]
        B3[MCP Integration]
        B --> B1 & B2 & B3
    end
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **SQLModel** - Type-safe database interactions
- **Claude Code SDK** - AI integration
- **FastMCP** - MCP server framework
- **SSE-Starlette** - Server-Sent Events support
- **Watchdog** - File system monitoring
- **PostgreSQL** - Primary database (optional)

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible component library
- **React Hook Form** - Form management
- **Framer Motion** - Animations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional)

### Backend Setup

```bash
cd backend

# Install dependencies with uv
uv sync --dev

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the server
make run
# or: uv run uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or: pnpm install

# Run development server
npm run dev
# or: pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to access the application.

## 📁 Project Structure

```
yc_winning_project/
├── backend/                    # FastAPI backend service
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   ├── core/              # Core configuration
│   │   ├── services/          # Business logic services
│   │   └── models.py          # Database models
│   ├── mcps/                  # MCP server implementations
│   ├── workspaces/            # User workspaces
│   └── tests/                 # Test suite
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   ├── components/       # React components
│   │   └── lib/              # Utility functions
│   └── public/               # Static assets
├── prompts/                   # System prompts
└── sandbox/                   # Development sandbox
```

## 🔄 Development Workflow

### Building MCP Tools

1. **Requirements Gathering**: Start by describing your MCP tool needs
2. **AI Planning**: Claude analyzes requirements and creates implementation plans
3. **Code Generation**: Real-time code generation with live file updates
4. **Testing & Refinement**: Iterate with Claude to refine and improve the tool
5. **Deployment**: Deploy your MCP tool to supported platforms

### Key Commands

#### Backend
```bash
make check          # Run linting and type checking
make test           # Run test suite
make orm            # Regenerate database models
```

#### Frontend
```bash
npm run build       # Build for production
npm run lint        # Run ESLint
```

## 🌐 API Endpoints

### Frontend API Routes
- `/api/claude` - Main Claude chat endpoint
- `/api/claude/health` - Backend health check
- `/api/stream` - Server-Sent Events streaming
- `/api/tts` - Text-to-speech functionality

### Backend API Routes
- `/api/v1/claude/` - Claude integration endpoints
- `/api/v1/file-stream/` - File monitoring and streaming
- `/api/v1/services/` - MCP service management
- `/api/v1/utils/health-check` - System health status

## 🔧 Configuration

### Environment Variables

#### Backend
```env
ENVIRONMENT=local
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/db
CLAUDE_API_KEY=your-claude-api-key
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

#### Frontend
```env
CLAUDE_BACKEND_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
make test MODE=full    # Run full test suite with coverage
make smoke             # Quick smoke tests
```

### Frontend Tests
```bash
cd frontend
npm test               # Run test suite
```

## 🚀 Deployment

### Backend Deployment
- Docker support with multi-stage builds
- PostgreSQL database recommended for production
- Environment-specific configurations

### Frontend Deployment
- Vercel-ready with Next.js
- Static export support
- Environment variable configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow existing code conventions
- Add tests for new features
- Update documentation as needed
- Ensure type safety with TypeScript/Python typing

## 📄 License

This project is part of the YC Hack MCP initiative.

## 🆘 Support

- Check the individual README files in `backend/` and `frontend/` for detailed setup instructions
- Review the API documentation for integration details
- Open issues for bugs or feature requests

## 🎯 Roadmap

- [ ] Enhanced MCP tool templates
- [ ] Multi-language support for generated tools
- [ ] Advanced deployment options
- [ ] Team collaboration features
- [ ] Plugin marketplace integration

---

Built with ❤️ for the YC Hack MCP initiative
