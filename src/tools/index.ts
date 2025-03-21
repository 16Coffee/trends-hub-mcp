export const tools = Promise.all([
  import('./36kr'),
  import('./bilibili'),
  import('./douban'),
  import('./douyin'),
  import('./toutiao'),
  import('./weibo'),
  import('./zhihu'),
]);
