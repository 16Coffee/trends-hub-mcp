import { defineToolConfig, handleSuccessResult, http } from '../utils';

export default defineToolConfig({
  name: 'get-toutiao-trending',
  description: '获取今日头条热榜',
  func: async () => {
    const resp = await http.get<{
      data: any[];
    }>('https://www.toutiao.com/hot-event/hot-board/', {
      params: {
        origin: 'toutiao_pc',
      },
    });
    if (!Array.isArray(resp.data.data)) {
      throw new Error('获取今日头条热榜失败');
    }
    return handleSuccessResult(
      ...resp.data.data.map((item) => {
        return {
          title: item.Title,
          cover: item.Image.url,
          popularity: item.HotValue,
          link: item.Url,
        };
      }),
    );
  },
});
