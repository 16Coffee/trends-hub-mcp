import { z } from 'zod';
import { defineToolConfig, getRssItems, omit } from '../utils';

const infoqRequestSchema = z
  .object({
    region: z.enum(['cn', 'global']).optional().default('cn'),
  })
  .transform((data) => {
    const url = {
      cn: 'https://www.infoq.cn/feed',
      global: 'https://feed.infoq.com/',
    }[data.region];
    return {
      ...data,
      url,
    };
  });

export default defineToolConfig({
  name: 'get-infoq-news',
  description: '获取 InfoQ 技术资讯，包含软件开发、架构设计、云计算、AI等企业级技术内容和前沿开发者动态',
  zodSchema: infoqRequestSchema,
  func: async (args) => {
    const { url, region } = infoqRequestSchema.parse(args);
    const resp = await getRssItems(url);
    // 中文版 description 没有实质内容
    if (region === 'cn') {
      return resp.map((item) => omit(item, ['description']));
    }
    return resp;
  },
});
