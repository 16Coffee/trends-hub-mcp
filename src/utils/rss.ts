import { XMLParser } from 'fast-xml-parser';
import { http } from './http';
import { logger } from './logger';

export const getRss = async (url: string) => {
  const resp = await http.get(url);
  const parser = new XMLParser();
  return parser.parse(resp.data);
};

export const getRssItems = async (url: string) => {
  const data = await getRss(url);
  logger.info(data);
  if (!Array.isArray(data.rss?.channel?.item)) {
    return [];
  }
  return (data.rss.channel.item as any[]).map((item) => {
    let category = '';
    if (typeof item.category === 'string') {
      category = item.category;
    }
    if (Array.isArray(item.category)) {
      category = item.category.join(', ');
    }
    return {
      title: item.title,
      description: item.description,
      category,
      author: item.author || item['dc:creator'],
      publish_time: item.pubDate,
      link: item.link,
    };
  });
};
