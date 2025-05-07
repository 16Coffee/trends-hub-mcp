import { z } from 'zod';
import { dayjs, defineToolConfig, handleSuccessResult, http } from '../utils';

const zhihuTrendingSchema = z.object({
  limit: z.number().optional().default(50),
});

export default defineToolConfig({
  name: 'get-zhihu-trending',
  description: '获取知乎热榜，包含时事热点、社会话题、科技动态、娱乐八卦等多领域的热门问答和讨论的中文资讯',
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
      const id = item.target?.url.split('/').pop();
      return {
        title: data.title,
        description: data.excerpt,
        cover: item.children[0].thumbnail,
        created: dayjs.unix(data.created).toISOString(),
        popularity: item.detail_text,
        link: id ? `https://www.zhihu.com/question/${id}` : undefined,
      };
    });
  },
});
