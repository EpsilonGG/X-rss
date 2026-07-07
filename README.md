# X-rss

一个基于 GitHub Actions 的**Twitter/X RSS 聚合器**。

可生成标准 RSS，并发布到 GitHub Pages，供各类 RSS 阅读器订阅。

支持 Provider 自动切换，当某个公开实例不可用时，会自动尝试下一个 Provider，提高长期运行稳定性。

生成后的 RSS 文件可以给 RSS 阅读器使用，例如 FreshRSS、Inoreader、NetNewsWire、Reeder 等。

## 项目架构

```.
├── .github/
│   └── workflows/        # GitHub Actions
├── app/                  # 程序入口与调度
├── config/               # 项目配置
├── domain/               # 数据模型
├── exporters/            # RSS 导出
├── fetchers/             # Provider 实现
├── infrastructure/       # HTTP 等基础设施
├── parsers/              # HTML / RSS 解析
├── utils/                # 通用工具
├── feeds/                # 生成的 RSS 文件
├── accounts.yaml         # 订阅账号列表
├── main.py               # 程序入口
└── pyproject.toml
```

## 适合谁使用

这个项目适合想用 RSS 订阅公开 X/Twitter 账号的人。

无需理解项目内部代码，只需要知道三件事：

1. 在 `accounts.yaml` 里填写账号名。
2. 运行 `python main.py`。
3. 到 `feeds/` 文件夹里找到生成的 RSS 文件。

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
feeds/
生成对应 RSS。

例如：
feeds/OpenAI.xml
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

生成的 RSS 文件会放在 `feeds/` 文件夹里。

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

它的作用是让 GitHub 自动运行这个项目，并更新 `feeds/` 文件夹里的 RSS 文件。

默认设置是每 6 小时运行一次，也可以在 GitHub 页面里手动运行。

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

很多 RSS 阅读器需要一个网址，而不是电脑里的本地文件。可以把生成的 `feeds/` 文件夹发布到 GitHub Pages 后再订阅。
