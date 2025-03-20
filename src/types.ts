import type { ListToolsResult, ServerResult } from "@modelcontextprotocol/sdk/types.js";
import type { z } from "zod";

export type ToolConfig = Omit<ListToolsResult['tools'][number], 'inputSchema'> & {
  func: (args: unknown) => Promise<ServerResult>,
  zodSchema: z.ZodSchema<unknown>;
}