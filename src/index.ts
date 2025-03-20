#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { getTools } from "./tools";
import zodToJsonSchema from 'zod-to-json-schema';
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const mcpServer = new McpServer({
  name: 'Trends Hub',
  version: process.env.PACKAGE_VERSION ?? '0.0.0',
}, {
  capabilities: {
    tools: {},
  }
})

mcpServer.server.setRequestHandler(ListToolsRequestSchema, async () => {
  const tools = await getTools()
  return {
    tools: tools.map((item) => ({
      name: item.config.name,
      description: item.config.description,
      inputSchema: zodToJsonSchema(item.config.zodSchema),
    }))
  }
})

mcpServer.server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const tools = await getTools()
  const tool = tools.find((item) => item.config.name === request.params.name)
  return tool?.config.func(request.params.args) ?? {}
});

(async () => {
  const transport = new StdioServerTransport();
  await mcpServer.connect(transport);
})();

