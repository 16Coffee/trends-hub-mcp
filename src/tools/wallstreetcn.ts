import { defineToolConfig, getRssItems } from '../utils';

export default defineToolConfig({
  name: 'get-wallstreetcn-news',
  description: '获取华尔街见闻最新资讯',
  func: async () => {
    return getRssItems('https://rsshub.app/wallstreetcn/news');
  },
});
