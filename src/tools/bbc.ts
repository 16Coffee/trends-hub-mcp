import { defineToolConfig, getRssItems } from '../utils';

export default defineToolConfig({
  name: 'get-bbc-news',
  description: '获取 BBC 新闻最新国际要闻',
  func: async () => {
    return getRssItems('https://feeds.bbci.co.uk/news/world/rss.xml');
  },
});
