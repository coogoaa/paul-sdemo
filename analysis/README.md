# analysis 目录说明

本目录用于存放 **数据分析相关的代码与文档**，与前端静态站点解耦。

## 目录结构建议

```text
analysis/
  README.md          # 本说明
  scripts/           # Python 分析脚本（纳入 git 管理）
  notebooks/         # Jupyter Notebook（可选，纳入 git 管理）
  data_local/        # 本地数据与中间结果（不纳入 git）
```

> 其中 `data_local/` 建议在仓库根目录的 `.gitignore` 中单独忽略，例如：`analysis/data_local/`。

## 放置约定

- **分析脚本**
  - 统一放在 `analysis/scripts/` 下，例如：
    - `analysis/scripts/export_report.py`
    - `analysis/scripts/clean_data.py`
  - 这些脚本会被 git 跟踪，方便版本管理与多机同步。

- **Notebook**
  - 若需要可视化探索或展示过程，可放在 `analysis/notebooks/` 下。
  - 建议控制大小，避免在 Notebook 中嵌入过大的图片或输出。

- **本地数据与输出**
  - 所有体积较大的原始数据、导出结果、中间 CSV 等，统一放在 `analysis/data_local/` 或现有的 `datas/` 目录下。
  - 这些目录应通过 `.gitignore` 忽略，不推送到远程仓库，也不会参与 GitHub Pages 部署。

## 与 GitHub Pages 的关系

- GitHub Pages 只会部署 CI 中构建的 `site/` 目录内容（如 `gs-admin/`、`demo_html/`、`index.html` 等）。
- `analysis/` 下的脚本与数据 **不会被复制到 `site/` 中**，不会影响线上静态站点。

通过这种结构，可以在同一个仓库里同时维护：
- 静态前端页面（对外展示，通过 GitHub Pages 部署）；
- 分析代码与文档（内部使用，通过 git 做版本管理），互不干扰。
