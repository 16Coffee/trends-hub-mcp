export const tools = Promise.all([
  import('./bilibili'),
  import('./douban-movie'),
  import('./douyin'),
  import('./toutiao'),
  import('./weibo'),
  import('./zhihu'),
]);
