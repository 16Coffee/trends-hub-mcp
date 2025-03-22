import { defineToolConfig, getRssItems } from '../utils';

export default defineToolConfig({
  name: 'get-gcores-new',
  description: '获取机核新闻',
  func: () => getRssItems('https://www.gcores.com/rss'),
});
