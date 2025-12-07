
## 用户回收问卷
### 目的：
1. 对安装商的响应速度进行监督
2. 积累安装商的评价数据，了解终端用户对安装商的反馈信息
### 需求：
用户提交留资后会分为 2 个阶段，需要设计2 个评分页面，响应布局
1. 页面整体结构
```
移动优先、简洁快速、目标明确。用户是在帮你的忙，所以要让他们的操作尽可能简单。
通用页面元素
页头 (Header):
Emily's Smart Quote 的 Logo。
清晰的标题。
页脚 (Footer):
简单的感谢语。
提交后的感谢页面 (Thank You Page):
用户提交后，必须跳转到一个感谢页面，明确告知他们反馈已收到。例如：“Thank you! Your feedback helps us improve.”
```

2. 阶段 1：用户留资后，对安装商的相应速度进行监督，对报价偏差进行信息收集。
- 页面布局参考:
```
+----------------------------------------------------+
| [Emily's Smart Quote Logo]                         |
|                                                    |
|  Quick Check on Your Solar Plan                    |
| -------------------------------------------------- |
|                                                    |
|  Hi {{customer_name}},                             |
|  Thanks for helping us check in on your plan for   |
|  {{address_street}} with {{installer_company_name}}. |
|                                                    |
+----------------------------------------------------+
|                                                    |
|  1. Has the installer contacted you yet?           |
|                                                    |
|  [ ( ) Yes ]         [ ( ) No (Still waiting) ]    |
|   (大尺寸、易于点击的按钮样式)                       |
|                                                    |
+----------------------------------------------------+
|                                                    |
|  2. Was the final quote close to our AI estimate?  |
|                                                    |
|  [ Cheaper than AI ]  [ Similar to AI ]  [ More expensive ] |
|   (分段控件或大按钮样式)                               |
|                                                    |
+----------------------------------------------------+
|                                                    |
|  3. How easy was it to use our AI Sales Agent?     |
|                                                    |
|  ☆ ☆ ☆ ☆ ☆                                       |
|  (1-5星评分组件)                                     |
|                                                    |
+----------------------------------------------------+
|                                                    |
|              [    Submit Feedback    ]             |
|                  (清晰、显眼的CTA按钮)               |
|                                                    |
+----------------------------------------------------+
|  Your feedback helps us keep our service high-quality. |
|  The GreenSketch Team                              |
+----------------------------------------------------+

```

2. 阶段 2：对项目安装完成后的安装商评价回收
- 涉及的评分维度：
Value for Money：性价比
Quality of System：系统质量
INSTALLATION：安装质量与体验
Customer Service：客户服务

- 页面布局参考：
```
+----------------------------------------------------+
| [Emily's Smart Quote Logo]                         |
|                                                    |
|  Review Your Solar Installation                    |
| -------------------------------------------------- |
|                                                    |
|  Hi {{customer_name}},                             |
|  We hope you're enjoying your new solar system!    |
|  Please take a moment to review your experience    |
|  with {{installer_company_name}}.                  |
|                                                    |
+----------------------------------------------------+
|                                                    |
|  Please rate the following aspects of the service: |
|                                                    |
|  Value for Money                                   |
|  ☆ ☆ ☆ ☆ ☆                                       |
|                                                    |
|  Quality of System                                 |
|  ☆ ☆ ☆ ☆ ☆                                       |
|                                                    |
|  Installation Quality & Experience                 |
|  ☆ ☆ ☆ ☆ ☆                                       |
|                                                    |
|  Customer Service                                  |
|  ☆ ☆ ☆ ☆ ☆                                       |
|                                                    |
+----------------------------------------------------+
|                                                    |
|  Any other comments? (Optional)                    |
|  What went well? What could be improved?           |
|  +-----------------------------------------------+ |
|  |                                               | |
|  | (多行文本输入框)                              | |
|  |                                               | |
|  +-----------------------------------------------+ |
|                                                    |
+----------------------------------------------------+
|                                                    |
|              [    Submit Review    ]               |
|                                                    |
+----------------------------------------------------+
|  Thank you for sharing your experience. It's       |
|  invaluable for us and future customers.           |
+----------------------------------------------------+

```