# Installer Branded Pages

这个目录包含为安装商定制的品牌页面。

## 文件说明

### 1. installer-branded-page.html
- **用途**: 移动端页面
- **布局**: 单栏布局，最大宽度 448px (max-w-md)
- **特点**: 
  - 包含移动端浏览器地址栏模拟
  - 左侧显示安装商 logo (lucas.gu.au)
  - 右上角显示 GreenSketch AI logo
  - 适配移动设备触摸操作

### 2. installer-branded-page-desktop.html
- **用途**: PC 桌面端页面
- **布局**: 双栏网格布局，最大宽度 1280px (max-w-7xl)
- **特点**:
  - 顶部导航栏设计
  - 左侧显示 RENOSTAIN 品牌 logo（闪电图标 + 品牌名称）
  - 右上角显示 GreenSketch AI logo 和名称
  - 内容区域采用左右双栏布局（聊天区 + 卡片区）
  - 更大的内边距和间距，适配桌面端显示

## 品牌元素

### RENOSTAIN Logo
- 橙色闪电图标配合双圆环设计
- 中心带有字母 "R"
- 品牌名称使用粗体 Arial 字体

### GreenSketch AI Logo
- 绿色渐变背景
- 白色层叠图形图标
- 代表 AI 驱动的太阳能平台

## 使用方式

1. 在浏览器中直接打开对应的 HTML 文件
2. 移动端页面建议在移动设备或浏览器开发者工具的移动模式下查看
3. 桌面端页面建议在标准桌面浏览器中查看

## 定制说明

如需修改安装商品牌信息：
- 修改 logo SVG 代码（第 39-48 行）
- 修改公司名称（第 51 行）
- 调整品牌颜色主题
