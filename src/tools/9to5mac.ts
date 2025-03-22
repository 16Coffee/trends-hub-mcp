import { defineToolConfig, getRssItems } from '../utils';

export default defineToolConfig({
  name: 'get-9to5mac-news',
  description: '获取 9to5mac 新闻',
  func: () => getRssItems('https://9to5mac.com/feed/'),
});
