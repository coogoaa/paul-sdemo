在 installer_page/installer-config_v4.html 的基础上做修改：

1. Customer service phone number 不变
2. Lead submission email 不变
3. Preliminary quote adjustment range (%) 删除
4. Additional customer incentive (A$) 删除

- 在 Lead submission email 下新增
1. Additional Charges
可以填写 
Item Name （文本）
Unit Cost （数值，范围[0, 10000]）
这个目的是安装商在原始报价基础上增加一些额外的收费项目，最终在 SalsAgent 的页面的最终报价结果商做调整

2. Deductions
参考截图的布局，不要展示开关，STCs 个数置灰，可以修改 Unit Price(数值，范围[0, 60])，自动计算 Amount
默认个增加一个其他补贴（翻译为英文），可以填写数值[0, 100000]
这个是安装商在原始的补贴金额基础上做一定的调整，并提供其他让利补贴的选项

---
1. Additional Charges 
- 去掉 Add item 按钮
- 提供一行空的 Item Name，Unit Cost
2. Deductions
- 去掉 Add deduction 按钮
- 保留STC Panel Rebate、STC Battery Rebate、Solar VIC Rebate、Solar VIC PV Interest Free Loan
- Solar VIC PV Interest Free Loan 下方的Other installer incentive 内容默认为空。用户自行填写

--
1. Additional Charges
- 文案修改：
Add installer-specific line items that will be applied on top of the base quote. These appear in the SalesAgent final pricing summary. 这部分改为 视情况在 Sales Agent 自动计算的最终报价的结果之上，增加额外的投入。你可以优化一下文案，使用英语展示。
- Item name：输入框不需要提示文字了
- 不需要 Remove 按钮

2. Deductions
- 文案修改：
Fine-tune rebates and incentives. STC counts stay fixed, but you can adjust pricing and add other incentives.
改为：
可以在 SalesAgent 自动计算的结果之上，调整单价，或者增加补贴金额。你优化下 使用英文展示。

- Certificates： 
    - STC Panel Rebate：去除 (Installation Year: 2025)，不展示 STCs 个数
    - STC Battery Rebate：去除 (Installation Year: 2025)，不展示 STCs 个数
    - Solar VIC Rebate：
    - Solar VIC PV Interest Free Loan：
    - Other installer incentive：

---
- 去除Solar VIC Rebate、Solar VIC PV Interest Free Loan 展示
- Add other installer incentives or rebates here. 使用STC Panel Rebate 一样的标题展示 简单一些 例如 就是 installer incentives or rebates

Deductions 去掉 Amount (A$) 这一列


- 当前 Other installer incentive 的输入框的提示文字 改为：
Other installer incentives or rebates
- 删除 当前的 Installer incentives or rebates 文字

