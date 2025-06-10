import { defineToolConfig, getRssItems } from '../utils';

export default defineToolConfig({
  name: 'get-seekingalpha-news',
  description: '获取 Seeking Alpha 热点新闻',
  func: async () => {
    return getRssItems('https://seekingalpha.com/market_currents.xml');
  },
});
