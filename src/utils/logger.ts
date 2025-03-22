import fs from 'node:fs';
import path from 'node:path';
import { inspect } from 'node:util';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

class Logger {
  private get logPath() {
    return path.resolve('app.log');
  }

  private mcpServer: McpServer | null = null;

  setMcpServer(mcpServer: McpServer) {
    this.mcpServer = mcpServer;
  }

  log(level: Parameters<McpServer['server']['sendLoggingMessage']>[0]['level'], data: unknown) {
    // this.mcpServer?.server.sendLoggingMessage({
    //   level,
    //   data,
    // });
    if (process.env.NODE_ENV === 'development') {
      const date = new Date().toLocaleString();
      const message = inspect(data, true, Number.POSITIVE_INFINITY, false);
      fs.appendFileSync(this.logPath, `${date} [${level.toLocaleLowerCase()}] ${message}\n`);
    }
  }

  info(data: unknown) {
    this.log('info', data);
  }

  error(data: unknown) {
    this.log('error', data);
  }

  warn(data: unknown) {
    this.log('warning', data);
  }

  debug(data: unknown) {
    this.log('debug', data);
  }
}

export const logger = new Logger();
