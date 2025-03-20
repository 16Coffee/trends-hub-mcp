import path from 'node:path';
import fs from 'node:fs';
import { inspect } from 'node:util';

class Logger {
  private get logPath() {
    return path.resolve('app.log');
  }

  log(badge: string, data: unknown) {
    const date = new Date().toISOString();
    const message = inspect(data, true, Number.POSITIVE_INFINITY, false);
    fs.appendFileSync(this.logPath, `${date} ${badge || ''} ${message}\n`);
  }

  info(data: unknown) {
    this.log('[INFO]', data);
  }

  error(data: unknown) {
    this.log('[ERROR]', data);
  }

  warn(data: unknown) {
    this.log('[WARN]', data);
  }

  debug(data: unknown) {
    this.log('[DEBUG]', data);
  }
}

export const logger =
  process.env.NODE_ENV === 'development' ? new Logger() : new Proxy({} as Logger, { get: () => () => {} });
