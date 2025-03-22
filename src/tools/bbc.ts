import { z } from 'zod';
import { defineToolConfig, getRssItems } from '../utils';

const bbcRequestSchema = z
  .object({
    category: z
      .union([
        z.literal('').describe('热门新闻'),
        z.literal('world').describe('国际'),
        z.literal('uk').describe('英国'),
        z.literal('business').describe('商业'),
        z.literal('politics').describe('政治'),
        z.literal('health').describe('健康'),
        z.literal('education').describe('教育'),
        z.literal('science_and_environment').describe('科学与环境'),
        z.literal('technology').describe('科技'),
        z.literal('entertainment_and_arts').describe('娱乐与艺术'),
      ])
      .optional()
      .default(''),
    edition: z
      .union([
        z.literal(''),
        z.literal('uk').describe('UK'),
        z.literal('us').describe('US & Canada'),
        z.literal('int').describe('Rest of the world'),
      ])
      .optional()
      .default('')
      .describe('版本，仅对 `category` 为空有效'),
  })
  .transform((values) => {
    let url = 'https://feeds.bbci.co.uk/news/';
    if (values.category) {
      url += `${values.category}/`;
    }
    url += 'rss.xml';
    if (values.edition) {
      url += `?edition=${values.edition}`;
    }
    return {
      ...values,
      url,
    };
  });

export default defineToolConfig({
  name: 'get-bbc-news',
  description: '获取 BBC 新闻，提供全球新闻、英国新闻、商业、政治、健康、教育、科技、娱乐等资讯',
  zodSchema: bbcRequestSchema,
  func: async (args) => {
    const { url } = bbcRequestSchema.parse(args);
    return getRssItems(url);
  },
});
