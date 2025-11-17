// 页面模板
const pages = {
  export: `
    <div class="topbar">
      <div>
        <div class="breadcrumbs">Sales Agent Management / 数据导出</div>
        <h1>线上数据自助导出</h1>
      </div>
    </div>
    <div class="card">
      <h2>筛选条件</h2>
      <div class="filter-grid" style="margin-top:18px">
        <div><label>项目创建时间 - 起</label><input type="date" id="startDate"></div>
        <div><label>项目创建时间 - 止</label><input type="date" id="endDate"></div>
      </div>
      <div class="button-row">
        <button class="btn btn-primary" id="filterBtn">筛选</button>
        <button class="btn btn-primary">导出 CSV</button>
      </div>
    </div>
    <div class="card" id="resultCard" style="display:none">
      <h2>筛选结果列表</h2>
      <div style="overflow-x:auto">
        <table>
          <thead><tr>
            <th>项目创建时间</th><th>project_id</th><th>address</th><th>实际分析地址</th>
            <th>实际分析经度</th><th>实际分析纬度</th><th>map_link</th><th>sketch_map_link</th>
            <th>type</th><th>design_id</th><th>design_type</th><th>system_size</th>
            <th>upfront_investment_max</th><th>upfront_investment_min</th>
            <th>upfront_investment</th><th>subsidy</th><th>annual_bill_savings_max</th>
            <th>annual_bill_savings_min</th><th>annual_bill_savings</th>
            <th>irr</th><th>payback_period_max</th>
            <th>payback_period_min</th><th>payback_period</th>
            <th>battery_capacity</th><th>self_consumption_max</th>
            <th>self_consumption_min</th><th>self_consumption</th>
            <th>rendering_link</th><th>card_link</th><th>user_name</th><th>email</th>
            <th>phone</th><th>postcode</th><th>sketch_project_link</th><th>线索类型</th>
          </tr></thead>
          <tbody id="tableBody">
            <tr>
              <td>2025-08-19 14:23:15</td><td>321</td><td>7XM7+8XQ, Fawkner VIC 3060, Australia</td><td>7XM7+8XQ, Fawkner VIC 3060, Australia</td>
              <td>144.9649844</td><td>-37.7166625</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250819/7005/image_144.9649844_-37.7166625_drawed.jpg" target="_blank">查看</a></td><td>-</td>
              <td>储能扩容</td><td>422</td><td>A</td><td>3.96</td>
              <td>9220.575</td><td>8342.425</td><td>8781.5</td><td>4875</td><td>1555.718167</td>
              <td>1407.554532</td><td>1481.63635</td><td>0.120304</td><td>9.1875</td>
              <td>8.3125</td><td>8.75</td><td>15</td><td>0.997508</td>
              <td>0.902508</td><td>0.950008</td><td>-</td><td>-</td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>正常流程</td>
            </tr>
            <tr>
              <td>2025-08-19 14:25:32</td><td>321</td><td>7XM7+8XQ, Fawkner VIC 3060, Australia</td><td>7XM7+8XQ, Fawkner VIC 3060, Australia</td>
              <td>144.9649844</td><td>-37.7166625</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250819/7005/image_144.9649844_-37.7166625_drawed.jpg" target="_blank">查看</a></td><td>-</td>
              <td>储能扩容</td><td>423</td><td>C</td><td>3.96</td>
              <td>10076.55285</td><td>9116.88115</td><td>9596.717</td><td>5421</td><td>1555.718167</td>
              <td>1407.554532</td><td>1481.63635</td><td>0.100371</td><td>10.416</td>
              <td>9.424</td><td>9.92</td><td>16.67</td><td>0.997508</td>
              <td>0.902508</td><td>0.950008</td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/28/rendering/321/423/a77bfb06-f8ad-4195-814f-0c37c287f75a.png" target="_blank">查看</a></td><td>-</td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>正常流程</td>
            </tr>
            <tr>
              <td>2025-08-20 09:15:48</td><td>322</td><td>Melbourne VIC 3000, Australia</td><td>Melbourne VIC 3000, Australia</td>
              <td>145.069368647</td><td>-37.839358297</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250820/7137/image_145.069368647_-37.839358297_drawed.jpg" target="_blank">查看</a></td><td>-</td>
              <td>新建系统</td><td>425</td><td>A</td><td>8.8</td>
              <td>15910.86315</td><td>14395.54285</td><td>15153.203</td><td>8073</td><td>2207.839023</td>
              <td>1997.56864</td><td>2102.703832</td><td>0.094849</td><td>10.1535</td>
              <td>9.1865</td><td>9.67</td><td>17.33</td><td>0.597736</td>
              <td>0.540809</td><td>0.569272</td><td>-</td><td>-</td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>正常流程</td>
            </tr>
            <tr>
              <td>2025-08-20 09:18:22</td><td>322</td><td>Melbourne VIC 3000, Australia</td><td>Melbourne VIC 3000, Australia</td>
              <td>145.069368647</td><td>-37.839358297</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250820/7137/image_145.069368647_-37.839358297_drawed.jpg" target="_blank">查看</a></td><td>-</td>
              <td>新建系统</td><td>426</td><td>C</td><td>8.8</td>
              <td>22919.15535</td><td>20736.37865</td><td>21827.767</td><td>11973</td><td>2207.839023</td>
              <td>1997.56864</td><td>2102.703832</td><td>0.026538</td><td>14.8785</td>
              <td>13.4615</td><td>14.17</td><td>29.33</td><td>0.597736</td>
              <td>0.540809</td><td>0.569272</td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/29/rendering/322/426/3140b244-8c77-492a-b525-4ef3b0e23da9.png" target="_blank">查看</a></td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/29/card/322/426/1c2fbaac-44c3-4f26-b2ab-c707737ff0f6.png" target="_blank">查看</a></td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>正常流程</td>
            </tr>
            <tr>
              <td>2025-09-14 16:42:09</td><td>323</td><td>11 Marvin Way, Paralowie SA 5108, Australia</td><td>11 Marvin Way, Paralowie SA 5108, Australia</td>
              <td>138.5988792</td><td>-34.75845</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250914/7081/image_138.5988792_-34.75845_drawed.jpg" target="_blank">查看</a></td><td>-</td>
              <td>储能扩容</td><td>428</td><td>C</td><td>6.16</td>
              <td>12467.78715</td><td>11280.37885</td><td>11874.083</td><td>6942</td><td>2120.162602</td>
              <td>1918.242354</td><td>2019.202478</td><td>0.11992</td><td>9.45</td>
              <td>8.55</td><td>9</td><td>21.33</td><td>0.732653</td>
              <td>0.662877</td><td>0.697765</td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/29/rendering/323/428/24b80230-6c3d-4148-bd69-6527d59ec4cf.png" target="_blank">查看</a></td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/29/card/323/428/e5bf835d-0d45-4eab-9a4b-43f0885c28e0.png" target="_blank">查看</a></td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>正常流程</td>
            </tr>
            <tr>
              <td>2025-09-14 18:25:33</td><td>333</td><td>JVWP+3VH, Lyons NT 0810, Australia</td><td>JVWP+3VH, Lyons NT 0810, Australia</td>
              <td>130.8872344</td><td>-12.3548125</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250914/7142/image_130.8872344_-12.3548125_drawed.jpg" target="_blank">查看</a></td><td>-</td>
              <td>新建系统</td><td>431</td><td>A</td><td>17.16</td>
              <td>19485.8391</td><td>17630.0449</td><td>18557.942</td><td>13416</td><td>4358.735952</td>
              <td>3943.618243</td><td>4151.177097</td><td>0.174855</td><td>5.775</td>
              <td>5.225</td><td>5.5</td><td>22.22</td><td>0.397757</td>
              <td>0.359875</td><td>0.378816</td><td>-</td><td>-</td>
              <td>p1</td><td>123@gmail.com</td><td>123456789</td><td>810</td><td>-</td><td>正常流程</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span>Total: 581</span>
        <div style="display:flex;align-items:center;gap:12px">
          <button class="pagination-btn">&lt;</button>
          <button class="pagination-btn active">1</button>
          <button class="pagination-btn">2</button>
          <button class="pagination-btn">3</button>
          <button class="pagination-btn">4</button>
          <button class="pagination-btn">5</button>
          <span>...</span>
          <button class="pagination-btn">25</button>
          <button class="pagination-btn">&gt;</button>
          <select id="pageSize" style="padding:6px 10px;border-radius:8px;border:1px solid var(--border)">
            <option value="10">10 / Page</option>
            <option value="20">20 / Page</option>
            <option value="30">30 / Page</option>
            <option value="50">50 / Page</option>
          </select>
        </div>
      </div>
    </div>
  `,
  
  params: `
    <div class="topbar">
      <div>
        <div class="breadcrumbs">Sales Agent Management / 参数配置</div>
        <h1>核心参数配置</h1>
      </div>
    </div>
    <div class="card">
      <div class="tabs">
        <button class="tab active" data-tab="gis">GIS参数</button>
        <button class="tab" data-tab="house3d">3D房屋参数</button>
        <button class="tab" data-tab="plan">方案参数</button>
        <button class="tab" data-tab="device">设备参数</button>
        <button class="tab" data-tab="cost">成本参数</button>
        <button class="tab" data-tab="economic">经济参数</button>
        <button class="tab" data-tab="display">前端展示参数</button>
        <button class="tab" data-tab="mapping">映射数据</button>
        <button class="tab" data-tab="fallback">兜底参数</button>
      </div>
      <div class="tab-content active" id="tab-gis">
        <div class="params-grid">
          <div class="param-item"><label>min_2D_area_filter_m2</label><input type="number" value="50"><small>最小屋顶面积过滤 (m²)</small></div>
          <div class="param-item"><label>max_2D_area_filter_m2</label><input type="number" value="600"><small>最大屋顶面积过滤 (m²)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">恢复默认值</button><button class="btn btn-primary">保存配置</button></div>
      </div>
      <div class="tab-content" id="tab-house3d">
        <h3>面板尺寸</h3>
        <div class="params-grid">
          <div class="param-item"><label>panel_length_mm</label><input type="number" value="1762"><small>长度 (mm)</small></div>
          <div class="param-item"><label>panel_width_mm</label><input type="number" value="1134"><small>宽度 (mm)</small></div>
          <div class="param-item"><label>panel_thickness_mm</label><input type="number" value="30"><small>厚度 (mm)</small></div>
        </div>
        <h3 style="margin-top:24px">排布间距</h3>
        <div class="params-grid">
          <div class="param-item"><label>inter_module_spacing_mm</label><input type="number" value="20"><small>Inter-module spacing (mm)</small></div>
          <div class="param-item"><label>inter_row_spacing_mm</label><input type="number" value="20"><small>Inter-row spacing (mm)</small></div>
        </div>
        <h3 style="margin-top:24px">电池尺寸</h3>
        <div class="params-grid">
          <div class="param-item"><label>battery_length_mm</label><input type="number" value="900"><small>Length (mm)</small></div>
          <div class="param-item"><label>battery_width_mm</label><input type="number" value="1100"><small>Width (mm)</small></div>
          <div class="param-item"><label>battery_height_mm</label><input type="number" value="2000"><small>Height (mm)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">恢复默认值</button><button class="btn btn-primary">保存配置</button></div>
      </div>
      <div class="tab-content" id="tab-plan">
        <div class="params-grid">
          <div class="param-item"><label>plan_c_capacity_factor</label><input type="number" step="0.01" value="0.9"><small>方案 C 容量系数</small></div>
          <div class="param-item"><label>plan_c_target_sc_rate</label><input type="number" value="50"><small>方案 C 目标自用率 (%)</small></div>
          <div class="param-item"><label>dc_ac_ratio</label><input type="number" step="0.1" value="1.5"><small>容配比 (DC/AC)</small></div>
          <div class="param-item"><label>rooftop_use_factor</label><input type="number" step="0.1" value="0.7"><small>屋顶理论最大容量使用系数</small></div>
          <div class="param-item"><label>baseline_self_consumption_rate</label><input type="number" value="30"><small>基线自用率 (无电池) %</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">恢复默认值</button><button class="btn btn-primary">保存配置</button></div>
      </div>
      <div class="tab-content" id="tab-device">
        <div class="params-grid">
          <div class="param-item"><label>battery_dod</label><input type="number" value="90"><small>电池放电深度 DoD (%)</small></div>
          <div class="param-item"><label>battery_rte</label><input type="number" value="95"><small>电池往返效率 RTE (%)</small></div>
          <div class="param-item"><label>panel_power_kw</label><input type="number" step="0.01" value="0.44"><small>标准化面板单元功率 (kW)</small></div>
          <div class="param-item"><label>panel_first_year_degradation_rate</label><input type="number" value="0"><small>面板首年衰减率 (%)</small></div>
          <div class="param-item"><label>panel_annual_degradation_rate</label><input type="number" step="0.01" value="0.40"><small>面板次年起衰减率 (%)</small></div>
          <div class="param-item"><label>pv_system_efficiency</label><input type="number" value="85"><small>系统效率 (%)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">恢复默认值</button><button class="btn btn-primary">保存配置</button></div>
      </div>
      <div class="tab-content" id="tab-cost">
        <div class="params-grid">
          <div class="param-item"><label>panel_unit_price_per_kw</label><input type="number" value="540"><small>每 kW 面板税前报价 (AUD/kW)</small></div>
          <div class="param-item"><label>inverter_unit_price_per_kw</label><input type="number" value="280"><small>每 kW 逆变器税前报价 (AUD/kW)</small></div>
          <div class="param-item"><label>battery_unit_price_per_kwh</label><input type="number" value="865"><small>每 kWh 电池税前报价 (AUD/kWh)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">恢复默认值</button><button class="btn btn-primary">保存配置</button></div>
      </div>
      <div class="tab-content" id="tab-economic">
        <div class="params-grid">
          <div class="param-item"><label>grid_buy_rate</label><input type="number" step="0.01" value="0.3"><small>购电价 (AUD/kWh)</small></div>
          <div class="param-item"><label>grid_sell_rate</label><input type="number" step="0.01" value="0.07"><small>售电价 (AUD/kWh)</small></div>
          <div class="param-item"><label>daily_fixed_charge</label><input type="number" step="0.01" value="0.35"><small>日均固定费用 (AUD/day)</small></div>
          <div class="param-item"><label>electricity_inflation_rate</label><input type="number" step="0.01" value="3.97"><small>电费膨胀率 (%)</small></div>
          <div class="param-item"><label>cash_interest_rate</label><input type="number" step="0.01" value="1.36"><small>现金利率 (%)</small></div>
          <div class="param-item"><label>existing_sc_rate</label><input type="number" value="30"><small>已有系统基线自用率 (%)</small></div>
          <div class="param-item"><label>battery_replacement_year</label><input type="number" value="10"><small>更换电池年限 (年)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">恢复默认值</button><button class="btn btn-primary">保存配置</button></div>
      </div>
      <div class="tab-content" id="tab-display">
        <div class="params-grid">
          <div class="param-item"><label>display_range_percent_self_consumption</label><input type="number" value="5"><small>自用率展示浮动范围 (%)</small></div>
          <div class="param-item"><label>display_range_percent_annual_savings</label><input type="number" value="5"><small>年度节省浮动范围 (%)</small></div>
          <div class="param-item"><label>display_range_percent_payback_period</label><input type="number" value="5"><small>回本周期浮动范围 (%)</small></div>
          <div class="param-item"><label>display_range_percent_final_price</label><input type="number" value="5"><small>最终报价浮动范围 (%)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">恢复默认值</button><button class="btn btn-primary">保存配置</button></div>
      </div>
      <div class="tab-content" id="tab-fallback">
        <div class="params-grid">
          <div class="param-item"><label>yield_per_kw_per_year_fallback</label><input type="number" value="1526"><small>每 kW 年发电量 (兜底) (kWh/kW/yr)</small></div>
        </div>
        
        <h3 style="margin-top:32px">小时发电量兜底数据</h3>
        <div class="upload-area">
          <p>支持上传 Excel 或 CSV 文件替换现有兜底数据</p>
          <input type="file" id="upload-hourly" accept=".xlsx,.xls,.csv">
          <label for="upload-hourly" class="upload-label">选择文件上传</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>月</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th><th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th><th>24</th></tr></thead>
            <tbody>
              <tr><td>1</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.693099355</td><td>1.38619871</td><td>2.425847742</td><td>3.465496774</td><td>4.505145806</td><td>4.851695484</td><td>4.851695484</td><td>4.505145806</td><td>3.465496774</td><td>2.425847742</td><td>1.38619871</td><td>0.693099355</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>2</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.690624</td><td>1.381248</td><td>2.417184</td><td>3.45312</td><td>4.489056</td><td>4.834368</td><td>4.834368</td><td>4.489056</td><td>3.45312</td><td>2.417184</td><td>1.381248</td><td>0.690624</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>3</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.623789419</td><td>1.247578839</td><td>2.183262968</td><td>3.118947097</td><td>4.054631226</td><td>4.366525935</td><td>4.366525935</td><td>4.054631226</td><td>3.118947097</td><td>2.183262968</td><td>1.247578839</td><td>0.623789419</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>4</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.572962133</td><td>1.145924267</td><td>2.005367467</td><td>2.864810667</td><td>3.724253867</td><td>4.010734933</td><td>4.010734933</td><td>3.724253867</td><td>2.864810667</td><td>2.005367467</td><td>1.145924267</td><td>0.572962133</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>5</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.485169548</td><td>0.970339097</td><td>1.698093419</td><td>2.425847742</td><td>3.153602065</td><td>3.396186839</td><td>3.396186839</td><td>3.153602065</td><td>2.425847742</td><td>1.698093419</td><td>0.970339097</td><td>0.485169548</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>6</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.4297216</td><td>0.8594432</td><td>1.5040256</td><td>2.148608</td><td>2.7931904</td><td>3.0080512</td><td>3.0080512</td><td>2.7931904</td><td>2.148608</td><td>1.5040256</td><td>0.8594432</td><td>0.4297216</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>7</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.485169548</td><td>0.970339097</td><td>1.698093419</td><td>2.425847742</td><td>3.153602065</td><td>3.396186839</td><td>3.396186839</td><td>3.153602065</td><td>2.425847742</td><td>1.698093419</td><td>0.970339097</td><td>0.485169548</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>8</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.554479484</td><td>1.108958968</td><td>1.940678194</td><td>2.772397419</td><td>3.604116645</td><td>3.881356387</td><td>3.881356387</td><td>3.604116645</td><td>2.772397419</td><td>1.940678194</td><td>1.108958968</td><td>0.554479484</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>9</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.6445824</td><td>1.2891648</td><td>2.2560384</td><td>3.222912</td><td>4.1897856</td><td>4.5120768</td><td>4.5120768</td><td>4.1897856</td><td>3.222912</td><td>2.2560384</td><td>1.2891648</td><td>0.6445824</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>10</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.623789419</td><td>1.247578839</td><td>2.183262968</td><td>3.118947097</td><td>4.054631226</td><td>4.366525935</td><td>4.366525935</td><td>4.054631226</td><td>3.118947097</td><td>2.183262968</td><td>1.247578839</td><td>0.623789419</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>11</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.6445824</td><td>1.2891648</td><td>2.2560384</td><td>3.222912</td><td>4.1897856</td><td>4.5120768</td><td>4.5120768</td><td>4.1897856</td><td>3.222912</td><td>2.2560384</td><td>1.2891648</td><td>0.6445824</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
              <tr><td>12</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0.623789419</td><td>1.247578839</td><td>2.183262968</td><td>3.118947097</td><td>4.054631226</td><td>4.366525935</td><td>4.366525935</td><td>4.054631226</td><td>3.118947097</td><td>2.183262968</td><td>1.247578839</td><td>0.623789419</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
            </tbody>
          </table>
        </div>
        
        <div class="button-row"><button class="btn btn-outline">恢复默认值</button><button class="btn btn-primary">保存配置</button></div>
      </div>
      <div class="tab-content" id="tab-mapping">
        <h3>GS 功率映射表</h3>
        <div class="upload-area">
          <p>支持上传 Excel 或 CSV 文件替换现有映射参数</p>
          <input type="file" id="upload-gs" accept=".xlsx,.xls,.csv">
          <label for="upload-gs" class="upload-label">选择文件上传</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>起始值</th><th>区间值</th><th>nominal_battery_capacity_kwh</th><th>usable_battery_capacity_kwh</th><th>inverter_kw</th></tr></thead>
            <tbody>
              <tr><td>0</td><td>(0,5]</td><td>22.44</td><td>20.2</td><td>8</td></tr>
              <tr><td>5</td><td>(5,7.5]</td><td>22.22</td><td>20</td><td>9.6</td></tr>
              <tr><td>7.5</td><td>(7.5,12]</td><td>29.33</td><td>26.4</td><td>9.994</td></tr>
              <tr><td>12</td><td>(12,20]</td><td>28.04</td><td>25.24</td><td>9.3</td></tr>
              <tr><td>20</td><td>(20,100]</td><td>50.32</td><td>45.29</td><td>19.50</td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row"><button class="btn btn-primary">保存映射数据</button></div>
        
        <h3 style="margin-top:32px">GD 功率映射表</h3>
        <div class="upload-area">
          <p>支持上传 Excel 或 CSV 文件替换现有映射参数</p>
          <input type="file" id="upload-gd" accept=".xlsx,.xls,.csv">
          <label for="upload-gd" class="upload-label">选择文件上传</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>起始值</th><th>区间值</th><th>nominal_battery_capacity_kwh</th><th>usable_battery_capacity_kwh</th><th>inverter_kw</th></tr></thead>
            <tbody>
              <tr><td>0</td><td>(0,5]</td><td>15.00</td><td>13.50</td><td>5.00</td></tr>
              <tr><td>5</td><td>(5,7.5]</td><td>14.82</td><td>13.34</td><td>5.00</td></tr>
              <tr><td>7.5</td><td>(7.5,12]</td><td>17.33</td><td>15.60</td><td>7.22</td></tr>
              <tr><td>12</td><td>(12,20]</td><td>22.22</td><td>20.00</td><td>10.00</td></tr>
              <tr><td>20</td><td>(20,100]</td><td>41.93</td><td>37.74</td><td>15.00</td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row"><button class="btn btn-primary">保存映射数据</button></div>
        
        <h3 style="margin-top:32px">储能扩容功率映射表</h3>
        <div class="upload-area">
          <p>支持上传 Excel 或 CSV 文件替换现有映射参数</p>
          <input type="file" id="upload-battery" accept=".xlsx,.xls,.csv">
          <label for="upload-battery" class="upload-label">选择文件上传</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>起始值</th><th>pv kw</th><th>标称容量 A</th><th>可用容量 A</th><th>标称容量 B</th><th>可用容量 B</th><th>标称容量 C</th><th>可用容量 C</th></tr></thead>
            <tbody>
              <tr><td>0</td><td>(0,5]</td><td>11.11</td><td>10.00</td><td>15.00</td><td>13.50</td><td>16.67</td><td>15.00</td></tr>
              <tr><td>5</td><td>(5,7.5]</td><td>11.11</td><td>10.00</td><td>15.00</td><td>13.50</td><td>21.33</td><td>19.20</td></tr>
              <tr><td>7.5</td><td>(7.5,12]</td><td>15.33</td><td>13.80</td><td>17.78</td><td>16.00</td><td>26.00</td><td>23.40</td></tr>
              <tr><td>12</td><td>(12,20]</td><td>21.33</td><td>19.20</td><td>26.00</td><td>23.40</td><td>33.33</td><td>30.00</td></tr>
              <tr><td>20</td><td>(20,100]</td><td>33.33</td><td>30.00</td><td>47.78</td><td>43.00</td><td>55.56</td><td>50.00</td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row"><button class="btn btn-primary">保存映射数据</button></div>
        
        <h3 style="margin-top:32px">各州领地年用电量配置</h3>
        <div class="upload-area">
          <p>支持上传 Excel 或 CSV 文件替换现有配置数据</p>
          <input type="file" id="upload-states" accept=".xlsx,.xls,.csv">
          <label for="upload-states" class="upload-label">选择文件上传</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>States</th><th>Avg. Annual kWh Usage</th></tr></thead>
            <tbody>
              <tr><td>TAS</td><td>10148</td></tr>
              <tr><td>NT</td><td>10008</td></tr>
              <tr><td>ACT</td><td>8632</td></tr>
              <tr><td>SA</td><td>7129</td></tr>
              <tr><td>NSW</td><td>7778</td></tr>
              <tr><td>QLD</td><td>7270</td></tr>
              <tr><td>WA</td><td>7634</td></tr>
              <tr><td>VIC</td><td>6778</td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row"><button class="btn btn-primary">保存配置数据</button></div>
      </div>
    </div>
  `
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('toggleSidebar');
  const mainContent = document.getElementById('mainContent');
  const menuItems = document.querySelectorAll('.sidebar li');
  
  // 侧边栏收起/展开
  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
  
  // 页面切换
  function switchPage(pageName) {
    mainContent.innerHTML = pages[pageName];
    menuItems.forEach(item => item.classList.remove('active'));
    document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
    
    // 如果是参数配置页，初始化Tab切换
    if (pageName === 'params') {
      initTabs();
    }
    
    // 如果是数据导出页，初始化筛选按钮
    if (pageName === 'export') {
      initExportPage();
    }
  }
  
  // 数据导出页初始化
  function initExportPage() {
    const filterBtn = document.getElementById('filterBtn');
    const resultCard = document.getElementById('resultCard');
    
    if (filterBtn) {
      filterBtn.addEventListener('click', () => {
        resultCard.style.display = 'block';
      });
    }
  }
  
  // Tab切换
  function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(tc => tc.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(`tab-${targetTab}`).classList.add('active');
      });
    });
  }
  
  // 菜单点击事件
  menuItems.forEach(item => {
    item.addEventListener('click', () => {
      const pageName = item.dataset.page;
      switchPage(pageName);
    });
  });
  
  // 默认加载数据导出页
  switchPage('export');
  
  // 用户菜单交互
  const userMenuBtn = document.getElementById('userMenuBtn');
  const userDropdown = document.getElementById('userDropdown');
  const changePasswordBtn = document.getElementById('changePasswordBtn');
  const logoutBtn = document.getElementById('logoutBtn');
  
  if (userMenuBtn) {
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('show');
    });
  }
  
  // 点击外部关闭菜单
  document.addEventListener('click', (e) => {
    if (userDropdown && !userDropdown.contains(e.target) && e.target !== userMenuBtn) {
      userDropdown.classList.remove('show');
    }
  });
  
  // 修改密码
  if (changePasswordBtn) {
    changePasswordBtn.addEventListener('click', () => {
      alert('修改密码功能');
      userDropdown.classList.remove('show');
    });
  }
  
  // 退出登录
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      window.location.href = 'login.html';
    });
  }
});
