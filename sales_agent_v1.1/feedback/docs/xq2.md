
1. sales_agent_v1.1/feedback/feedback_stage1.html 页面做下修改：
```
设备优先：Mobile First（大多数用户会通过手机短信/邮件点开）。
视觉焦点：首屏展示项目图片，建立情感连接。
动态逻辑：如果用户回答“没联系”，就不应该展示“报价对比”题目（否则逻辑不通）。
🎨 页面布局架构 (Wireframe)
1. Header (顶部导航)
Logo: Emily's Smart Quote
Title: Project Check-in
2. Hero Section (项目唤醒区) —— 新增需求
这是用户点进来第一眼看到的内容，用于确认身份和项目。
布局建议：左侧卫星地图、右侧 3D 房屋
文字信息：
Address: {{address_street}}
Plan Selected: {{plan_name}} (e.g., The Smart Starter)
Est. Price: {{ai_estimated_price}} (用户当时看到的 AI 价格，帮助回忆)
3. Form Section (动态问卷区)
这是交互的核心。
📝 题目详细设计 (带逻辑)
Q1. 安装商响应监督 (Gatekeeper Question)
Have you heard from {{installer_name}} regarding this project?
(您收到安装商的联系了吗？)
🔘 Yes, we've been in touch. -> (触发显示 Q2, Q3)
🔘 No, not yet. -> (跳过 Q2, Q3，直接显示 Q4)
UI 反馈：若选 No，下方出现一行小字提示："Thanks for letting us know. We will send them a reminder right away."
Q2. 报价偏差验证 (Calibration)
(仅当 Q1 = Yes 时显示)
How did their final quote compare to Emily's AI estimate ({{ai_estimated_price}})?
(他们的最终报价与 AI 预估价相比如何？)
🔘 It was Cheaper (比 AI 便宜)
🔘 About the same (差不多)
🔘 It was More Expensive (比 AI 贵)
Q3. 真实数据收集 (Data Collection)
(仅当 Q1 = Yes 时显示)
Would you be willing to share the final quote amount?
This helps Emily learn and improve accuracy for future Aussie families.
(您愿意分享最终的报价金额吗？这将帮助 AI 学习并提高准确度。)
$ [ Input Field ] (数字键盘，非必填 Optional)
Placeholder: e.g., 4500
Q4. 开放留言 (Feedback)
(所有人可见)
Anything else you'd like to share?
(还有其他想说的吗？)
[ Text Area ]
Placeholder: e.g., The installer was very professional / The AI design missed my skylight...
5. Footer (提交)
Button: [ Submit Feedback ]

```
- 图片素材：sales_agent_v1.1/feedback/pic 目录
- 文案素材：
- 地址：65 Astoria Blvd, Hilbert WA 6112
- 系统信息及报价： 
Plan: The Smart Starter
Estimated Investment: $14,520 - $16,048
(Includes an estimated $9,009 in Government & Installer Rebates. Subject to eligibility.)


2. sales_agent_v1.1/feedback/feedback_thankyou.html
去掉 下面的Return to Home 按钮 和 S

3. sales_agent_v1.1/feedback/feedback_stage2.html
五角星默认是无填充颜色的，点击才会有黄色五角星填充效果。

4. 对应的 Logo 都改一下。

