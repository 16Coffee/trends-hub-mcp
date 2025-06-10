import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { afterAll, describe, expect, test } from 'vitest';

const transport = new StdioClientTransport({
  command: 'node',
  args: ['.'],
});

const client = new Client({
  name: 'test-client',
  version: '0.0.0',
});

describe('MCP 工具测试', async () => {
  await client.connect(transport);

  const toolsResponse = await client.listTools();

  afterAll(async () => {
    await client.close();
  });

  test('应能列出可用工具', async () => {
    expect(toolsResponse).toBeDefined();
    expect(toolsResponse).toHaveProperty('tools');
    expect(toolsResponse.tools).toBeInstanceOf(Array);
    expect(toolsResponse.tools).toHaveLength(6);
    const toolNames = toolsResponse.tools.map((t) => t.name);
    expect(toolNames).toEqual(
      expect.arrayContaining([
        'get-nytimes-news',
        'get-wallstreetcn-news',
        'get-bbc-news',
        'get-washington-post-news',
        'get-xinhuanet-news',
        'get-people-news',
      ]),
    );
  });

  test('应能调用 BBC 新闻工具', async () => {
    const result = await client.callTool({
      name: 'get-bbc-news',
    });
    expect(result).toBeDefined();
    expect(result).toHaveProperty('content');
    expect(result.content).toBeInstanceOf(Array);
    expect(result.content).not.toHaveLength(0);
  });
});
