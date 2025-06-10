# 🔥 Trends Hub

[![smithery badge](https://smithery.ai/badge/@baranwang/mcp-trends-hub)](https://smithery.ai/server/@baranwang/mcp-trends-hub)
[![NPM Version](https://img.shields.io/npm/v/mcp-trends-hub)](https://www.npmjs.com/package/mcp-trends-hub)
![NPM License](https://img.shields.io/npm/l/mcp-trends-hub)

基于 Model Context Protocol (MCP) 协议的多源新闻服务

## 示例效果

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/case-dark.png">
  <img src="./assets/case-light.png" alt="Trends Hub 示例">
</picture>

## ✨ 特性

- 📊 **精选新闻** - 提供纽约时报、华尔街见闻、BBC、华盛顿邮报、新华网、人民日报等热点资讯
- 🔄 **实时更新** - 保持与源站同步的最新热点数据
- 🧩 **MCP 协议支持** - 完全兼容 Model Context Protocol，轻松集成到 AI 应用
- 🎨 **灵活定制** - 通过环境变量轻松调整返回字段

## 📖 使用指南

首先需要了解 [MCP](https://modelcontextprotocol.io/introduction) 协议，然后按照以下配置添加 Trends Hub 服务

不同的 MCP 客户端实现可能有所不同，以下是一些常见的配置示例：

### JSON 配置

<!-- usage-json-start -->
```json
{
  "mcpServers": {
    "trends-hub": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-trends-hub@1.6.2"
      ]
    }
  }
}
```

<!-- usage-json-end -->

### 命令行配置

<!-- usage-bash-start -->
```bash
npx -y mcp-trends-hub@1.6.2
```

<!-- usage-bash-end -->

### 安装

#### 使用 Smithery 安装

通过 [Smithery](https://smithery.ai/server/@baranwang/mcp-trends-hub) 安装 Trends Hub，适用于 Claude Desktop 客户端：

```bash
npx -y @smithery/cli install @baranwang/mcp-trends-hub --client claude
```

（以下仅适用于 MCP 模型客户端）

### 配置环境变量

### `TRENDS_HUB_HIDDEN_FIELDS` - 隐藏的字段列表

通过此环境变量可控制返回数据中的字段显示：

- 作用于所有工具：`{field-name}`，例如 `cover`
- 作用于特定工具：`{tool-name}:{field-name}`，例如 `get-toutiao-trending:cover`

多个配置用西文逗号分隔，例如：

```jsonc
{
  "mcpServers": {
    "trends-hub": {
      "command": "npx",
      "args": ["-y", "mcp-trends-hub"],
      "env": {
        "TRENDS_HUB_HIDDEN_FIELDS": "cover,get-nytimes-news:description" // 隐藏所有工具的封面返回和纽约时报新闻的描述
      }
    }
  }
}
```


## 🛠️ 支持的工具

<!-- tools-start -->
| 工具名称 | 描述 |
| --- | --- |
| get-bbc-news | 获取 BBC 新闻最新国际要闻 |
| get-nytimes-news | 获取纽约时报新闻，包含国际政治、经济金融、社会文化、科学技术及艺术评论的高质量英文或中文国际新闻资讯 |
| get-people-news | 获取人民日报政治新闻 |
| get-wallstreetcn-news | 获取华尔街见闻最新资讯 |
| get-washington-post-news | 获取华盛顿邮报的国际新闻 |
| get-xinhuanet-news | 获取新华网英文频道国际新闻 |


<!-- tools-end -->


## 鸣谢

- [DailyHotApi](https://github.com/imsyy/DailyHotApi)
- [RSSHub](https://github.com/DIYgod/RSSHub)
