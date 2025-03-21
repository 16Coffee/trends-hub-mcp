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

(async () => {
  const toolConfigs = new Map(
    (await Promise.all((await tools).map((item) => item.default.catch(() => null))))
      .filter((item) => !!item)
      .map((item) => [item.name, item]),
  );

  const toolList = Array.from(toolConfigs.values());

  mcpServer.server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: toolList.map((item) => {
        const { name, description, zodSchema = z.object({}) } = item;
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
      const tool = toolConfigs.get(request.params.name);
      if (!tool) {
        throw new Error('Tool not found');
      }
      const result = await tool.func(request.params.arguments ?? {});
      return result;
    } catch (error) {
      return handleErrorResult(error);
    }
  });
  const transport = new StdioServerTransport();
  await mcpServer.connect(transport);
})();
