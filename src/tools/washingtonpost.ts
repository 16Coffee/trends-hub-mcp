import { defineToolConfig, getRssItems } from '../utils';

export default defineToolConfig({
  name: 'get-washington-post-news',
  description: '获取华盛顿邮报的国际新闻',
  func: async () => {
    return getRssItems('https://feeds.washingtonpost.com/rss/world');
  },
});
