# English Learning · 英语学习札记

一个面向中国学生的静态英语学习博客。中文为主，穿插英文；不展示个人身份资料。首页统一显示“全部札记”，支持标题与摘要搜索、手机适配，还有可点击翻页的单词卡。初始保留一篇阅读示例，可替换为正式内容。

## 首次启用 GitHub Pages

代码推送后，打开仓库 **Settings → Pages**：

1. Source 选择 **Deploy from a branch**。
2. Branch 选择 **main**，目录选择 **/docs**，点击 Save。
3. 等待 Pages 部署完成，访问 https://shengzhiruchu.github.io/EnglishLearning/ 。

GitHub Free 需要公开仓库才能启用 Pages。这里只发布 `docs/`，文章源文件、生成脚本和 skill 不属于网站发布目录。通过 SSH Deploy key 推送的发布更新，首次配置后需实际验证 Pages 部署是否成功；仓库管理员负责网站设置。

## 目录

```text
site.json                        网站标题、简介、网址
templates/                       首页、文章页和公共 HTML 模板
assets/                          样式、交互、图标及后续图片
content/posts/                   每篇文章的 JSON 信息和 HTML 正文
content/words.json               首页单词卡的六组内容
scripts/build.py                 生成首页和所有已发布文章
scripts/check.py                 验证本地链接、图片与锚点
scripts/publish.py               生成、检查，可选提交与推送
docs/                            自动生成的网站，提交到 Git
skills/publish-learning-note/    可安装到老师助手的发布 skill
.github/workflows/check.yml      自动检查构建和输出一致性
```

## 本地预览

只需要 Python 3.10+ 和 Git，不需要安装额外 Python 库。运行：

```sh
python scripts/publish.py
python -m http.server 8000 --directory docs
```

打开 http://localhost:8000/ 。本地服务器仅供预览，线上不运行 Python。

## 新增文章

例如创建 `content/posts/my-new-note.json`：

```json
{
  "slug": "my-new-note",
  "title": "文章标题",
  "date": "2026-10-09",
  "summary": "文章的简短摘要。",
  "reading_minutes": 3,
  "draft": false,
  "example": false
}
```

同时创建同名的 `my-new-note.html`，只写正文片段：

```html
<p>文章开头。</p>
<h2>小标题</h2>
<p>正文内容。</p>
<blockquote><p lang="en">An English example.</p></blockquote>
```

slug 与文件名必须一致，无需填写分类。`draft: true` 的文章不会生成网页；`example: true` 的文章会标注“示例”。日期用于排序，不代表定时发布；未来日期的非草稿也会立即发布。正文为可信作者编写的 HTML，不接受不可信用户直接上传。

图片放到 `assets/images/my-new-note/`；文章正文引用 `../../assets/images/my-new-note/example.jpg`。不要把私钥、密码、未公开材料放进这个仓库。GitHub 项目网站有 `/EnglishLearning/` 前缀，使用现有相对路径规则，不写 `/assets/...` 这样的根路径。

生成程序自动更新首页列表、篇数和文章页。文章按照日期从新到旧显示。修改页面设计时编辑 `templates/` 或 `assets/`；不要直接修改 `docs/`，下次构建会重新生成它。

## 发布

首页单词卡内容保存在 `content/words.json`。点击卡片、左右按钮或聚焦卡片后按左右方向键，可循环切换六个词；Enter / 空格也可翻到下一张。不会自动轮播；偏好减少动态效果的设备直接切换。每个词沿用同一个纸张模板，配有不同的窗景颜色、音标、释义与两行原创例句。六词参考[新东方四级高频词整理](https://cet4-6.xdf.cn/202607/15278999.html)选取，不表示官方频次排名。修改该文件后同样重新生成并提交网站。

先同步仓库、编辑文章、预览确认，再运行：

```sh
python scripts/publish.py --push --message "Publish: 文章标题"
```

程序会生成网站、检查链接，把 `site.json`、文章、模板、资源及 `docs/` 的改动提交到 main，然后正常推送。不会强制推送，也不会提交其他目录里已有的工作。若没有内容变更则不会新增提交。Pages 部署需要一些时间，推送后查看仓库 Actions 和 Settings → Pages 的状态。

## 老师无需 GitHub 账号的设置

在老师实际运行助手的环境里生成专用 SSH 密钥；你将公钥添加到这个仓库的 **Settings → Deploy keys** 并勾选 **Allow write access**。私钥留在老师环境，不进入仓库。为这个本地仓库配置专用密钥和 Git 提交身份，测试读取与推送。写权限覆盖整个仓库。

将 `skills/publish-learning-note` 文件夹安装到老师所用助手的 skills 目录（具体位置取决于其 harness）。skill 已描述从文章整理、生成、检查到推送的流程；首次安装仍需要你完成 Git/Python、仓库位置和 SSH 授权设置。

## 验证

```sh
python scripts/build.py
python scripts/check.py
```

GitHub Actions 会运行同样的检查，并验证提交的 `docs/` 是否与源文件一致。首次搭建或改动发布流程时，还应实际检查线上文章链接。日常更新由 skill 完成，老师无需编辑首页。
