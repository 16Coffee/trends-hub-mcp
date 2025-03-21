export const tools = Promise.all([
  import('./bilibili'),
  import('./douban'),
  import('./douyin'),
  import('./toutiao'),
  import('./weibo'),
  import('./zhihu'),
]);
