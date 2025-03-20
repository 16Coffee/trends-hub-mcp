import { z } from "zod";
import { cacheStorage, handleErrorResult, handleSuccessResult, http } from "../utils";
import { URLSearchParams } from 'node:url';
import { createHash } from 'node:crypto';
import type { ToolConfig } from "../types";

export const bilibiliRequestSchema = z.object({
  type: z.union([
    z.literal(0).describe('全站'),
    z.literal(1).describe('动画'),
    z.literal(3).describe('音乐'),
    z.literal(4).describe('游戏'),
    z.literal(5).describe('娱乐'),
    z.literal(188).describe('科技'),
    z.literal(119).describe('鬼畜'),
    z.literal(129).describe('舞蹈'),
    z.literal(155).describe('时尚'),
    z.literal(160).describe('生活'),
    z.literal(168).describe('国创相关'),
    z.literal(181).describe('影视'),
  ]).optional().default(0).describe('排行榜分区')
});


const mixinKeyEncTab = [
  46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28,
  14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54,
  21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
];

const getMixinKey = (orig: string): string =>
  mixinKeyEncTab
    .map((n) => orig[n])
    .join("")
    .slice(0, 32);

const encodeWbi = (params: Record<string, string>, imgKey: string, subKey: string): string => {
  // 过滤特殊字符
  const chrFilter = /[!'()*]/g;

  // 创建URL参数对象
  const search = new URLSearchParams();

  // 添加时间戳参数
  const paramsWithTs: Record<string, string> = {
    ...params,
    wts: Math.round(Date.now() / 1000).toString()
  };

  // 按照字典序遍历参数
  const sortedKeys = Object.keys(paramsWithTs).sort();
  for (const key of sortedKeys) {
    const value = paramsWithTs[key].toString().replace(chrFilter, "");
    search.set(key, value);
  }

  // 计算wbi签名
  const wbiSign = createHash('md5').update(search.toString() + getMixinKey(imgKey + subKey)).digest('hex');
  search.set("w_rid", wbiSign);

  return search.toString();
};

const getWbiKeys = async () => {
  const resp = await http.get("https://api.bilibili.com/x/web-interface/nav", {
    headers: {
      Cookie: "SESSDATA=xxxxxx",
      "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
      Referer: "https://www.bilibili.com/",
    }
  })
  const { img_url: imgUrl = '', sub_url: subUrl = '' } = resp.data.wbi_img

  const getFileNameFromUrl = (url: string) => url.slice(url.lastIndexOf("/") + 1, url.lastIndexOf("."));

  return {
    imgKey: getFileNameFromUrl(imgUrl),
    subKey: getFileNameFromUrl(subUrl),
  };
};


const getBiliWbi = async (): Promise<string> => {
  const CACHE_KEY = "bilibili-wbi";
  const cachedData = cacheStorage.getItem(CACHE_KEY)
  if (cachedData) {
    return cachedData
  }
  const { imgKey, subKey } = await getWbiKeys();
  const params = { foo: "114", bar: "514", baz: '1919810' };
  const query = encodeWbi(params, imgKey, subKey);
  cacheStorage.setItem(CACHE_KEY, query);
  return query;
};

const getBilibiliRankList = async (args: unknown) => {
  try {
    const { type } = bilibiliRequestSchema.parse(args);
    const wbiData = await getBiliWbi();
    const resp = await http.get(`https://api.bilibili.com/x/web-interface/ranking/v2?rid=${type}&type=all&${wbiData}`, {
      headers: {
        'Referer': 'https://www.bilibili.com/ranking/all',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
      },
    })
    return handleSuccessResult(resp.data)
  } catch (error) {
    return handleErrorResult(error);
  }
}

export const config: ToolConfig = {
  name: 'get-bilibili-rank',
  description: '获取B站排行榜',
  zodSchema: bilibiliRequestSchema,
  func: getBilibiliRankList,
}
