- 地图选型：先用 Leaflet（免 Key）可以吗？后续再切换 Google Maps。 -- 可以，他是卫星地图么？
- 3D 深度：先做简化盒体 + 面板网格占位，可以吗？还是先用静态 2D 示意。- 先看下你的方案实现后的效果。
- 主题视觉：是否沿用 demo_grey 的灰色主题？有品牌色/Logo 吗。- 可以
- 价格假设与浮动：是否采用 ±10% 报价区间；是否显示“非最终报价”免责声明。- 可以，数值都是虚拟的，只是一个演示 demo
- 补贴提示：是否默认开启？文案是否使用“约 $XXXX”（占位自动计算或静态示例）。- 默认开启，补贴金额是虚拟的，只是一个演示 demo
- 留资字段：提交项与验证规则（姓名、电话/邮箱、联系时间）。- 可以
- 本地化：货币单位（AUD/¥）、数字格式、语言是否只保留中文。- AUD
-兜底文案：是否采用 docs/dialog_flow.md 中默认文案，是否需要更强的转化话术。- 可以先用这一版
- 埋点：是否需要接 GA/其他统计（若需，提供 ID）。- 不需要

----
分析下sales_agent_v1.1/generated-page-v1.1.html 这个页面。
获取地图的部分，如果我提供一个虚拟的地图图片，你是否可以实现缩放、拖动、点击屋顶的功能？
另外点击屋顶，我希望把屋顶的图层高亮显示，能否快速实现？需要我提供多大的图片尺寸？
还需要提供什么要素？
先说方案，先不要更改代码，

--
我还需要：
- 助手的头像更换为我想要的头像，地址我放在了 sales_agent_v1.1/Pic/TechBot_small.jpeg
- 为您生成的 3D 屋顶模型这个卡片的高度也适当调低一些。
- 如果 3D 屋顶的模型我想替换一下（一个假的），我需要什么格式的文件？

接下来：
- 3D 模型的窗口部分，我提供视频文件、gif 文件和 glb 文件，你看下哪种效果和实现方式更合适? 他们分别在 sales_agent_v1.1 下的目录中
- 地图页面，点击确认，应该有房屋屋顶高亮显示，在这个 demo 考虑下如何呈现一个假的效果


- 所有文案改为英文

- 如果我要替换 glb 文件，实现起来方便么，如果我把文件放到目录里。


- 报价部分
- <!-- Step 5: Plan interaction --> 中的


<!-- Step 6: Value presentation -->
- Estimated annual savings 要改为系统预算范围并提供一个区间值：
- 回本周期和自用率也要给出一个区间范围
- 电费节省金额需要在系统预算范围提供一个区间范围展示
- 提供一个简要说明，说明这个预算是初步估算，含税。单不含并网流程和补贴差异，为确保准确报价，请您提供详细信息。
- 支持复制报价信息及分享预算报价。
- 点击不同报价计划时，3D 模型要有切换效果


- Estimated annual savings 应该改为系统预算范围，并提供一个区间范围展示
- Payback period 和 Self-consumption 也应该是一个区间范围展示
- 提供一个简要说明，说明这个预算是初步估算，含税。单不含并网流程和补贴差异，为确保准确报价，请您提供详细信息。
- 支持复制报价信息及分享预算报价。
所有都是英文文案，你看下师傅实现了？

showStep?.(4); 当前是 3D 模型+ 方案滚动条 + Estimated annual savings 对吧
能否在 showStep?.(4) 的基础上，点击方案 下方不展示 Estimated annual savings 直接展示
Budget quote (range) 的内容，内容包括System budget (incl. tax) 、Estimated system size、Payback period、Self-consumption、Annual bill savings
在最底层 统一给出 tips 提示These are preliminary estimates incl. tax, excluding grid connection & subsidy differences. Provide details to receive an accurate quote.
然后是Copy、Share、Refine info 的按钮












