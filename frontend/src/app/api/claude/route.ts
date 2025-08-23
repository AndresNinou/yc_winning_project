export async function POST(req: Request) {
  try {
    const body = await req.json()
    const { prompt, conversation_id, system_prompt, max_turns, allowed_tools, permission_mode, cwd } = body

    // Forward request to Claude backend
    const backendUrl = process.env.CLAUDE_BACKEND_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/v1/claude/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({
        prompt,
        conversation_id: conversation_id || 'default',
        system_prompt: system_prompt || 'You are Claude, a helpful AI assistant helping with MCP tool building. Be conversational and provide practical guidance.',
        max_turns: max_turns || 300,
        allowed_tools: allowed_tools || ['Read', 'Write', 'Bash', 'ListDir', 'Search', 'StrReplace', 'CreateFile', 'ViewFile'],
        permission_mode: permission_mode || 'default',
        cwd: cwd || process.cwd()
      }),
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`)
    }

    // Return the SSE stream directly
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control',
      },
    })

  } catch (error) {
    console.error('Claude API bridge error:', error)
    return new Response(
      JSON.stringify({ error: 'Failed to connect to Claude service' }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}

