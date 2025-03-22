import { defineToolConfig, getRss, getRssItems } from '../utils';

export default defineToolConfig(async () => {
  const rssUrl = process.env.TRENDS_HUB_CUSTOM_RSS_URL;
  if (!rssUrl) {
    throw new Error('TRENDS_HUB_CUSTOM_RSS_URL not found');
  }
  const resp = await getRss(rssUrl);
  if (!resp?.rss?.channel) {
    throw new Error('Invalid RSS feed');
  }
  let description = resp.rss.channel.title;
  if (resp.rss.channel.description) {
    description += ` - ${resp.rss.channel.description}`;
  }
  return {
    name: 'custom-rss',
    description,
    func: () => getRssItems(rssUrl),
  };
});
