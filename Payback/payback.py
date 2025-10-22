# 完整 Python 实现（严格对应 Excel / Java 原始逻辑）
import math
import numpy as np
import pandas as pd
from decimal import Decimal, getcontext, ROUND_HALF_UP

getcontext().prec = 28

inputs = {
    "initialFinalPrice": Decimal("10000"),
    "batteryTotalFee": Decimal("3000"),
    "fixedChargeDayIncTax": Decimal("0.5"),
    "electricityPricePerKwhIncTax": Decimal("0.30"),
    "feedInTariffIncTax": Decimal("0.07"),
    "priceIndexation": Decimal("0.03"),
    "effectiveInterestRate": Decimal("0.05"),
    "subsequentAnnualPowerDegradation": Decimal("0.004"),
    "isHasBattery": True,
    "default_daysInMonth": 30,
    "default_month_mP": Decimal("100"),
    "default_month_mE": Decimal("150"),
    "selfConsumption_default": Decimal("0.5"),
}

rows = []
for cum in range(1, 253):
    year = (cum - 1) // 12
    month = ((cum - 1) % 12) + 1
    rows.append({"Year": year, "Month": month, "CumMonth": cum})

df = pd.DataFrame(rows)
df["daysInMonth"] = inputs["default_daysInMonth"]
df["mP"] = float(inputs["default_month_mP"])
df["mE"] = float(inputs["default_month_mE"])
df["selfConsumption"] = float(inputs["selfConsumption_default"])

def D(x): return Decimal(str(x))

q = Decimal(1) + inputs["priceIndexation"]
m = Decimal(1) + inputs["effectiveInterestRate"]
battery10YearAvgFee = inputs["batteryTotalFee"] / Decimal(120)  # 修改为120个月，符合Java逻辑

df["monthFixedCharge"] = df["daysInMonth"].apply(lambda d: D(d) * inputs["fixedChargeDayIncTax"])
df["mA"] = df.apply(lambda r: D(r["mE"]) * inputs["electricityPricePerKwhIncTax"] + r["monthFixedCharge"], axis=1)

def calc_ymKzx(row):
    year = int(row["Year"])
    if year >= 1:
        mA = D(row["mA"])
        return mA * (q ** Decimal(year)) / (m ** Decimal(year))
    else:
        return Decimal(0)
df["ymKzx"] = df.apply(calc_ymKzx, axis=1)

buyBeforeCum = Decimal(0)
buyAfterCum = Decimal(0)
finalPrice = inputs["initialFinalPrice"]
monthsSinceInstall = 0
batteryAmortizationCum = Decimal(0)  # 累计电池摊销费用

cols = ["ymP","ymU","ymS","ymD","ymGzx","ymCzx","buyBeforeCum_post","buyAfterCum_post","monthsSinceInstall","batteryAmortizationCum","finalPrice_current","cumulativeDiff"]
for c in cols:
    df[c] = None

payback = None
payback_flag = False

for idx, row in df.iterrows():
    year = int(row["Year"])
    month = int(row["Month"])
    monthFixedCharge = D(row["monthFixedCharge"])
    mE = D(row["mE"])
    mA = D(row["mA"])
    ymKzx_val = D(row["ymKzx"])
    if year >= 1:
        buyBeforeCum = buyBeforeCum + ymKzx_val
        
        ymP_val = D(row["mP"]) * ((Decimal(1) - inputs["subsequentAnnualPowerDegradation"]) ** Decimal(year - 1))
        if inputs["isHasBattery"]:
            ymU_val = min(ymP_val * D(row["selfConsumption"]), mE)
        else:
            ymU_val = ymP_val * D(row["selfConsumption"])
        ymS_val = ymP_val - ymU_val
        ymD_val = max(mE - ymU_val, Decimal(0))
        ymGzx_val = ymS_val * inputs["feedInTariffIncTax"] / (m ** Decimal(year))
        ymCzx_val = (ymD_val * inputs["electricityPricePerKwhIncTax"] + monthFixedCharge) * (q ** Decimal(year)) / (m ** Decimal(year))
        buyAfterCum = buyAfterCum + (ymCzx_val - ymGzx_val)
        monthsSinceInstall = monthsSinceInstall + 1
        
        # 按Java逻辑：每月累加电池摊销费用到finalPrice
        batteryAmortizationCum = batteryAmortizationCum + battery10YearAvgFee
        finalPrice = inputs["initialFinalPrice"] + batteryAmortizationCum
        cumulativeDiff_val = buyAfterCum + finalPrice - buyBeforeCum
    else:
        ymP_val = Decimal(0)
        ymU_val = Decimal(0)
        ymS_val = Decimal(0)
        ymD_val = Decimal(0)
        ymGzx_val = Decimal(0)
        ymCzx_val = Decimal(0)
        batteryAmortizationCum = Decimal(0)
        monthsSinceInstall = 0
        cumulativeDiff_val = Decimal(0)

    df.at[idx,"ymP"] = float(ymP_val)
    df.at[idx,"ymU"] = float(ymU_val)
    df.at[idx,"ymS"] = float(ymS_val)
    df.at[idx,"ymD"] = float(ymD_val)
    df.at[idx,"ymGzx"] = float(ymGzx_val)
    df.at[idx,"ymCzx"] = float(ymCzx_val)
    df.at[idx,"buyBeforeCum_post"] = float(buyBeforeCum)
    df.at[idx,"buyAfterCum_post"] = float(buyAfterCum)
    df.at[idx,"monthsSinceInstall"] = int(monthsSinceInstall)
    df.at[idx,"batteryAmortizationCum"] = float(batteryAmortizationCum)
    df.at[idx,"finalPrice_current"] = float(finalPrice)
    df.at[idx,"cumulativeDiff"] = float(cumulativeDiff_val)

    if (not payback_flag) and year >= 1 and cumulativeDiff_val <= Decimal(0):
        fraction = (Decimal(month) / Decimal(12)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        payback = (Decimal(year - 1) + fraction)
        payback_flag = True

cash_flows = []
cash_flows.append(-float(inputs["initialFinalPrice"]))
buyElectricityMoneyBeforeLastYearInstallSolar = None

for year in range(1,21):
    yK = Decimal(0)
    yC = Decimal(0)
    yG = Decimal(0)
    for month_idx in range(12):
        row = df[(df["Year"]==year) & (df["Month"]==(month_idx+1))].iloc[0]
        mA = D(row["mA"])
        yK += mA
        ymP = D(row["ymP"])
        ymU = D(row["ymU"])
        ymS = D(row["ymS"])
        ymD = D(row["ymD"])
        monthFixedCharge = D(row["monthFixedCharge"])
        ymG = ymS * inputs["feedInTariffIncTax"]
        ymC = ymD * inputs["electricityPricePerKwhIncTax"] + monthFixedCharge
        yG += ymG
        yC += ymC
    if year == 1:
        buyElectricityMoneyBeforeLastYearInstallSolar = yK
    cashFlow_year = yC + yG - buyElectricityMoneyBeforeLastYearInstallSolar
    if year == 10:
        cashFlow_year = cashFlow_year + inputs["batteryTotalFee"]
    cash_flows.append(float(cashFlow_year))

try:
    irr = np.irr(cash_flows)
except Exception:
    irr = None

out_path = "payback_table_python_exact.xlsx"
df.to_excel(out_path, index=False)

print("Saved exact payback table to:", out_path)
print("Payback detected (per code logic):", (str(payback) if payback_flag else "未在 20 年内回本（payback 默认 100）"))
print("IRR from cash flows (numpy.irr):", irr)
print("\nSample post-install months (first 12):")
print(df[df["Year"]>=1].head(12)[["Year","Month","buyBeforeCum_post","buyAfterCum_post","finalPrice_current","cumulativeDiff"]].to_string(index=False))
