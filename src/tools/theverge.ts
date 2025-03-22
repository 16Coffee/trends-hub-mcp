import { defineToolConfig, getRss } from '../utils';
import { URL } from 'node:url';

export default defineToolConfig({
  name: 'get-theverge-news',
  description: '获取 The Verge 新闻',
  func: async () => {
    const rss = await getRss('https://www.theverge.com/rss/index.xml');
    if (!Array.isArray(rss.feed.entry)) {
      throw new Error('获取 The Verge 新闻失败');
    }
    return (rss.feed.entry as any[]).map((item) => {
      let link = item.link;
      if (!link && item.id) {
        link = item.id;
      }
      const url = new URL(link);
      if (url.searchParams.has('p')) {
        url.pathname = url.searchParams.get('p') as string;
        url.search = '';
        link = url.toString();
      }
      return {
        title: item.title,
        description: item.summary,
        publish_time: item.published,
        link,
      };
    });
  },
});
