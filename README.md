# PCL Intelligence Homepage

一个可以在 PCL2 启动器上使用 Google Gemini 或其他大模型的主页。

> [!NOTE]
> 现在可以直接在 Plain Craft Launcher 2 启动器内的 `联网更新` 填写 `https://pclintelligence.19991230.xyz`。

## 部署方法

### 前言
> [!TIP]
> 当前未适配全局 URL（即主页按钮发送对 Gemini 请求的链接），部分文件指向的链接仍为 `https://pclintelligence.19991230.xyz`。如需自行部署，请自行更改相关链接文件：
> - templates/index.html
> - templates/empty.html

> [!WARNING]
> 1. 请务必按照以下指示部署你的 PCL Intelligence Homepage，不当的操作可能会导致你的 API Key 被泄露。
> 2. 当前操作会导致**后续更新无法及时推送到你 Fork 后的仓库内**，请慎重考虑。
> 3. 请关注 Vercel Usage 使用情况（位于 [Vercel 主菜单](https://vercel.com) 左侧），需重点关注 `Fluid Active CPU` 和 `Edge Requests` 使用量。请不要用超了。更多 Usage Limit 请查看主菜单横条上的 `Usage` 选项。

以下是来自 Google AI 文档中 **免费计划** 的 API 速率限制：

| 模型                | 每分钟请求数  | 每分钟输入数（令牌）       | 每日请求数   |
|----------------------|------|-----------|-------|
| Gemini 2.5 Pro       | 5    | 250,000   | 100   |
| Gemini 2.5 Flash     | 10   | 250,000   | 250   |
| Gemini 2.5 Flash-Lite| 15   | 250,000   | 1,000 |
| Gemini 2.0 Flash     | 15   | 1,000,000 | 200   |
| Gemini 2.0 Flash-Lite| 30   | 1,000,000 | 200   |


### 需求
- 一个 [Vercel](https://vercel.com/signup) 账号：用于部署主页后端。
- [Google AI Studio API 密钥](https://aistudio.google.com/apikey)（香港地区不支持访问 Google AI Studio）：用于请求模型。
    - 如需请求多个 API Key 用于后续的多 API Key 模式，请从[https://console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate) 创建多个项目，后在 AI Studio 中创建 API Key。遇到问题请自行 Google。

### 部署
1. [Fork 本仓库](https://github.com/Ad-closeNN/PCL-Intelligence-Homepage/fork) ，点击 **Create Fork** 按钮即可 Fork。
2. 将可见性改为 **私密**。
    1. 在仓库顶端点击 **Settings**。
    2. 滑至底部，点击 **Leave fork network** 按钮并确认操作。 ![Leave fork network](README/Leave%20fork%20network.png)
    3. 等待10至30秒，使 Fork 后的仓库脱离 Fork 网络。
    4. 刷新页面，待 **Danger Zone** 里的 **Change visibility** 按钮可用后，点击 **Change visibility** 按钮并确认操作。 ![Change visibility](README/Change%20visibility.png)
3. 更改 config/api_key 文件，删掉原有内容，把从 [Google AI Studio](#需求) 申请的 API Key 以 **一行一个 Key** 的格式填入。
4. 使用 Vercel 部署：[Create New Project](https://vercel.com/new)

    需要填写相关变量:
    - 使用**单个 API 密钥**（如需使用多个 API 密钥，请勿填写此变量）：
        - Env Name: `api_key`
        - Env Value: `你的 API 密钥`
    - 使用**多个 API 密钥**，**不能填写**上面的 `api_key`：
        - Env Name: `mode`
        - Env Value:
            - `local`：本地获取 API Key，位于 config/api_key，一行一个 API Key。
            - URL 链接：如 `https://google-api-key.pclc.cc`，**必须以 http 开头**，返回的内容需为**单个 API Key**。
5. （可选、**建议**）在 Vercel 绑定自定义域名（中国大陆网络连接 `vercel.app` 比较困难）。
6. （可选、**不建议**）对 Vercel Anycast IP 进行优选。[LINUX DO 文章](https://linux.do/t/topic/128871)
7. 在 PCL2 启动器选择 `联网更新`，输入从 Vercel 部署的根 URL，例如 `https://abc.vercel.app` 或 `https://intelligence.pcl-community.org`。


## 开源项目

此项目使用到了以下项目：

- [Light-Beacon/HomepageBuilder](https://github.com/Light-Beacon/HomepageBuilder) （本项目已对其进行部分更改，已使用相同的开源许可证 **AGPL-3.0 License**）
    - 本项目使用的更改后的同许可证源代码可在 [Ad-closeNN/HomepageBuilder](https://github.com/Ad-closeNN/HomepageBuilder) 查看

- [Google Fonts - Material Symbols & Icons](https://fonts.google.com/icons)

## TODO

- 优化加载速度
- 适配全局 URL
- 支持解析通过 URL 获取列表（['sk1','sk2','sk3']）形式的 API Key
- 支持当 `api_key` 和 `mode` 同时出现的时候优先选择 `mode` 方式。

---

~~不管了能用就行~~ 如果有大佬们能改进的地方，欢迎 PR