# GitHub Pages 部署问题排查与最佳实践

## 1. 背景

- 仓库：`coogoaa/paul-sdemo`
- 目标：
  - 托管 `gs-admin/login.html`、`gs-admin/dashboard_v2.html` 等静态页面到 GitHub Pages。
  - 访问路径示例：
    - `https://coogoaa.github.io/paul-sdemo/gs-admin/login.html`
    - `https://coogoaa.github.io/paul-sdemo/gs-admin/dashboard_v2.html`

## 2. 问题现象

- 根路径 `https://coogoaa.github.io/paul-sdemo/` 可以打开旧内容。
- 新增的 `gs-admin` 页面访问 404。
- GitHub Actions 中 "pages build and deployment" 工作流：
  - 10 月 16 日之前为绿色成功。
  - 之后所有运行均失败，集中在 **build / Upload artifact** 步骤。
- 典型错误：
  - `Error: Process completed with exit code 1.`
  - 在尝试只上传部分目录时曾出现：
    - `tar: index.html\n./gs-admin ...: Cannot open: No such file or directory`

## 3. 根因分析

1. **仓库体积与文件数量过大**
   - 仓库约 700+ MB，包含大量与静态站点无关的数据与输出：
     - `PVGIS/node_modules`
     - `datas/` 及其 `output/` CSV
     - `屋顶发电量/output`
     - `方案计算 1014/` 及图表
     - `proposal/outputs/` 等。
   - GitHub Pages 默认会将整个仓库打包成 artifact 上传，导致上传阶段超限，构建失败。

2. **默认 Pages + Jekyll 部署方式的局限**
   - 初始配置：Pages Source = `main` 分支 / `(root)`，使用 Jekyll 构建。
   - 即便增加 `.nojekyll` 禁用 Jekyll，仍然需要打包/上传整个仓库，问题没有根本解决。

3. **自定义 Actions workflow 初版问题**
   - 初版 `deploy.yml` 使用：
     - `actions/configure-pages@v4`
     - `actions/upload-pages-artifact@v3`
     - `actions/deploy-pages@v4`
   - 一开始配置 `path: '.'`，仍然上传整个仓库 → 继续超限。
   - 之后尝试用多行 `path: |` 同时列出多个目录，`upload-pages-artifact` 内部的 `tar` 将整段文本当成一个文件名解析，导致：
     - `tar: index.html\n./gs-admin ...: Cannot open`

> 结论：真正的问题不在前端 HTML，而在于 **部署范围过大 + artifact 配置不当**。

## 4. 最终解决方案

### 4.1 清理和忽略不需要部署的大文件

1. 更新 `.gitignore`，忽略：
   - 环境与依赖：
     - `.venv/`
     - `node_modules/`
     - `.DS_Store` 等。
   - 大体积数据与导出：
     - `datas/`
     - `方案计算 1014/`
     - `屋顶发电量/`
     - `output/`、`outputs/`、`**/output/`、`**/outputs/`
     - 所有 `*.csv`。
   - 一些仅本地分析或文档目录（如 `prd/` 等）。

2. 使用 `git rm -r --cached` 将已提交的大目录从 Git 跟踪中移除，然后 commit + push。

### 4.2 新增根目录入口页面

- 在仓库根目录加入 `index.html`，作为统一入口：
  - 提供跳转到：
    - `gs-admin/login.html`
    - `gs-admin/dashboard.html`
    - `gs-admin/dashboard_v2.html`。

### 4.3 改用 GitHub Actions 部署 Pages

1. 在 `.github/workflows/deploy.yml` 中定义自定义 workflow，大致结构：

   - 触发条件：
     - push 到 `main`。
     - 手动执行 `workflow_dispatch`。
   - 权限：允许写 `pages`、`id-token`。
   - 步骤包括：
     - Checkout 代码。
     - Setup Pages。
     - **Prepare static site directory：构建 `site/` 目录。**
       - 创建 `site/` 目录。
       - 拷贝需要对外暴露的目录/文件：
         - `index.html` → `site/index.html`
         - `gs-admin` → `site/gs-admin`
         - `demo_html` → `site/demo_html`
         - `404page` → `site/404page`
         - `installer_page` → `site/installer_page`
         - `sales_agent_v1.1` → `site/sales_agent_v1.1`
         - `roof_rush` → `site/roof_rush`
         - `Payback` → `site/Payback`
         - `Review_page` → `site/Review_page`。
       - 不复制任何数据、output 或分析脚本目录。
     - `upload-pages-artifact`：只上传 `./site`。
     - `deploy-pages`：发布到 GitHub Pages。

2. 在 GitHub 仓库 Settings → Pages 中，将：
   - **Source** 设置为：`GitHub Actions`。

### 4.4 部署结果

- Actions 中最新一次 "Deploy to GitHub Pages" 为绿色成功（deploy job 成功）。
- 实际访问：
  - `https://coogoaa.github.io/paul-sdemo/` 正常。
  - `https://coogoaa.github.io/paul-sdemo/gs-admin/login.html` 正常。
  - `https://coogoaa.github.io/paul-sdemo/gs-admin/dashboard_v2.html` 正常。

## 5. 后续静态页面部署流程

只要页面位于已经复制到 `site/` 的目录（例如 `gs-admin/` 或 `demo_html/`），后续部署步骤非常简单：

1. 在本地修改或新增静态页面（HTML/CSS/JS）。
2. `git add` + `git commit` + `git push` 到 `main` 分支。
3. 等待 GitHub Actions 中 "Deploy to GitHub Pages" 工作流变成绿色成功。
4. 通过对应 URL 访问即可。

> 若新增一个新的目录希望对外暴露，例如 `new-demo/`，只需：
> - 在仓库根目录创建 `new-demo/` 并放入页面；
> - 在 `deploy.yml` 的 `Prepare static site directory` 步骤中增加：
>   `[ -d new-demo ] && cp -R new-demo site/new-demo`；
> - 提交并推送后，部署成功即可访问 `https://coogoaa.github.io/paul-sdemo/new-demo/...`。

## 6. 分析脚本与数据管理（方案 A）

本项目除了静态站点，还有一部分分析脚本与数据。建议分开管理：

### 6.1 分析脚本（需要纳入版本管理）

- 采用 **方案 A**：分析脚本纳入 git 管理，便于回溯与多机同步。
- 调整 `.gitignore`：
  - 保留对 `.venv/`、`__pycache__/`、`*.pyc` 等的忽略。
  - **移除对 `*.py` 的忽略规则**，让分析脚本重新被 git 追踪。
- 建议目录结构：

```text
analysis/
  scripts/        # Python 脚本
  notebooks/      # Jupyter Notebook（如有）
  data_local/     # 本地数据（不进入 git）
```

- 在 `.gitignore` 中忽略：
  - `analysis/data_local/`（或其他本地数据目录）。
- 优点：
  - 脚本有版本历史，多人协同简单。
  - 不会影响 GitHub Pages，因为部署只取 `site/` 中的内容。

### 6.2 数据文件（不建议放入 GitHub Pages 仓库）

- 原始数据、大体积导出、一次性分析结果等：
  - 统一放在 `datas/`、`analysis/data_local/` 等已忽略目录中。
  - 不随 repo 分发，也不参与 Pages 部署。
- 若需要长期保存且多人共享的数据：
  - 可以考虑放到单独仓库、对象存储或专门的数据版本管理工具（DVC 等），与本仓库解耦。

## 7. 出现问题时的排查步骤

1. **先看页面是否真的部署失败**
   - 强制刷新浏览器缓存（Cmd/Ctrl + Shift + R）。

2. **打开 GitHub Actions**
   - 查看最新一次 "Deploy to GitHub Pages" 工作流是否为绿色。
   - 若为红色：展开 `deploy` job，重点查看：
     - `Prepare static site directory`
     - `Upload artifact`
     - `Deploy to GitHub Pages`
     的错误信息。

3. **确认要访问的页面是否被复制到 `site/`**
   - 检查 `deploy.yml` 中 `Prepare static site directory` 步骤：
     - 是否对目标目录执行了 `cp -R ... site/...`。
   - 如果是新增目录但没有复制逻辑，需要补上一行对应的 `cp` 命令。

通过以上机制，可以在保持仓库分析能力的同时，让 GitHub Pages 部署过程稳定可控，只发布需要对外暴露的静态页面。
