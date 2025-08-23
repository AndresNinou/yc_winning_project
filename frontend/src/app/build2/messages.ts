export interface MessageType {
  role: "assistant" | "user" | "loading";
  text: string;
  ts: number;
  tool?: string;
}

export interface Tool {
  type: "code" | "reasoning" | "error";
  status: "done" | "success" | "error";
}
