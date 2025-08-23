export async function GET() {
  try {
    // Check backend Claude service health
    const backendUrl = process.env.CLAUDE_BACKEND_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/v1/claude/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.status}`)
    }

    const healthData = await response.json()
    
    return Response.json({
      status: 'healthy',
      backend: healthData,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Claude health check failed:', error)
    return Response.json(
      { 
        status: 'unhealthy', 
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 503 }
    )
  }
}

