# paul-sdemo

静态演示与离线运行说明。

## 在线演示（GitHub Pages）
当你在仓库中启用 Pages 后，可通过如下地址访问演示页面：

```
https://coogoaa.github.io/paul-sdemo/sales_agent_v1.1/generated-page-v1.4_en.html
```

### 启用 GitHub Pages（一次性配置）
- 打开仓库：Settings → Pages
- Build and deployment:
  - Source：Deploy from a branch
  - Branch：main，Folder：/root
- 保存后等待 1–3 分钟生效（首次可能更久）

### 建议的仓库根文件
- `.nojekyll`：避免 Jekyll 处理，确保 `vendor/`、`3d/` 这类目录可直接静态访问。
- （可选）`index.html`：跳转到 `sales_agent_v1.1/generated-page-v1.4_en.html`，便于分享。

## 离线运行（file:// 直接双击）
将以下目录与文件一起复制到目标机器，直接双击页面即可运行：

```
sales_agent_v1.1/
├─ generated-page-v1.4_en.html
├─ 3d/43792833-0cb3-4884-85ef-1fb678777d5c/base_basic_shaded.glb
├─ vendor/
│  ├─ model-viewer/model-viewer-umd.min.js
│  ├─ lucide/lucide.min.js
│  ├─ inter/inter.css  （可选：若使用本地字体，需要 font-files/*.woff2）
│  └─ tailwind/tailwind.min.css （当前为空占位；线上用 CDN，需彻底离线可预编译 CSS）
└─ Pic/（页面引用到的图片）
```

说明：
- 我们采用 `model-viewer` 的 UMD 构建（非模块），兼容 `file://` 打开。
- Tailwind 目前走 CDN（本地有空占位），若需完全离线请生成并替换为预编译 CSS。
- Inter 字体如不下载 woff2 文件，控制台会有 404，不影响功能。

## 常见问题
- 页面空白或 3D 区域报错：检查控制台是否有 `custom element not defined`。
  - 解决：确认 `vendor/model-viewer/model-viewer-umd.min.js` 存在且可访问。
- 3D 模型不显示：检查 `.glb` 路径是否与 HTML 中的 `src` 一致（大小写、层级必须匹配）。
- 本地服务器下 Tailwind 报 MIME 警告：使用 `file://` 打开或提供正确的 `text/css` 响应类型；或仅保留 CDN。

## 私有仓库与公开访问
- 个人/组织的 GitHub Pages 默认是公开访问的，即使源码仓库是私有，站点也会公开（源码仍保持私有）。
- 仅企业版（GitHub Enterprise）支持对 Pages 进行访问控制（限制组织成员访问）。
- 因此：如果你将本仓库改为私有，且仍启用 Pages，其他人依然可以访问该站点链接；若希望不公开，请关闭 Pages 或使用企业版的访问控制。

## 目录结构（节选）
```
sales_agent_v1.1/
  ├─ generated-page-v1.4_en.html
  ├─ vendor/
  ├─ 3d/
  └─ Pic/
```

---
如需我将 Inter 字体与 Tailwind 完全本地化、添加 `.nojekyll` 与主页跳转文件、或配置 `docs/` 目录下的发布方式，请说明需求。

---

## Streamlit 界面：光伏与储能报价演示

本仓库在 `proposal/` 目录下提供了一个基于 Streamlit 的交互式应用：

- 入口：`proposal/app.py`
- 计算引擎：`proposal/calc_engine.py`（与 `proposal/proposal.py` 的公式保持一致）
- 参数模型：`proposal/schemas.py`
- 文档：
  - 计算逻辑详解：`proposal/docs/proposal_logic.md`
  - 开发计划：`proposal/docs/dev_plan.md`

### 环境准备（推荐使用 venv）

```bash
# 在 macOS/Apple Silicon 上，优先使用 Homebrew Python（arm64）
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

### 启动

```bash
# 如 8501 被占用，可改 8502
python -m streamlit run proposal/app.py --server.headless true --server.port 8502 --server.address localhost
```

启动后访问：

- http://localhost:8502

### 功能说明

- 侧边栏参数表单：编辑关键输入参数，点击“应用参数并计算”。
- Tab 1：新建系统 — 详细版/简化版 对比
  - 并列展示两套方案的核心指标表格。
  - 鼠标悬停在第一列单元格，可查看对应行的“计算公式/口径说明”。
- Tab 2：储能扩容（Battery Retrofit）
  - 展示 A/B/C/D 容量档的节省、成本、回本年限等。
  - 同样支持首列逐行悬停查看计算说明。
- Tab 3：计算逻辑（文档）
  - 直接渲染 `proposal/docs/proposal_logic.md`，便于对照核验公式。
- 导出 Excel：侧边栏提供“一键导出（详细版/简化版）”，输出目录为：`proposal/outputs/`。

### 注意事项

- 出于安全与可控性，`proposal/app.py` 导出 Excel 时仅加载 `proposal/proposal.py` 的函数定义，不执行其底部示例写文件逻辑；因此不会再访问 `/mnt/data/`。
- 若遇到 `pydantic_core` 架构不兼容（x86_64 vs arm64），请使用上面的 venv 流程安装依赖。