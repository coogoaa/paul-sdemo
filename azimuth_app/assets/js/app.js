/* 方位角选择器 - 纯原生 SVG + JS 实现
 * 功能：
 * - 绘制 360° 方位盘（主/辅刻度 + 方位标签）
 * - 可拖拽扇形（中心线与末端手柄）
 * - 实时显示角度与方位名称
 * - 支持张角调节（滑块）
 */
(function () {
  const svg = document.getElementById('azimuthDial');
  const ticksGroup = document.getElementById('ticks');
  const cardinalGroup = document.getElementById('cardinal');
  const sectorPath = document.getElementById('sector');
  const sectorLine = document.getElementById('sectorLine');
  const handle = document.getElementById('handle');
  const angleValue = document.getElementById('angleValue');
  const compassNameEl = document.getElementById('compassName');
  const sectorWidthInput = document.getElementById('sectorWidth');
  const sectorWidthValue = document.getElementById('sectorWidthValue');

  const R = 160; // 半径，与 index.html 中的元素一致

  // 状态
  const state = {
    centerAngle: 0, // 以正北为 0°，顺时针递增
    sectorWidth: Number(sectorWidthInput?.value || 30),
    dragging: false,
    // 拖拽目标：'handle' | 'sector'
    dragTarget: null,
  };

  // 工具函数
  function degToRad(d) { return d * Math.PI / 180; }
  function radToDeg(r) { return r * 180 / Math.PI; }
  function mod360(a) { return (a % 360 + 360) % 360; }

  // 角度 -> 坐标（以正北为 0°，顺时针）
  function polarToXY(angleDeg, radius) {
    const a = degToRad(angleDeg);
    const x = Math.sin(a) * radius; // 注意：将 x 与 sin 关联，以 0° 在正上方
    const y = -Math.cos(a) * radius; // y 轴向下，0° 时 y = -R
    return { x, y };
  }

  // 坐标 -> 角度（正北=0°, 顺时针）
  function xyToAngle(x, y) {
    // 标准 atan2 的参数顺序 atan2(y, x)
    // 我们希望：正北=0°，顺时针增大 => angle = atan2(x, -y)
    const angleRad = Math.atan2(x, -y);
    return mod360(radToDeg(angleRad));
  }

  // 角度映射到 16 方位名称
  const COMPASS_16 = [
    'N', 'NNE', 'NE', 'ENE',
    'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW',
    'W', 'WNW', 'NW', 'NNW',
  ];
  function angleToCompassName(angle) {
    const idx = Math.round(mod360(angle) / 22.5) % 16;
    return COMPASS_16[idx];
  }

  // 绘制刻度与标签
  function drawTicks() {
    ticksGroup.innerHTML = '';

    for (let d = 0; d < 360; d += 10) {
      const isMajor = (d % 30 === 0);
      const innerR = isMajor ? R - 16 : R - 10;
      const outerR = R;
      const p1 = polarToXY(d, innerR);
      const p2 = polarToXY(d, outerR);

      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', p1.x.toFixed(3));
      line.setAttribute('y1', p1.y.toFixed(3));
      line.setAttribute('x2', p2.x.toFixed(3));
      line.setAttribute('y2', p2.y.toFixed(3));
      line.setAttribute('class', isMajor ? 'tick-major' : 'tick-minor');
      ticksGroup.appendChild(line);

      if (isMajor) {
        const tl = polarToXY(d, R + 14);
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', tl.x.toFixed(3));
        text.setAttribute('y', tl.y.toFixed(3));
        text.setAttribute('class', 'tick-label');
        text.textContent = String(d);
        ticksGroup.appendChild(text);
      }
    }
  }

  // 绘制方位标签 N E S W 与 NE 等
  function drawCardinalLabels() {
    cardinalGroup.innerHTML = '';

    const labels = [
      { a: 0,   t: 'N' },
      { a: 45,  t: 'NE' },
      { a: 90,  t: 'E' },
      { a: 135, t: 'SE' },
      { a: 180, t: 'S' },
      { a: 225, t: 'SW' },
      { a: 270, t: 'W' },
      { a: 315, t: 'NW' },
    ];

    labels.forEach(({ a, t }) => {
      const pos = polarToXY(a, R + 28);
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', pos.x.toFixed(3));
      text.setAttribute('y', pos.y.toFixed(3));
      text.setAttribute('class', 'cardinal-label');
      text.textContent = t;
      cardinalGroup.appendChild(text);
    });
  }

  // 更新扇形与中心线、手柄位置
  function updateSector() {
    const c = state.centerAngle;
    const half = state.sectorWidth / 2;
    const start = mod360(c - half);
    const end = mod360(c + half);

    const pStart = polarToXY(start, R);
    const pEnd = polarToXY(end, R);

    // 大弧标志：因为 sectorWidth <= 120，不会超过 180，因此固定 0 更安全
    const largeArcFlag = state.sectorWidth > 180 ? 1 : 0; // 当前滑块上限 120，此处仍处理泛化
    const sweepFlag = 1; // 顺时针

    const d = [
      `M 0 0`,
      `L ${pStart.x.toFixed(3)} ${pStart.y.toFixed(3)}`,
      `A ${R} ${R} 0 ${largeArcFlag} ${sweepFlag} ${pEnd.x.toFixed(3)} ${pEnd.y.toFixed(3)}`,
      `Z`
    ].join(' ');
    sectorPath.setAttribute('d', d);

    // 更新中心线与手柄
    const pc = polarToXY(c, R);
    sectorLine.setAttribute('x2', pc.x.toFixed(3));
    sectorLine.setAttribute('y2', pc.y.toFixed(3));
    handle.setAttribute('cx', pc.x.toFixed(3));
    handle.setAttribute('cy', pc.y.toFixed(3));

    // 读数
    angleValue.textContent = `${Math.round(c)}°`;
    compassNameEl.textContent = angleToCompassName(c);
  }

  // 指针位置 -> 更新角度
  function updateAngleFromPointer(evt) {
    const pt = getSVGPoint(evt);
    const angle = xyToAngle(pt.x, pt.y);
    state.centerAngle = angle;
    updateSector();
  }

  // 将事件坐标转换到 SVG 本地坐标
  function getSVGPoint(evt) {
    const point = svg.createSVGPoint();
    const isTouch = evt.touches && evt.touches.length;
    const clientX = isTouch ? evt.touches[0].clientX : evt.clientX;
    const clientY = isTouch ? evt.touches[0].clientY : evt.clientY;
    point.x = clientX;
    point.y = clientY;
    const ctm = svg.getScreenCTM();
    return point.matrixTransform(ctm.inverse());
  }

  // 事件绑定
  function bindInteractions() {
    function startDrag(target) {
      return function (evt) {
        evt.preventDefault();
        state.dragging = true;
        state.dragTarget = target;
        updateAngleFromPointer(evt);
      };
    }
    function duringDrag(evt) {
      if (!state.dragging) return;
      updateAngleFromPointer(evt);
    }
    function endDrag() {
      state.dragging = false;
      state.dragTarget = null;
    }

    // 支持在扇形、中心线、手柄上开始拖拽
    ['mousedown', 'touchstart'].forEach(ev => {
      handle.addEventListener(ev, startDrag('handle'));
      sectorPath.addEventListener(ev, startDrag('sector'));
      sectorLine.addEventListener(ev, startDrag('sector'));
    });

    ['mousemove', 'touchmove'].forEach(ev => {
      window.addEventListener(ev, duringDrag, { passive: false });
    });
    ['mouseup', 'mouseleave', 'touchend', 'touchcancel'].forEach(ev => {
      window.addEventListener(ev, endDrag);
    });

    // 点击空白区域也可以快速设定角度
    svg.addEventListener('click', function (evt) {
      // 避免拖拽结束瞬间触发 click 再次更新
      if (state.dragging) return;
      updateAngleFromPointer(evt);
    });

    // 滑块 - 扇形张角
    sectorWidthInput.addEventListener('input', () => {
      const val = Number(sectorWidthInput.value);
      state.sectorWidth = Math.min(Math.max(val, 5), 160);
      sectorWidthValue.textContent = String(state.sectorWidth);
      updateSector();
    });
  }

  // 初始化
  function init() {
    drawTicks();
    drawCardinalLabels();
    bindInteractions();
    updateSector();
  }

  init();
})();
