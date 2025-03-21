import type { ServerResult } from '@modelcontextprotocol/sdk/types.js';
import type { z } from 'zod';

export type ToolConfig = {
  name: string;
  description: string;
  zodSchema?: z.ZodSchema<unknown>;
  func: (args: unknown) => Promise<ServerResult>;
};
