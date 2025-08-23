export interface MessageType {
  role: "assistant" | "user" | "loading";
  text: string;
  ts: number;
  tool?: string;
  imageUrl?: string;
}

export interface Tool {
  type: "code" | "reasoning" | "error";
  status: "done" | "success" | "error";
}

export interface Files {
  type: "";
}
