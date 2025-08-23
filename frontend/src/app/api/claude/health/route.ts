export async function GET() {
  try {
    // Check Claude backend health
    const backendUrl = process.env.CLAUDE_BACKEND_URL || 'https://integral-mozilla-ref-db.trycloudflare.com'
    const response = await fetch(`${backendUrl}/api/v1/claude/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`)
    }

    const healthData = await response.json()
    
    return Response.json({
      status: 'healthy',
      backend: healthData,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Health check error:', error)
    return Response.json(
      { 
        status: 'unhealthy',
        error: 'Failed to connect to Claude service',
        timestamp: new Date().toISOString()
      },
      { status: 503 }
    )
  }
}

