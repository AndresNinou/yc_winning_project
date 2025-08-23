example_mcp = """├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── bun.lock
├── mcp.md
├── package.json
├── src
    ├── cli.ts
    ├── client.ts
    ├── config.ts
    ├── index.ts
    ├── server.ts
    ├── tools
    │   ├── index.ts
    │   └── search.ts
    ├── transport
    │   ├── http.ts
    │   ├── index.ts
    │   └── stdio.ts
    └── types.ts
└── tsconfig.json


/.env.example:
--------------------------------------------------------------------------------
1 | BRAVE_API_KEY=
2 | 


--------------------------------------------------------------------------------
/.gitignore:
--------------------------------------------------------------------------------
 1 | # Dependencies
 2 | node_modules/
 3 | .npm
 4 | 
 5 | # Build
 6 | build/
 7 | dist/
 8 | coverage/
 9 | 
10 | # Environment
11 | .env
12 | .env.local
13 | .env.*.local
14 | 
15 | # IDE
16 | .vscode/
17 | .idea/
18 | *.swp
19 | *.swo
20 | 
21 | # LLMs
22 | **/.claude/
23 | 
24 | # Logs
25 | logs/
26 | *.log
27 | npm-debug.log*
28 | yarn-debug.log*
29 | yarn-error.log*
30 | server.log
31 | 
32 | # OS
33 | .DS_Store
34 | Thumbs.db
35 | 


--------------------------------------------------------------------------------
/Dockerfile:
--------------------------------------------------------------------------------
 1 | # Use official Node.js runtime as base image
 2 | FROM public.ecr.aws/docker/library/node:22-alpine
 3 | 
 4 | # Set working directory inside container
 5 | WORKDIR /app
 6 | 
 7 | # Copy package files first for better caching
 8 | COPY package.json package-lock.json* ./
 9 | 
10 | # Install dependencies without running postinstall scripts to avoid build failures
11 | RUN npm install --ignore-scripts
12 | 
13 | # Install TypeScript globally for running .ts files directly
14 | RUN npm install -g typescript ts-node
15 | 
16 | # Copy source code
17 | COPY . .
18 | 
19 | # Build the TypeScript code - handle gracefully if build fails
20 | RUN npm run build || echo "Build step failed, but continuing..."
21 | 
22 | # Create a non-root user for security
23 | RUN addgroup -g 1001 -S nodejs && \
24 |     adduser -S mcp -u 1001
25 | 
26 | # Change ownership of app directory to non-root user
27 | RUN chown -R mcp:nodejs /app
28 | 
29 | # Switch to non-root user
30 | USER mcp
31 | 
32 | # Set environment variables for Lambda Web Adapter
33 | ENV NODE_ENV=production
34 | ENV PORT=8000
35 | ENV AWS_LAMBDA_EXEC_WRAPPER=/opt/extensions/lambda-adapter
36 | 
37 | # Expose port 8000 for the MCP server
38 | EXPOSE 8000
39 | 
40 | # Command to run the server
41 | # Use compiled JavaScript for production, with --port flag for HTTP transport
42 | CMD ["node", "dist/index.js", "--port", "8000"]
43 | 


--------------------------------------------------------------------------------
/README.md:
--------------------------------------------------------------------------------
  1 | # Brave Search MCP Server
  2 | 
  3 | An MCP server implementation that integrates the Brave Search API, providing both web and local search capabilities.
  4 | 
  5 | ## Features
  6 | 
  7 | - **Web Search**: General queries, news, articles, with pagination and freshness controls
  8 | - **Local Search**: Find businesses, restaurants, and services with detailed information
  9 | - **Flexible Filtering**: Control result types, safety levels, and content freshness
 10 | - **Smart Fallbacks**: Local search automatically falls back to web when no results are found
 11 | 
 12 | ## Tools
 13 | 
 14 | - **brave_web_search**
 15 | 
 16 |   - Execute web searches with pagination and filtering
 17 |   - Inputs:
 18 |     - `query` (string): Search terms
 19 |     - `count` (number, optional): Results per page (max 20)
 20 |     - `offset` (number, optional): Pagination offset (max 9)
 21 | 
 22 | - **brave_local_search**
 23 |   - Search for local businesses and services
 24 |   - Inputs:
 25 |     - `query` (string): Local search terms
 26 |     - `count` (number, optional): Number of results (max 20)
 27 |   - Automatically falls back to web search if no local results found
 28 | 
 29 | ## Configuration
 30 | 
 31 | ### Getting an API Key
 32 | 
 33 | 1. Sign up for a [Brave Search API account](https://brave.com/search/api/)
 34 | 2. Choose a plan (Free tier available with 2,000 queries/month)
 35 | 3. Generate your API key [from the developer dashboard](https://api-dashboard.search.brave.com/app/keys)
 36 | 
 37 | ### Usage with Claude Desktop
 38 | 
 39 | Add this to your `claude_desktop_config.json`:
 40 | 
 41 | ### Docker
 42 | 
 43 | ```json
 44 | {
 45 |   "mcpServers": {
 46 |     "brave-search": {
 47 |       "command": "docker",
 48 |       "args": [
 49 |         "run",
 50 |         "-i",
 51 |         "--rm",
 52 |         "-e",
 53 |         "BRAVE_API_KEY",
 54 |         "mcp/brave-search"
 55 |       ],
 56 |       "env": {
 57 |         "BRAVE_API_KEY": "YOUR_API_KEY_HERE"
 58 |       }
 59 |     }
 60 |   }
 61 | }
 62 | ```
 63 | 
 64 | ### NPX
 65 | 
 66 | ```json
 67 | {
 68 |   "mcpServers": {
 69 |     "brave-search": {
 70 |       "command": "npx",
 71 |       "args": [
 72 |         "-y",
 73 |         "@modelcontextprotocol/server-brave-search"
 74 |       ],
 75 |       "env": {
 76 |         "BRAVE_API_KEY": "YOUR_API_KEY_HERE"
 77 |       }
 78 |     }
 79 |   }
 80 | }
 81 | ```
 82 | 
 83 | ### Usage with VS Code
 84 | 
 85 | For quick installation, use the one-click installation buttons below...
 86 | 
 87 | [![Install with NPX in VS Code](https://img.shields.io/badge/VS_Code-NPM-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=brave&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22apiKey%22%7D%5D&config=%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40modelcontextprotocol%2Fserver-brave-search%22%5D%2C%22env%22%3A%7B%22BRAVE_API_KEY%22%3A%22%24%7Binput%3Abrave_api_key%7D%22%7D%7D) [![Install with NPX in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-NPM-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=brave&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22apiKey%22%7D%5D&config=%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40modelcontextprotocol%2Fserver-brave-search%22%5D%2C%22env%22%3A%7B%22BRAVE_API_KEY%22%3A%22%24%7Binput%3Abrave_api_key%7D%22%7D%7D&quality=insiders)
 88 | 
 89 | [![Install with Docker in VS Code](https://img.shields.io/badge/VS_Code-Docker-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=brave&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22apiKey%22%7D%5D&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22-e%22%2C%22BRAVE_API_KEY%22%2C%22mcp%2Fbrave-search%22%5D%2C%22env%22%3A%7B%22BRAVE_API_KEY%22%3A%22%24%7Binput%3Abrave_api_key%7D%22%7D%7D) [![Install with Docker in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-Docker-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=brave&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22apiKey%22%7D%5D&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22-e%22%2C%22BRAVE_API_KEY%22%2C%22mcp%2Fbrave-search%22%5D%2C%22env%22%3A%7B%22BRAVE_API_KEY%22%3A%22%24%7Binput%3Abrave_api_key%7D%22%7D%7D&quality=insiders)
 90 | 
 91 | For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open User Settings (JSON)`.
 92 | 
 93 | Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.
 94 | 
 95 | > Note that the `mcp` key is not needed in the `.vscode/mcp.json` file.
 96 | 
 97 | #### Docker
 98 | 
 99 | ```json
100 | {
101 |   "mcp": {
102 |     "inputs": [
103 |       {
104 |         "type": "promptString",
105 |         "id": "brave_api_key",
106 |         "description": "Brave Search API Key",
107 |         "password": true
108 |       }
109 |     ],
110 |     "servers": {
111 |       "brave-search": {
112 |         "command": "docker",
113 |         "args": [
114 |           "run",
115 |           "-i",
116 |           "--rm",
117 |           "-e",
118 |           "BRAVE_API_KEY",
119 |           "mcp/brave-search"
120 |         ],
121 |         "env": {
122 |           "BRAVE_API_KEY": "${input:brave_api_key}"
123 |         }
124 |       }
125 |     }
126 |   }
127 | }
128 | ```
129 | 
130 | #### NPX
131 | 
132 | ```json
133 | {
134 |   "mcp": {
135 |     "inputs": [
136 |       {
137 |         "type": "promptString",
138 |         "id": "brave_api_key",
139 |         "description": "Brave Search API Key",
140 |         "password": true
141 |       }
142 |     ],
143 |     "servers": {
144 |       "brave-search": {
145 |         "command": "npx",
146 |         "args": ["-y", "@modelcontextprotocol/server-brave-search"],
147 |         "env": {
148 |           "BRAVE_API_KEY": "${input:brave_api_key}"
149 |         }
150 |       }
151 |     }
152 |   }
153 | }
154 | ```
155 | 
156 | ## Build
157 | 
158 | Docker build:
159 | 
160 | ```bash
161 | docker build -t mcp/brave-search:latest -f src/brave-search/Dockerfile .
162 | ```
163 | 
164 | ## License
165 | 
166 | This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
167 | 


--------------------------------------------------------------------------------
/bun.lock:
--------------------------------------------------------------------------------
  1 | {
  2 |   "lockfileVersion": 1,
  3 |   "workspaces": {
  4 |     "": {
  5 |       "name": "@modelcontextprotocol/server-brave-search",
  6 |       "dependencies": {
  7 |         "@modelcontextprotocol/sdk": "1.16.0",
  8 |         "@playwright/test": "^1.54.2",
  9 |         "axios": "^1.11.0",
 10 |         "dotenv": "^17.2.1",
 11 |       },
 12 |       "devDependencies": {
 13 |         "@types/node": "^24.2.0",
 14 |         "tsx": "^4.20.3",
 15 |         "typescript": "^5.9.2",
 16 |       },
 17 |     },
 18 |   },
 19 |   "packages": {
 20 |     "@esbuild/aix-ppc64": ["@esbuild/aix-ppc64@0.25.8", "", { "os": "aix", "cpu": "ppc64" }, "sha512-urAvrUedIqEiFR3FYSLTWQgLu5tb+m0qZw0NBEasUeo6wuqatkMDaRT+1uABiGXEu5vqgPd7FGE1BhsAIy9QVA=="],
 21 | 
 22 |     "@esbuild/android-arm": ["@esbuild/android-arm@0.25.8", "", { "os": "android", "cpu": "arm" }, "sha512-RONsAvGCz5oWyePVnLdZY/HHwA++nxYWIX1atInlaW6SEkwq6XkP3+cb825EUcRs5Vss/lGh/2YxAb5xqc07Uw=="],
 23 | 
 24 |     "@esbuild/android-arm64": ["@esbuild/android-arm64@0.25.8", "", { "os": "android", "cpu": "arm64" }, "sha512-OD3p7LYzWpLhZEyATcTSJ67qB5D+20vbtr6vHlHWSQYhKtzUYrETuWThmzFpZtFsBIxRvhO07+UgVA9m0i/O1w=="],
 25 | 
 26 |     "@esbuild/android-x64": ["@esbuild/android-x64@0.25.8", "", { "os": "android", "cpu": "x64" }, "sha512-yJAVPklM5+4+9dTeKwHOaA+LQkmrKFX96BM0A/2zQrbS6ENCmxc4OVoBs5dPkCCak2roAD+jKCdnmOqKszPkjA=="],
 27 | 
 28 |     "@esbuild/darwin-arm64": ["@esbuild/darwin-arm64@0.25.8", "", { "os": "darwin", "cpu": "arm64" }, "sha512-Jw0mxgIaYX6R8ODrdkLLPwBqHTtYHJSmzzd+QeytSugzQ0Vg4c5rDky5VgkoowbZQahCbsv1rT1KW72MPIkevw=="],
 29 | 
 30 |     "@esbuild/darwin-x64": ["@esbuild/darwin-x64@0.25.8", "", { "os": "darwin", "cpu": "x64" }, "sha512-Vh2gLxxHnuoQ+GjPNvDSDRpoBCUzY4Pu0kBqMBDlK4fuWbKgGtmDIeEC081xi26PPjn+1tct+Bh8FjyLlw1Zlg=="],
 31 | 
 32 |     "@esbuild/freebsd-arm64": ["@esbuild/freebsd-arm64@0.25.8", "", { "os": "freebsd", "cpu": "arm64" }, "sha512-YPJ7hDQ9DnNe5vxOm6jaie9QsTwcKedPvizTVlqWG9GBSq+BuyWEDazlGaDTC5NGU4QJd666V0yqCBL2oWKPfA=="],
 33 | 
 34 |     "@esbuild/freebsd-x64": ["@esbuild/freebsd-x64@0.25.8", "", { "os": "freebsd", "cpu": "x64" }, "sha512-MmaEXxQRdXNFsRN/KcIimLnSJrk2r5H8v+WVafRWz5xdSVmWLoITZQXcgehI2ZE6gioE6HirAEToM/RvFBeuhw=="],
 35 | 
 36 |     "@esbuild/linux-arm": ["@esbuild/linux-arm@0.25.8", "", { "os": "linux", "cpu": "arm" }, "sha512-FuzEP9BixzZohl1kLf76KEVOsxtIBFwCaLupVuk4eFVnOZfU+Wsn+x5Ryam7nILV2pkq2TqQM9EZPsOBuMC+kg=="],
 37 | 
 38 |     "@esbuild/linux-arm64": ["@esbuild/linux-arm64@0.25.8", "", { "os": "linux", "cpu": "arm64" }, "sha512-WIgg00ARWv/uYLU7lsuDK00d/hHSfES5BzdWAdAig1ioV5kaFNrtK8EqGcUBJhYqotlUByUKz5Qo6u8tt7iD/w=="],
 39 | 
 40 |     "@esbuild/linux-ia32": ["@esbuild/linux-ia32@0.25.8", "", { "os": "linux", "cpu": "ia32" }, "sha512-A1D9YzRX1i+1AJZuFFUMP1E9fMaYY+GnSQil9Tlw05utlE86EKTUA7RjwHDkEitmLYiFsRd9HwKBPEftNdBfjg=="],
 41 | 
 42 |     "@esbuild/linux-loong64": ["@esbuild/linux-loong64@0.25.8", "", { "os": "linux", "cpu": "none" }, "sha512-O7k1J/dwHkY1RMVvglFHl1HzutGEFFZ3kNiDMSOyUrB7WcoHGf96Sh+64nTRT26l3GMbCW01Ekh/ThKM5iI7hQ=="],
 43 | 
 44 |     "@esbuild/linux-mips64el": ["@esbuild/linux-mips64el@0.25.8", "", { "os": "linux", "cpu": "none" }, "sha512-uv+dqfRazte3BzfMp8PAQXmdGHQt2oC/y2ovwpTteqrMx2lwaksiFZ/bdkXJC19ttTvNXBuWH53zy/aTj1FgGw=="],
 45 | 
 46 |     "@esbuild/linux-ppc64": ["@esbuild/linux-ppc64@0.25.8", "", { "os": "linux", "cpu": "ppc64" }, "sha512-GyG0KcMi1GBavP5JgAkkstMGyMholMDybAf8wF5A70CALlDM2p/f7YFE7H92eDeH/VBtFJA5MT4nRPDGg4JuzQ=="],
 47 | 
 48 |     "@esbuild/linux-riscv64": ["@esbuild/linux-riscv64@0.25.8", "", { "os": "linux", "cpu": "none" }, "sha512-rAqDYFv3yzMrq7GIcen3XP7TUEG/4LK86LUPMIz6RT8A6pRIDn0sDcvjudVZBiiTcZCY9y2SgYX2lgK3AF+1eg=="],
 49 | 
 50 |     "@esbuild/linux-s390x": ["@esbuild/linux-s390x@0.25.8", "", { "os": "linux", "cpu": "s390x" }, "sha512-Xutvh6VjlbcHpsIIbwY8GVRbwoviWT19tFhgdA7DlenLGC/mbc3lBoVb7jxj9Z+eyGqvcnSyIltYUrkKzWqSvg=="],
 51 | 
 52 |     "@esbuild/linux-x64": ["@esbuild/linux-x64@0.25.8", "", { "os": "linux", "cpu": "x64" }, "sha512-ASFQhgY4ElXh3nDcOMTkQero4b1lgubskNlhIfJrsH5OKZXDpUAKBlNS0Kx81jwOBp+HCeZqmoJuihTv57/jvQ=="],
 53 | 
 54 |     "@esbuild/netbsd-arm64": ["@esbuild/netbsd-arm64@0.25.8", "", { "os": "none", "cpu": "arm64" }, "sha512-d1KfruIeohqAi6SA+gENMuObDbEjn22olAR7egqnkCD9DGBG0wsEARotkLgXDu6c4ncgWTZJtN5vcgxzWRMzcw=="],
 55 | 
 56 |     "@esbuild/netbsd-x64": ["@esbuild/netbsd-x64@0.25.8", "", { "os": "none", "cpu": "x64" }, "sha512-nVDCkrvx2ua+XQNyfrujIG38+YGyuy2Ru9kKVNyh5jAys6n+l44tTtToqHjino2My8VAY6Lw9H7RI73XFi66Cg=="],
 57 | 
 58 |     "@esbuild/openbsd-arm64": ["@esbuild/openbsd-arm64@0.25.8", "", { "os": "openbsd", "cpu": "arm64" }, "sha512-j8HgrDuSJFAujkivSMSfPQSAa5Fxbvk4rgNAS5i3K+r8s1X0p1uOO2Hl2xNsGFppOeHOLAVgYwDVlmxhq5h+SQ=="],
 59 | 
 60 |     "@esbuild/openbsd-x64": ["@esbuild/openbsd-x64@0.25.8", "", { "os": "openbsd", "cpu": "x64" }, "sha512-1h8MUAwa0VhNCDp6Af0HToI2TJFAn1uqT9Al6DJVzdIBAd21m/G0Yfc77KDM3uF3T/YaOgQq3qTJHPbTOInaIQ=="],
 61 | 
 62 |     "@esbuild/openharmony-arm64": ["@esbuild/openharmony-arm64@0.25.8", "", { "os": "none", "cpu": "arm64" }, "sha512-r2nVa5SIK9tSWd0kJd9HCffnDHKchTGikb//9c7HX+r+wHYCpQrSgxhlY6KWV1nFo1l4KFbsMlHk+L6fekLsUg=="],
 63 | 
 64 |     "@esbuild/sunos-x64": ["@esbuild/sunos-x64@0.25.8", "", { "os": "sunos", "cpu": "x64" }, "sha512-zUlaP2S12YhQ2UzUfcCuMDHQFJyKABkAjvO5YSndMiIkMimPmxA+BYSBikWgsRpvyxuRnow4nS5NPnf9fpv41w=="],
 65 | 
 66 |     "@esbuild/win32-arm64": ["@esbuild/win32-arm64@0.25.8", "", { "os": "win32", "cpu": "arm64" }, "sha512-YEGFFWESlPva8hGL+zvj2z/SaK+pH0SwOM0Nc/d+rVnW7GSTFlLBGzZkuSU9kFIGIo8q9X3ucpZhu8PDN5A2sQ=="],
 67 | 
 68 |     "@esbuild/win32-ia32": ["@esbuild/win32-ia32@0.25.8", "", { "os": "win32", "cpu": "ia32" }, "sha512-hiGgGC6KZ5LZz58OL/+qVVoZiuZlUYlYHNAmczOm7bs2oE1XriPFi5ZHHrS8ACpV5EjySrnoCKmcbQMN+ojnHg=="],
 69 | 
 70 |     "@esbuild/win32-x64": ["@esbuild/win32-x64@0.25.8", "", { "os": "win32", "cpu": "x64" }, "sha512-cn3Yr7+OaaZq1c+2pe+8yxC8E144SReCQjN6/2ynubzYjvyqZjTXfQJpAcQpsdJq3My7XADANiYGHoFC69pLQw=="],
 71 | 
 72 |     "@modelcontextprotocol/sdk": ["@modelcontextprotocol/sdk@1.16.0", "", { "dependencies": { "ajv": "^6.12.6", "content-type": "^1.0.5", "cors": "^2.8.5", "cross-spawn": "^7.0.5", "eventsource": "^3.0.2", "eventsource-parser": "^3.0.0", "express": "^5.0.1", "express-rate-limit": "^7.5.0", "pkce-challenge": "^5.0.0", "raw-body": "^3.0.0", "zod": "^3.23.8", "zod-to-json-schema": "^3.24.1" } }, "sha512-8ofX7gkZcLj9H9rSd50mCgm3SSF8C7XoclxJuLoV0Cz3rEQ1tv9MZRYYvJtm9n1BiEQQMzSmE/w2AEkNacLYfg=="],
 73 | 
 74 |     "@playwright/test": ["@playwright/test@1.54.2", "", { "dependencies": { "playwright": "1.54.2" }, "bin": { "playwright": "cli.js" } }, "sha512-A+znathYxPf+72riFd1r1ovOLqsIIB0jKIoPjyK2kqEIe30/6jF6BC7QNluHuwUmsD2tv1XZVugN8GqfTMOxsA=="],
 75 | 
 76 |     "@types/node": ["@types/node@24.2.0", "", { "dependencies": { "undici-types": "~7.10.0" } }, "sha512-3xyG3pMCq3oYCNg7/ZP+E1ooTaGB4cG8JWRsqqOYQdbWNY4zbaV0Ennrd7stjiJEFZCaybcIgpTjJWHRfBSIDw=="],
 77 | 
 78 |     "accepts": ["accepts@2.0.0", "", { "dependencies": { "mime-types": "^3.0.0", "negotiator": "^1.0.0" } }, "sha512-5cvg6CtKwfgdmVqY1WIiXKc3Q1bkRqGLi+2W/6ao+6Y7gu/RCwRuAhGEzh5B4KlszSuTLgZYuqFqo5bImjNKng=="],
 79 | 
 80 |     "ajv": ["ajv@6.12.6", "", { "dependencies": { "fast-deep-equal": "^3.1.1", "fast-json-stable-stringify": "^2.0.0", "json-schema-traverse": "^0.4.1", "uri-js": "^4.2.2" } }, "sha512-j3fVLgvTo527anyYyJOGTYJbG+vnnQYvE0m5mmkc1TK+nxAppkCLMIL0aZ4dblVCNoGShhm+kzE4ZUykBoMg4g=="],
 81 | 
 82 |     "asynckit": ["asynckit@0.4.0", "", {}, "sha512-Oei9OH4tRh0YqU3GxhX79dM/mwVgvbZJaSNaRk+bshkj0S5cfHcgYakreBjrHwatXKbz+IoIdYLxrKim2MjW0Q=="],
 83 | 
 84 |     "axios": ["axios@1.11.0", "", { "dependencies": { "follow-redirects": "^1.15.6", "form-data": "^4.0.4", "proxy-from-env": "^1.1.0" } }, "sha512-1Lx3WLFQWm3ooKDYZD1eXmoGO9fxYQjrycfHFC8P0sCfQVXyROp0p9PFWBehewBOdCwHc+f/b8I0fMto5eSfwA=="],
 85 | 
 86 |     "body-parser": ["body-parser@2.2.0", "", { "dependencies": { "bytes": "^3.1.2", "content-type": "^1.0.5", "debug": "^4.4.0", "http-errors": "^2.0.0", "iconv-lite": "^0.6.3", "on-finished": "^2.4.1", "qs": "^6.14.0", "raw-body": "^3.0.0", "type-is": "^2.0.0" } }, "sha512-02qvAaxv8tp7fBa/mw1ga98OGm+eCbqzJOKoRt70sLmfEEi+jyBYVTDGfCL/k06/4EMk/z01gCe7HoCH/f2LTg=="],
 87 | 
 88 |     "bytes": ["bytes@3.1.2", "", {}, "sha512-/Nf7TyzTx6S3yRJObOAV7956r8cr2+Oj8AC5dt8wSP3BQAoeX58NoHyCU8P8zGkNXStjTSi6fzO6F0pBdcYbEg=="],
 89 | 
 90 |     "call-bind-apply-helpers": ["call-bind-apply-helpers@1.0.2", "", { "dependencies": { "es-errors": "^1.3.0", "function-bind": "^1.1.2" } }, "sha512-Sp1ablJ0ivDkSzjcaJdxEunN5/XvksFJ2sMBFfq6x0ryhQV/2b/KwFe21cMpmHtPOSij8K99/wSfoEuTObmuMQ=="],
 91 | 
 92 |     "call-bound": ["call-bound@1.0.4", "", { "dependencies": { "call-bind-apply-helpers": "^1.0.2", "get-intrinsic": "^1.3.0" } }, "sha512-+ys997U96po4Kx/ABpBCqhA9EuxJaQWDQg7295H4hBphv3IZg0boBKuwYpt4YXp6MZ5AmZQnU/tyMTlRpaSejg=="],
 93 | 
 94 |     "combined-stream": ["combined-stream@1.0.8", "", { "dependencies": { "delayed-stream": "~1.0.0" } }, "sha512-FQN4MRfuJeHf7cBbBMJFXhKSDq+2kAArBlmRBvcvFE5BB1HZKXtSFASDhdlz9zOYwxh8lDdnvmMOe/+5cdoEdg=="],
 95 | 
 96 |     "content-disposition": ["content-disposition@1.0.0", "", { "dependencies": { "safe-buffer": "5.2.1" } }, "sha512-Au9nRL8VNUut/XSzbQA38+M78dzP4D+eqg3gfJHMIHHYa3bg067xj1KxMUWj+VULbiZMowKngFFbKczUrNJ1mg=="],
 97 | 
 98 |     "content-type": ["content-type@1.0.5", "", {}, "sha512-nTjqfcBFEipKdXCv4YDQWCfmcLZKm81ldF0pAopTvyrFGVbcR6P/VAAd5G7N+0tTr8QqiU0tFadD6FK4NtJwOA=="],
 99 | 
100 |     "cookie": ["cookie@0.7.2", "", {}, "sha512-yki5XnKuf750l50uGTllt6kKILY4nQ1eNIQatoXEByZ5dWgnKqbnqmTrBE5B4N7lrMJKQ2ytWMiTO2o0v6Ew/w=="],
101 | 
102 |     "cookie-signature": ["cookie-signature@1.2.2", "", {}, "sha512-D76uU73ulSXrD1UXF4KE2TMxVVwhsnCgfAyTg9k8P6KGZjlXKrOLe4dJQKI3Bxi5wjesZoFXJWElNWBjPZMbhg=="],
103 | 
104 |     "cors": ["cors@2.8.5", "", { "dependencies": { "object-assign": "^4", "vary": "^1" } }, "sha512-KIHbLJqu73RGr/hnbrO9uBeixNGuvSQjul/jdFvS/KFSIH1hWVd1ng7zOHx+YrEfInLG7q4n6GHQ9cDtxv/P6g=="],
105 | 
106 |     "cross-spawn": ["cross-spawn@7.0.6", "", { "dependencies": { "path-key": "^3.1.0", "shebang-command": "^2.0.0", "which": "^2.0.1" } }, "sha512-uV2QOWP2nWzsy2aMp8aRibhi9dlzF5Hgh5SHaB9OiTGEyDTiJJyx0uy51QXdyWbtAHNua4XJzUKca3OzKUd3vA=="],
107 | 
108 |     "debug": ["debug@4.4.1", "", { "dependencies": { "ms": "^2.1.3" } }, "sha512-KcKCqiftBJcZr++7ykoDIEwSa3XWowTfNPo92BYxjXiyYEVrUQh2aLyhxBCwww+heortUFxEJYcRzosstTEBYQ=="],
109 | 
110 |     "delayed-stream": ["delayed-stream@1.0.0", "", {}, "sha512-ZySD7Nf91aLB0RxL4KGrKHBXl7Eds1DAmEdcoVawXnLD7SDhpNgtuII2aAkg7a7QS41jxPSZ17p4VdGnMHk3MQ=="],
111 | 
112 |     "depd": ["depd@2.0.0", "", {}, "sha512-g7nH6P6dyDioJogAAGprGpCtVImJhpPk/roCzdb3fIh61/s/nPsfR6onyMwkCAR/OlC3yBC0lESvUoQEAssIrw=="],
113 | 
114 |     "dotenv": ["dotenv@17.2.1", "", {}, "sha512-kQhDYKZecqnM0fCnzI5eIv5L4cAe/iRI+HqMbO/hbRdTAeXDG+M9FjipUxNfbARuEg4iHIbhnhs78BCHNbSxEQ=="],
115 | 
116 |     "dunder-proto": ["dunder-proto@1.0.1", "", { "dependencies": { "call-bind-apply-helpers": "^1.0.1", "es-errors": "^1.3.0", "gopd": "^1.2.0" } }, "sha512-KIN/nDJBQRcXw0MLVhZE9iQHmG68qAVIBg9CqmUYjmQIhgij9U5MFvrqkUL5FbtyyzZuOeOt0zdeRe4UY7ct+A=="],
117 | 
118 |     "ee-first": ["ee-first@1.1.1", "", {}, "sha512-WMwm9LhRUo+WUaRN+vRuETqG89IgZphVSNkdFgeb6sS/E4OrDIN7t48CAewSHXc6C8lefD8KKfr5vY61brQlow=="],
119 | 
120 |     "encodeurl": ["encodeurl@2.0.0", "", {}, "sha512-Q0n9HRi4m6JuGIV1eFlmvJB7ZEVxu93IrMyiMsGC0lrMJMWzRgx6WGquyfQgZVb31vhGgXnfmPNNXmxnOkRBrg=="],
121 | 
122 |     "es-define-property": ["es-define-property@1.0.1", "", {}, "sha512-e3nRfgfUZ4rNGL232gUgX06QNyyez04KdjFrF+LTRoOXmrOgFKDg4BCdsjW8EnT69eqdYGmRpJwiPVYNrCaW3g=="],
123 | 
124 |     "es-errors": ["es-errors@1.3.0", "", {}, "sha512-Zf5H2Kxt2xjTvbJvP2ZWLEICxA6j+hAmMzIlypy4xcBg1vKVnx89Wy0GbS+kf5cwCVFFzdCFh2XSCFNULS6csw=="],
125 | 
126 |     "es-object-atoms": ["es-object-atoms@1.1.1", "", { "dependencies": { "es-errors": "^1.3.0" } }, "sha512-FGgH2h8zKNim9ljj7dankFPcICIK9Cp5bm+c2gQSYePhpaG5+esrLODihIorn+Pe6FGJzWhXQotPv73jTaldXA=="],
127 | 
128 |     "es-set-tostringtag": ["es-set-tostringtag@2.1.0", "", { "dependencies": { "es-errors": "^1.3.0", "get-intrinsic": "^1.2.6", "has-tostringtag": "^1.0.2", "hasown": "^2.0.2" } }, "sha512-j6vWzfrGVfyXxge+O0x5sh6cvxAog0a/4Rdd2K36zCMV5eJ+/+tOAngRO8cODMNWbVRdVlmGZQL2YS3yR8bIUA=="],
129 | 
130 |     "esbuild": ["esbuild@0.25.8", "", { "optionalDependencies": { "@esbuild/aix-ppc64": "0.25.8", "@esbuild/android-arm": "0.25.8", "@esbuild/android-arm64": "0.25.8", "@esbuild/android-x64": "0.25.8", "@esbuild/darwin-arm64": "0.25.8", "@esbuild/darwin-x64": "0.25.8", "@esbuild/freebsd-arm64": "0.25.8", "@esbuild/freebsd-x64": "0.25.8", "@esbuild/linux-arm": "0.25.8", "@esbuild/linux-arm64": "0.25.8", "@esbuild/linux-ia32": "0.25.8", "@esbuild/linux-loong64": "0.25.8", "@esbuild/linux-mips64el": "0.25.8", "@esbuild/linux-ppc64": "0.25.8", "@esbuild/linux-riscv64": "0.25.8", "@esbuild/linux-s390x": "0.25.8", "@esbuild/linux-x64": "0.25.8", "@esbuild/netbsd-arm64": "0.25.8", "@esbuild/netbsd-x64": "0.25.8", "@esbuild/openbsd-arm64": "0.25.8", "@esbuild/openbsd-x64": "0.25.8", "@esbuild/openharmony-arm64": "0.25.8", "@esbuild/sunos-x64": "0.25.8", "@esbuild/win32-arm64": "0.25.8", "@esbuild/win32-ia32": "0.25.8", "@esbuild/win32-x64": "0.25.8" }, "bin": { "esbuild": "bin/esbuild" } }, "sha512-vVC0USHGtMi8+R4Kz8rt6JhEWLxsv9Rnu/lGYbPR8u47B+DCBksq9JarW0zOO7bs37hyOK1l2/oqtbciutL5+Q=="],
131 | 
132 |     "escape-html": ["escape-html@1.0.3", "", {}, "sha512-NiSupZ4OeuGwr68lGIeym/ksIZMJodUGOSCZ/FSnTxcrekbvqrgdUxlJOMpijaKZVjAJrWrGs/6Jy8OMuyj9ow=="],
133 | 
134 |     "etag": ["etag@1.8.1", "", {}, "sha512-aIL5Fx7mawVa300al2BnEE4iNvo1qETxLrPI/o05L7z6go7fCw1J6EQmbK4FmJ2AS7kgVF/KEZWufBfdClMcPg=="],
135 | 
136 |     "eventsource": ["eventsource@3.0.7", "", { "dependencies": { "eventsource-parser": "^3.0.1" } }, "sha512-CRT1WTyuQoD771GW56XEZFQ/ZoSfWid1alKGDYMmkt2yl8UXrVR4pspqWNEcqKvVIzg6PAltWjxcSSPrboA4iA=="],
137 | 
138 |     "eventsource-parser": ["eventsource-parser@3.0.3", "", {}, "sha512-nVpZkTMM9rF6AQ9gPJpFsNAMt48wIzB5TQgiTLdHiuO8XEDhUgZEhqKlZWXbIzo9VmJ/HvysHqEaVeD5v9TPvA=="],
139 | 
140 |     "express": ["express@5.1.0", "", { "dependencies": { "accepts": "^2.0.0", "body-parser": "^2.2.0", "content-disposition": "^1.0.0", "content-type": "^1.0.5", "cookie": "^0.7.1", "cookie-signature": "^1.2.1", "debug": "^4.4.0", "encodeurl": "^2.0.0", "escape-html": "^1.0.3", "etag": "^1.8.1", "finalhandler": "^2.1.0", "fresh": "^2.0.0", "http-errors": "^2.0.0", "merge-descriptors": "^2.0.0", "mime-types": "^3.0.0", "on-finished": "^2.4.1", "once": "^1.4.0", "parseurl": "^1.3.3", "proxy-addr": "^2.0.7", "qs": "^6.14.0", "range-parser": "^1.2.1", "router": "^2.2.0", "send": "^1.1.0", "serve-static": "^2.2.0", "statuses": "^2.0.1", "type-is": "^2.0.1", "vary": "^1.1.2" } }, "sha512-DT9ck5YIRU+8GYzzU5kT3eHGA5iL+1Zd0EutOmTE9Dtk+Tvuzd23VBU+ec7HPNSTxXYO55gPV/hq4pSBJDjFpA=="],
141 | 
142 |     "express-rate-limit": ["express-rate-limit@7.5.1", "", { "peerDependencies": { "express": ">= 4.11" } }, "sha512-7iN8iPMDzOMHPUYllBEsQdWVB6fPDMPqwjBaFrgr4Jgr/+okjvzAy+UHlYYL/Vs0OsOrMkwS6PJDkFlJwoxUnw=="],
143 | 
144 |     "fast-deep-equal": ["fast-deep-equal@3.1.3", "", {}, "sha512-f3qQ9oQy9j2AhBe/H9VC91wLmKBCCU/gDOnKNAYG5hswO7BLKj09Hc5HYNz9cGI++xlpDCIgDaitVs03ATR84Q=="],
145 | 
146 |     "fast-json-stable-stringify": ["fast-json-stable-stringify@2.1.0", "", {}, "sha512-lhd/wF+Lk98HZoTCtlVraHtfh5XYijIjalXck7saUtuanSDyLMxnHhSXEDJqHxD7msR8D0uCmqlkwjCV8xvwHw=="],
147 | 
148 |     "finalhandler": ["finalhandler@2.1.0", "", { "dependencies": { "debug": "^4.4.0", "encodeurl": "^2.0.0", "escape-html": "^1.0.3", "on-finished": "^2.4.1", "parseurl": "^1.3.3", "statuses": "^2.0.1" } }, "sha512-/t88Ty3d5JWQbWYgaOGCCYfXRwV1+be02WqYYlL6h0lEiUAMPM8o8qKGO01YIkOHzka2up08wvgYD0mDiI+q3Q=="],
149 | 
150 |     "follow-redirects": ["follow-redirects@1.15.11", "", {}, "sha512-deG2P0JfjrTxl50XGCDyfI97ZGVCxIpfKYmfyrQ54n5FO/0gfIES8C/Psl6kWVDolizcaaxZJnTS0QSMxvnsBQ=="],
151 | 
152 |     "form-data": ["form-data@4.0.4", "", { "dependencies": { "asynckit": "^0.4.0", "combined-stream": "^1.0.8", "es-set-tostringtag": "^2.1.0", "hasown": "^2.0.2", "mime-types": "^2.1.12" } }, "sha512-KrGhL9Q4zjj0kiUt5OO4Mr/A/jlI2jDYs5eHBpYHPcBEVSiipAvn2Ko2HnPe20rmcuuvMHNdZFp+4IlGTMF0Ow=="],
153 | 
154 |     "forwarded": ["forwarded@0.2.0", "", {}, "sha512-buRG0fpBtRHSTCOASe6hD258tEubFoRLb4ZNA6NxMVHNw2gOcwHo9wyablzMzOA5z9xA9L1KNjk/Nt6MT9aYow=="],
155 | 
156 |     "fresh": ["fresh@2.0.0", "", {}, "sha512-Rx/WycZ60HOaqLKAi6cHRKKI7zxWbJ31MhntmtwMoaTeF7XFH9hhBp8vITaMidfljRQ6eYWCKkaTK+ykVJHP2A=="],
157 | 
158 |     "fsevents": ["fsevents@2.3.3", "", { "os": "darwin" }, "sha512-5xoDfX+fL7faATnagmWPpbFtwh/R77WmMMqqHGS65C3vvB0YHrgF+B1YmZ3441tMj5n63k0212XNoJwzlhffQw=="],
159 | 
160 |     "function-bind": ["function-bind@1.1.2", "", {}, "sha512-7XHNxH7qX9xG5mIwxkhumTox/MIRNcOgDrxWsMt2pAr23WHp6MrRlN7FBSFpCpr+oVO0F744iUgR82nJMfG2SA=="],
161 | 
162 |     "get-intrinsic": ["get-intrinsic@1.3.0", "", { "dependencies": { "call-bind-apply-helpers": "^1.0.2", "es-define-property": "^1.0.1", "es-errors": "^1.3.0", "es-object-atoms": "^1.1.1", "function-bind": "^1.1.2", "get-proto": "^1.0.1", "gopd": "^1.2.0", "has-symbols": "^1.1.0", "hasown": "^2.0.2", "math-intrinsics": "^1.1.0" } }, "sha512-9fSjSaos/fRIVIp+xSJlE6lfwhES7LNtKaCBIamHsjr2na1BiABJPo0mOjjz8GJDURarmCPGqaiVg5mfjb98CQ=="],
163 | 
164 |     "get-proto": ["get-proto@1.0.1", "", { "dependencies": { "dunder-proto": "^1.0.1", "es-object-atoms": "^1.0.0" } }, "sha512-sTSfBjoXBp89JvIKIefqw7U2CCebsc74kiY6awiGogKtoSGbgjYE/G/+l9sF3MWFPNc9IcoOC4ODfKHfxFmp0g=="],
165 | 
166 |     "get-tsconfig": ["get-tsconfig@4.10.1", "", { "dependencies": { "resolve-pkg-maps": "^1.0.0" } }, "sha512-auHyJ4AgMz7vgS8Hp3N6HXSmlMdUyhSUrfBF16w153rxtLIEOE+HGqaBppczZvnHLqQJfiHotCYpNhl0lUROFQ=="],
167 | 
168 |     "gopd": ["gopd@1.2.0", "", {}, "sha512-ZUKRh6/kUFoAiTAtTYPZJ3hw9wNxx+BIBOijnlG9PnrJsCcSjs1wyyD6vJpaYtgnzDrKYRSqf3OO6Rfa93xsRg=="],
169 | 
170 |     "has-symbols": ["has-symbols@1.1.0", "", {}, "sha512-1cDNdwJ2Jaohmb3sg4OmKaMBwuC48sYni5HUw2DvsC8LjGTLK9h+eb1X6RyuOHe4hT0ULCW68iomhjUoKUqlPQ=="],
171 | 
172 |     "has-tostringtag": ["has-tostringtag@1.0.2", "", { "dependencies": { "has-symbols": "^1.0.3" } }, "sha512-NqADB8VjPFLM2V0VvHUewwwsw0ZWBaIdgo+ieHtK3hasLz4qeCRjYcqfB6AQrBggRKppKF8L52/VqdVsO47Dlw=="],
173 | 
174 |     "hasown": ["hasown@2.0.2", "", { "dependencies": { "function-bind": "^1.1.2" } }, "sha512-0hJU9SCPvmMzIBdZFqNPXWa6dqh7WdH0cII9y+CyS8rG3nL48Bclra9HmKhVVUHyPWNH5Y7xDwAB7bfgSjkUMQ=="],
175 | 
176 |     "http-errors": ["http-errors@2.0.0", "", { "dependencies": { "depd": "2.0.0", "inherits": "2.0.4", "setprototypeof": "1.2.0", "statuses": "2.0.1", "toidentifier": "1.0.1" } }, "sha512-FtwrG/euBzaEjYeRqOgly7G0qviiXoJWnvEH2Z1plBdXgbyjv34pHTSb9zoeHMyDy33+DWy5Wt9Wo+TURtOYSQ=="],
177 | 
178 |     "iconv-lite": ["iconv-lite@0.6.3", "", { "dependencies": { "safer-buffer": ">= 2.1.2 < 3.0.0" } }, "sha512-4fCk79wshMdzMp2rH06qWrJE4iolqLhCUH+OiuIgU++RB0+94NlDL81atO7GX55uUKueo0txHNtvEyI6D7WdMw=="],
179 | 
180 |     "inherits": ["inherits@2.0.4", "", {}, "sha512-k/vGaX4/Yla3WzyMCvTQOXYeIHvqOKtnqBduzTHpzpQZzAskKMhZ2K+EnBiSM9zGSoIFeMpXKxa4dYeZIQqewQ=="],
181 | 
182 |     "ipaddr.js": ["ipaddr.js@1.9.1", "", {}, "sha512-0KI/607xoxSToH7GjN1FfSbLoU0+btTicjsQSWQlh/hZykN8KpmMf7uYwPW3R+akZ6R/w18ZlXSHBYXiYUPO3g=="],
183 | 
184 |     "is-promise": ["is-promise@4.0.0", "", {}, "sha512-hvpoI6korhJMnej285dSg6nu1+e6uxs7zG3BYAm5byqDsgJNWwxzM6z6iZiAgQR4TJ30JmBTOwqZUw3WlyH3AQ=="],
185 | 
186 |     "isexe": ["isexe@2.0.0", "", {}, "sha512-RHxMLp9lnKHGHRng9QFhRCMbYAcVpn69smSGcq3f36xjgVVWThj4qqLbTLlq7Ssj8B+fIQ1EuCEGI2lKsyQeIw=="],
187 | 
188 |     "json-schema-traverse": ["json-schema-traverse@0.4.1", "", {}, "sha512-xbbCH5dCYU5T8LcEhhuh7HJ88HXuW3qsI3Y0zOZFKfZEHcpWiHU/Jxzk629Brsab/mMiHQti9wMP+845RPe3Vg=="],
189 | 
190 |     "math-intrinsics": ["math-intrinsics@1.1.0", "", {}, "sha512-/IXtbwEk5HTPyEwyKX6hGkYXxM9nbj64B+ilVJnC/R6B0pH5G4V3b0pVbL7DBj4tkhBAppbQUlf6F6Xl9LHu1g=="],
191 | 
192 |     "media-typer": ["media-typer@1.1.0", "", {}, "sha512-aisnrDP4GNe06UcKFnV5bfMNPBUw4jsLGaWwWfnH3v02GnBuXX2MCVn5RbrWo0j3pczUilYblq7fQ7Nw2t5XKw=="],
193 | 
194 |     "merge-descriptors": ["merge-descriptors@2.0.0", "", {}, "sha512-Snk314V5ayFLhp3fkUREub6WtjBfPdCPY1Ln8/8munuLuiYhsABgBVWsozAG+MWMbVEvcdcpbi9R7ww22l9Q3g=="],
195 | 
196 |     "mime-db": ["mime-db@1.54.0", "", {}, "sha512-aU5EJuIN2WDemCcAp2vFBfp/m4EAhWJnUNSSw0ixs7/kXbd6Pg64EmwJkNdFhB8aWt1sH2CTXrLxo/iAGV3oPQ=="],
197 | 
198 |     "mime-types": ["mime-types@3.0.1", "", { "dependencies": { "mime-db": "^1.54.0" } }, "sha512-xRc4oEhT6eaBpU1XF7AjpOFD+xQmXNB5OVKwp4tqCuBpHLS/ZbBDrc07mYTDqVMg6PfxUjjNp85O6Cd2Z/5HWA=="],
199 | 
200 |     "ms": ["ms@2.1.3", "", {}, "sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA=="],
201 | 
202 |     "negotiator": ["negotiator@1.0.0", "", {}, "sha512-8Ofs/AUQh8MaEcrlq5xOX0CQ9ypTF5dl78mjlMNfOK08fzpgTHQRQPBxcPlEtIw0yRpws+Zo/3r+5WRby7u3Gg=="],
203 | 
204 |     "object-assign": ["object-assign@4.1.1", "", {}, "sha512-rJgTQnkUnH1sFw8yT6VSU3zD3sWmu6sZhIseY8VX+GRu3P6F7Fu+JNDoXfklElbLJSnc3FUQHVe4cU5hj+BcUg=="],
205 | 
206 |     "object-inspect": ["object-inspect@1.13.4", "", {}, "sha512-W67iLl4J2EXEGTbfeHCffrjDfitvLANg0UlX3wFUUSTx92KXRFegMHUVgSqE+wvhAbi4WqjGg9czysTV2Epbew=="],
207 | 
208 |     "on-finished": ["on-finished@2.4.1", "", { "dependencies": { "ee-first": "1.1.1" } }, "sha512-oVlzkg3ENAhCk2zdv7IJwd/QUD4z2RxRwpkcGY8psCVcCYZNq4wYnVWALHM+brtuJjePWiYF/ClmuDr8Ch5+kg=="],
209 | 
210 |     "once": ["once@1.4.0", "", { "dependencies": { "wrappy": "1" } }, "sha512-lNaJgI+2Q5URQBkccEKHTQOPaXdUxnZZElQTZY0MFUAuaEqe1E+Nyvgdz/aIyNi6Z9MzO5dv1H8n58/GELp3+w=="],
211 | 
212 |     "parseurl": ["parseurl@1.3.3", "", {}, "sha512-CiyeOxFT/JZyN5m0z9PfXw4SCBJ6Sygz1Dpl0wqjlhDEGGBP1GnsUVEL0p63hoG1fcj3fHynXi9NYO4nWOL+qQ=="],
213 | 
214 |     "path-key": ["path-key@3.1.1", "", {}, "sha512-ojmeN0qd+y0jszEtoY48r0Peq5dwMEkIlCOu6Q5f41lfkswXuKtYrhgoTpLnyIcHm24Uhqx+5Tqm2InSwLhE6Q=="],
215 | 
216 |     "path-to-regexp": ["path-to-regexp@8.2.0", "", {}, "sha512-TdrF7fW9Rphjq4RjrW0Kp2AW0Ahwu9sRGTkS6bvDi0SCwZlEZYmcfDbEsTz8RVk0EHIS/Vd1bv3JhG+1xZuAyQ=="],
217 | 
218 |     "pkce-challenge": ["pkce-challenge@5.0.0", "", {}, "sha512-ueGLflrrnvwB3xuo/uGob5pd5FN7l0MsLf0Z87o/UQmRtwjvfylfc9MurIxRAWywCYTgrvpXBcqjV4OfCYGCIQ=="],
219 | 
220 |     "playwright": ["playwright@1.54.2", "", { "dependencies": { "playwright-core": "1.54.2" }, "optionalDependencies": { "fsevents": "2.3.2" }, "bin": { "playwright": "cli.js" } }, "sha512-Hu/BMoA1NAdRUuulyvQC0pEqZ4vQbGfn8f7wPXcnqQmM+zct9UliKxsIkLNmz/ku7LElUNqmaiv1TG/aL5ACsw=="],
221 | 
222 |     "playwright-core": ["playwright-core@1.54.2", "", { "bin": { "playwright-core": "cli.js" } }, "sha512-n5r4HFbMmWsB4twG7tJLDN9gmBUeSPcsBZiWSE4DnYz9mJMAFqr2ID7+eGC9kpEnxExJ1epttwR59LEWCk8mtA=="],
223 | 
224 |     "proxy-addr": ["proxy-addr@2.0.7", "", { "dependencies": { "forwarded": "0.2.0", "ipaddr.js": "1.9.1" } }, "sha512-llQsMLSUDUPT44jdrU/O37qlnifitDP+ZwrmmZcoSKyLKvtZxpyV0n2/bD/N4tBAAZ/gJEdZU7KMraoK1+XYAg=="],
225 | 
226 |     "proxy-from-env": ["proxy-from-env@1.1.0", "", {}, "sha512-D+zkORCbA9f1tdWRK0RaCR3GPv50cMxcrz4X8k5LTSUD1Dkw47mKJEZQNunItRTkWwgtaUSo1RVFRIG9ZXiFYg=="],
227 | 
228 |     "punycode": ["punycode@2.3.1", "", {}, "sha512-vYt7UD1U9Wg6138shLtLOvdAu+8DsC/ilFtEVHcH+wydcSpNE20AfSOduf6MkRFahL5FY7X1oU7nKVZFtfq8Fg=="],
229 | 
230 |     "qs": ["qs@6.14.0", "", { "dependencies": { "side-channel": "^1.1.0" } }, "sha512-YWWTjgABSKcvs/nWBi9PycY/JiPJqOD4JA6o9Sej2AtvSGarXxKC3OQSk4pAarbdQlKAh5D4FCQkJNkW+GAn3w=="],
231 | 
232 |     "range-parser": ["range-parser@1.2.1", "", {}, "sha512-Hrgsx+orqoygnmhFbKaHE6c296J+HTAQXoxEF6gNupROmmGJRoyzfG3ccAveqCBrwr/2yxQ5BVd/GTl5agOwSg=="],
233 | 
234 |     "raw-body": ["raw-body@3.0.0", "", { "dependencies": { "bytes": "3.1.2", "http-errors": "2.0.0", "iconv-lite": "0.6.3", "unpipe": "1.0.0" } }, "sha512-RmkhL8CAyCRPXCE28MMH0z2PNWQBNk2Q09ZdxM9IOOXwxwZbN+qbWaatPkdkWIKL2ZVDImrN/pK5HTRz2PcS4g=="],
235 | 
236 |     "resolve-pkg-maps": ["resolve-pkg-maps@1.0.0", "", {}, "sha512-seS2Tj26TBVOC2NIc2rOe2y2ZO7efxITtLZcGSOnHHNOQ7CkiUBfw0Iw2ck6xkIhPwLhKNLS8BO+hEpngQlqzw=="],
237 | 
238 |     "router": ["router@2.2.0", "", { "dependencies": { "debug": "^4.4.0", "depd": "^2.0.0", "is-promise": "^4.0.0", "parseurl": "^1.3.3", "path-to-regexp": "^8.0.0" } }, "sha512-nLTrUKm2UyiL7rlhapu/Zl45FwNgkZGaCpZbIHajDYgwlJCOzLSk+cIPAnsEqV955GjILJnKbdQC1nVPz+gAYQ=="],
239 | 
240 |     "safe-buffer": ["safe-buffer@5.2.1", "", {}, "sha512-rp3So07KcdmmKbGvgaNxQSJr7bGVSVk5S9Eq1F+ppbRo70+YeaDxkw5Dd8NPN+GD6bjnYm2VuPuCXmpuYvmCXQ=="],
241 | 
242 |     "safer-buffer": ["safer-buffer@2.1.2", "", {}, "sha512-YZo3K82SD7Riyi0E1EQPojLz7kpepnSQI9IyPbHHg1XXXevb5dJI7tpyN2ADxGcQbHG7vcyRHk0cbwqcQriUtg=="],
243 | 
244 |     "send": ["send@1.2.0", "", { "dependencies": { "debug": "^4.3.5", "encodeurl": "^2.0.0", "escape-html": "^1.0.3", "etag": "^1.8.1", "fresh": "^2.0.0", "http-errors": "^2.0.0", "mime-types": "^3.0.1", "ms": "^2.1.3", "on-finished": "^2.4.1", "range-parser": "^1.2.1", "statuses": "^2.0.1" } }, "sha512-uaW0WwXKpL9blXE2o0bRhoL2EGXIrZxQ2ZQ4mgcfoBxdFmQold+qWsD2jLrfZ0trjKL6vOw0j//eAwcALFjKSw=="],
245 | 
246 |     "serve-static": ["serve-static@2.2.0", "", { "dependencies": { "encodeurl": "^2.0.0", "escape-html": "^1.0.3", "parseurl": "^1.3.3", "send": "^1.2.0" } }, "sha512-61g9pCh0Vnh7IutZjtLGGpTA355+OPn2TyDv/6ivP2h/AdAVX9azsoxmg2/M6nZeQZNYBEwIcsne1mJd9oQItQ=="],
247 | 
248 |     "setprototypeof": ["setprototypeof@1.2.0", "", {}, "sha512-E5LDX7Wrp85Kil5bhZv46j8jOeboKq5JMmYM3gVGdGH8xFpPWXUMsNrlODCrkoxMEeNi/XZIwuRvY4XNwYMJpw=="],
249 | 
250 |     "shebang-command": ["shebang-command@2.0.0", "", { "dependencies": { "shebang-regex": "^3.0.0" } }, "sha512-kHxr2zZpYtdmrN1qDjrrX/Z1rR1kG8Dx+gkpK1G4eXmvXswmcE1hTWBWYUzlraYw1/yZp6YuDY77YtvbN0dmDA=="],
251 | 
252 |     "shebang-regex": ["shebang-regex@3.0.0", "", {}, "sha512-7++dFhtcx3353uBaq8DDR4NuxBetBzC7ZQOhmTQInHEd6bSrXdiEyzCvG07Z44UYdLShWUyXt5M/yhz8ekcb1A=="],
253 | 
254 |     "side-channel": ["side-channel@1.1.0", "", { "dependencies": { "es-errors": "^1.3.0", "object-inspect": "^1.13.3", "side-channel-list": "^1.0.0", "side-channel-map": "^1.0.1", "side-channel-weakmap": "^1.0.2" } }, "sha512-ZX99e6tRweoUXqR+VBrslhda51Nh5MTQwou5tnUDgbtyM0dBgmhEDtWGP/xbKn6hqfPRHujUNwz5fy/wbbhnpw=="],
255 | 
256 |     "side-channel-list": ["side-channel-list@1.0.0", "", { "dependencies": { "es-errors": "^1.3.0", "object-inspect": "^1.13.3" } }, "sha512-FCLHtRD/gnpCiCHEiJLOwdmFP+wzCmDEkc9y7NsYxeF4u7Btsn1ZuwgwJGxImImHicJArLP4R0yX4c2KCrMrTA=="],
257 | 
258 |     "side-channel-map": ["side-channel-map@1.0.1", "", { "dependencies": { "call-bound": "^1.0.2", "es-errors": "^1.3.0", "get-intrinsic": "^1.2.5", "object-inspect": "^1.13.3" } }, "sha512-VCjCNfgMsby3tTdo02nbjtM/ewra6jPHmpThenkTYh8pG9ucZ/1P8So4u4FGBek/BjpOVsDCMoLA/iuBKIFXRA=="],
259 | 
260 |     "side-channel-weakmap": ["side-channel-weakmap@1.0.2", "", { "dependencies": { "call-bound": "^1.0.2", "es-errors": "^1.3.0", "get-intrinsic": "^1.2.5", "object-inspect": "^1.13.3", "side-channel-map": "^1.0.1" } }, "sha512-WPS/HvHQTYnHisLo9McqBHOJk2FkHO/tlpvldyrnem4aeQp4hai3gythswg6p01oSoTl58rcpiFAjF2br2Ak2A=="],
261 | 
262 |     "statuses": ["statuses@2.0.2", "", {}, "sha512-DvEy55V3DB7uknRo+4iOGT5fP1slR8wQohVdknigZPMpMstaKJQWhwiYBACJE3Ul2pTnATihhBYnRhZQHGBiRw=="],
263 | 
264 |     "toidentifier": ["toidentifier@1.0.1", "", {}, "sha512-o5sSPKEkg/DIQNmH43V0/uerLrpzVedkUh8tGNvaeXpfpuwjKenlSox/2O/BTlZUtEe+JG7s5YhEz608PlAHRA=="],
265 | 
266 |     "tsx": ["tsx@4.20.3", "", { "dependencies": { "esbuild": "~0.25.0", "get-tsconfig": "^4.7.5" }, "optionalDependencies": { "fsevents": "~2.3.3" }, "bin": { "tsx": "dist/cli.mjs" } }, "sha512-qjbnuR9Tr+FJOMBqJCW5ehvIo/buZq7vH7qD7JziU98h6l3qGy0a/yPFjwO+y0/T7GFpNgNAvEcPPVfyT8rrPQ=="],
267 | 
268 |     "type-is": ["type-is@2.0.1", "", { "dependencies": { "content-type": "^1.0.5", "media-typer": "^1.1.0", "mime-types": "^3.0.0" } }, "sha512-OZs6gsjF4vMp32qrCbiVSkrFmXtG/AZhY3t0iAMrMBiAZyV9oALtXO8hsrHbMXF9x6L3grlFuwW2oAz7cav+Gw=="],
269 | 
270 |     "typescript": ["typescript@5.9.2", "", { "bin": { "tsc": "bin/tsc", "tsserver": "bin/tsserver" } }, "sha512-CWBzXQrc/qOkhidw1OzBTQuYRbfyxDXJMVJ1XNwUHGROVmuaeiEm3OslpZ1RV96d7SKKjZKrSJu3+t/xlw3R9A=="],
271 | 
272 |     "undici-types": ["undici-types@7.10.0", "", {}, "sha512-t5Fy/nfn+14LuOc2KNYg75vZqClpAiqscVvMygNnlsHBFpSXdJaYtXMcdNLpl/Qvc3P2cB3s6lOV51nqsFq4ag=="],
273 | 
274 |     "unpipe": ["unpipe@1.0.0", "", {}, "sha512-pjy2bYhSsufwWlKwPc+l3cN7+wuJlK6uz0YdJEOlQDbl6jo/YlPi4mb8agUkVC8BF7V8NuzeyPNqRksA3hztKQ=="],
275 | 
276 |     "uri-js": ["uri-js@4.4.1", "", { "dependencies": { "punycode": "^2.1.0" } }, "sha512-7rKUyy33Q1yc98pQ1DAmLtwX109F7TIfWlW1Ydo8Wl1ii1SeHieeh0HHfPeL2fMXK6z0s8ecKs9frCuLJvndBg=="],
277 | 
278 |     "vary": ["vary@1.1.2", "", {}, "sha512-BNGbWLfd0eUPabhkXUVm0j8uuvREyTh5ovRa/dyow/BqAbZJyC+5fU+IzQOzmAKzYqYRAISoRhdQr3eIZ/PXqg=="],
279 | 
280 |     "which": ["which@2.0.2", "", { "dependencies": { "isexe": "^2.0.0" }, "bin": { "node-which": "./bin/node-which" } }, "sha512-BLI3Tl1TW3Pvl70l3yq3Y64i+awpwXqsGBYWkkqMtnbXgrMD+yj7rhW0kuEDxzJaYXGjEW5ogapKNMEKNMjibA=="],
281 | 
282 |     "wrappy": ["wrappy@1.0.2", "", {}, "sha512-l4Sp/DRseor9wL6EvV2+TuQn63dMkPjZ/sp9XkghTEbV9KlPS1xUsZ3u7/IQO4wxtcFB4bgpQPRcR3QCvezPcQ=="],
283 | 
284 |     "zod": ["zod@3.25.76", "", {}, "sha512-gzUt/qt81nXsFGKIFcC3YnfEAx5NkunCfnDlvuBSSFS02bcXu4Lmea0AFIUwbLWxWPx3d9p8S5QoaujKcNQxcQ=="],
285 | 
286 |     "zod-to-json-schema": ["zod-to-json-schema@3.24.6", "", { "peerDependencies": { "zod": "^3.24.1" } }, "sha512-h/z3PKvcTcTetyjl1fkj79MHNEjm+HpD6NXheWjzOekY7kV+lwDYnHw+ivHkijnCSMz1yJaWBD9vu/Fcmk+vEg=="],
287 | 
288 |     "form-data/mime-types": ["mime-types@2.1.35", "", { "dependencies": { "mime-db": "1.52.0" } }, "sha512-ZDY+bPm5zTTF+YpCrAU9nK0UgICYPT0QtT1NZWFv4s++TNkcgVaT0g6+4R2uI4MjQjzysHB1zxuWL50hzaeXiw=="],
289 | 
290 |     "http-errors/statuses": ["statuses@2.0.1", "", {}, "sha512-RwNA9Z/7PrK06rYLIzFMlaF+l73iwpzsqRIFgbMLbTcLD6cOao82TaWefPXQvB2fOC4AjuYSEndS7N/mTCbkdQ=="],
291 | 
292 |     "playwright/fsevents": ["fsevents@2.3.2", "", { "os": "darwin" }, "sha512-xiqMQR4xAeHTuB9uWm+fFRcIOgKBMiOBP+eXiyT7jsgVCq1bkVygt00oASowB7EdtpOHaaPgKt812P9ab+DDKA=="],
293 | 
294 |     "form-data/mime-types/mime-db": ["mime-db@1.52.0", "", {}, "sha512-sPU4uV7dYlvtWJxwwxHD0PuihVNiE7TyAbQ5SWxDCB9mUYvOgroQOwYQQOKPJ8CIbE+1ETVlOoK1UC2nU3gYvg=="],
295 |   }
296 | }
297 | 


--------------------------------------------------------------------------------
/mcp.md:
--------------------------------------------------------------------------------
  1 | # Brave Search MCP Server Documentation
  2 | 
  3 | ## Overview
  4 | 
  5 | This guide walks you through setting up and running a Model Context Protocol (MCP) server that provides Brave Search functionality via Streamable HTTP transport. The server offers two search tools: web search and local business search.
  6 | 
  7 | ## Prerequisites
  8 | 
  9 | ### Required Software
 10 | - **Bun** (JavaScript runtime) - Install from [bun.sh](https://bun.sh)
 11 | - **Brave Search API Key** - Obtain from [Brave Search API](https://api.search.brave.com/)
 12 | - **Basic terminal/command line knowledge**
 13 | 
 14 | ### System Requirements
 15 | - Node.js 18+ compatible environment
 16 | - Internet connection for API calls
 17 | - Available port (default: 8000)
 18 | 
 19 | ## Installation & Setup
 20 | 
 21 | ### 1. Project Setup
 22 | ```bash
 23 | # Clone or download the brave-search MCP server files
 24 | # Ensure you have these files:
 25 | # - index.ts (main server file)
 26 | # - package.json (dependencies)
 27 | # - tsconfig.json (TypeScript config)
 28 | ```
 29 | 
 30 | ### 2. Install Dependencies
 31 | ```bash
 32 | # Navigate to the brave-search directory
 33 | cd /path/to/brave-search
 34 | 
 35 | # Install all required packages
 36 | bun install
 37 | ```
 38 | 
 39 | **What this does:** Downloads the MCP SDK and other dependencies needed to run the server.
 40 | 
 41 | ### 3. API Key Configuration
 42 | ```bash
 43 | # Option 1: Environment variable (recommended for production)
 44 | export BRAVE_API_KEY="your-brave-api-key-here"
 45 | 
 46 | # Option 2: The server has a fallback hardcoded key for testing
 47 | # (already configured in the current implementation)
 48 | ```
 49 | 
 50 | **Security Note:** Never commit API keys to version control. Use environment variables in production.
 51 | 
 52 | ## Running the Server
 53 | 
 54 | ### Starting the Server
 55 | ```bash
 56 | # Start the server on port 8000 with Streamable HTTP transport
 57 | bun run index.ts --port 8000
 58 | ```
 59 | 
 60 | **Expected Output:**
 61 | ```
 62 | Listening on http://localhost:8000
 63 | Put this in your client config:
 64 | {
 65 |   "mcpServers": {
 66 |     "brave-search": {
 67 |       "url": "http://localhost:8000/sse"
 68 |     }
 69 |   }
 70 | }
 71 | If your client supports streamable HTTP, you can use the /mcp endpoint instead.
 72 | ```
 73 | 
 74 | ### Understanding the Endpoints
 75 | 
 76 | The server provides two endpoints:
 77 | 
 78 | 1. **`/sse`** - Server-Sent Events transport (for backward compatibility)
 79 | 2. **`/mcp`** - Streamable HTTP transport (recommended for new implementations)
 80 | 
 81 | ## Testing the Server
 82 | 
 83 | ### 1. Initialize MCP Session
 84 | ```bash
 85 | curl -v -X POST http://localhost:8000/mcp \
 86 |   -H "Accept: application/json, text/event-stream" \
 87 |   -H "Content-Type: application/json" \
 88 |   -d '{
 89 |     "jsonrpc": "2.0",
 90 |     "id": 1,
 91 |     "method": "initialize",
 92 |     "params": {
 93 |       "protocolVersion": "2024-11-05",
 94 |       "capabilities": {
 95 |         "tools": {}
 96 |       },
 97 |       "clientInfo": {
 98 |         "name": "TestClient",
 99 |         "version": "1.0.0"
100 |       }
101 |     }
102 |   }'
103 | ```
104 | 
105 | **What to look for:**
106 | - Status: `200 OK`
107 | - Header: `mcp-session-id: [uuid]` (save this for next steps)
108 | - Response: JSON with server capabilities
109 | 
110 | ### 2. Send Initialized Notification
111 | ```bash
112 | curl -X POST http://localhost:8000/mcp \
113 |   -H "Accept: application/json, text/event-stream" \
114 |   -H "Content-Type: application/json" \
115 |   -H "Mcp-Session-Id: YOUR_SESSION_ID_FROM_STEP_1" \
116 |   -d '{
117 |     "jsonrpc": "2.0",
118 |     "method": "notifications/initialized"
119 |   }'
120 | ```
121 | 
122 | **Critical:** Replace `YOUR_SESSION_ID_FROM_STEP_1` with the actual session ID from step 1.
123 | 
124 | ### 3. List Available Tools
125 | ```bash
126 | curl -X POST http://localhost:8000/mcp \
127 |   -H "Accept: application/json, text/event-stream" \
128 |   -H "Content-Type: application/json" \
129 |   -H "Mcp-Session-Id: YOUR_SESSION_ID" \
130 |   -d '{
131 |     "jsonrpc": "2.0",
132 |     "id": 2,
133 |     "method": "tools/list"
134 |   }'
135 | ```
136 | 
137 | **Expected Response:** List of two tools:
138 | - `brave_web_search` - General web search
139 | - `brave_local_search` - Local business search
140 | 
141 | ### 4. Perform Web Search
142 | ```bash
143 | curl -X POST http://localhost:8000/mcp \
144 |   -H "Accept: application/json, text/event-stream" \
145 |   -H "Content-Type: application/json" \
146 |   -H "Mcp-Session-Id: YOUR_SESSION_ID" \
147 |   -d '{
148 |     "jsonrpc": "2.0",
149 |     "id": 3,
150 |     "method": "tools/call",
151 |     "params": {
152 |       "name": "brave_web_search",
153 |       "arguments": {
154 |         "query": "latest AI news",
155 |         "count": 3
156 |       }
157 |     }
158 |   }'
159 | ```
160 | 
161 | ### 5. Perform Local Search
162 | ```bash
163 | curl -X POST http://localhost:8000/mcp \
164 |   -H "Accept: application/json, text/event-stream" \
165 |   -H "Content-Type: application/json" \
166 |   -H "Mcp-Session-Id: YOUR_SESSION_ID" \
167 |   -d '{
168 |     "jsonrpc": "2.0",
169 |     "id": 4,
170 |     "method": "tools/call",
171 |     "params": {
172 |       "name": "brave_local_search",
173 |       "arguments": {
174 |         "query": "pizza near Times Square NYC",
175 |         "count": 2
176 |       }
177 |     }
178 |   }'
179 | ```
180 | 
181 | ## Implementation Details: From Stdio to Streamable HTTP
182 | 
183 | ### What We Changed
184 | The original brave-search MCP server only supported stdio transport (standard input/output). We modified it to support Streamable HTTP transport for AWS Lambda compatibility and better web integration.
185 | 
186 | ### Key Code Changes
187 | 
188 | #### 1. Added HTTP Transport Imports
189 | ```typescript
190 | // Added these imports
191 | import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
192 | import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
193 | import { createServer } from "http";
194 | import { randomUUID } from "crypto";
195 | ```
196 | 
197 | #### 2. Command Line Argument Parsing
198 | ```typescript
199 | // Added argument parsing for --port flag
200 | function parseArgs() {
201 |   const args = process.argv.slice(2);
202 |   const options: { port?: number; headless?: boolean } = {};
203 |   
204 |   for (let i = 0; i < args.length; i++) {
205 |     if (args[i] === '--port' && i + 1 < args.length) {
206 |       options.port = parseInt(args[i + 1], 10);
207 |       i++;
208 |     }
209 |   }
210 |   return options;
211 | }
212 | ```
213 | 
214 | #### 3. HTTP Server Setup
215 | ```typescript
216 | // Added HTTP server with dual transport support
217 | function startHttpServer(port: number) {
218 |   const httpServer = createServer();
219 |   
220 |   httpServer.on('request', async (req, res) => {
221 |     const url = new URL(req.url!, `http://${req.headers.host}`);
222 |     
223 |     if (url.pathname === '/sse') {
224 |       await handleSSE(req, res);
225 |     } else if (url.pathname === '/mcp') {
226 |       await handleStreamable(req, res);
227 |     } else {
228 |       res.writeHead(404, { 'Content-Type': 'text/plain' });
229 |       res.end('Not Found');
230 |     }
231 |   });
232 | }
233 | ```
234 | 
235 | #### 4. Session Management
236 | ```typescript
237 | // Added session storage for concurrent connections
238 | const streamableSessions = new Map<string, {transport: any, server: any}>();
239 | 
240 | // Each session gets its own server instance
241 | function createServerInstance() {
242 |   const serverInstance = new Server({...});
243 |   // Set up tool handlers...
244 |   return serverInstance;
245 | }
246 | ```
247 | 
248 | #### 5. Transport Handlers
249 | ```typescript
250 | // Streamable HTTP transport handler
251 | async function handleStreamable(req: any, res: any) {
252 |   const sessionId = req.headers['mcp-session-id'] as string | undefined;
253 |   
254 |   if (sessionId) {
255 |     // Use existing session
256 |     const session = streamableSessions.get(sessionId);
257 |     return await session.transport.handleRequest(req, res);
258 |   }
259 |   
260 |   // Create new session for initialization
261 |   const serverInstance = createServerInstance();
262 |   const transport = new StreamableHTTPServerTransport({
263 |     sessionIdGenerator: () => randomUUID(),
264 |     onsessioninitialized: (sessionId) => {
265 |       streamableSessions.set(sessionId, { transport, server: serverInstance });
266 |     }
267 |   });
268 |   
269 |   await serverInstance.connect(transport);
270 |   await transport.handleRequest(req, res);
271 | }
272 | ```
273 | 
274 | ### Why These Changes Were Necessary
275 | 
276 | 1. **Lambda Compatibility**: AWS Lambda doesn't support stdio, requiring HTTP-based communication
277 | 2. **Web Integration**: HTTP transport enables direct browser and web service integration
278 | 3. **Concurrent Sessions**: Multiple clients can connect simultaneously with session isolation
279 | 4. **Modern Protocol**: Streamable HTTP is the modern MCP transport standard
280 | 
281 | ### Transport Comparison
282 | 
283 | | Feature | Stdio Transport | Streamable HTTP Transport |
284 | |---------|----------------|---------------------------|
285 | | Use Case | CLI applications | Web services, Lambda |
286 | | Concurrency | Single client | Multiple concurrent clients |
287 | | State Management | Process-based | Session-based |
288 | | AWS Lambda | ❌ Not supported | ✅ Fully supported |
289 | | Web Browser | ❌ Not possible | ✅ Direct integration |
290 | | Debugging | Simple | Requires HTTP tools |
291 | 
292 | ## Understanding MCP Concepts
293 | 
294 | ### Session Management
295 | - Each client connection gets a unique session ID
296 | - Sessions maintain state between requests
297 | - Sessions are automatically cleaned up when connections close
298 | - **Important:** Always include the `Mcp-Session-Id` header after initialization
299 | 
300 | ### Transport Types
301 | 1. **Streamable HTTP** (`/mcp`): Modern, efficient, supports streaming responses
302 | 2. **SSE** (`/sse`): Backward compatibility, uses Server-Sent Events
303 | 
304 | ### Message Flow
305 | 1. **Initialize** - Establish capabilities and protocol version
306 | 2. **Initialized** - Confirm initialization complete
307 | 3. **Tools/List** - Discover available tools
308 | 4. **Tools/Call** - Execute tool functions
309 | 
310 | ## Common Issues & Troubleshooting
311 | 
312 | ### "Server not initialized" Error
313 | **Cause:** Missing or incorrect session ID  
314 | **Solution:** Ensure you're using the session ID from the initialization response
315 | 
316 | ### "Session not found" Error
317 | **Cause:** Session expired or invalid session ID  
318 | **Solution:** Re-initialize with a new session
319 | 
320 | ### Port Already in Use
321 | **Cause:** Another process is using port 8000  
322 | **Solution:** 
323 | ```bash
324 | # Kill process on port 8000
325 | lsof -ti:8000 | xargs kill -9
326 | 
327 | # Or use a different port
328 | bun run index.ts --port 8001
329 | ```
330 | 
331 | ### API Rate Limiting
332 | **Cause:** Exceeded Brave Search API limits  
333 | **Solution:** The server has built-in rate limiting (1 request/second, 15000/month)
334 | 
335 | ### Connection Timeout
336 | **Cause:** Network issues or server overload  
337 | **Solution:** Check network connectivity and server resources
338 | 
339 | ## Concurrent Connection Management
340 | 
341 | ### How It Works
342 | - Each client gets its own server instance and transport
343 | - Sessions are isolated - no shared state between clients
344 | - Automatic cleanup when clients disconnect
345 | - Memory-efficient session storage using Maps
346 | 
347 | ### Scaling Considerations
348 | ```typescript
349 | // Current session storage (in-memory)
350 | const streamableSessions = new Map<string, {transport: any, server: any}>();
351 | ```
352 | 
353 | **For production:**
354 | - Consider Redis for session storage across multiple instances
355 | - Implement session cleanup timeouts
356 | - Monitor memory usage for session maps
357 | - Use load balancers for horizontal scaling
358 | 
359 | ### Connection Limits
360 | - Default: No explicit connection limit
361 | - Memory-bound by available system resources
362 | - Each session uses ~1-5MB of memory
363 | 
364 | ## Production Deployment
365 | 
366 | ### Environment Variables
367 | ```bash
368 | export BRAVE_API_KEY="your-production-api-key"
369 | export PORT="8000"
370 | export NODE_ENV="production"
371 | ```
372 | 
373 | ### Process Management
374 | ```bash
375 | # Using PM2 for process management
376 | npm install -g pm2
377 | pm2 start "bun run index.ts --port 8000" --name brave-search-mcp
378 | ```
379 | 
380 | ### Docker Deployment
381 | ```dockerfile
382 | FROM oven/bun:latest
383 | WORKDIR /app
384 | COPY package.json bun.lockb ./
385 | RUN bun install
386 | COPY . .
387 | EXPOSE 8000
388 | CMD ["bun", "run", "index.ts", "--port", "8000"]
389 | ```
390 | 
391 | ### AWS Lambda Deployment
392 | The server supports Streamable HTTP, making it suitable for serverless deployment:
393 | - Configure API Gateway to proxy requests to `/mcp`
394 | - Set appropriate timeout values (30s+)
395 | - Handle cold starts gracefully
396 | 
397 | ## Security Best Practices
398 | 
399 | ### API Key Security
400 | - Use environment variables, never hardcode keys
401 | - Rotate API keys regularly
402 | - Monitor API usage and set alerts
403 | 
404 | ### Network Security
405 | - Bind to localhost (`127.0.0.1`) for local development
406 | - Use HTTPS in production
407 | - Implement proper authentication for public deployments
408 | 
409 | ### Input Validation
410 | - The server validates JSON-RPC message format
411 | - Search queries are limited to 400 characters
412 | - Count parameters are bounded (1-20 results)
413 | 
414 | ## Monitoring & Logging
415 | 
416 | ### Built-in Logging
417 | The server logs:
418 | - Session creation/destruction
419 | - API errors and rate limiting
420 | - Connection events
421 | 
422 | ### Health Checks
423 | ```bash
424 | # Simple health check
425 | curl -f http://localhost:8000/mcp || echo "Server down"
426 | ```
427 | 
428 | ### Metrics to Monitor
429 | - Active session count
430 | - API call frequency
431 | - Response times
432 | - Error rates
433 | - Memory usage
434 | 
435 | ## Advanced Configuration
436 | 
437 | ### Custom Rate Limiting
438 | ```typescript
439 | const RATE_LIMIT = {
440 |   perSecond: 1,     // Requests per second
441 |   perMonth: 15000   // Monthly request limit
442 | };
443 | ```
444 | 
445 | ### Timeout Configuration
446 | ```typescript
447 | // Adjust in createServerInstance() if needed
448 | const serverInstance = new Server({
449 |   name: "brave-search",
450 |   version: "1.0.0"
451 | }, {
452 |   capabilities: { tools: {} },
453 |   // Add timeout configs here
454 | });
455 | ```
456 | 
457 | ## Support & Further Reading
458 | 
459 | - [MCP Specification](https://modelcontextprotocol.io/specification/draft/)
460 | - [Brave Search API Documentation](https://api.search.brave.com/app/documentation)
461 | - [Bun Documentation](https://bun.sh/docs)
462 | 
463 | This server is now ready for production use and can handle multiple concurrent connections efficiently while providing reliable Brave Search functionality through the MCP protocol.
464 | 


--------------------------------------------------------------------------------
/package.json:
--------------------------------------------------------------------------------
 1 | {
 2 |   "name": "@windsornguyen/brave-search-mcp",
 3 |   "version": "0.1.0",
 4 |   "description": "A Model Context Protocol server for web and local search using the Brave Search API",
 5 |   "private": false,
 6 |   "type": "module",
 7 |   "bin": {
 8 |     "brave-search-mcp": "./dist/index.js"
 9 |   },
10 |   "files": [
11 |     "dist"
12 |   ],
13 |   "scripts": {
14 |     "build": "tsc && node -e \"require('fs').chmodSync('dist/index.js', '755')\"",
15 |     "start": "node dist/index.js --port 3002",
16 |     "dev:stdio": "tsx src/index.ts",
17 |     "dev:shttp": "tsx src/index.ts --port 3002",
18 |     "prepare": "bun run build",
19 |     "watch": "tsc --watch",
20 |     "inspector": "npx @modelcontextprotocol/inspector dist/index.js"
21 |   },
22 |   "repository": {
23 |     "type": "git",
24 |     "url": "git+https://github.com/windsornguyen/brave-search-mcp.git"
25 |   },
26 |   "keywords": [
27 |     "mcp",
28 |     "brave-search",
29 |     "web-search",
30 |     "local-search",
31 |     "search-api"
32 |   ],
33 |   "author": {
34 |     "name": "Windsor Nguyen",
35 |     "url": "https://windsornguyen.com"
36 |   },
37 |   "license": "MIT",
38 |   "bugs": {
39 |     "url": "https://github.com/windsornguyen/brave-search-mcp/issues"
40 |   },
41 |   "homepage": "https://github.com/windsornguyen/brave-search-mcp#readme",
42 |   "dependencies": {
43 |     "@modelcontextprotocol/sdk": "1.16.0",
44 |     "@playwright/test": "^1.54.2",
45 |     "axios": "^1.11.0",
46 |     "dotenv": "^17.2.1"
47 |   },
48 |   "devDependencies": {
49 |     "@types/node": "^24.2.0",
50 |     "tsx": "^4.20.3",
51 |     "typescript": "^5.9.2"
52 |   }
53 | }
54 | 


--------------------------------------------------------------------------------
/src/cli.ts:
--------------------------------------------------------------------------------
 1 | /**
 2 |  * Command-line options interface
 3 |  * @interface CliOptions
 4 |  */
 5 | export interface CliOptions {
 6 |     /** Optional port override for HTTP server */
 7 |     port?: number;
 8 |     /** Force STDIO transport mode */
 9 |     stdio?: boolean;
10 | }
11 | 
12 | /**
13 |  * Parses command-line arguments
14 |  * @returns {CliOptions} Parsed CLI options
15 |  * @example
16 |  * // node index.js --port 3002
17 |  * // Returns: { port: 3002 }
18 |  * @example
19 |  * // node index.js --stdio
20 |  * // Returns: { stdio: true }
21 |  */
22 | export function parseArgs(): CliOptions {
23 |     const args = process.argv.slice(2);
24 |     const options: CliOptions = {};
25 | 
26 |     for (let i = 0; i < args.length; i++) {
27 |         switch (args[i]) {
28 |             case '--port':
29 |                 if (i + 1 < args.length) {
30 |                     options.port = parseInt(args[++i], 10);
31 |                 }
32 |                 break;
33 |             case '--stdio':
34 |                 options.stdio = true;
35 |                 break;
36 |         }
37 |     }
38 | 
39 |     return options;
40 | }


--------------------------------------------------------------------------------
/src/client.ts:
--------------------------------------------------------------------------------
  1 | import {
  2 |     RateLimit,
  3 |     RequestCount,
  4 |     BraveWeb,
  5 |     BravePoiResponse,
  6 |     BraveDescription,
  7 |     BraveLocation
  8 | } from './types.js';
  9 | 
 10 | /**
 11 |  * Client for interacting with the Brave Search API
 12 |  * @class BraveClient
 13 |  */
 14 | export class BraveClient {
 15 |     private readonly apiKey: string;
 16 |     private readonly rateLimit: RateLimit = {
 17 |         perSecond: 1,
 18 |         perMonth: 15000
 19 |     };
 20 |     private requestCount: RequestCount = {
 21 |         second: 0,
 22 |         month: 0,
 23 |         lastReset: Date.now()
 24 |     };
 25 | 
 26 |     /**
 27 |      * Creates a new BraveClient instance
 28 |      * @param {string} apiKey - Brave API key for authentication
 29 |      */
 30 |     constructor(apiKey: string) {
 31 |         if (!apiKey) {
 32 |             throw new Error('API key is required');
 33 |         }
 34 |         this.apiKey = apiKey;
 35 |     }
 36 | 
 37 |     /**
 38 |      * Checks and enforces rate limiting
 39 |      * @throws {Error} If rate limit is exceeded
 40 |      * @private
 41 |      */
 42 |     private checkRateLimit(): void {
 43 |         const now = Date.now();
 44 |         if (now - this.requestCount.lastReset > 1000) {
 45 |             this.requestCount.second = 0;
 46 |             this.requestCount.lastReset = now;
 47 |         }
 48 |         if (this.requestCount.second >= this.rateLimit.perSecond ||
 49 |             this.requestCount.month >= this.rateLimit.perMonth) {
 50 |             throw new Error('Rate limit exceeded');
 51 |         }
 52 |         this.requestCount.second++;
 53 |         this.requestCount.month++;
 54 |     }
 55 | 
 56 |     /**
 57 |      * Performs a web search using Brave's Web Search API
 58 |      * @param {string} query - Search query
 59 |      * @param {number} count - Number of results to return (default: 10, max: 20)
 60 |      * @param {number} offset - Pagination offset (default: 0, max: 9)
 61 |      * @returns {Promise<string>} Formatted search results
 62 |      */
 63 |     async performWebSearch(query: string, count: number = 10, offset: number = 0): Promise<string> {
 64 |         this.checkRateLimit();
 65 |         const url = new URL('https://api.search.brave.com/res/v1/web/search');
 66 |         url.searchParams.set('q', query);
 67 |         url.searchParams.set('count', Math.min(count, 20).toString());
 68 |         url.searchParams.set('offset', offset.toString());
 69 | 
 70 |         const response = await fetch(url, {
 71 |             headers: {
 72 |                 'Accept': 'application/json',
 73 |                 'Accept-Encoding': 'gzip',
 74 |                 'X-Subscription-Token': this.apiKey
 75 |             }
 76 |         });
 77 | 
 78 |         if (!response.ok) {
 79 |             throw new Error(`Brave API error: ${response.status} ${response.statusText}\n${await response.text()}`);
 80 |         }
 81 | 
 82 |         const data = await response.json() as BraveWeb;
 83 | 
 84 |         // Extract web results
 85 |         const results = (data.web?.results || []).map(result => ({
 86 |             title: result.title || '',
 87 |             description: result.description || '',
 88 |             url: result.url || ''
 89 |         }));
 90 | 
 91 |         return results.map(r =>
 92 |             `Title: ${r.title}\nDescription: ${r.description}\nURL: ${r.url}`
 93 |         ).join('\n\n');
 94 |     }
 95 | 
 96 |     /**
 97 |      * Performs a local search using Brave's Local Search API
 98 |      * @param {string} query - Local search query
 99 |      * @param {number} count - Number of results to return (default: 5, max: 20)
100 |      * @returns {Promise<string>} Formatted local search results
101 |      */
102 |     async performLocalSearch(query: string, count: number = 5): Promise<string> {
103 |         this.checkRateLimit();
104 |         
105 |         // Initial search to get location IDs
106 |         const webUrl = new URL('https://api.search.brave.com/res/v1/web/search');
107 |         webUrl.searchParams.set('q', query);
108 |         webUrl.searchParams.set('search_lang', 'en');
109 |         webUrl.searchParams.set('result_filter', 'locations');
110 |         webUrl.searchParams.set('count', Math.min(count, 20).toString());
111 | 
112 |         const webResponse = await fetch(webUrl, {
113 |             headers: {
114 |                 'Accept': 'application/json',
115 |                 'Accept-Encoding': 'gzip',
116 |                 'X-Subscription-Token': this.apiKey
117 |             }
118 |         });
119 | 
120 |         if (!webResponse.ok) {
121 |             throw new Error(`Brave API error: ${webResponse.status} ${webResponse.statusText}\n${await webResponse.text()}`);
122 |         }
123 | 
124 |         const webData = await webResponse.json() as BraveWeb;
125 |         const locationIds = webData.locations?.results?.filter((r): r is { id: string; title?: string } => r.id != null).map(r => r.id) || [];
126 | 
127 |         if (locationIds.length === 0) {
128 |             return this.performWebSearch(query, count); // Fallback to web search
129 |         }
130 | 
131 |         // Get POI details and descriptions in parallel
132 |         const [poisData, descriptionsData] = await Promise.all([
133 |             this.getPoisData(locationIds),
134 |             this.getDescriptionsData(locationIds)
135 |         ]);
136 | 
137 |         return this.formatLocalResults(poisData, descriptionsData);
138 |     }
139 | 
140 |     /**
141 |      * Fetches POI (Points of Interest) data for given location IDs
142 |      * @param {string[]} ids - Array of location IDs
143 |      * @returns {Promise<BravePoiResponse>} POI data response
144 |      * @private
145 |      */
146 |     private async getPoisData(ids: string[]): Promise<BravePoiResponse> {
147 |         this.checkRateLimit();
148 |         const url = new URL('https://api.search.brave.com/res/v1/local/pois');
149 |         ids.filter(Boolean).forEach(id => url.searchParams.append('ids', id));
150 |         
151 |         const response = await fetch(url, {
152 |             headers: {
153 |                 'Accept': 'application/json',
154 |                 'Accept-Encoding': 'gzip',
155 |                 'X-Subscription-Token': this.apiKey
156 |             }
157 |         });
158 | 
159 |         if (!response.ok) {
160 |             throw new Error(`Brave API error: ${response.status} ${response.statusText}\n${await response.text()}`);
161 |         }
162 | 
163 |         return await response.json() as BravePoiResponse;
164 |     }
165 | 
166 |     /**
167 |      * Fetches description data for given location IDs
168 |      * @param {string[]} ids - Array of location IDs
169 |      * @returns {Promise<BraveDescription>} Descriptions data response
170 |      * @private
171 |      */
172 |     private async getDescriptionsData(ids: string[]): Promise<BraveDescription> {
173 |         this.checkRateLimit();
174 |         const url = new URL('https://api.search.brave.com/res/v1/local/descriptions');
175 |         ids.filter(Boolean).forEach(id => url.searchParams.append('ids', id));
176 |         
177 |         const response = await fetch(url, {
178 |             headers: {
179 |                 'Accept': 'application/json',
180 |                 'Accept-Encoding': 'gzip',
181 |                 'X-Subscription-Token': this.apiKey
182 |             }
183 |         });
184 | 
185 |         if (!response.ok) {
186 |             throw new Error(`Brave API error: ${response.status} ${response.statusText}\n${await response.text()}`);
187 |         }
188 | 
189 |         return await response.json() as BraveDescription;
190 |     }
191 | 
192 |     /**
193 |      * Formats local search results for display
194 |      * @param {BravePoiResponse} poisData - POI data
195 |      * @param {BraveDescription} descData - Descriptions data
196 |      * @returns {string} Formatted results string
197 |      * @private
198 |      */
199 |     private formatLocalResults(poisData: BravePoiResponse, descData: BraveDescription): string {
200 |         return (poisData.results || []).map(poi => {
201 |             const address = [
202 |                 poi.address?.streetAddress ?? '',
203 |                 poi.address?.addressLocality ?? '',
204 |                 poi.address?.addressRegion ?? '',
205 |                 poi.address?.postalCode ?? ''
206 |             ].filter(part => part !== '').join(', ') || 'N/A';
207 | 
208 |             return `Name: ${poi.name}
209 | Address: ${address}
210 | Phone: ${poi.phone || 'N/A'}
211 | Rating: ${poi.rating?.ratingValue ?? 'N/A'} (${poi.rating?.ratingCount ?? 0} reviews)
212 | Price Range: ${poi.priceRange || 'N/A'}
213 | Hours: ${(poi.openingHours || []).join(', ') || 'N/A'}
214 | Description: ${descData.descriptions[poi.id] || 'No description available'}
215 | `;
216 |         }).join('\n---\n') || 'No local results found';
217 |     }
218 | }


--------------------------------------------------------------------------------
/src/config.ts:
--------------------------------------------------------------------------------
 1 | /**
 2 |  * Configuration interface for the Brave Search MCP Server
 3 |  * @interface Config
 4 |  */
 5 | export interface Config {
 6 |     /** Brave API key for authentication */
 7 |     apiKey: string;
 8 |     /** Port number for HTTP server */
 9 |     port: number;
10 |     /** Current environment mode */
11 |     nodeEnv: 'development' | 'production';
12 |     /** Convenience flag for production environment */
13 |     isProduction: boolean;
14 | }
15 | 
16 | /**
17 |  * Loads and validates configuration from environment variables
18 |  * @returns {Config} Validated configuration object
19 |  * @throws {Error} If required environment variables are missing
20 |  */
21 | export function loadConfig(): Config {
22 |     const apiKey = process.env.BRAVE_API_KEY;
23 |     if (!apiKey) {
24 |         throw new Error('BRAVE_API_KEY environment variable is required');
25 |     }
26 | 
27 |     const nodeEnv = process.env.NODE_ENV === 'production' ? 'production' : 'development';
28 |     const port = parseInt(process.env.PORT || '3002', 10);
29 | 
30 |     return {
31 |         apiKey,
32 |         port,
33 |         nodeEnv,
34 |         isProduction: nodeEnv === 'production',
35 |     };
36 | }


--------------------------------------------------------------------------------
/src/index.ts:
--------------------------------------------------------------------------------
 1 | #!/usr/bin/env node
 2 | 
 3 | import { config as loadEnv } from 'dotenv';
 4 | 
 5 | // Load environment variables
 6 | loadEnv();
 7 | 
 8 | import { loadConfig } from './config.js';
 9 | import { parseArgs } from './cli.js';
10 | import { BraveServer } from './server.js';
11 | import { runStdioTransport, startHttpTransport } from './transport/index.js';
12 | 
13 | /**
14 |  * Main entry point for the Brave Search MCP Server
15 |  * 
16 |  * Transport selection logic:
17 |  * 1. --stdio flag forces STDIO transport
18 |  * 2. --port flag or PORT env var triggers HTTP transport
19 |  * 3. Default: STDIO for local development
20 |  */
21 | async function main() {
22 |     try {
23 |         const config = loadConfig();
24 |         const cliOptions = parseArgs();
25 |         
26 |         // Determine transport mode
27 |         const shouldUseHttp = cliOptions.port || (process.env.PORT && !cliOptions.stdio);
28 |         const port = cliOptions.port || config.port;
29 |         
30 |         if (shouldUseHttp) {
31 |             // HTTP transport for production/cloud deployment
32 |             startHttpTransport({ ...config, port });
33 |         } else {
34 |             // STDIO transport for local development
35 |             const server = new BraveServer(config.apiKey);
36 |             await runStdioTransport(server.getServer());
37 |         }
38 |     } catch (error) {
39 |         console.error("Fatal error running Brave Search server:", error);
40 |         process.exit(1);
41 |     }
42 | }
43 | 
44 | // Run the server
45 | main();
46 | 


--------------------------------------------------------------------------------
/src/server.ts:
--------------------------------------------------------------------------------
  1 | import { Server } from '@modelcontextprotocol/sdk/server/index.js';
  2 | import {
  3 |     CallToolRequestSchema,
  4 |     ErrorCode,
  5 |     ListToolsRequestSchema,
  6 |     McpError,
  7 | } from '@modelcontextprotocol/sdk/types.js';
  8 | import { BraveClient } from './client.js';
  9 | import {
 10 |     webSearchToolDefinition,
 11 |     localSearchToolDefinition,
 12 |     handleWebSearchTool,
 13 |     handleLocalSearchTool
 14 | } from './tools/index.js';
 15 | 
 16 | /**
 17 |  * Main server class for Brave Search MCP integration
 18 |  * @class BraveServer
 19 |  */
 20 | export class BraveServer {
 21 |     private client: BraveClient;
 22 |     private server: Server;
 23 | 
 24 |     /**
 25 |      * Creates a new BraveServer instance
 26 |      * @param {string} apiKey - Brave API key for authentication
 27 |      */
 28 |     constructor(apiKey: string) {
 29 |         this.client = new BraveClient(apiKey);
 30 |         this.server = new Server(
 31 |             {
 32 |                 name: 'brave-search',
 33 |                 version: '0.1.0',
 34 |             },
 35 |             {
 36 |                 capabilities: {
 37 |                     tools: {},
 38 |                 },
 39 |             }
 40 |         );
 41 | 
 42 |         this.setupHandlers();
 43 |         this.setupErrorHandling();
 44 |     }
 45 | 
 46 |     /**
 47 |      * Sets up MCP request handlers for tools
 48 |      * @private
 49 |      */
 50 |     private setupHandlers(): void {
 51 |         // List available tools
 52 |         this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
 53 |             tools: [webSearchToolDefinition, localSearchToolDefinition],
 54 |         }));
 55 | 
 56 |         // Handle tool calls
 57 |         this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
 58 |             const { name, arguments: args } = request.params;
 59 | 
 60 |             switch (name) {
 61 |                 case 'brave_web_search':
 62 |                     return handleWebSearchTool(this.client, args);
 63 |                 
 64 |                 case 'brave_local_search':
 65 |                     return handleLocalSearchTool(this.client, args);
 66 |                 
 67 |                 default:
 68 |                     throw new McpError(
 69 |                         ErrorCode.MethodNotFound,
 70 |                         `Unknown tool: ${name}`
 71 |                     );
 72 |             }
 73 |         });
 74 |     }
 75 | 
 76 |     /**
 77 |      * Configures error handling and graceful shutdown
 78 |      * @private
 79 |      */
 80 |     private setupErrorHandling(): void {
 81 |         this.server.onerror = (error) => console.error('[MCP Error]', error);
 82 |         
 83 |         process.on('SIGINT', async () => {
 84 |             await this.server.close();
 85 |             process.exit(0);
 86 |         });
 87 |     }
 88 | 
 89 |     /**
 90 |      * Returns the underlying MCP server instance
 91 |      * @returns {Server} MCP server instance
 92 |      */
 93 |     getServer(): Server {
 94 |         return this.server;
 95 |     }
 96 | }
 97 | 
 98 | /**
 99 |  * Factory function for creating standalone server instances
100 |  * Used by HTTP transport for session-based connections
101 |  * @param {string} apiKey - Brave API key for authentication
102 |  * @returns {Server} Configured MCP server instance
103 |  */
104 | export function createStandaloneServer(apiKey: string): Server {
105 |     const server = new Server(
106 |         {
107 |             name: "brave-search-discovery",
108 |             version: "0.1.0",
109 |         },
110 |         {
111 |             capabilities: {
112 |                 tools: {},
113 |             },
114 |         },
115 |     );
116 | 
117 |     const client = new BraveClient(apiKey);
118 | 
119 |     // Set up handlers
120 |     server.setRequestHandler(ListToolsRequestSchema, async () => ({
121 |         tools: [webSearchToolDefinition, localSearchToolDefinition],
122 |     }));
123 | 
124 |     server.setRequestHandler(CallToolRequestSchema, async (request) => {
125 |         const { name, arguments: args } = request.params;
126 | 
127 |         switch (name) {
128 |             case 'brave_web_search':
129 |                 return handleWebSearchTool(client, args);
130 |             
131 |             case 'brave_local_search':
132 |                 return handleLocalSearchTool(client, args);
133 |             
134 |             default:
135 |                 throw new McpError(
136 |                     ErrorCode.MethodNotFound,
137 |                     `Unknown tool: ${name}`
138 |                 );
139 |         }
140 |     });
141 | 
142 |     return server;
143 | }


--------------------------------------------------------------------------------
/src/tools/index.ts:
--------------------------------------------------------------------------------
1 | export { 
2 |     webSearchToolDefinition, 
3 |     localSearchToolDefinition, 
4 |     handleWebSearchTool, 
5 |     handleLocalSearchTool 
6 | } from './search.js';


--------------------------------------------------------------------------------
/src/tools/search.ts:
--------------------------------------------------------------------------------
  1 | import { Tool, CallToolResult } from '@modelcontextprotocol/sdk/types.js';
  2 | import { BraveClient } from '../client.js';
  3 | import { WebSearchArgs, LocalSearchArgs } from '../types.js';
  4 | 
  5 | /**
  6 |  * Tool definition for Brave web search
  7 |  */
  8 | export const webSearchToolDefinition: Tool = {
  9 |     name: "brave_web_search",
 10 |     description:
 11 |         "Performs a web search using the Brave Search API, ideal for general queries, news, articles, and online content. " +
 12 |         "Use this for broad information gathering, recent events, or when you need diverse web sources. " +
 13 |         "Supports pagination, content filtering, and freshness controls. " +
 14 |         "Maximum 20 results per request, with offset for pagination.",
 15 |     inputSchema: {
 16 |         type: "object",
 17 |         properties: {
 18 |             query: {
 19 |                 type: "string",
 20 |                 description: "Search query (max 400 chars, 50 words)"
 21 |             },
 22 |             count: {
 23 |                 type: "number",
 24 |                 description: "Number of results (1-20, default 10)",
 25 |                 default: 10
 26 |             },
 27 |             offset: {
 28 |                 type: "number",
 29 |                 description: "Pagination offset (max 9, default 0)",
 30 |                 default: 0
 31 |             },
 32 |         },
 33 |         required: ["query"],
 34 |     },
 35 | };
 36 | 
 37 | /**
 38 |  * Tool definition for Brave local search
 39 |  */
 40 | export const localSearchToolDefinition: Tool = {
 41 |     name: "brave_local_search",
 42 |     description:
 43 |         "Searches for local businesses and places using Brave's Local Search API. " +
 44 |         "Best for queries related to physical locations, businesses, restaurants, services, etc. " +
 45 |         "Returns detailed information including:\n" +
 46 |         "- Business names and addresses\n" +
 47 |         "- Ratings and review counts\n" +
 48 |         "- Phone numbers and opening hours\n" +
 49 |         "Use this when the query implies 'near me' or mentions specific locations. " +
 50 |         "Automatically falls back to web search if no local results are found.",
 51 |     inputSchema: {
 52 |         type: "object",
 53 |         properties: {
 54 |             query: {
 55 |                 type: "string",
 56 |                 description: "Local search query (e.g. 'pizza near Central Park')"
 57 |             },
 58 |             count: {
 59 |                 type: "number",
 60 |                 description: "Number of results (1-20, default 5)",
 61 |                 default: 5
 62 |             },
 63 |         },
 64 |         required: ["query"]
 65 |     }
 66 | };
 67 | 
 68 | /**
 69 |  * Type guard for web search arguments
 70 |  * @param {unknown} args - Arguments to validate
 71 |  * @returns {boolean} True if arguments are valid for web search
 72 |  */
 73 | function isWebSearchArgs(args: unknown): args is WebSearchArgs {
 74 |     return (
 75 |         typeof args === "object" &&
 76 |         args !== null &&
 77 |         "query" in args &&
 78 |         typeof (args as { query: string }).query === "string"
 79 |     );
 80 | }
 81 | 
 82 | /**
 83 |  * Type guard for local search arguments
 84 |  * @param {unknown} args - Arguments to validate
 85 |  * @returns {boolean} True if arguments are valid for local search
 86 |  */
 87 | function isLocalSearchArgs(args: unknown): args is LocalSearchArgs {
 88 |     return (
 89 |         typeof args === "object" &&
 90 |         args !== null &&
 91 |         "query" in args &&
 92 |         typeof (args as { query: string }).query === "string"
 93 |     );
 94 | }
 95 | 
 96 | /**
 97 |  * Handles web search tool calls
 98 |  * @param {BraveClient} client - Brave API client instance
 99 |  * @param {unknown} args - Tool call arguments
100 |  * @returns {Promise<CallToolResult>} Tool call result
101 |  */
102 | export async function handleWebSearchTool(client: BraveClient, args: unknown): Promise<CallToolResult> {
103 |     try {
104 |         if (!args) {
105 |             throw new Error("No arguments provided");
106 |         }
107 | 
108 |         if (!isWebSearchArgs(args)) {
109 |             throw new Error("Invalid arguments for brave_web_search");
110 |         }
111 | 
112 |         const { query, count = 10, offset = 0 } = args;
113 |         const results = await client.performWebSearch(query, count, offset);
114 |         
115 |         return {
116 |             content: [{ type: "text", text: results }],
117 |             isError: false,
118 |         };
119 |     } catch (error) {
120 |         return {
121 |             content: [
122 |                 {
123 |                     type: "text",
124 |                     text: `Error: ${error instanceof Error ? error.message : String(error)}`,
125 |                 },
126 |             ],
127 |             isError: true,
128 |         };
129 |     }
130 | }
131 | 
132 | /**
133 |  * Handles local search tool calls
134 |  * @param {BraveClient} client - Brave API client instance
135 |  * @param {unknown} args - Tool call arguments
136 |  * @returns {Promise<CallToolResult>} Tool call result
137 |  */
138 | export async function handleLocalSearchTool(client: BraveClient, args: unknown): Promise<CallToolResult> {
139 |     try {
140 |         if (!args) {
141 |             throw new Error("No arguments provided");
142 |         }
143 | 
144 |         if (!isLocalSearchArgs(args)) {
145 |             throw new Error("Invalid arguments for brave_local_search");
146 |         }
147 | 
148 |         const { query, count = 5 } = args;
149 |         const results = await client.performLocalSearch(query, count);
150 |         
151 |         return {
152 |             content: [{ type: "text", text: results }],
153 |             isError: false,
154 |         };
155 |     } catch (error) {
156 |         return {
157 |             content: [
158 |                 {
159 |                     type: "text",
160 |                     text: `Error: ${error instanceof Error ? error.message : String(error)}`,
161 |                 },
162 |             ],
163 |             isError: true,
164 |         };
165 |     }
166 | }
167 | 


--------------------------------------------------------------------------------
/src/transport/http.ts:
--------------------------------------------------------------------------------
  1 | import { createServer, IncomingMessage, ServerResponse } from 'http';
  2 | import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
  3 | import { randomUUID } from 'crypto';
  4 | import { createStandaloneServer } from '../server.js';
  5 | import { Config } from '../config.js';
  6 | 
  7 | /** Session storage for streamable HTTP connections */
  8 | const sessions = new Map<string, { transport: StreamableHTTPServerTransport; server: any }>();
  9 | 
 10 | /**
 11 |  * Starts the HTTP transport server
 12 |  * @param {Config} config - Server configuration
 13 |  */
 14 | export function startHttpTransport(config: Config): void {
 15 |     const httpServer = createServer();
 16 | 
 17 |     httpServer.on('request', async (req, res) => {
 18 |         const url = new URL(req.url!, `http://${req.headers.host}`);
 19 | 
 20 |         switch (url.pathname) {
 21 |             case '/mcp':
 22 |                 await handleMcpRequest(req, res, config);
 23 |                 break;
 24 |             case '/health':
 25 |                 handleHealthCheck(res);
 26 |                 break;
 27 |             default:
 28 |                 handleNotFound(res);
 29 |         }
 30 |     });
 31 | 
 32 |     const host = config.isProduction ? '0.0.0.0' : 'localhost';
 33 |     
 34 |     httpServer.listen(config.port, host, () => {
 35 |         logServerStart(config);
 36 |     });
 37 | }
 38 | 
 39 | /**
 40 |  * Handles MCP protocol requests
 41 |  * @param {IncomingMessage} req - HTTP request
 42 |  * @param {ServerResponse} res - HTTP response
 43 |  * @param {Config} config - Server configuration
 44 |  * @returns {Promise<void>}
 45 |  * @private
 46 |  */
 47 | async function handleMcpRequest(
 48 |     req: IncomingMessage,
 49 |     res: ServerResponse,
 50 |     config: Config
 51 | ): Promise<void> {
 52 |     const sessionId = req.headers['mcp-session-id'] as string | undefined;
 53 | 
 54 |     if (sessionId) {
 55 |         const session = sessions.get(sessionId);
 56 |         if (!session) {
 57 |             res.statusCode = 404;
 58 |             res.end('Session not found');
 59 |             return;
 60 |         }
 61 |         return await session.transport.handleRequest(req, res);
 62 |     }
 63 | 
 64 |     if (req.method === 'POST') {
 65 |         await createNewSession(req, res, config);
 66 |         return;
 67 |     }
 68 | 
 69 |     res.statusCode = 400;
 70 |     res.end('Invalid request');
 71 | }
 72 | 
 73 | /**
 74 |  * Creates a new MCP session for HTTP transport
 75 |  * @param {IncomingMessage} req - HTTP request
 76 |  * @param {ServerResponse} res - HTTP response
 77 |  * @param {Config} config - Server configuration
 78 |  * @returns {Promise<void>}
 79 |  * @private
 80 |  */
 81 | async function createNewSession(
 82 |     req: IncomingMessage,
 83 |     res: ServerResponse,
 84 |     config: Config
 85 | ): Promise<void> {
 86 |     const serverInstance = createStandaloneServer(config.apiKey);
 87 |     const transport = new StreamableHTTPServerTransport({
 88 |         sessionIdGenerator: () => randomUUID(),
 89 |         onsessioninitialized: (sessionId) => {
 90 |             sessions.set(sessionId, { transport, server: serverInstance });
 91 |             console.log('New Brave Search session created:', sessionId);
 92 |         }
 93 |     });
 94 | 
 95 |     transport.onclose = () => {
 96 |         if (transport.sessionId) {
 97 |             sessions.delete(transport.sessionId);
 98 |             console.log('Brave Search session closed:', transport.sessionId);
 99 |         }
100 |     };
101 | 
102 |     try {
103 |         await serverInstance.connect(transport);
104 |         await transport.handleRequest(req, res);
105 |     } catch (error) {
106 |         console.error('Streamable HTTP connection error:', error);
107 |         res.statusCode = 500;
108 |         res.end('Internal server error');
109 |     }
110 | }
111 | 
112 | /**
113 |  * Handles health check endpoint
114 |  * @param {ServerResponse} res - HTTP response
115 |  * @private
116 |  */
117 | function handleHealthCheck(res: ServerResponse): void {
118 |     res.writeHead(200, { 'Content-Type': 'application/json' });
119 |     res.end(JSON.stringify({ 
120 |         status: 'healthy', 
121 |         timestamp: new Date().toISOString() 
122 |     }));
123 | }
124 | 
125 | /**
126 |  * Handles 404 Not Found responses
127 |  * @param {ServerResponse} res - HTTP response
128 |  * @private
129 |  */
130 | function handleNotFound(res: ServerResponse): void {
131 |     res.writeHead(404, { 'Content-Type': 'text/plain' });
132 |     res.end('Not Found');
133 | }
134 | 
135 | /**
136 |  * Logs server startup information
137 |  * @param {Config} config - Server configuration
138 |  * @private
139 |  */
140 | function logServerStart(config: Config): void {
141 |     const displayUrl = config.isProduction 
142 |         ? `Port ${config.port}` 
143 |         : `http://localhost:${config.port}`;
144 |     
145 |     console.log(`Brave Search MCP Server listening on ${displayUrl}`);
146 | 
147 |     if (!config.isProduction) {
148 |         console.log('Put this in your client config:');
149 |         console.log(JSON.stringify({
150 |             "mcpServers": {
151 |                 "brave-search": {
152 |                     "url": `http://localhost:${config.port}/mcp`
153 |                 }
154 |             }
155 |         }, null, 2));
156 |     }
157 | }


--------------------------------------------------------------------------------
/src/transport/index.ts:
--------------------------------------------------------------------------------
1 | export { runStdioTransport } from './stdio.js';
2 | export { startHttpTransport } from './http.js';


--------------------------------------------------------------------------------
/src/transport/stdio.ts:
--------------------------------------------------------------------------------
 1 | import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
 2 | import { Server } from '@modelcontextprotocol/sdk/server/index.js';
 3 | 
 4 | /**
 5 |  * Runs the MCP server using STDIO transport
 6 |  * Used for local development and debugging
 7 |  * @param {Server} server - MCP server instance to connect
 8 |  * @returns {Promise<void>}
 9 |  */
10 | export async function runStdioTransport(server: Server): Promise<void> {
11 |     const transport = new StdioServerTransport();
12 |     await server.connect(transport);
13 |     console.error('Brave Search MCP server running on stdio');
14 | }


--------------------------------------------------------------------------------
/src/types.ts:
--------------------------------------------------------------------------------
  1 | /**
  2 |  * Type definitions for Brave Search API integration
  3 |  */
  4 | 
  5 | /**
  6 |  * Rate limiting configuration
  7 |  * @interface RateLimit
  8 |  */
  9 | export interface RateLimit {
 10 |     /** Requests per second */
 11 |     perSecond: number;
 12 |     /** Requests per month */
 13 |     perMonth: number;
 14 | }
 15 | 
 16 | /**
 17 |  * Rate limiting state tracking
 18 |  * @interface RequestCount
 19 |  */
 20 | export interface RequestCount {
 21 |     /** Current second count */
 22 |     second: number;
 23 |     /** Current month count */
 24 |     month: number;
 25 |     /** Last reset timestamp */
 26 |     lastReset: number;
 27 | }
 28 | 
 29 | /**
 30 |  * Brave Web Search API response structure
 31 |  * @interface BraveWeb
 32 |  */
 33 | export interface BraveWeb {
 34 |     web?: {
 35 |         results?: Array<{
 36 |             title: string;
 37 |             description: string;
 38 |             url: string;
 39 |             language?: string;
 40 |             published?: string;
 41 |             rank?: number;
 42 |         }>;
 43 |     };
 44 |     locations?: {
 45 |         results?: Array<{
 46 |             id: string;
 47 |             title?: string;
 48 |         }>;
 49 |     };
 50 | }
 51 | 
 52 | /**
 53 |  * Brave Local Search location data
 54 |  * @interface BraveLocation
 55 |  */
 56 | export interface BraveLocation {
 57 |     id: string;
 58 |     name: string;
 59 |     address: {
 60 |         streetAddress?: string;
 61 |         addressLocality?: string;
 62 |         addressRegion?: string;
 63 |         postalCode?: string;
 64 |     };
 65 |     coordinates?: {
 66 |         latitude: number;
 67 |         longitude: number;
 68 |     };
 69 |     phone?: string;
 70 |     rating?: {
 71 |         ratingValue?: number;
 72 |         ratingCount?: number;
 73 |     };
 74 |     openingHours?: string[];
 75 |     priceRange?: string;
 76 | }
 77 | 
 78 | /**
 79 |  * Brave POI (Points of Interest) API response
 80 |  * @interface BravePoiResponse
 81 |  */
 82 | export interface BravePoiResponse {
 83 |     results: BraveLocation[];
 84 | }
 85 | 
 86 | /**
 87 |  * Brave Descriptions API response
 88 |  * @interface BraveDescription
 89 |  */
 90 | export interface BraveDescription {
 91 |     descriptions: { [id: string]: string };
 92 | }
 93 | 
 94 | /**
 95 |  * Web search tool arguments
 96 |  * @interface WebSearchArgs
 97 |  */
 98 | export interface WebSearchArgs {
 99 |     query: string;
100 |     count?: number;
101 |     offset?: number;
102 | }
103 | 
104 | /**
105 |  * Local search tool arguments
106 |  * @interface LocalSearchArgs
107 |  */
108 | export interface LocalSearchArgs {
109 |     query: string;
110 |     count?: number;
111 | }


--------------------------------------------------------------------------------
/tsconfig.json:
--------------------------------------------------------------------------------
 1 | {
 2 |     "compilerOptions": {
 3 |       "target": "ES2022",
 4 |       "module": "ES2022",
 5 |       "moduleResolution": "node",
 6 |       "outDir": "./dist",
 7 |       "rootDir": "./src",
 8 |       "strict": true,
 9 |       "esModuleInterop": true,
10 |       "skipLibCheck": true,
11 |       "forceConsistentCasingInFileNames": true
12 |     },
13 |     "include": [
14 |       "src/**/*.ts"
15 |     ]
16 |   }
17 | 


--------------------------------------------------------------------------------"""

docs = """# MCP TypeScript SDK ![NPM Version](https://img.shields.io/npm/v/%40modelcontextprotocol%2Fsdk) ![MIT licensed](https://img.shields.io/npm/l/%40modelcontextprotocol%2Fsdk)

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quickstart](#quick-start)
- [What is MCP?](#what-is-mcp)
- [Core Concepts](#core-concepts)
  - [Server](#server)
  - [Resources](#resources)
  - [Tools](#tools)
  - [Prompts](#prompts)
  - [Completions](#completions)
  - [Sampling](#sampling)
- [Running Your Server](#running-your-server)
  - [stdio](#stdio)
  - [Streamable HTTP](#streamable-http)
  - [Testing and Debugging](#testing-and-debugging)
- [Examples](#examples)
  - [Echo Server](#echo-server)
  - [SQLite Explorer](#sqlite-explorer)
- [Advanced Usage](#advanced-usage)
  - [Dynamic Servers](#dynamic-servers)
  - [Low-Level Server](#low-level-server)
  - [Writing MCP Clients](#writing-mcp-clients)
  - [Proxy Authorization Requests Upstream](#proxy-authorization-requests-upstream)
  - [Backwards Compatibility](#backwards-compatibility)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Model Context Protocol allows applications to provide context for LLMs in a standardized way, separating the concerns of providing context from the actual LLM interaction. This TypeScript SDK implements the full MCP specification, making it easy to:

- Build MCP clients that can connect to any MCP server
- Create MCP servers that expose resources, prompts and tools
- Use standard transports like stdio and Streamable HTTP
- Handle all MCP protocol messages and lifecycle events

## Installation

```bash
npm install @modelcontextprotocol/sdk
```

> ⚠️ MCP requires Node.js v18.x or higher to work fine.

## Quick Start

Let's create a simple MCP server that exposes a calculator tool and some data:

```typescript
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create an MCP server
const server = new McpServer({
  name: "demo-server",
  version: "1.0.0"
});

// Add an addition tool
server.registerTool("add",
  {
    title: "Addition Tool",
    description: "Add two numbers",
    inputSchema: { a: z.number(), b: z.number() }
  },
  async ({ a, b }) => ({
    content: [{ type: "text", text: String(a + b) }]
  })
);

// Add a dynamic greeting resource
server.registerResource(
  "greeting",
  new ResourceTemplate("greeting://{name}", { list: undefined }),
  { 
    title: "Greeting Resource",      // Display name for UI
    description: "Dynamic greeting generator"
  },
  async (uri, { name }) => ({
    contents: [{
      uri: uri.href,
      text: `Hello, ${name}!`
    }]
  })
);

// Start receiving messages on stdin and sending messages on stdout
const transport = new StdioServerTransport();
await server.connect(transport);
```

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) lets you build servers that expose data and functionality to LLM applications in a secure, standardized way. Think of it like a web API, but specifically designed for LLM interactions. MCP servers can:

- Expose data through **Resources** (think of these sort of like GET endpoints; they are used to load information into the LLM's context)
- Provide functionality through **Tools** (sort of like POST endpoints; they are used to execute code or otherwise produce a side effect)
- Define interaction patterns through **Prompts** (reusable templates for LLM interactions)
- And more!

## Core Concepts

### Server

The McpServer is your core interface to the MCP protocol. It handles connection management, protocol compliance, and message routing:

```typescript
const server = new McpServer({
  name: "my-app",
  version: "1.0.0"
});
```

### Resources

Resources are how you expose data to LLMs. They're similar to GET endpoints in a REST API - they provide data but shouldn't perform significant computation or have side effects:

```typescript
// Static resource
server.registerResource(
  "config",
  "config://app",
  {
    title: "Application Config",
    description: "Application configuration data",
    mimeType: "text/plain"
  },
  async (uri) => ({
    contents: [{
      uri: uri.href,
      text: "App configuration here"
    }]
  })
);

// Dynamic resource with parameters
server.registerResource(
  "user-profile",
  new ResourceTemplate("users://{userId}/profile", { list: undefined }),
  {
    title: "User Profile",
    description: "User profile information"
  },
  async (uri, { userId }) => ({
    contents: [{
      uri: uri.href,
      text: `Profile data for user ${userId}`
    }]
  })
);

// Resource with context-aware completion
server.registerResource(
  "repository",
  new ResourceTemplate("github://repos/{owner}/{repo}", {
    list: undefined,
    complete: {
      // Provide intelligent completions based on previously resolved parameters
      repo: (value, context) => {
        if (context?.arguments?.["owner"] === "org1") {
          return ["project1", "project2", "project3"].filter(r => r.startsWith(value));
        }
        return ["default-repo"].filter(r => r.startsWith(value));
      }
    }
  }),
  {
    title: "GitHub Repository",
    description: "Repository information"
  },
  async (uri, { owner, repo }) => ({
    contents: [{
      uri: uri.href,
      text: `Repository: ${owner}/${repo}`
    }]
  })
);
```

### Tools

Tools let LLMs take actions through your server. Unlike resources, tools are expected to perform computation and have side effects:

```typescript
// Simple tool with parameters
server.registerTool(
  "calculate-bmi",
  {
    title: "BMI Calculator",
    description: "Calculate Body Mass Index",
    inputSchema: {
      weightKg: z.number(),
      heightM: z.number()
    }
  },
  async ({ weightKg, heightM }) => ({
    content: [{
      type: "text",
      text: String(weightKg / (heightM * heightM))
    }]
  })
);

// Async tool with external API call
server.registerTool(
  "fetch-weather",
  {
    title: "Weather Fetcher",
    description: "Get weather data for a city",
    inputSchema: { city: z.string() }
  },
  async ({ city }) => {
    const response = await fetch(`https://api.weather.com/${city}`);
    const data = await response.text();
    return {
      content: [{ type: "text", text: data }]
    };
  }
);

// Tool that returns ResourceLinks
server.registerTool(
  "list-files",
  {
    title: "List Files",
    description: "List project files",
    inputSchema: { pattern: z.string() }
  },
  async ({ pattern }) => ({
    content: [
      { type: "text", text: `Found files matching "${pattern}":` },
      // ResourceLinks let tools return references without file content
      {
        type: "resource_link",
        uri: "file:///project/README.md",
        name: "README.md",
        mimeType: "text/markdown",
        description: 'A README file'
      },
      {
        type: "resource_link",
        uri: "file:///project/src/index.ts",
        name: "index.ts",
        mimeType: "text/typescript",
        description: 'An index file'
      }
    ]
  })
);
```

#### ResourceLinks

Tools can return `ResourceLink` objects to reference resources without embedding their full content. This is essential for performance when dealing with large files or many resources - clients can then selectively read only the resources they need using the provided URIs.

### Prompts

Prompts are reusable templates that help LLMs interact with your server effectively:

```typescript
import { completable } from "@modelcontextprotocol/sdk/server/completable.js";

server.registerPrompt(
  "review-code",
  {
    title: "Code Review",
    description: "Review code for best practices and potential issues",
    argsSchema: { code: z.string() }
  },
  ({ code }) => ({
    messages: [{
      role: "user",
      content: {
        type: "text",
        text: `Please review this code:\n\n${code}`
      }
    }]
  })
);

// Prompt with context-aware completion
server.registerPrompt(
  "team-greeting",
  {
    title: "Team Greeting",
    description: "Generate a greeting for team members",
    argsSchema: {
      department: completable(z.string(), (value) => {
        // Department suggestions
        return ["engineering", "sales", "marketing", "support"].filter(d => d.startsWith(value));
      }),
      name: completable(z.string(), (value, context) => {
        // Name suggestions based on selected department
        const department = context?.arguments?.["department"];
        if (department === "engineering") {
          return ["Alice", "Bob", "Charlie"].filter(n => n.startsWith(value));
        } else if (department === "sales") {
          return ["David", "Eve", "Frank"].filter(n => n.startsWith(value));
        } else if (department === "marketing") {
          return ["Grace", "Henry", "Iris"].filter(n => n.startsWith(value));
        }
        return ["Guest"].filter(n => n.startsWith(value));
      })
    }
  },
  ({ department, name }) => ({
    messages: [{
      role: "assistant",
      content: {
        type: "text",
        text: `Hello ${name}, welcome to the ${department} team!`
      }
    }]
  })
);
```

### Completions

MCP supports argument completions to help users fill in prompt arguments and resource template parameters. See the examples above for [resource completions](#resources) and [prompt completions](#prompts).

#### Client Usage

```typescript
// Request completions for any argument
const result = await client.complete({
  ref: {
    type: "ref/prompt",  // or "ref/resource"
    name: "example"      // or uri: "template://..."
  },
  argument: {
    name: "argumentName",
    value: "partial"     // What the user has typed so far
  },
  context: {             // Optional: Include previously resolved arguments
    arguments: {
      previousArg: "value"
    }
  }
});

```

### Display Names and Metadata

All resources, tools, and prompts support an optional `title` field for better UI presentation. The `title` is used as a display name, while `name` remains the unique identifier.

**Note:** The `register*` methods (`registerTool`, `registerPrompt`, `registerResource`) are the recommended approach for new code. The older methods (`tool`, `prompt`, `resource`) remain available for backwards compatibility.

#### Title Precedence for Tools

For tools specifically, there are two ways to specify a title:
- `title` field in the tool configuration
- `annotations.title` field (when using the older `tool()` method with annotations)

The precedence order is: `title` → `annotations.title` → `name`

```typescript
// Using registerTool (recommended)
server.registerTool("my_tool", {
  title: "My Tool",              // This title takes precedence
  annotations: {
    title: "Annotation Title"    // This is ignored if title is set
  }
}, handler);

// Using tool with annotations (older API)
server.tool("my_tool", "description", {
  title: "Annotation Title"      // This is used as title
}, handler);
```

When building clients, use the provided utility to get the appropriate display name:

```typescript
import { getDisplayName } from "@modelcontextprotocol/sdk/shared/metadataUtils.js";

// Automatically handles the precedence: title → annotations.title → name
const displayName = getDisplayName(tool);
```

### Sampling

MCP servers can request LLM completions from connected clients that support sampling.

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const mcpServer = new McpServer({
  name: "tools-with-sample-server",
  version: "1.0.0",
});

// Tool that uses LLM sampling to summarize any text
mcpServer.registerTool(
  "summarize",
  {
    description: "Summarize any text using an LLM",
    inputSchema: {
      text: z.string().describe("Text to summarize"),
    },
  },
  async ({ text }) => {
    // Call the LLM through MCP sampling
    const response = await mcpServer.server.createMessage({
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Please summarize the following text concisely:\n\n${text}`,
          },
        },
      ],
      maxTokens: 500,
    });

    return {
      content: [
        {
          type: "text",
          text: response.content.type === "text" ? response.content.text : "Unable to generate summary",
        },
      ],
    };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await mcpServer.connect(transport);
  console.log("MCP server is running...");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
```


## Running Your Server

MCP servers in TypeScript need to be connected to a transport to communicate with clients. How you start the server depends on the choice of transport:

### stdio

For command-line tools and direct integrations:

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({
  name: "example-server",
  version: "1.0.0"
});

// ... set up server resources, tools, and prompts ...

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Streamable HTTP

For remote servers, set up a Streamable HTTP transport that handles both client requests and server-to-client notifications.

#### With Session Management

In some cases, servers need to be stateful. This is achieved by [session management](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#session-management).

```typescript
import express from "express";
import { randomUUID } from "node:crypto";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js"



const app = express();
app.use(express.json());

// Map to store transports by session ID
const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};

// Handle POST requests for client-to-server communication
app.post('/mcp', async (req, res) => {
  // Check for existing session ID
  const sessionId = req.headers['mcp-session-id'] as string | undefined;
  let transport: StreamableHTTPServerTransport;

  if (sessionId && transports[sessionId]) {
    // Reuse existing transport
    transport = transports[sessionId];
  } else if (!sessionId && isInitializeRequest(req.body)) {
    // New initialization request
    transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),
      onsessioninitialized: (sessionId) => {
        // Store the transport by session ID
        transports[sessionId] = transport;
      },
      // DNS rebinding protection is disabled by default for backwards compatibility. If you are running this server
      // locally, make sure to set:
      // enableDnsRebindingProtection: true,
      // allowedHosts: ['127.0.0.1'],
    });

    // Clean up transport when closed
    transport.onclose = () => {
      if (transport.sessionId) {
        delete transports[transport.sessionId];
      }
    };
    const server = new McpServer({
      name: "example-server",
      version: "1.0.0"
    });

    // ... set up server resources, tools, and prompts ...

    // Connect to the MCP server
    await server.connect(transport);
  } else {
    // Invalid request
    res.status(400).json({
      jsonrpc: '2.0',
      error: {
        code: -32000,
        message: 'Bad Request: No valid session ID provided',
      },
      id: null,
    });
    return;
  }

  // Handle the request
  await transport.handleRequest(req, res, req.body);
});

// Reusable handler for GET and DELETE requests
const handleSessionRequest = async (req: express.Request, res: express.Response) => {
  const sessionId = req.headers['mcp-session-id'] as string | undefined;
  if (!sessionId || !transports[sessionId]) {
    res.status(400).send('Invalid or missing session ID');
    return;
  }
  
  const transport = transports[sessionId];
  await transport.handleRequest(req, res);
};

// Handle GET requests for server-to-client notifications via SSE
app.get('/mcp', handleSessionRequest);

// Handle DELETE requests for session termination
app.delete('/mcp', handleSessionRequest);

app.listen(3000);
```

> [!TIP]
> When using this in a remote environment, make sure to allow the header parameter `mcp-session-id` in CORS. Otherwise, it may result in a `Bad Request: No valid session ID provided` error. Read the following section for examples.


#### CORS Configuration for Browser-Based Clients

If you'd like your server to be accessible by browser-based MCP clients, you'll need to configure CORS headers. The `Mcp-Session-Id` header must be exposed for browser clients to access it:

```typescript
import cors from 'cors';

// Add CORS middleware before your MCP routes
app.use(cors({
  origin: '*', // Configure appropriately for production, for example:
  // origin: ['https://your-remote-domain.com', 'https://your-other-remote-domain.com'],
  exposedHeaders: ['Mcp-Session-Id'],
  allowedHeaders: ['Content-Type', 'mcp-session-id'],
}));
```

This configuration is necessary because:
- The MCP streamable HTTP transport uses the `Mcp-Session-Id` header for session management
- Browsers restrict access to response headers unless explicitly exposed via CORS
- Without this configuration, browser-based clients won't be able to read the session ID from initialization responses

#### Without Session Management (Stateless)

For simpler use cases where session management isn't needed:

```typescript
const app = express();
app.use(express.json());

app.post('/mcp', async (req: Request, res: Response) => {
  // In stateless mode, create a new instance of transport and server for each request
  // to ensure complete isolation. A single instance would cause request ID collisions
  // when multiple clients connect concurrently.
  
  try {
    const server = getServer(); 
    const transport: StreamableHTTPServerTransport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
    });
    res.on('close', () => {
      console.log('Request closed');
      transport.close();
      server.close();
    });
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    console.error('Error handling MCP request:', error);
    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: '2.0',
        error: {
          code: -32603,
          message: 'Internal server error',
        },
        id: null,
      });
    }
  }
});

// SSE notifications not supported in stateless mode
app.get('/mcp', async (req: Request, res: Response) => {
  console.log('Received GET MCP request');
  res.writeHead(405).end(JSON.stringify({
    jsonrpc: "2.0",
    error: {
      code: -32000,
      message: "Method not allowed."
    },
    id: null
  }));
});

// Session termination not needed in stateless mode
app.delete('/mcp', async (req: Request, res: Response) => {
  console.log('Received DELETE MCP request');
  res.writeHead(405).end(JSON.stringify({
    jsonrpc: "2.0",
    error: {
      code: -32000,
      message: "Method not allowed."
    },
    id: null
  }));
});


// Start the server
const PORT = 3000;
setupServer().then(() => {
  app.listen(PORT, (error) => {
    if (error) {
      console.error('Failed to start server:', error);
      process.exit(1);
    }
    console.log(`MCP Stateless Streamable HTTP Server listening on port ${PORT}`);
  });
}).catch(error => {
  console.error('Failed to set up the server:', error);
  process.exit(1);
});

```

This stateless approach is useful for:

- Simple API wrappers
- RESTful scenarios where each request is independent
- Horizontally scaled deployments without shared session state

#### DNS Rebinding Protection

The Streamable HTTP transport includes DNS rebinding protection to prevent security vulnerabilities. By default, this protection is **disabled** for backwards compatibility.

**Important**: If you are running this server locally, enable DNS rebinding protection:

```typescript
const transport = new StreamableHTTPServerTransport({
  sessionIdGenerator: () => randomUUID(),
  enableDnsRebindingProtection: true,

  allowedHosts: ['127.0.0.1', ...],
  allowedOrigins: ['https://yourdomain.com', 'https://www.yourdomain.com']
});
```

### Testing and Debugging

To test your server, you can use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector). See its README for more information.

## Examples

### Echo Server

A simple server demonstrating resources, tools, and prompts:

```typescript
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "echo-server",
  version: "1.0.0"
});

server.registerResource(
  "echo",
  new ResourceTemplate("echo://{message}", { list: undefined }),
  {
    title: "Echo Resource",
    description: "Echoes back messages as resources"
  },
  async (uri, { message }) => ({
    contents: [{
      uri: uri.href,
      text: `Resource echo: ${message}`
    }]
  })
);

server.registerTool(
  "echo",
  {
    title: "Echo Tool",
    description: "Echoes back the provided message",
    inputSchema: { message: z.string() }
  },
  async ({ message }) => ({
    content: [{ type: "text", text: `Tool echo: ${message}` }]
  })
);

server.registerPrompt(
  "echo",
  {
    title: "Echo Prompt",
    description: "Creates a prompt to process a message",
    argsSchema: { message: z.string() }
  },
  ({ message }) => ({
    messages: [{
      role: "user",
      content: {
        type: "text",
        text: `Please process this message: ${message}`
      }
    }]
  })
);
```

### SQLite Explorer

A more complex example showing database integration:

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import sqlite3 from "sqlite3";
import { promisify } from "util";
import { z } from "zod";

const server = new McpServer({
  name: "sqlite-explorer",
  version: "1.0.0"
});

// Helper to create DB connection
const getDb = () => {
  const db = new sqlite3.Database("database.db");
  return {
    all: promisify<string, any[]>(db.all.bind(db)),
    close: promisify(db.close.bind(db))
  };
};

server.registerResource(
  "schema",
  "schema://main",
  {
    title: "Database Schema",
    description: "SQLite database schema",
    mimeType: "text/plain"
  },
  async (uri) => {
    const db = getDb();
    try {
      const tables = await db.all(
        "SELECT sql FROM sqlite_master WHERE type='table'"
      );
      return {
        contents: [{
          uri: uri.href,
          text: tables.map((t: {sql: string}) => t.sql).join("\n")
        }]
      };
    } finally {
      await db.close();
    }
  }
);

server.registerTool(
  "query",
  {
    title: "SQL Query",
    description: "Execute SQL queries on the database",
    inputSchema: { sql: z.string() }
  },
  async ({ sql }) => {
    const db = getDb();
    try {
      const results = await db.all(sql);
      return {
        content: [{
          type: "text",
          text: JSON.stringify(results, null, 2)
        }]
      };
    } catch (err: unknown) {
      const error = err as Error;
      return {
        content: [{
          type: "text",
          text: `Error: ${error.message}`
        }],
        isError: true
      };
    } finally {
      await db.close();
    }
  }
);
```

## Advanced Usage

### Dynamic Servers

If you want to offer an initial set of tools/prompts/resources, but later add additional ones based on user action or external state change, you can add/update/remove them _after_ the Server is connected. This will automatically emit the corresponding `listChanged` notifications:

```ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "Dynamic Example",
  version: "1.0.0"
});

const listMessageTool = server.tool(
  "listMessages",
  { channel: z.string() },
  async ({ channel }) => ({
    content: [{ type: "text", text: await listMessages(channel) }]
  })
);

const putMessageTool = server.tool(
  "putMessage",
  { channel: z.string(), message: z.string() },
  async ({ channel, message }) => ({
    content: [{ type: "text", text: await putMessage(channel, message) }]
  })
);
// Until we upgrade auth, `putMessage` is disabled (won't show up in listTools)
putMessageTool.disable()

const upgradeAuthTool = server.tool(
  "upgradeAuth",
  { permission: z.enum(["write", "admin"])},
  // Any mutations here will automatically emit `listChanged` notifications
  async ({ permission }) => {
    const { ok, err, previous } = await upgradeAuthAndStoreToken(permission)
    if (!ok) return {content: [{ type: "text", text: `Error: ${err}` }]}

    // If we previously had read-only access, 'putMessage' is now available
    if (previous === "read") {
      putMessageTool.enable()
    }

    if (permission === 'write') {
      // If we've just upgraded to 'write' permissions, we can still call 'upgradeAuth' 
      // but can only upgrade to 'admin'. 
      upgradeAuthTool.update({
        paramsSchema: { permission: z.enum(["admin"]) }, // change validation rules
      })
    } else {
      // If we're now an admin, we no longer have anywhere to upgrade to, so fully remove that tool
      upgradeAuthTool.remove()
    }
  }
)

// Connect as normal
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Improving Network Efficiency with Notification Debouncing

When performing bulk updates that trigger notifications (e.g., enabling or disabling multiple tools in a loop), the SDK can send a large number of messages in a short period. To improve performance and reduce network traffic, you can enable notification debouncing.

This feature coalesces multiple, rapid calls for the same notification type into a single message. For example, if you disable five tools in a row, only one `notifications/tools/list_changed` message will be sent instead of five.

> [!IMPORTANT]
> This feature is designed for "simple" notifications that do not carry unique data in their parameters. To prevent silent data loss, debouncing is **automatically bypassed** for any notification that contains a `params` object or a `relatedRequestId`. Such notifications will always be sent immediately.

This is an opt-in feature configured during server initialization.

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

const server = new McpServer(
  {
    name: "efficient-server",
    version: "1.0.0"
  },
  {
    // Enable notification debouncing for specific methods
    debouncedNotificationMethods: [
      'notifications/tools/list_changed',
      'notifications/resources/list_changed',
      'notifications/prompts/list_changed'
    ]
  }
);

// Now, any rapid changes to tools, resources, or prompts will result
// in a single, consolidated notification for each type.
server.registerTool("tool1", ...).disable();
server.registerTool("tool2", ...).disable();
server.registerTool("tool3", ...).disable();
// Only one 'notifications/tools/list_changed' is sent.
```

### Low-Level Server

For more control, you can use the low-level Server class directly:

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListPromptsRequestSchema,
  GetPromptRequestSchema
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "example-server",
    version: "1.0.0"
  },
  {
    capabilities: {
      prompts: {}
    }
  }
);

server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: [{
      name: "example-prompt",
      description: "An example prompt template",
      arguments: [{
        name: "arg1",
        description: "Example argument",
        required: true
      }]
    }]
  };
});

server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  if (request.params.name !== "example-prompt") {
    throw new Error("Unknown prompt");
  }
  return {
    description: "Example prompt",
    messages: [{
      role: "user",
      content: {
        type: "text",
        text: "Example prompt text"
      }
    }]
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Eliciting User Input

MCP servers can request additional information from users through the elicitation feature. This is useful for interactive workflows where the server needs user input or confirmation:

```typescript
// Server-side: Restaurant booking tool that asks for alternatives
server.tool(
  "book-restaurant",
  { 
    restaurant: z.string(),
    date: z.string(),
    partySize: z.number()
  },
  async ({ restaurant, date, partySize }) => {
    // Check availability
    const available = await checkAvailability(restaurant, date, partySize);
    
    if (!available) {
      // Ask user if they want to try alternative dates
      const result = await server.server.elicitInput({
        message: `No tables available at ${restaurant} on ${date}. Would you like to check alternative dates?`,
        requestedSchema: {
          type: "object",
          properties: {
            checkAlternatives: {
              type: "boolean",
              title: "Check alternative dates",
              description: "Would you like me to check other dates?"
            },
            flexibleDates: {
              type: "string",
              title: "Date flexibility",
              description: "How flexible are your dates?",
              enum: ["next_day", "same_week", "next_week"],
              enumNames: ["Next day", "Same week", "Next week"]
            }
          },
          required: ["checkAlternatives"]
        }
      });

      if (result.action === "accept" && result.content?.checkAlternatives) {
        const alternatives = await findAlternatives(
          restaurant, 
          date, 
          partySize, 
          result.content.flexibleDates as string
        );
        return {
          content: [{
            type: "text",
            text: `Found these alternatives: ${alternatives.join(", ")}`
          }]
        };
      }
      
      return {
        content: [{
          type: "text",
          text: "No booking made. Original date not available."
        }]
      };
    }
    
    // Book the table
    await makeBooking(restaurant, date, partySize);
    return {
      content: [{
        type: "text",
        text: `Booked table for ${partySize} at ${restaurant} on ${date}`
      }]
    };
  }
);
```

Client-side: Handle elicitation requests

```typescript
// This is a placeholder - implement based on your UI framework
async function getInputFromUser(message: string, schema: any): Promise<{
  action: "accept" | "decline" | "cancel";
  data?: Record<string, any>;
}> {
  // This should be implemented depending on the app
  throw new Error("getInputFromUser must be implemented for your platform");
}

client.setRequestHandler(ElicitRequestSchema, async (request) => {
  const userResponse = await getInputFromUser(
    request.params.message, 
    request.params.requestedSchema
  );
  
  return {
    action: userResponse.action,
    content: userResponse.action === "accept" ? userResponse.data : undefined
  };
});
```

**Note**: Elicitation requires client support. Clients must declare the `elicitation` capability during initialization.

### Writing MCP Clients

The SDK provides a high-level client interface:

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: "node",
  args: ["server.js"]
});

const client = new Client(
  {
    name: "example-client",
    version: "1.0.0"
  }
);

await client.connect(transport);

// List prompts
const prompts = await client.listPrompts();

// Get a prompt
const prompt = await client.getPrompt({
  name: "example-prompt",
  arguments: {
    arg1: "value"
  }
});

// List resources
const resources = await client.listResources();

// Read a resource
const resource = await client.readResource({
  uri: "file:///example.txt"
});

// Call a tool
const result = await client.callTool({
  name: "example-tool",
  arguments: {
    arg1: "value"
  }
});

```

### Proxy Authorization Requests Upstream

You can proxy OAuth requests to an external authorization provider:

```typescript
import express from 'express';
import { ProxyOAuthServerProvider } from '@modelcontextprotocol/sdk/server/auth/providers/proxyProvider.js';
import { mcpAuthRouter } from '@modelcontextprotocol/sdk/server/auth/router.js';

const app = express();

const proxyProvider = new ProxyOAuthServerProvider({
    endpoints: {
        authorizationUrl: "https://auth.external.com/oauth2/v1/authorize",
        tokenUrl: "https://auth.external.com/oauth2/v1/token",
        revocationUrl: "https://auth.external.com/oauth2/v1/revoke",
    },
    verifyAccessToken: async (token) => {
        return {
            token,
            clientId: "123",
            scopes: ["openid", "email", "profile"],
        }
    },
    getClient: async (client_id) => {
        return {
            client_id,
            redirect_uris: ["http://localhost:3000/callback"],
        }
    }
})

app.use(mcpAuthRouter({
    provider: proxyProvider,
    issuerUrl: new URL("http://auth.external.com"),
    baseUrl: new URL("http://mcp.example.com"),
    serviceDocumentationUrl: new URL("https://docs.example.com/"),
}))
```

This setup allows you to:

- Forward OAuth requests to an external provider
- Add custom token validation logic
- Manage client registrations
- Provide custom documentation URLs
- Maintain control over the OAuth flow while delegating to an external provider

### Backwards Compatibility

Clients and servers with StreamableHttp transport can maintain [backwards compatibility](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#backwards-compatibility) with the deprecated HTTP+SSE transport (from protocol version 2024-11-05) as follows

#### Client-Side Compatibility

For clients that need to work with both Streamable HTTP and older SSE servers:

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
let client: Client|undefined = undefined
const baseUrl = new URL(url);
try {
  client = new Client({
    name: 'streamable-http-client',
    version: '1.0.0'
  });
  const transport = new StreamableHTTPClientTransport(
    new URL(baseUrl)
  );
  await client.connect(transport);
  console.log("Connected using Streamable HTTP transport");
} catch (error) {
  // If that fails with a 4xx error, try the older SSE transport
  console.log("Streamable HTTP connection failed, falling back to SSE transport");
  client = new Client({
    name: 'sse-client',
    version: '1.0.0'
  });
  const sseTransport = new SSEClientTransport(baseUrl);
  await client.connect(sseTransport);
  console.log("Connected using SSE transport");
}
```

#### Server-Side Compatibility

For servers that need to support both Streamable HTTP and older clients:

```typescript
import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

const server = new McpServer({
  name: "backwards-compatible-server",
  version: "1.0.0"
});

// ... set up server resources, tools, and prompts ...

const app = express();
app.use(express.json());

// Store transports for each session type
const transports = {
  streamable: {} as Record<string, StreamableHTTPServerTransport>,
  sse: {} as Record<string, SSEServerTransport>
};

// Modern Streamable HTTP endpoint
app.all('/mcp', async (req, res) => {
  // Handle Streamable HTTP transport for modern clients
  // Implementation as shown in the "With Session Management" example
  // ...
});

// Legacy SSE endpoint for older clients
app.get('/sse', async (req, res) => {
  // Create SSE transport for legacy clients
  const transport = new SSEServerTransport('/messages', res);
  transports.sse[transport.sessionId] = transport;
  
  res.on("close", () => {
    delete transports.sse[transport.sessionId];
  });
  
  await server.connect(transport);
});

// Legacy message endpoint for older clients
app.post('/messages', async (req, res) => {
  const sessionId = req.query.sessionId as string;
  const transport = transports.sse[sessionId];
  if (transport) {
    await transport.handlePostMessage(req, res, req.body);
  } else {
    res.status(400).send('No transport found for sessionId');
  }
});

app.listen(3000);
```

**Note**: The SSE transport is now deprecated in favor of Streamable HTTP. New implementations should use Streamable HTTP, and existing SSE implementations should plan to migrate.

## Documentation

- [Model Context Protocol documentation](https://modelcontextprotocol.io)
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [Example Servers](https://github.com/modelcontextprotocol/servers)

## Contributing

Issues and pull requests are welcome on GitHub at <https://github.com/modelcontextprotocol/typescript-sdk>.

## License

This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details."""

system_prompt = """"""