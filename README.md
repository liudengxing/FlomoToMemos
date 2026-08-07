# Flomo To Memos

将 flomo（浮墨笔记）导出的 HTML 数据迁移到 memos，支持**文字内容 + 图片附件 + 原始创建时间**。

## 实现思路

1. `servicer.py` — 解析 flomo 导出 HTML，生成 `flomo/myMemos.json`
2. `controller.py` — 读取 JSON，通过 memos API 上传内容和图片

## 当前环境

| 组件 | 版本 |
|------|------|
| Python | >= 3.10 |
| memos | >= v0.22（使用 v1 API：`/api/v1/memos`、`/api/v1/attachments`） |
| flomo | 全版本通用（使用 HTML 导出，解析 `memos` class 结构的 DOM） |

## 使用方法

### 1. 导出 flomo 数据

在 flomo 中导出笔记，下载的 HTML 文件放入 `flomo/` 文件夹。默认读取 `flomo/index.html`，文件名不同的话改 `servicer.py` 第 4 行。

### 2. 配置

- **修改 `memos/api.py` 的 `Host`** — 你的 memos 站点地址，结尾不加斜杠
- **填写 `token.txt`** — memos 的 Access Token（设置 → 我的账号 → Access Tokens）

### 3. 安装依赖

```bash
pip install beautifulsoup4 requests
```

### 4. 运行

```bash
# 第一步：解析 flomo 数据
python servicer.py

# 第二步：上传到 memos
python controller.py
```

图片附件多的建议先在 memos 里配置好对象存储。

### 5. 不满意？回滚

运行 `controller.py` 中的 `delete()` 方法删除已上传内容，再去资源库一键清空未使用图片。

## API 兼容说明

memos v1 相比旧版 API 有这些变化（本项目已适配）：

| 项目 | 旧版 | v1 |
|------|------|----|
| 创建 memo | `POST /api/v1/memo` | `POST /api/v1/memos` |
| 上传附件 | `POST /api/v1/resource/blob` (multipart) | `POST /api/v1/attachments` (base64 JSON) |
| 时间字段 | `createdTs` (Unix 秒) | `createTime` (ISO 8601 字符串) |
| 附件关联 | 创建 memo 时传 `resourceIdList` | 先建 memo，上传附件时带 `memo` 字段 |
