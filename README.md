# X-rss

一个基于 GitHub Actions 的**Twitter/X RSS 聚合器**。

可生成标准 RSS，并发布到 GitHub Pages，供各类 RSS 阅读器订阅。

支持 Provider 自动切换，当某个公开实例不可用时，会自动尝试下一个 Provider，提高长期运行稳定性。

生成后的 RSS 文件可以给 RSS 阅读器使用，例如 FreshRSS、Inoreader、NetNewsWire、Reeder 等。

## 项目架构

```
X-rss/
│
├── app/                                      # 应用启动与流程编排层
│   │
│   ├── main.py                               # 程序入口
│   ├── runner.py                             # 主运行流程控制，不包含业务逻辑
│   ├── pipeline.py                           # 定义 Fetch→Parse→Export 的执行链
│   └── bootstrap.py                          # 创建并组装 Provider、Parser、Exporter 等对象
│
├── config/                                   # 配置管理层
│   │
│   ├── loader.py                             # 加载 yaml/json 配置
│   ├── models.py                             # Pydantic 配置模型定义
│   ├── validator.py                          # 配置合法性检查
│   ├── defaults.py                           # 默认配置参数
│   └── schema.yaml                           # 配置文件结构说明
│
├── domain/                                   # 核心业务模型层，与外部平台无关
│   │
│   ├── models/
│   │   ├── tweet.py                          # 统一内容模型
│   │   ├── author.py                         # 作者模型
│   │   ├── media.py                          # 图片/视频等媒体模型
│   │   ├── attachment.py                     # 附件模型
│   │   ├── account.py                        # 订阅账号模型
│   │   └── feed.py                           # RSS Feed抽象模型
│   │
│   ├── enums.py                              # 公共枚举
│   ├── types.py                              # 公共类型定义
│   └── exceptions.py                         # Domain异常定义
│
├── providers/                                # 外部平台适配层
│   │
│   ├── base.py                               # Provider统一接口定义
│   │
│   ├── twitter/                              # Twitter/X平台实现
│   │   ├── fetcher.py                        # Twitter数据获取
│   │   ├── parser.py                         # Twitter数据解析
│   │   └── config.py                         # Twitter专属配置
│   │
│   ├── mastodon/                             # Mastodon平台实现
│   │   ├── fetcher.py                        # Mastodon数据获取
│   │   ├── parser.py                         # Mastodon数据解析
│   │   └── config.py                         # Mastodon专属配置
│   │
│   └── registry.py                           # Provider注册与发现
│
├── infrastructure/                           # 基础设施实现层
│   │
│   ├── http/
│   │   ├── client.py                         # HTTP请求封装
│   │   ├── response.py                       # HTTP响应模型
│   │   ├── retry.py                          # 请求重试策略
│   │   └── headers.py                        # 请求Header管理
│   │
│   ├── logging/
│   │   └── logger.py                         # 日志系统
│   │
│   └── storage/
│       └── cache.py                          # 本地缓存与状态保存
│
├── exporters/                                # 输出格式转换层
│   │
│   ├── base.py                               # Exporter接口
│   ├── rss.py                                # RSS XML生成
│   └── jsonfeed.py                           # JSON Feed输出（未来）
│
├── processors/                               # 输出后处理Pipeline
│   │
│   ├── base.py                               # Processor接口
│   ├── rss_cleaner.py                        # RSS清理规范化
│   ├── deduplicator.py                       # 内容去重
│   └── formatter.py                          # 阅读器兼容格式调整
│
├── summarizers/                               # AI内容处理层
│   │
│   ├── base.py                               # AI摘要接口
│   ├── openai.py                             # OpenAI摘要实现
│   └── prompts/
│       └── default.txt                       # 摘要Prompt模板
│
├── publishers/                               # 发布渠道层
│   │
│   ├── base.py                               # 发布接口
│   ├── github_pages.py                       # GitHub Pages发布
│   └── telegram.py                           # Telegram发布适配
│
├── storage/                                  # 数据持久化
│   │
│   ├── feeds/                                # 原始RSS输出
│   ├── processed/                             # Processor处理后的RSS
│   └── summaries/                             # AI摘要结果
│
├── tests/                                    # 自动化测试
│   │
│   ├── domain/                               # Domain模型测试
│   ├── providers/                            # Provider测试
│   ├── parsers/                              # Parser测试
│   ├── exporters/                            # 输出测试
│   └── fixtures/                             # 测试数据样本
│
├── docs/                                     # 项目文档
│   │
│   ├── architecture.md                       # 架构说明
│   ├── provider.md                           # 如何新增Provider
│   ├── pipeline.md                           # 数据流说明
│   └── configuration.md                      # 配置说明
│
├── .github/
│   └── workflows/
│       ├── rss.yml                           # 定时运行RSS生成任务
│       └── ci.yml                            # Lint/Test自动检查
│
├── accounts.yaml                             # 用户订阅账号配置
├── config.yaml                               # 项目运行配置
├── requirements.txt                          # Python依赖
├── pyproject.toml                             # Python项目配置
├── README.md                                 # 项目介绍文档
└── LICENSE                                   # 开源许可证
```

## 适合谁使用

这个项目适合想用 RSS 订阅公开 X/Twitter 账号的人。

无需理解项目内部代码，只需要如下操作：

1. 在 `accounts.yaml` 里填写账号名。
2. 运行 `python main.py`。
3. 到 `output/feeds_processed/` 文件夹里找到生成的 RSS 文件。
4. 将xml后缀文件网址保存并改为 `https://raw.githubusercontent.com/<你的Github用户名>/<你在fork时起的项目名>/main/output/feeds_processed/<推特用户ID>.xml` 
`例： https://raw.githubusercontent.com/EpsilonGG/X-rss/main/output/feeds_processed/openAI.xml`
5. 把该网址用于你的RSS阅读器。
  

## 使用前准备

你需要先安装 Python。建议使用 Python 3.12 或更高版本。

安装好 Python 后，打开项目文件夹，在命令行里运行下面的命令安装依赖：

```powershell
pip install -r requirements.txt
```

依赖可以理解为“这个项目运行时需要用到的工具包”。

## 使用方法
```
1. Fork 本仓库

Fork 到自己的 GitHub 账号。

2. 配置账号

编辑 accounts.yaml：

accounts:
  - OpenAI
  - AnthropicAI
  - Nintendo

可根据需要添加或删除账号。

3. 配置参数

编辑：
config/config.yaml

可修改：
Provider 顺序
超时时间
重试次数
RSS 输出目录
GitHub Pages 配置等。

4. 启用 GitHub Actions
确保仓库已启用 GitHub Actions。

项目支持：
定时运行（Schedule）
手动运行（workflow_dispatch）

5. 获取 RSS

运行完成后将在：
output/feeds_processed/
生成对应可用 RSS。

例如：
output/feeds_processed/OpenAI.xml
也可通过 GitHub Pages 公开订阅。
```

## 运行项目

在项目根目录运行：

```powershell
python main.py
```

如果运行成功，你会看到类似这样的输出：

```text
============================================================
OpenAI
Status      : 200
ContentType : text/html; charset=utf-8
Bytes       : 215384
URL         : https://xcancel.com/OpenAI
Tweets      : 20
RSS         : feeds/OpenAI.xml
```

这表示项目已经成功读取了 `OpenAI` 这个账号，并生成了 RSS 文件。

## RSS 文件在哪里

生成的 RSS 文件会放在 `output/feeds_processed/` 文件夹里。

例如：

```text
feeds/OpenAI.xml
feeds/github.xml
feeds/nasa.xml
```

你可以把这些 XML 文件的访问地址添加到 RSS 阅读器里。

如果你把项目部署到 GitHub Pages，RSS 地址通常会类似这样：

```text
https://你的用户名.github.io/仓库名/feeds/OpenAI.xml
```

## 自动更新

项目里已经包含 GitHub Actions 配置：

```text
.github/workflows/update-feeds.yml
```

它的作用是让 GitHub 自动运行这个项目，并更新 `output/feeds_processed/` 文件夹里的 RSS 文件。

默认设置是每 24 小时运行一次，也可以在 GitHub 页面里手动运行。

## 常见问题

### 运行时提示找不到 Python

说明电脑还没有安装 Python，或者 Python 没有加入系统路径。请先安装 Python 3.12 或更高版本。

### 运行时提示缺少某个包

请先运行：

```powershell
pip install -r requirements.txt
```

### 某个账号没有生成内容

可能原因包括：

- 账号名写错了。
- 账号不是公开账号。
- Nitter/Xcancel 临时无法访问。
- 网页结构变化，导致解析失败。

### RSS 阅读器不能直接读取本地文件

很多 RSS 阅读器需要一个网址，而不是电脑里的本地文件。可以把生成的 `output/feeds_processed/` 文件夹发布到 GitHub Pages 后再订阅。
