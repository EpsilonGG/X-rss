# X-rss

X-rss 是一个用来把公开的 X/Twitter 账号内容转换成 RSS 订阅文件的小工具。

简单说，你可以在 `accounts.yaml` 里写上想关注的 X/Twitter 用户名，然后运行这个项目。项目会去公开网页抓取这些账号的最新内容，并在 `feeds/` 文件夹里生成对应的 RSS 文件。

生成后的 RSS 文件可以给 RSS 阅读器使用，例如 FreshRSS、Inoreader、NetNewsWire、Reeder 等。

## 这个项目能做什么

- 读取你填写的 X/Twitter 用户名。
- 通过 XCancel 这类公开网页获取账号内容。
- 把获取到的内容整理成 RSS 文件。
- 每个账号生成一个 RSS 文件，例如 `feeds/OpenAI.xml`。
- 可以配合 GitHub Actions 定时自动更新。

## 适合谁使用

这个项目适合想用 RSS 订阅公开 X/Twitter 账号的人。

你不需要理解项目内部代码，只需要知道三件事：

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

## 添加要订阅的账号

打开项目根目录下的 `accounts.yaml` 文件。

示例：

```yaml
accounts:
  - username: OpenAI
  - username: github
```

这里的 `username` 就是 X/Twitter 账号名，不需要加 `@`。

例如你想订阅 `@OpenAI`，就写：

```yaml
- username: OpenAI
```

如果想订阅多个账号，就继续往下加：

```yaml
accounts:
  - username: OpenAI
  - username: github
  - username: nasa
```

## 修改抓取来源和输出位置

一般情况下不用改这个文件。

如果你确实需要修改，可以打开 `config/config.yaml`：

```yaml
provider:
  endpoints:
    - https://xcancel.com

http:
  timeout: 20

rss:
  output: feeds/
```

其中：

- `https://xcancel.com` 是用来读取公开 X/Twitter 内容的网站。
- `timeout: 20` 表示最多等待 20 秒。
- `feeds/` 表示 RSS 文件会生成到 `feeds` 文件夹。

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
- XCancel 临时无法访问。
- 网页结构变化，导致解析失败。

### RSS 阅读器不能直接读取本地文件

很多 RSS 阅读器需要一个网址，而不是电脑里的本地文件。可以把生成的 `feeds/` 文件夹发布到 GitHub Pages 后再订阅。

## 当前项目结构

下面是项目里几个主要文件夹的作用，不需要理解代码也可以使用：

```text
accounts.yaml          你要订阅的账号列表
config/                项目配置
fetchers/              负责下载网页内容
parsers/               负责把网页内容整理成推文数据
exporters/             负责生成 RSS 文件
feeds/                 生成后的 RSS 文件
main.py                运行入口
```
