// 测试HTML页面中的JavaScript计算逻辑
function testCalculation() {
    const inputs = {
        initialFinalPrice: 10000,
        batteryTotalFee: 3000,
        fixedChargeDayIncTax: 0.5,
        electricityPricePerKwhIncTax: 0.30,
        feedInTariffIncTax: 0.07,
        priceIndexation: 0.03,
        effectiveInterestRate: 0.05,
        subsequentAnnualPowerDegradation: 0.004,
        isHasBattery: true,
        defaultMonthMP: 100,
        defaultMonthME: 150,
        selfConsumptionDefault: 0.5
    };

    // 测试新的电池摊销逻辑
    const battery10YearAvgFee = inputs.batteryTotalFee / 120;  // 按120个月摊销
    console.log("每月电池摊销费用:", battery10YearAvgFee.toFixed(2), "元");

    let batteryAmortizationCum = 0;
    let finalPrice = inputs.initialFinalPrice;

    // 测试前12个月的累加逻辑
    console.log("\n前12个月的电池费用累加:");
    for (let month = 1; month <= 12; month++) {
        batteryAmortizationCum += battery10YearAvgFee;
        finalPrice = inputs.initialFinalPrice + batteryAmortizationCum;
        console.log(`第${month}月: 累计摊销=${batteryAmortizationCum.toFixed(2)}, 最终价格=${finalPrice.toFixed(2)}`);
    }

    // 对比旧逻辑
    console.log("\n对比旧逻辑 (第12个月):");
    const oldBatteryAvgFee = inputs.batteryTotalFee / 10;
    const oldBatteryAmort = 12 * oldBatteryAvgFee;
    const oldFinalPrice = inputs.initialFinalPrice + oldBatteryAmort;
    console.log(`旧逻辑: 累计摊销=${oldBatteryAmort.toFixed(2)}, 最终价格=${oldFinalPrice.toFixed(2)}`);
    
    console.log("\n差异分析:");
    console.log(`新逻辑月摊销: ${battery10YearAvgFee.toFixed(2)} 元/月`);
    console.log(`旧逻辑月摊销: ${oldBatteryAvgFee.toFixed(2)} 元/月`);
    console.log(`12个月后价格差异: ${(finalPrice - oldFinalPrice).toFixed(2)} 元`);
}

// 运行测试
testCalculation();
