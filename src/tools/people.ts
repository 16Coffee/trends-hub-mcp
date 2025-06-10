import { defineToolConfig, getRssItems } from '../utils';

export default defineToolConfig({
  name: 'get-people-news',
  description: '获取人民日报政治新闻',
  func: async () => {
    return getRssItems('http://www.people.com.cn/rss/politics.xml');
  },
});
