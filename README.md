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