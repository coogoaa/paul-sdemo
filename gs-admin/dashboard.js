// Page templates
const pages = {
  export: `
    <div class="topbar">
      <div>
        <div class="breadcrumbs">Emily Data Export</div>
        <h1>Online Data Self-Service Export</h1>
      </div>
    </div>
    <div class="card">
      <h2>Filter Criteria</h2>
      <div class="filter-grid" style="margin-top:18px">
        <div><label>Project Creation Date - From</label><input type="date" id="startDate"></div>
        <div><label>Project Creation Date - To</label><input type="date" id="endDate"></div>
        <div>
          <label>Lead Type</label>
          <select id="clueType">
            <option value="" disabled selected>Please select Leads Type</option>
            <option value="base-design">base-design</option>
            <option value="high-value">High-Value Lead</option>
            <option value="future-opportunity">Future Opportunity Lead</option>
            <option value="manual-assessment">Manual Assessment Lead</option>
            <option value="quote-help">Quote and Help Lead</option>
          </select>
        </div>
      </div>
      <div class="button-row">
        <button class="btn btn-primary" id="filterBtn">Filter</button>
        <button class="btn btn-primary">Export CSV</button>
      </div>
    </div>
    <div class="card" id="resultCard" style="display:none">
      <h2>Filter Results</h2>
      <div style="overflow-x:auto">
        <table>
          <thead><tr>
            <th>Project Created At</th><th>Project ID</th><th>Address</th><th>Analyzed Address</th>
            <th>Analyzed Longitude</th><th>Analyzed Latitude</th><th>Map Link</th><th>Sketch Map Link</th>
            <th>Type</th><th>Design ID</th><th>Design Type</th><th>System Size (kW)</th>
            <th>Upfront Investment Max (AUD)</th><th>Upfront Investment Min (AUD)</th>
            <th>Upfront Investment (AUD)</th><th>Subsidy (AUD)</th><th>Annual Bill Savings Max (AUD)</th>
            <th>Annual Bill Savings Min (AUD)</th><th>Annual Bill Savings (AUD)</th>
            <th>IRR</th><th>Payback Period Max (Years)</th>
            <th>Payback Period Min (Years)</th><th>Payback Period (Years)</th>
            <th>Battery Capacity (kWh)</th><th>Self Consumption Max</th>
            <th>Self Consumption Min</th><th>Self Consumption</th>
            <th>Rendering Link</th><th>Card Link</th><th>User Name</th><th>Email</th>
            <th>Phone</th><th>Postcode</th><th>Sketch Project Link</th><th>Lead Type</th>
          </tr></thead>
          <tbody id="tableBody">
            <tr>
              <td>2025-08-19 14:23:15</td><td>321</td><td>7XM7+8XQ, Fawkner VIC 3060, Australia</td><td>7XM7+8XQ, Fawkner VIC 3060, Australia</td>
              <td>144.9649844</td><td>-37.7166625</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250819/7005/image_144.9649844_-37.7166625_drawed.jpg" target="_blank">View</a></td><td>-</td>
              <td>Battery Expansion</td><td>422</td><td>A</td><td>3.96</td>
              <td>9220.575</td><td>8342.425</td><td>8781.5</td><td>4875</td><td>1555.718167</td>
              <td>1407.554532</td><td>1481.63635</td><td>0.120304</td><td>9.1875</td>
              <td>8.3125</td><td>8.75</td><td>15</td><td>0.997508</td>
              <td>0.902508</td><td>0.950008</td><td>-</td><td>-</td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>base-design</td>
            </tr>
            <tr>
              <td>2025-08-19 14:25:32</td><td>321</td><td>7XM7+8XQ, Fawkner VIC 3060, Australia</td><td>7XM7+8XQ, Fawkner VIC 3060, Australia</td>
              <td>144.9649844</td><td>-37.7166625</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250819/7005/image_144.9649844_-37.7166625_drawed.jpg" target="_blank">View</a></td><td>-</td>
              <td>Battery Expansion</td><td>423</td><td>C</td><td>3.96</td>
              <td>10076.55285</td><td>9116.88115</td><td>9596.717</td><td>5421</td><td>1555.718167</td>
              <td>1407.554532</td><td>1481.63635</td><td>0.100371</td><td>10.416</td>
              <td>9.424</td><td>9.92</td><td>16.67</td><td>0.997508</td>
              <td>0.902508</td><td>0.950008</td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/28/rendering/321/423/a77bfb06-f8ad-4195-814f-0c37c287f75a.png" target="_blank">View</a></td><td>-</td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>base-design</td>
            </tr>
            <tr>
              <td>2025-08-20 09:15:48</td><td>322</td><td>Melbourne VIC 3000, Australia</td><td>Melbourne VIC 3000, Australia</td>
              <td>145.069368647</td><td>-37.839358297</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250820/7137/image_145.069368647_-37.839358297_drawed.jpg" target="_blank">View</a></td><td>-</td>
              <td>New System</td><td>425</td><td>A</td><td>8.8</td>
              <td>15910.86315</td><td>14395.54285</td><td>15153.203</td><td>8073</td><td>2207.839023</td>
              <td>1997.56864</td><td>2102.703832</td><td>0.094849</td><td>10.1535</td>
              <td>9.1865</td><td>9.67</td><td>17.33</td><td>0.597736</td>
              <td>0.540809</td><td>0.569272</td><td>-</td><td>-</td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>base-design</td>
            </tr>
            <tr>
              <td>2025-08-20 09:18:22</td><td>322</td><td>Melbourne VIC 3000, Australia</td><td>Melbourne VIC 3000, Australia</td>
              <td>145.069368647</td><td>-37.839358297</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250820/7137/image_145.069368647_-37.839358297_drawed.jpg" target="_blank">View</a></td><td>-</td>
              <td>New System</td><td>426</td><td>C</td><td>8.8</td>
              <td>22919.15535</td><td>20736.37865</td><td>21827.767</td><td>11973</td><td>2207.839023</td>
              <td>1997.56864</td><td>2102.703832</td><td>0.026538</td><td>14.8785</td>
              <td>13.4615</td><td>14.17</td><td>29.33</td><td>0.597736</td>
              <td>0.540809</td><td>0.569272</td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/29/rendering/322/426/3140b244-8c77-492a-b525-4ef3b0e23da9.png" target="_blank">View</a></td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/29/card/322/426/1c2fbaac-44c3-4f26-b2ab-c707737ff0f6.png" target="_blank">View</a></td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>base-design</td>
            </tr>
            <tr>
              <td>2025-09-14 16:42:09</td><td>323</td><td>11 Marvin Way, Paralowie SA 5108, Australia</td><td>11 Marvin Way, Paralowie SA 5108, Australia</td>
              <td>138.5988792</td><td>-34.75845</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250914/7081/image_138.5988792_-34.75845_drawed.jpg" target="_blank">View</a></td><td>-</td>
              <td>Battery Expansion</td><td>428</td><td>C</td><td>6.16</td>
              <td>12467.78715</td><td>11280.37885</td><td>11874.083</td><td>6942</td><td>2120.162602</td>
              <td>1918.242354</td><td>2019.202478</td><td>0.11992</td><td>9.45</td>
              <td>8.55</td><td>9</td><td>21.33</td><td>0.732653</td>
              <td>0.662877</td><td>0.697765</td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/29/rendering/323/428/24b80230-6c3d-4148-bd69-6527d59ec4cf.png" target="_blank">View</a></td><td><a href="https://file.greensketch.ai/green-sketch/prod/2025/10/29/card/323/428/e5bf835d-0d45-4eab-9a4b-43f0885c28e0.png" target="_blank">View</a></td>
              <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>base-design</td>
            </tr>
            <tr>
              <td>2025-09-14 18:25:33</td><td>333</td><td>JVWP+3VH, Lyons NT 0810, Australia</td><td>JVWP+3VH, Lyons NT 0810, Australia</td>
              <td>130.8872344</td><td>-12.3548125</td><td><a href="https://file.greensketch.ai/maps/sale_agent/image/metromap/20250914/7142/image_130.8872344_-12.3548125_drawed.jpg" target="_blank">View</a></td><td>-</td>
              <td>New System</td><td>431</td><td>A</td><td>17.16</td>
              <td>19485.8391</td><td>17630.0449</td><td>18557.942</td><td>13416</td><td>4358.735952</td>
              <td>3943.618243</td><td>4151.177097</td><td>0.174855</td><td>5.775</td>
              <td>5.225</td><td>5.5</td><td>22.22</td><td>0.397757</td>
              <td>0.359875</td><td>0.378816</td><td>-</td><td>-</td>
              <td>p1</td><td>123@gmail.com</td><td>123456789</td><td>810</td><td>-</td><td>base-design</td>
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
        <div class="breadcrumbs">Emily Configuration</div>
        <h1>Core Parameter Configuration</h1>
      </div>
    </div>
    <div class="card">
      <div class="tabs">
        <button class="tab active" data-tab="gis">GIS Parameters</button>
        <button class="tab" data-tab="house3d">3D House Parameters</button>
        <button class="tab" data-tab="plan">Solution Parameters</button>
        <button class="tab" data-tab="device">Device Parameters</button>
        <button class="tab" data-tab="cost">Cost Parameters</button>
        <button class="tab" data-tab="economic">Economic Parameters</button>
        <button class="tab" data-tab="display">Display Parameters</button>
        <button class="tab" data-tab="mapping">Mapping Data</button>
        <button class="tab" data-tab="fallback">Fallback Parameters</button>
      </div>
      <div class="tab-content active" id="tab-gis">
        <h3>2D Area Parameters</h3>
        <div class="params-grid">
          <div class="param-item"><label>min_2D_area_filter_m2</label><input type="number" value="50"><small>Minimum Roof Area Filter (m²)</small></div>
          <div class="param-item"><label>max_2D_area_filter_m2</label><input type="number" value="600"><small>Maximum Roof Area Filter (m²)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
      </div>
      <div class="tab-content" id="tab-house3d">
        <h3>Panel Dimensions</h3>
        <div class="params-grid">
          <div class="param-item"><label>panel_length_mm</label><input type="number" value="1762"><small>Length (mm)</small></div>
          <div class="param-item"><label>panel_width_mm</label><input type="number" value="1134"><small>Width (mm)</small></div>
          <div class="param-item"><label>panel_thickness_mm</label><input type="number" value="30"><small>Thickness (mm)</small></div>
        </div>
        <h3 style="margin-top:24px">Layout Spacing</h3>
        <div class="params-grid">
          <div class="param-item"><label>inter_module_spacing_mm</label><input type="number" value="20"><small>Inter-module spacing (mm)</small></div>
          <div class="param-item"><label>inter_row_spacing_mm</label><input type="number" value="20"><small>Inter-row spacing (mm)</small></div>
        </div>
        <h3 style="margin-top:24px">Battery Dimensions</h3>
        <div class="params-grid">
          <div class="param-item"><label>battery_length_mm</label><input type="number" value="900"><small>Length (mm)</small></div>
          <div class="param-item"><label>battery_width_mm</label><input type="number" value="1100"><small>Width (mm)</small></div>
          <div class="param-item"><label>battery_height_mm</label><input type="number" value="2000"><small>Height (mm)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
      </div>
      <div class="tab-content" id="tab-plan">
        <h3>Solution Parameters</h3>
        <div class="params-grid">
          <div class="param-item"><label>plan_c_capacity_factor</label><input type="number" step="0.01" value="0.9"><small>Plan C Capacity Factor</small></div>
          <div class="param-item"><label>plan_c_target_sc_rate</label><input type="number" value="50"><small>Plan C Target Self-Consumption Rate (%)</small></div>
          <div class="param-item"><label>dc_ac_ratio</label><input type="number" step="0.1" value="1.5"><small>DC/AC Ratio</small></div>
          <div class="param-item"><label>rooftop_use_factor</label><input type="number" step="0.1" value="0.7"><small>Rooftop Theoretical Max Capacity Factor</small></div>
          <div class="param-item"><label>baseline_self_consumption_rate</label><input type="number" value="30"><small>Baseline Self-Consumption Rate (No Battery) %</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
      </div>
      <div class="tab-content" id="tab-device">
        <h3>Panel Parameters</h3>
        <div class="params-grid">
          <div class="param-item"><label>panel_power_kw</label><input type="number" step="0.01" value="0.44"><small>Standardized Panel Unit Power (kW)</small></div>
          <div class="param-item"><label>panel_first_year_degradation_rate</label><input type="number" value="0"><small>Panel First Year Degradation Rate (%)</small></div>
          <div class="param-item"><label>panel_annual_degradation_rate</label><input type="number" step="0.01" value="0.40"><small>Panel Annual Degradation Rate (from Year 2) (%)</small></div>
          <div class="param-item"><label>pv_system_efficiency</label><input type="number" value="85"><small>System Efficiency (%)</small></div>
        </div>
        
        <h3 style="margin-top:24px">Battery Parameters</h3>
        <div class="params-grid">
          <div class="param-item"><label>battery_dod</label><input type="number" value="90"><small>Battery Depth of Discharge (DoD) (%)</small></div>
          <div class="param-item"><label>battery_rte</label><input type="number" value="95"><small>Battery Round-Trip Efficiency (RTE) (%)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
      </div>
      <div class="tab-content" id="tab-cost">
        <h3>Pre-Tax Pricing Parameters</h3>
        <div class="params-grid">
          <div class="param-item"><label>panel_unit_price_per_kw</label><input type="number" value="540"><small>Panel Unit Price per kW (AUD/kW)</small></div>
          <div class="param-item"><label>inverter_unit_price_per_kw</label><input type="number" value="280"><small>Inverter Unit Price per kW (AUD/kW)</small></div>
          <div class="param-item"><label>battery_unit_price_per_kwh</label><input type="number" value="865"><small>Battery Unit Price per kWh (AUD/kWh)</small></div>
        </div>
        
        <h3 style="margin-top:24px">Tax Parameters</h3>
        <div class="params-grid">
          <div class="param-item"><label>tax_rate</label><input type="number" step="0.01" value="10"><small>Tax Rate (%)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
      </div>
      <div class="tab-content" id="tab-economic">
        <h3>Electricity Pricing & Economic Parameters</h3>
        <div class="params-grid">
          <div class="param-item"><label>grid_buy_rate</label><input type="number" step="0.01" value="0.3"><small>Grid Buy Rate (AUD/kWh)</small></div>
          <div class="param-item"><label>grid_sell_rate</label><input type="number" step="0.01" value="0.07"><small>Grid Sell Rate (AUD/kWh)</small></div>
          <div class="param-item"><label>daily_fixed_charge</label><input type="number" step="0.01" value="0.35"><small>Daily Fixed Charge (AUD/day)</small></div>
          <div class="param-item"><label>electricity_inflation_rate</label><input type="number" step="0.01" value="3.97"><small>Electricity Inflation Rate (%)</small></div>
          <div class="param-item"><label>cash_interest_rate</label><input type="number" step="0.01" value="1.36"><small>Cash Interest Rate (%)</small></div>
          <div class="param-item"><label>existing_sc_rate</label><input type="number" value="30"><small>Existing System Baseline Self-Consumption Rate (%)</small></div>
          <div class="param-item"><label>battery_replacement_year</label><input type="number" value="10"><small>Battery Replacement Year (Years)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
        
        <h3 style="margin-top:32px">Annual Electricity Usage by State/Territory</h3>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>States</th><th>Avg. Annual kWh Usage</th></tr></thead>
            <tbody>
              <tr><td>TAS</td><td><input type="number" value="10148" style="width:120px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>NT</td><td><input type="number" value="10008" style="width:120px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>ACT</td><td><input type="number" value="8632" style="width:120px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>SA</td><td><input type="number" value="7129" style="width:120px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>NSW</td><td><input type="number" value="7778" style="width:120px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>QLD</td><td><input type="number" value="7270" style="width:120px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>WA</td><td><input type="number" value="7634" style="width:120px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>VIC</td><td><input type="number" value="6778" style="width:120px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
      </div>
      <div class="tab-content" id="tab-display">
        <h3>Display Range Parameters</h3>
        <div class="params-grid">
          <div class="param-item"><label>display_range_percent_self_consumption</label><input type="number" value="5"><small>Self-Consumption Display Range (%)</small></div>
          <div class="param-item"><label>display_range_percent_annual_savings</label><input type="number" value="5"><small>Annual Savings Display Range (%)</small></div>
          <div class="param-item"><label>display_range_percent_payback_period</label><input type="number" value="5"><small>Payback Period Display Range (%)</small></div>
          <div class="param-item"><label>display_range_percent_final_price</label><input type="number" value="5"><small>Final Price Display Range (%)</small></div>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
      </div>
      <div class="tab-content" id="tab-fallback">
        <h3>Part 1: Hourly Generation Fallback</h3>
        <div class="params-grid">
          <div class="param-item"><label>yield_per_kw_per_year_fallback</label><input type="number" value="1526"><small>Annual Generation Coefficient (kWh/kW/yr)</small></div>
        </div>
        <div class="button-row" style="justify-content:flex-start"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
        
        <h3 style="margin-top:24px">Monthly Generation Ratio Fallback Configuration</h3>
        <div class="upload-area">
          <p>Upload Excel or CSV file to replace current configuration</p>
          <input type="file" id="upload-monthly-ratio" accept=".xlsx,.xls,.csv">
          <label for="upload-monthly-ratio" class="upload-label">Choose File to Upload</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>Month</th><th>Generation Ratio (%)</th></tr></thead>
            <tbody>
              <tr><td>January</td><td>8.5</td></tr>
              <tr><td>February</td><td>8.2</td></tr>
              <tr><td>March</td><td>8.8</td></tr>
              <tr><td>April</td><td>8.0</td></tr>
              <tr><td>May</td><td>7.5</td></tr>
              <tr><td>June</td><td>7.0</td></tr>
              <tr><td>July</td><td>7.5</td></tr>
              <tr><td>August</td><td>8.0</td></tr>
              <tr><td>September</td><td>8.5</td></tr>
              <tr><td>October</td><td>9.0</td></tr>
              <tr><td>November</td><td>9.5</td></tr>
              <tr><td>December</td><td>9.5</td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row" style="justify-content:flex-start"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
        
        <h3 style="margin-top:24px">24-Hour Generation Ratio Fallback Configuration</h3>
        <div class="upload-area">
          <p>Upload Excel or CSV file to replace current configuration</p>
          <input type="file" id="upload-hourly-ratio" accept=".xlsx,.xls,.csv">
          <label for="upload-hourly-ratio" class="upload-label">Choose File to Upload</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>Hour</th><th>Generation Ratio (%)</th></tr></thead>
            <tbody>
              <tr><td>0-1</td><td>0</td></tr>
              <tr><td>1-2</td><td>0</td></tr>
              <tr><td>2-3</td><td>0</td></tr>
              <tr><td>3-4</td><td>0</td></tr>
              <tr><td>4-5</td><td>0</td></tr>
              <tr><td>5-6</td><td>0</td></tr>
              <tr><td>6-7</td><td>2.5</td></tr>
              <tr><td>7-8</td><td>5.0</td></tr>
              <tr><td>8-9</td><td>8.5</td></tr>
              <tr><td>9-10</td><td>11.0</td></tr>
              <tr><td>10-11</td><td>13.0</td></tr>
              <tr><td>11-12</td><td>14.5</td></tr>
              <tr><td>12-13</td><td>15.0</td></tr>
              <tr><td>13-14</td><td>14.5</td></tr>
              <tr><td>14-15</td><td>13.0</td></tr>
              <tr><td>15-16</td><td>11.0</td></tr>
              <tr><td>16-17</td><td>8.5</td></tr>
              <tr><td>17-18</td><td>5.0</td></tr>
              <tr><td>18-19</td><td>2.5</td></tr>
              <tr><td>19-20</td><td>0</td></tr>
              <tr><td>20-21</td><td>0</td></tr>
              <tr><td>21-22</td><td>0</td></tr>
              <tr><td>22-23</td><td>0</td></tr>
              <tr><td>23-24</td><td>0</td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row" style="justify-content:flex-start"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
        
        <h3 style="margin-top:32px">Part 2: State/Territory Postcode Fallback</h3>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>State/Territory</th><th>Fallback Postcode</th></tr></thead>
            <tbody>
              <tr><td>New South Wales (NSW)</td><td><input type="text" value="2000" style="width:100px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>Victoria (VIC)</td><td><input type="text" value="3000" style="width:100px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>Queensland (QLD)</td><td><input type="text" value="4000" style="width:100px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>South Australia (SA)</td><td><input type="text" value="5000" style="width:100px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>Western Australia (WA)</td><td><input type="text" value="6000" style="width:100px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>Tasmania (TAS)</td><td><input type="text" value="7000" style="width:100px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>Northern Territory (NT)</td><td><input type="text" value="0800" style="width:100px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
              <tr><td>Australian Capital Territory (ACT)</td><td><input type="text" value="2600" style="width:100px;padding:6px;border:1px solid var(--border);border-radius:6px"></td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
      </div>
      <div class="tab-content" id="tab-mapping">
        <h3>GS Power Mapping Table</h3>
        <div class="upload-area">
          <p>Upload Excel or CSV file to replace current mapping parameters</p>
          <input type="file" id="upload-gs" accept=".xlsx,.xls,.csv">
          <label for="upload-gs" class="upload-label">Choose File to Upload</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>Start Value</th><th>Range</th><th>nominal_battery_capacity_kwh</th><th>usable_battery_capacity_kwh</th><th>inverter_kw</th></tr></thead>
            <tbody>
              <tr><td>0</td><td>(0,5]</td><td>22.44</td><td>20.2</td><td>8</td></tr>
              <tr><td>5</td><td>(5,7.5]</td><td>22.22</td><td>20</td><td>9.6</td></tr>
              <tr><td>7.5</td><td>(7.5,12]</td><td>29.33</td><td>26.4</td><td>9.994</td></tr>
              <tr><td>12</td><td>(12,20]</td><td>28.04</td><td>25.24</td><td>9.3</td></tr>
              <tr><td>20</td><td>(20,100]</td><td>50.32</td><td>45.29</td><td>19.50</td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
        
        <h3 style="margin-top:32px">GD Power Mapping Table</h3>
        <div class="upload-area">
          <p>Upload Excel or CSV file to replace current mapping parameters</p>
          <input type="file" id="upload-gd" accept=".xlsx,.xls,.csv">
          <label for="upload-gd" class="upload-label">Choose File to Upload</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>Start Value</th><th>Range</th><th>nominal_battery_capacity_kwh</th><th>usable_battery_capacity_kwh</th><th>inverter_kw</th></tr></thead>
            <tbody>
              <tr><td>0</td><td>(0,5]</td><td>15.00</td><td>13.50</td><td>5.00</td></tr>
              <tr><td>5</td><td>(5,7.5]</td><td>14.82</td><td>13.34</td><td>5.00</td></tr>
              <tr><td>7.5</td><td>(7.5,12]</td><td>17.33</td><td>15.60</td><td>7.22</td></tr>
              <tr><td>12</td><td>(12,20]</td><td>22.22</td><td>20.00</td><td>10.00</td></tr>
              <tr><td>20</td><td>(20,100]</td><td>41.93</td><td>37.74</td><td>15.00</td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
        
        <h3 style="margin-top:32px">Battery Expansion Power Mapping Table</h3>
        <div class="upload-area">
          <p>Upload Excel or CSV file to replace current mapping parameters</p>
          <input type="file" id="upload-battery" accept=".xlsx,.xls,.csv">
          <label for="upload-battery" class="upload-label">Choose File to Upload</label>
        </div>
        <div style="overflow-x:auto">
          <table>
            <thead><tr><th>Start Value</th><th>PV kW</th><th>Nominal Capacity A</th><th>Usable Capacity A</th><th>Nominal Capacity B</th><th>Usable Capacity B</th><th>Nominal Capacity C</th><th>Usable Capacity C</th></tr></thead>
            <tbody>
              <tr><td>0</td><td>(0,5]</td><td>11.11</td><td>10.00</td><td>15.00</td><td>13.50</td><td>16.67</td><td>15.00</td></tr>
              <tr><td>5</td><td>(5,7.5]</td><td>11.11</td><td>10.00</td><td>15.00</td><td>13.50</td><td>21.33</td><td>19.20</td></tr>
              <tr><td>7.5</td><td>(7.5,12]</td><td>15.33</td><td>13.80</td><td>17.78</td><td>16.00</td><td>26.00</td><td>23.40</td></tr>
              <tr><td>12</td><td>(12,20]</td><td>21.33</td><td>19.20</td><td>26.00</td><td>23.40</td><td>33.33</td><td>30.00</td></tr>
              <tr><td>20</td><td>(20,100]</td><td>33.33</td><td>30.00</td><td>47.78</td><td>43.00</td><td>55.56</td><td>50.00</td></tr>
            </tbody>
          </table>
        </div>
        <div class="button-row"><button class="btn btn-outline">Reset to Default</button><button class="btn btn-primary">Save Configuration</button><button class="btn btn-outline">Set as Default</button></div>
      </div>
    </div>
  `
};

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('toggleSidebar');
  const mainContent = document.getElementById('mainContent');
  const menuItems = document.querySelectorAll('.sidebar li');
  
  // Sidebar collapse/expand
  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
  
  // Page switching
  function switchPage(pageName) {
    mainContent.innerHTML = pages[pageName];
    menuItems.forEach(item => item.classList.remove('active'));
    document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
    
    // If params page, initialize tab switching
    if (pageName === 'params') {
      initTabs();
    }
    
    // If export page, initialize filter button
    if (pageName === 'export') {
      initExportPage();
    }
  }
  
  // Data export page initialization
  function initExportPage() {
    const filterBtn = document.getElementById('filterBtn');
    const resultCard = document.getElementById('resultCard');
    
    if (filterBtn) {
      filterBtn.addEventListener('click', () => {
        resultCard.style.display = 'block';
      });
    }
  }
  
  // Tab switching
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
  
  // Menu click event
  menuItems.forEach(item => {
    item.addEventListener('click', () => {
      const pageName = item.dataset.page;
      // Accounts menu redirects to external link
      if (pageName === 'accounts') {
        window.location.href = 'https://gs-admin.greensketch.ai/accounts';
        return;
      }
      switchPage(pageName);
    });
  });
  
  // Load data export page by default
  switchPage('export');
  
  // User menu interaction
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
  
  // Click outside to close menu
  document.addEventListener('click', (e) => {
    if (userDropdown && !userDropdown.contains(e.target) && e.target !== userMenuBtn) {
      userDropdown.classList.remove('show');
    }
  });
  
  // Change password
  if (changePasswordBtn) {
    changePasswordBtn.addEventListener('click', () => {
      alert('Change password feature');
      userDropdown.classList.remove('show');
    });
  }
  
  // Logout
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      window.location.href = 'login.html';
    });
  }
});
