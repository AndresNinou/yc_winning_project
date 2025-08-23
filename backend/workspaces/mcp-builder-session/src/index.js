#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { Client } from "@notionhq/client";
import { NotionToMarkdown } from "notion-to-md";

// Initialize Notion client
const notion = new Client({
  auth: process.env.NOTION_TOKEN,
});

// Initialize NotionToMarkdown converter
const n2m = new NotionToMarkdown({ notionClient: notion });

// Create MCP server
const server = new Server(
  {
    name: "notion-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Helper function to extract page ID from Notion URL
function extractPageId(url) {
  try {
    // Handle various Notion URL formats
    const urlObj = new URL(url);
    
    // Extract the page ID from different URL formats
    // Format 1: https://notion.so/page-title-32-char-id
    // Format 2: https://www.notion.so/workspace/page-title-32-char-id
    // Format 3: https://notion.so/32-char-id
    
    const pathname = urlObj.pathname;
    const parts = pathname.split('/').filter(part => part.length > 0);
    
    if (parts.length === 0) {
      throw new Error("Invalid Notion URL: no path found");
    }
    
    // Get the last part which should contain the page ID
    const lastPart = parts[parts.length - 1];
    
    // Extract 32-character ID (with or without dashes)
    const idMatch = lastPart.match(/([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/i);
    
    if (!idMatch) {
      throw new Error("Invalid Notion URL: could not extract page ID");
    }
    
    // Remove dashes to get the raw 32-character ID
    const pageId = idMatch[1].replace(/-/g, '');
    
    // Validate it's exactly 32 characters
    if (pageId.length !== 32) {
      throw new Error("Invalid page ID length");
    }
    
    return pageId;
  } catch (error) {
    throw new Error(`Failed to parse Notion URL: ${error.message}`);
  }
}

// Register the fetch_notion_page tool
server.setRequestHandler("tools/list", async () => {
  return {
    tools: [
      {
        name: "fetch_notion_page",
        description: "Fetch a Notion page by URL and convert it to markdown",
        inputSchema: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description: "The Notion page URL to fetch",
            },
          },
          required: ["url"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "fetch_notion_page") {
    try {
      // Validate NOTION_TOKEN is set
      if (!process.env.NOTION_TOKEN) {
        throw new Error("NOTION_TOKEN environment variable is not set. Please set it to your Notion integration token.");
      }

      const { url } = args;
      
      if (!url || typeof url !== "string") {
        throw new Error("URL parameter is required and must be a string");
      }

      // Extract page ID from URL
      const pageId = extractPageId(url);

      // Fetch the page from Notion
      const page = await notion.pages.retrieve({ page_id: pageId });
      
      if (!page) {
        throw new Error("Page not found or you don't have access to it");
      }

      // Get page blocks
      const blocks = await notion.blocks.children.list({
        block_id: pageId,
        page_size: 100,
      });

      // Convert blocks to markdown
      const mdblocks = await n2m.blocksToMarkdown(blocks.results);
      const markdown = n2m.toMarkdownString(mdblocks);

      // Get page title
      let title = "Untitled";
      if (page.properties && page.properties.title) {
        const titleProperty = page.properties.title;
        if (titleProperty.type === "title" && titleProperty.title.length > 0) {
          title = titleProperty.title[0].plain_text;
        }
      } else if (page.properties) {
        // Look for other text properties that might contain the title
        const titleProp = Object.values(page.properties).find(
          prop => prop.type === "title" && prop.title && prop.title.length > 0
        );
        if (titleProp) {
          title = titleProp.title[0].plain_text;
        }
      }

      // Format the final markdown with title
      const finalMarkdown = `# ${title}\n\n${markdown.parent}`;

      return {
        content: [
          {
            type: "text",
            text: finalMarkdown,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error fetching Notion page: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Notion MCP server running on stdio");
}

main().catch((error) => {
  console.error("Server failed to start:", error);
  process.exit(1);
});