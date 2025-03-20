#!/usr/bin/env node

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import zodToJsonSchema from 'zod-to-json-schema';
import { tools } from './tools';
import { handleErrorResult } from './utils';
import { z } from 'zod';

const mcpServer = new McpServer(
  {
    name: 'Trends Hub',
    version: process.env.PACKAGE_VERSION ?? '0.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  },
);

mcpServer.server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: (await tools).map((item) => {
      const { name, description, zodSchema = z.object({}) } = item.default;
      return {
        name,
        description,
        inputSchema: zodToJsonSchema(zodSchema),
      };
    }),
  };
});

mcpServer.server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const tool = (await tools).find((item) => item.default.name === request.params.name)?.default;
    if (!tool) {
      throw new Error('Tool not found');
    }
    const result = await tool.func(request.params.args ?? {});
    return result;
  } catch (error) {
    return handleErrorResult(error);
  }
});

(async () => {
  const transport = new StdioServerTransport();
  await mcpServer.connect(transport);
})();
