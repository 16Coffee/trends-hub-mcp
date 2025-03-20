# Trends Hub

热点趋势聚合 Model Context Protocol (MCP) 服务

## 使用方法

```jsonc
{
  "mcpServers": {
    "trends-hub": {
      "command": "npx",
      "args": ["-y", "mcp-trends-hub@latest"]
    }
  }
}
```

## 工具列表

| 工具名称              | 描述               |
| --------------------- | ------------------ |
| get-bilibili-rank     | 获取哔哩哔哩排行榜 |
| get-douban-new-movies | 获取豆瓣电影新片榜 |
| get-douyin-trending   | 获取抖音热榜       |
| get-toutiao-trending  | 获取今日头条热榜   |
| get-weibo-trending    | 获取微博热搜榜     |
| get-zhihu-trending    | 获取知乎热榜       |

更多工具正在开发中，欢迎提交 PR 或 Issue。

## 鸣谢

- [DailyHotApi](https://github.com/imsyy/DailyHotApi)
