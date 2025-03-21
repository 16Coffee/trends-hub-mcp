import { z } from 'zod';
import { dayjs, defineToolConfig, handleSuccessResult, http } from '../utils';

const get36krRequestSchema = z.object({
  type: z
    .union([
      z.literal('hot').describe('人气榜'),
      z.literal('video').describe('视频榜'),
      z.literal('comment').describe('热议榜'),
      z.literal('collect').describe('收藏榜'),
    ])
    .optional()
    .default('hot'),
});

const LIST_TYPE_MAP: Record<z.infer<typeof get36krRequestSchema>['type'], string> = {
  hot: 'hotRankList',
  video: 'videoList',
  comment: 'remarkList',
  collect: 'collectList',
};

export default defineToolConfig({
  name: 'get-36kr-trending',
  description: '获取36氪热榜',
  zodSchema: get36krRequestSchema,
  func: async (args) => {
    const { type } = get36krRequestSchema.parse(args);

    const resp = await http.post<{
      data: Record<string, any[]>
    }>(
      `https://gateway.36kr.com/api/mis/nav/home/nav/rank/${type}`,
      {
        partner_id: 'wap',
        param: {
          siteId: 1,
          platformId: 2,
        },
        timestamp: Date.now(),
      },
      {
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
      },
    );
    
    return handleSuccessResult(
      ...resp.data.data[LIST_TYPE_MAP[type]].map((item)=>{
        const data= item.templateMaterial
        return {
          title: data.widgetTitle,
          cover: data.widgetImage,
          author: data.authorName,
          publish_time: dayjs(data.publishTime).toISOString(),
          read_count: data.statRead,
          collect_count: data.statCollect,
          comment_count: data.statComment,
          praise_count: data.statPraise,
          link: `https://www.36kr.com/p/${data.itemId}`,
        }
      })
    )
  },
});
