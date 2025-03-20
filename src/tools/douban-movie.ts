import { defineToolConfig, handleSuccessResult, http } from '../utils';
import { load } from 'cheerio';

export default defineToolConfig({
  name: 'get-douban-new-movies',
  description: '获取豆瓣电影新片榜',
  func: async () => {
    const resp = await http.get('https://movie.douban.com/chart', {
      headers: {
        'User-Agent':
          'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
      },
    });

    const $ = load(resp.data);
    const listDom = $('.article tr.item');
    return handleSuccessResult(
      ...listDom.toArray().map((item) => {
        const dom = $(item);
        const scoreDom = dom.find('.rating_nums');
        const score = scoreDom.length > 0 ? scoreDom.text() : '0.0';
        return {
          title: dom.find('a').attr('title'),
          score: score,
          cover: dom.find('img').attr('src'),
          description: dom.find('p.pl').text(),
          popularity: dom.find('span.pl').text().replace('(', '').replace(')', ''),
          url: dom.find('a').attr('href'),
        };
      }),
    );
  },
});
