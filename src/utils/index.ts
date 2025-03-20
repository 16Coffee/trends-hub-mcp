import type { ServerResult } from "@modelcontextprotocol/sdk/types.js";
import { ZodError } from "zod";
import { fromError } from 'zod-validation-error';

export { cacheStorage } from './cache'
export { http } from './http'

export const handleErrorResult = (error: unknown): ServerResult => {
  let errorMessage = '';
  if (error instanceof ZodError) {
    errorMessage = fromError(error).toString();
  } else if (error instanceof Error) {
    errorMessage = error.message;
  } else {
    errorMessage = JSON.stringify(error);
  }
  return {
    content: [{
      type: 'text',
      text: errorMessage,
    }],
    isError: true,
  };
}

export const handleSuccessResult = (...result: unknown[]): ServerResult => {
  return {
    content: result.map((item) => ({
      type: 'text',
      text: JSON.stringify(item),
    })),
  };
}