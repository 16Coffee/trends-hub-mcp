import { defineToolConfig, getRssItems } from '../utils';

export default defineToolConfig({
  name: 'get-xueqiu-hot-posts',
  description: '获取雪球热门帖子',
  func: async () => {
    return getRssItems('https://rsshub.app/xueqiu/hots');
  },
});
