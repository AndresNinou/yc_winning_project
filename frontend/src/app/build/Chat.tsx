import type { MessageType, Tool } from "@/app/build/types";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { CheckCircle, XCircle, Clock, Code, Brain } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ChatProps {
  messages: MessageType[];
  tools?: Record<string, Tool>;
}

export function Chat({ messages, tools = {} }: ChatProps) {
  const formatTimestamp = (ts: number) => {
    return new Date(ts).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getToolIcon = (type: Tool["type"]) => {
    switch (type) {
      case "code":
        return <Code className="w-3 h-3" />;
      case "reasoning":
        return <Brain className="w-3 h-3" />;
      case "error":
        return <XCircle className="w-3 h-3 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusIcon = (status: Tool["status"]) => {
    switch (status) {
      case "success":
        return <CheckCircle className="w-3 h-3 text-green-500" />;
      case "error":
        return <XCircle className="w-3 h-3 text-red-500" />;
      case "done":
        return <CheckCircle className="w-3 h-3 text-blue-500" />;
      default:
        return <Clock className="w-3 h-3 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: Tool["status"]) => {
    switch (status) {
      case "success":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "error":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "done":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div className="flex flex-col space-y-4 w-full mx-auto">
      <AnimatePresence mode="popLayout">
        {messages.map((message, index) => {
          const tool = message.tool ? tools[message.tool] : null;
          const isUser = message.role === "user";
          const isLoading = message.role === "loading";

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{
                duration: 0.3,
                ease: "easeOut",
                delay: index * 0.1,
              }}
              className={`flex gap-3 ${
                isUser ? "flex-row-reverse" : "flex-row"
              }`}
            >
              <Avatar className="w-8 h-8 flex-shrink-0">
                <AvatarFallback
                  className={
                    isUser
                      ? "bg-white text-black"
                      : "bg-blue-500 text-white"
                  }
                >
                  {isUser ? "U" : "A"}
                </AvatarFallback>
              </Avatar>

              <div
                className={`flex flex-col gap-2 max-w-[80%] ${
                  isUser ? "items-end" : "items-start"
                }`}
              >
                {isLoading ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Card className="p-3 bg-white/5 border border-white/10 backdrop-blur-sm">
                      <div className="flex items-center gap-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse delay-75"></div>
                          <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse delay-150"></div>
                        </div>
                        <span className="text-sm text-white/70">
                          Thinking...
                        </span>
                      </div>
                    </Card>
                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.2, delay: 0.1 }}
                  >
                    <Card
                      className={`p-3 ${
                        isUser
                          ? "bg-white text-black"
                          : "bg-white/5 border border-white/10 backdrop-blur-sm"
                      }`}
                    >
                      <p className={`text-md leading-normal whitespace-pre-wrap ${
                        isUser ? "text-black" : "text-white"
                      }`}>
                        {message.text}
                      </p>
                    </Card>
                  </motion.div>
                )}

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.2, delay: 0.2 }}
                  className={`flex items-center gap-2 text-xs text-white/60 ${
                    isUser ? "flex-row-reverse" : "flex-row"
                  }`}
                >
                  <span>{formatTimestamp(message.ts)}</span>

                  {tool && (
                    <Badge
                      variant="outline"
                      className={`flex items-center gap-1 ${getStatusColor(
                        tool.status
                      )}`}
                    >
                      {getToolIcon(tool.type)}
                      <span className="capitalize">{tool.type}</span>
                      {getStatusIcon(tool.status)}
                    </Badge>
                  )}
                </motion.div>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
