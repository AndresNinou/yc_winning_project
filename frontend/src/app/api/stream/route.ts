export const runtime = 'nodejs'

interface SSEData {
  text?: string
  id?: string
  file?: string
  note?: string
  ok?: boolean
}

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const q = searchParams.get('q') || 'Build an MCP'
  const answers = JSON.parse(searchParams.get('answers') || '[]')
  const encoder = new TextEncoder()

  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      function send(event: string, data: SSEData) {
        controller.enqueue(encoder.encode(`event: ${event}\n`))
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`))
      }

      // Log the request for debugging
      console.log(`SSE request: ${q} with ${answers.length} answers`)

      // Ask a planner question
      send('planner_question', { text: 'Which external API should this MCP connect to?' })
      setTimeout(() => send('step_start', { id: 'plan' }), 200)

      // Simulate scaffold + code generation with notes
      setTimeout(() => { 
        send('step_done', { id: 'plan', text: 'Planner asked 1 question' }); 
        send('step_start', { id: 'scaffold' }) 
      }, 900)
      
      setTimeout(() => { 
        send('step_log', { id: 'scaffold', text: 'Creating project structure' }); 
        send('code_update', { file: 'manifest.json', note: 'tool added: get_repo(owner, name)' }) 
      }, 1500)
      
      setTimeout(() => { 
        send('step_done', { id: 'scaffold', text: 'Scaffold complete' }); 
        send('step_start', { id: 'generate' }) 
      }, 2100)
      
      setTimeout(() => { 
        send('code_update', { file: 'server.py', note: 'implemented get_repo tool' }); 
        send('step_log', { id: 'generate', text: 'Writing server.py' }) 
      }, 2700)
      
      setTimeout(() => { 
        send('step_done', { id: 'generate', text: 'Code generated' }); 
        send('step_start', { id: 'handshake' }) 
      }, 3300)
      
      setTimeout(() => { 
        send('step_log', { id: 'handshake', text: 'Running handshake…' }) 
      }, 3800)
      
      setTimeout(() => { 
        send('step_done', { id: 'handshake', text: 'Handshake OK: 2 tools, 1 resource' }); 
        send('step_start', { id: 'ready' }) 
      }, 4300)
      
      setTimeout(() => { 
        send('step_done', { id: 'ready', text: 'Server ready' }); 
        send('build_done', { ok: true }); 
        controller.close() 
      }, 4900)
    }
  })

  return new Response(stream, { 
    headers: { 
      'Content-Type': 'text/event-stream', 
      'Cache-Control': 'no-cache, no-transform', 
      'Connection': 'keep-alive', 
      'X-Accel-Buffering': 'no' 
    } 
  })
}
