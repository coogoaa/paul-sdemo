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

