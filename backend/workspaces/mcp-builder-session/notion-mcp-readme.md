# Notion MCP Server

A Model Context Protocol (MCP) server that fetches Notion pages by URL and converts them to markdown format.

## Features

- 🔗 Fetch Notion pages using public URLs
- 📝 Convert Notion content to clean markdown
- 🛠️ Simple MCP tool integration
- 🔐 Secure authentication via Notion API token

## Prerequisites

- Node.js 18+ 
- A Notion integration token with read access to the pages you want to fetch

## Setup

### 1. Create a Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "MCP Server")
4. Select the workspace you want to access
5. Copy the "Internal Integration Token"

### 2. Share Pages with Your Integration

For each Notion page you want to access:
1. Open the page in Notion
2. Click "Share" in the top-right
3. Click "Invite" and search for your integration name
4. Grant it access

### 3. Install Dependencies

```bash
npm install
```

### 4. Set Environment Variable

Set your Notion integration token:

```bash
export NOTION_TOKEN="your_notion_integration_token_here"
```

Or create a `.env` file:
```bash
echo "NOTION_TOKEN=your_notion_integration_token_here" > .env
```

## Usage

### Running the Server

```bash
npm start
```

The server will start and listen for MCP requests on stdio.

### Using the Tool

The server provides one tool: `fetch_notion_page`

**Parameters:**
- `url` (string, required): The Notion page URL

**Example URL formats supported:**
- `https://notion.so/Page-Title-abc123def456...`
- `https://www.notion.so/workspace/Page-Title-abc123def456...`
- `https://notion.so/abc123def456...`

**Example usage in Claude Desktop or other MCP clients:**

```json
{
  "tool": "fetch_notion_page",
  "arguments": {
    "url": "https://notion.so/My-Page-Title-abc123def456789012345678901234"
  }
}
```

### Development

Run with auto-reload during development:

```bash
npm run dev
```

## Integration with Claude Desktop

To use this MCP server with Claude Desktop, add it to your MCP configuration:

### macOS/Linux
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "notion": {
      "command": "node",
      "args": ["/path/to/notion-mcp/src/index.js"],
      "env": {
        "NOTION_TOKEN": "your_notion_integration_token_here"
      }
    }
  }
}
```

### Windows
Add to `%APPDATA%\\Claude\\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "notion": {
      "command": "node",
      "args": ["C:\\path\\to\\notion-mcp\\src\\index.js"],
      "env": {
        "NOTION_TOKEN": "your_notion_integration_token_here"
      }
    }
  }
}
```

## Error Handling

The tool handles various error scenarios:

- **Invalid URLs**: Returns an error if the URL format is not recognized
- **Missing token**: Returns an error if `NOTION_TOKEN` is not set
- **Access denied**: Returns an error if the integration doesn't have access to the page
- **Page not found**: Returns an error if the page doesn't exist

## Supported Notion Content Types

The markdown converter supports:

- Text blocks (paragraphs, headings)
- Lists (bulleted, numbered, toggle)
- Code blocks and inline code
- Tables
- Images (as markdown image links)
- Quotes and callouts
- Basic formatting (bold, italic, strikethrough)

## Limitations

- Does not fetch child pages automatically
- Database views are converted to basic table markdown
- Some advanced Notion blocks may not convert perfectly
- Requires integration access to be manually granted for each page

## Troubleshooting

### "Page not found" error
- Make sure you've shared the page with your Notion integration
- Verify the URL is correct and accessible

### "NOTION_TOKEN not set" error
- Ensure the environment variable is properly set
- For Claude Desktop, make sure it's in the MCP configuration

### "Invalid URL" error
- Check that you're using a valid Notion page URL
- Make sure the URL contains the page ID

## License

MIT