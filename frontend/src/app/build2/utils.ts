interface StreamData {
  type: "progress" | "content" | "done";
  message_type?: "SystemMessage" | "AssistantMessage" | "ResultMessage";
  content?: string;
  block_index?: number;
  timestamp?: number;
}

export const parseStreamingResponse = async (response: Response): Promise<string> => {
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let content = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data: StreamData = JSON.parse(line.slice(6));
            
            if (data.type === "content" && data.content) {
              content += data.content;
            }
          } catch (e) {
            // Skip invalid JSON lines
            continue;
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  return content;
};

export const sendMessage = async (prompt: string, currentInput: string) =>
  await fetch("/api/claude", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt: `Context: You are helping the user build an MCP (Model Context Protocol) tool based on their initial prompt: "${prompt}". 

User's latest message: ${currentInput}

Your task:
1. Ask clarifying questions to understand requirements better
2. Once you have enough information and the user confirms (like saying "Yes, build"), help plan and generate the MCP tool
3. Be conversational and helpful

Please respond appropriately to continue the conversation.`,
      conversation_id: "mcp-builder-session",
      system_prompt:
        "You are Claude, an AI assistant specialized in helping developers build MCP (Model Context Protocol) tools. You ask clarifying questions, understand requirements, and help plan and generate code. Be conversational, helpful, and focused on practical implementation.",
      allowed_tools: ["Read", "Write", "CreateFile", "ListDir", "Search"],
      permission_mode: "default",
    }),
  });
