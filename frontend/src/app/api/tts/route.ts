// app/api/tts/route.ts
import type { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { text } = await req.json();
    if (!text || typeof text !== "string")
      return new Response("Bad Request", { status: 400 });

    const r = await fetch("https://api.openai.com/v1/audio/speech", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4o-mini-tts",
        voice: "alloy", // pick any available voice
        input: text,
        format: "mp3",
      }),
    });

    if (!r.ok) return new Response(await r.text(), { status: r.status });

    const buf = await r.arrayBuffer();
    return new Response(buf, {
      headers: {
        "Content-Type": "audio/mpeg",
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return new Response("TTS error", { status: 500 });
  }
}
