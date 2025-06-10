import { defineToolConfig, getRssItems } from '../utils';

export default defineToolConfig({
  name: 'get-xinhuanet-news',
  description: '获取新华网英文频道国际新闻',
  func: async () => {
    return getRssItems('https://english.news.cn/rss/worldrss.xml');
  },
});
