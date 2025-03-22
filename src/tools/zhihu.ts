import { z } from 'zod';
import { dayjs, defineToolConfig, handleSuccessResult, http } from '../utils';

const zhihuTrendingSchema = z.object({
  limit: z.number().optional().default(50),
});

export default defineToolConfig({
  name: 'get-zhihu-trending',
  description: '获取知乎热榜',
  zodSchema: zhihuTrendingSchema,
  func: async (args: unknown) => {
    const { limit } = zhihuTrendingSchema.parse(args);
    const resp = await http.get<{ data: any[] }>('https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total', {
      params: {
        limit,
        desktop: 'true',
      },
    });
    if (!Array.isArray(resp.data.data)) {
      throw new Error('获取知乎热榜失败');
    }
    return resp.data.data.map((item) => {
      const data = item.target;
      return {
        title: data.title,
        description: data.excerpt,
        cover: item.children[0].thumbnail,
        created: dayjs.unix(data.created).toISOString(),
        popularity: item.detail_text,
        link: `https://www.zhihu.com/question/${data.id}`,
      };
    });
  },
});
