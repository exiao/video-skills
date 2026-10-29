// Builds the AE-style workspace from build/timeline.json (window.TL injected by render_ui.js,
// or fetched when the page is served over http). Every coordinate that timeline.py defines is
// read from TL.layout; only intra-panel decoration (labels, icons) is placed here.
(async function () {
  const TL = window.TL || await (await fetch('../build/timeline.json')).json();
  const L = TL.layout;
  const ws = document.getElementById('ws');
  const DIM = '#8a8a8a', TXT = '#b5b5b5', HI = '#e4e4e4', BLUE = '#2d8ceb';

  // ------------------------------------------------------------------ helpers
  function box(x, y, w, h, css = {}, cls = '', parent = ws) {
    const d = document.createElement('div');
    if (cls) d.className = cls;
    Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px' }, css);
    parent.appendChild(d);
    return d;
  }
  // Text whose vertical centre is y. align: left | center | right (x is the anchor).
  function txt(x, y, s, o = {}) {
    const size = o.size || 9, h = Math.ceil(size * 1.5);
    const d = document.createElement('div');
    d.className = 't' + (o.cls ? ' ' + o.cls : '');
    d.textContent = s;
    const css = {
      top: (y - h / 2) + 'px', height: h + 'px', lineHeight: h + 'px', fontSize: size + 'px',
      color: o.color === 'class' ? '' : (o.color || TXT), fontWeight: o.weight || 400, letterSpacing: (o.ls || 0) + 'px',
    };
    if (o.align === 'right') { css.right = (1280 - x) + 'px'; css.textAlign = 'right'; }
    else if (o.align === 'center') { css.left = (x - 200) + 'px'; css.width = '400px'; css.textAlign = 'center'; }
    else css.left = x + 'px';
    if (o.italic) css.fontStyle = 'italic';
    Object.assign(d.style, css);
    (o.parent || ws).appendChild(d);
    return d;
  }
  // Icon centred on (cx, cy), drawn size x size px.
  function icon(name, cx, cy, size = 11, color = TXT, o = {}) {
    const d = box(cx - size / 2, cy - size / 2, size, size, { color }, 'ic' + (o.cls ? ' ' + o.cls : ''), o.parent || ws);
    d.innerHTML = `<svg width="${size}" height="${size}" viewBox="0 0 16 16">${ICONS[name]}</svg>`;
    return d;
  }
  const hline = (x, y, w, c = '#111', h = 1) => box(x, y, w, h, { background: c });
  const vline = (x, y, h, c = '#111', w = 1) => box(x, y, w, h, { background: c });
  function tabs(x, y, list, gap = 16) {
    // list: [label, {active, size}] ; returns x after last tab
    let cx = x;
    for (const [label, o = {}] of list) {
      const d = txt(cx, y, label, { size: o.size || 9, color: o.active ? HI : DIM, weight: o.active ? 600 : 400 });
      cx += d.getBoundingClientRect().width + gap;
    }
    return cx;
  }
  function dropdown(x, y, w, label, o = {}) {
    const d = box(x, y - 6.5, w, 13, {}, 'dd');
    txt(x + 4, y, label, { size: o.size || 8, color: o.color || TXT });
    icon('chevronDown', x + w - 6, y, 7, DIM);
    return d;
  }
  const P = L.panels;
  const panel = (name) => { const [x, y, w, h] = P[name]; return box(x + 1, y + 1, w - 2, h - 2, {}, 'panel'); };

  // ------------------------------------------------------------------ panels (slab rects from layout)
  for (const name of Object.keys(P)) panel(name);

  // ================================================================== TOPBAR
  {
    const [mx, my, mw, mh] = L.menubar, [tx, ty, tw, th] = L.toolbar;
    box(mx + 1, my + 1, mw - 2, mh - 1, { background: '#1f1f1f', borderRadius: '3px 3px 0 0' });
    hline(mx + 1, my + mh, mw - 2, '#141414');
    let x = mx + 12;
    for (const item of L.menu_items) {
      const d = txt(x, my + mh / 2, item, { size: 9.5, color: '#c4c4c4' });
      x += d.getBoundingClientRect().width + 15;
    }
    txt(mx + mw / 2, my + mh / 2, 'Untitled Project.aep *', { size: 9, color: DIM, align: 'center' });

    // toolbar keycaps at layout.tools (centres), each cap.w x cap.h
    const cw = L.cap.w, ch = L.cap.h;
    const flyouts = new Set(['Zoom', 'Rotate', 'Camera', 'PanBehind', 'Rectangle', 'Pen', 'Type', 'Puppet', 'Roto']);
    for (const name of L.tool_order) {
      const [cx, cy] = L.tools[name];
      const c = box(cx - cw / 2, cy - ch / 2, cw, ch, {}, 'cap' + (name === 'Selection' ? ' on' : ''));
      c.dataset.cap = name;
      icon(name, cw / 2 - 1, ch / 2 - 1, name === 'Type' ? 13 : 13, 'currentColor', { parent: c });
      if (flyouts.has(name)) { const f = document.createElement('div'); f.className = 'flyout'; c.appendChild(f); }
    }
    // Snapping
    const last = L.tools[L.tool_order[L.tool_order.length - 1]];
    const sx = last[0] + cw / 2 + 12, cy = ty + th / 2;
    vline(sx, ty + 7, th - 14, '#3a3a3a');
    icon('check', sx + 14, cy, 10, '#c8c8c8');
    icon('magnet', sx + 28, cy, 10, '#c8c8c8');
    txt(sx + 37, cy, 'Snapping', { size: 9, color: '#c4c4c4' });
    // workspaces (right side of toolbar row)
    const wsx = [['Default'], ['Review'], ['Learning'], ['Standard', true], ['Small Screen'], ['Libraries']];
    let rx = tx + tw - 38;
    icon('search', tx + tw - 16, cy, 11, '#c4c4c4');
    txt(rx + 6, cy, '»', { size: 10, color: DIM });
    for (let i = wsx.length - 1; i >= 0; i--) {
      const [label, active] = wsx[i];
      if (active) { txt(rx, cy, '≡', { size: 9, color: BLUE, align: 'right' }); rx -= 12; }
      const d = txt(rx, cy, label, { size: 9, color: active ? BLUE : '#a8a8a8', align: 'right', weight: active ? 600 : 400 });
      const w = d.getBoundingClientRect().width;
      if (active) box(rx - w, cy + 7, w, 2, { background: BLUE, borderRadius: '1px' });
      rx -= w + 20;
    }
  }

  // ================================================================== PROJECT
  {
    const [x, y, w, h] = P.project;
    box(x + 1, y + 1, w - 2, 19, {}, 'hdr');
    let nx = tabs(x + 10, y + 10, [['Project', { active: true }]], 4);
    txt(nx, y + 10, '≡', { size: 9, color: DIM });
    txt(nx + 18, y + 10, 'Effect Controls', { size: 9, color: DIM });
    txt(nx + 86, y + 10, 'MADE WITH CLAUDE', { size: 8.5, color: '#777' });
    // thumbnail + comp info
    box(x + 8, y + 27, 72, 40, { background: '#000', border: '1px solid #3a3a3a' });
    txt(x + 90, y + 33, 'Main Comp ▾', { size: 9, color: HI, weight: 600 });
    txt(x + 90, y + 46, '1920 x 1080 (1.00)', { size: 8.5 });
    txt(x + 90, y + 58, 'Δ 0;00;10;00, 30.00 fps', { size: 8.5 });
    // search
    box(x + 6, y + 75, w - 12, 15, {}, 'field');
    icon('search', x + 16, y + 82.5, 8, DIM);
    // columns
    hline(x + 1, y + 96, w - 2, '#1a1a1a');
    const hy = y + 104;
    txt(x + 30, hy, 'Name', { size: 8.5, color: DIM }); icon('chevronDown', x + 62, hy, 7, DIM);
    icon('label', x + 152, hy, 8, DIM);
    txt(x + 172, hy, 'Type', { size: 8.5, color: DIM });
    txt(x + 256, hy, 'Size', { size: 8.5, color: DIM });
    vline(x + 144, hy - 6, 12, '#3a3a3a'); vline(x + 164, hy - 6, 12, '#3a3a3a'); vline(x + 244, hy - 6, 12, '#3a3a3a');
    hline(x + 1, y + 112, w - 2, '#1a1a1a');
    const rows = [
      ['comp', 'Main Comp', '#e1b858', 'Composition', ''],
      ['footage', 'clawd.png', '#a99be0', 'PNG file', '240 KB'],
      ['audiofile', 'pop.wav', '#7fcfc0', 'WAV', '88 KB'],
      ['folder', 'Solids', '#e6c229', 'Folder', ''],
    ];
    rows.forEach(([ic, name, col, type, size], i) => {
      const ry = y + 122 + i * 18;
      if (i === 0) box(x + 2, ry - 9, w - 4, 18, { background: '#2c2c2c' });
      if (ic === 'folder') icon('chevronDown', x + 10, ry, 7, DIM, {}).style.transform = 'rotate(-90deg)';
      icon(ic, x + 21, ry, 10, ic === 'comp' ? '#c9c9c9' : '#a9a9a9');
      txt(x + 30, ry, name, { size: 9, color: i === 0 ? HI : '#c4c4c4' });
      box(x + 148, ry - 4, 8, 8, { background: col, borderRadius: '1px' });
      txt(x + 172, ry, type, { size: 8.5 });
      if (size) txt(x + 256, ry, size, { size: 8.5 });
    });
    // footer
    hline(x + 1, y + h - 22, w - 2, '#1a1a1a');
    const fy = y + h - 11;
    icon('newfolder', x + 14, fy, 10, '#9a9a9a');
    icon('newcomp', x + 32, fy, 10, '#9a9a9a');
    icon('footage', x + 50, fy, 10, '#9a9a9a');
    txt(x + 66, fy, '8 bpc', { size: 8.5, color: '#9a9a9a' });
    icon('trash', x + w - 16, fy, 10, '#9a9a9a');
  }

  // ================================================================== COMPOSITION
  {
    const [x, y, w, h] = P.comp;
    const [tx, ty, tw, th] = L.comp_tabs;
    box(tx + 1, ty + 1, tw - 2, th - 1, {}, 'hdr');
    const c1 = txt(tx + 12, ty + th / 2, 'Composition', { size: 9, color: HI, weight: 600 });
    const c1w = c1.getBoundingClientRect().width;
    const c2 = txt(tx + 18 + c1w, ty + th / 2, 'Main Comp', { size: 9, color: '#cfcfcf' });
    const c2r = c2.getBoundingClientRect().right;
    txt(c2r + 6, ty + th / 2, '≡', { size: 9, color: DIM });
    box(tx + 6, ty + th - 2, c2r + 16 - (tx + 6), 2, { background: BLUE, borderRadius: '1px' });
    txt(tx + 220, ty + th / 2, 'Layer  (none)', { size: 9, color: DIM });
    txt(tx + 350, ty + th / 2, 'Footage  (none)', { size: 9, color: DIM });
    // Main Comp sub-tab pill
    const [sx, sy, sw, sh] = L.comp_subtab;
    box(sx + 6, sy + 2, 112, sh - 4, { background: '#333', borderRadius: '7px' });
    icon('comp', sx + 16, sy + sh / 2, 9, '#bdbdbd');
    txt(sx + 26, sy + sh / 2, 'Main Comp', { size: 8.5, color: '#d0d0d0' });
    // viewer surround and the comp view (pure black; the comp canvas is overlaid in 3D)
    const [bx, by, bw, bh] = L.comp_bottom;
    box(x + 2, sy + sh, w - 4, by - (sy + sh), { background: '#2f2f2f' });
    const [vx, vy, vw, vh] = L.comp_view;
    const cv = box(vx, vy, vw, vh, { background: '#000' }); cv.id = 'comp_view';
    // bottom bar
    box(bx + 2, by, bw - 4, bh, { background: '#262626' });
    hline(bx + 2, by, bw - 4, '#151515');
    const cy = by + bh / 2;
    const [tcx, tcy, tcw, tch] = L.tc_comp;
    txt(bx + 10, cy, '50%', { size: 8.5, color: '#c4c4c4' }); icon('chevronDown', bx + 33, cy, 7, DIM);
    txt(bx + 48, cy, 'Full', { size: 8.5, color: '#c4c4c4' }); icon('chevronDown', bx + 68, cy, 7, DIM);
    icon('roi', bx + 88, cy, 9, '#bdbdbd');
    icon('grid', bx + 106, cy, 9, '#9c9c9c');
    icon('snapshot', tcx - 10, cy, 11, '#c4c4c4');
    const tcd = box(tcx, tcy, tcw, tch, {}); tcd.id = 'tc_comp';
    const tcs = txt(0, tch / 2, '', { size: 9.5, color: BLUE, weight: 500, parent: tcd, cls: 'tc' });
    tcs.style.left = '3px'; tcs.id = 'tc_comp_text';
    txt(tcx + tcw + 36, cy, 'Active Camera', { size: 9, color: '#c4c4c4' }); icon('chevronDown', tcx + tcw + 105, cy, 7, DIM);
    txt(tcx + tcw + 136, cy, '1 View', { size: 9, color: '#c4c4c4' }); icon('chevronDown', tcx + tcw + 172, cy, 7, DIM);
    txt(bx + bw - 12, cy, '+0.0', { size: 8.5, color: '#c4c4c4', align: 'right' });
    // active-panel outline (2px blue)
    box(x + 1, y + 1, w - 2, h - 2, { border: '2px solid ' + BLUE, borderRadius: '3px' });
  }

  // ================================================================== INFO
  {
    const [x, y, w, h] = P.info;
    box(x + 1, y + 1, w - 2, 19, {}, 'hdr');
    let nx = tabs(x + 10, y + 10, [['Info', { active: true }]], 4);
    txt(nx, y + 10, '≡', { size: 9, color: DIM });
    txt(nx + 18, y + 10, 'Audio', { size: 9, color: DIM });
    const rows = [['R:', '217', '#e5675f'], ['G:', '119', '#6cc66a'], ['B:', '87', '#5b9fe8']];
    rows.forEach(([k, v, c], i) => {
      txt(x + 12, y + 31 + i * 13, k, { size: 8.5, color: c, weight: 600 });
      txt(x + 30, y + 31 + i * 13, v, { size: 8.5, color: c });
    });
    txt(x + 110, y + 57, 'A:', { size: 8.5, weight: 600 }); txt(x + 126, y + 57, '255', { size: 8.5 });
    txt(x + 250, y + 31, 'X:', { size: 8.5, weight: 600 }); txt(x + 266, y + 31, '1068', { size: 8.5 });
    txt(x + 250, y + 44, 'Y:', { size: 8.5, weight: 600 }); txt(x + 266, y + 44, '532', { size: 8.5 });
  }

  // ================================================================== PREVIEW
  {
    const [x, y, w, h] = P.preview;
    const hy = L.preview_header_y;
    box(x + 1, y + 1, w - 2, (hy - y) * 2 - 1, {}, 'hdr');
    const nx = tabs(x + 10, hy, [['Preview', { active: true }]], 4);
    txt(nx, hy, '≡', { size: 9, color: DIM });
    const pw = L.preview_cap.w, ph = L.preview_cap.h;
    for (const name of ['First', 'Prev', 'Play', 'Next', 'Last']) {
      const [cx, cy] = L.preview_buttons[name];
      const c = box(cx - pw / 2, cy - ph / 2, pw, ph, {}, 'cap');
      c.dataset.cap = 'preview:' + name;
      icon(name, pw / 2 - 1, ph / 2 - 1, name === 'Play' ? 12 : 11, 'currentColor', { parent: c });
    }
    // right of transport: loop + include
    const lastx = L.preview_buttons.Last[0] + pw / 2;
    icon('loop', lastx + 22, L.preview_buttons.Last[1], 11, '#a9a9a9');
    const sy = L.preview_shortcut_y;
    txt(x + 10, sy, 'Shortcut', { size: 8.5, color: DIM });
    txt(x + 56, sy, 'Spacebar', { size: 8.5, color: BLUE });
    icon('chevronDown', x + 100, sy, 7, BLUE);
    txt(x + 232, sy, 'Include:', { size: 8.5, color: DIM });
    icon('video', x + 284, sy, 10, '#c4c4c4');
    icon('speaker', x + 302, sy, 10, '#c4c4c4');
    icon('overlay', x + 320, sy, 10, '#c4c4c4');
    icon('roi', x + 338, sy, 9, '#7a7a7a');
  }

  // ================================================================== EFFECTS & PRESETS
  {
    const [x, y, w, h] = P.effects;
    const hy = L.effects_header_y;
    box(x + 1, y + 1, w - 2, (hy - y) * 2 - 1, {}, 'hdr');
    const nx = tabs(x + 10, hy, [['Effects & Presets', { active: true }]], 4);
    txt(nx, hy, '≡', { size: 9, color: DIM });
    txt(nx + 20, hy, 'Libraries', { size: 9, color: DIM });
    const [sx, sy, sw, sh] = L.effects_search;
    box(sx, sy, sw, sh, {}, 'field');
    icon('search', sx + 11, sy + sh / 2, 9, '#a9a9a9');
    txt(sx + 22, sy + sh / 2, 'glow', { size: 9, color: '#dcdcdc' });
    icon('close', sx + sw - 11, sy + sh / 2, 8, '#a9a9a9');
    // Glow row highlight bar (active state only)
    const [gx, gy, gw, gh] = L.glow_row;
    const gb = box(gx, gy, gw, gh, {}); gb.id = 'glowbar';
    for (const [label, ry, level] of L.effects_rows) {
      const x0 = sx + 4 + level * 16;
      const isGlow = ry >= gy && ry <= gy + gh;
      const col = isGlow ? null : '#c4c4c4';
      if (label.startsWith('▾ ')) {
        icon('chevronDown', x0 + 4, ry, 8, '#9a9a9a');
        icon('folder', x0 + 17, ry, 10, '#b0b0b0');
        txt(x0 + 28, ry, label.slice(2), { size: 9, color: col });
      } else if (label.startsWith('fx ')) {
        const ic = icon('fx', x0 + 17, ry, 11, isGlow ? null : '#b9b9b9', { cls: isGlow ? 'glowrow' : '' });
        if (isGlow) ic.id = 'glow_fx';
        const t = txt(x0 + 28, ry, label.slice(3), { size: 9, color: isGlow ? 'class' : col, weight: isGlow ? 600 : 400, cls: isGlow ? 'glowrow' : '' });
        if (isGlow) t.id = 'glow_text';
      } else txt(x0 + 4, ry, label, { size: 9, color: col });
    }
  }

  // ================================================================== TIMELINE
  {
    const [x, y, w, h] = P.timeline;
    const [tx, ty, tw, th] = L.tl_tabs;
    box(tx + 1, ty + 1, tw - 2, th - 1, {}, 'hdr');
    box(tx + 10, ty + th / 2 - 4, 8, 8, { background: '#e1b858', borderRadius: '1px' });
    const t1 = txt(tx + 24, ty + th / 2, 'Main Comp', { size: 9, color: HI, weight: 600 });
    const t1r = t1.getBoundingClientRect().right;
    txt(t1r + 6, ty + th / 2, '≡', { size: 9, color: DIM });
    icon('close', t1r + 24, ty + th / 2, 7, DIM);
    txt(t1r + 44, ty + th / 2, 'Render Queue', { size: 9, color: DIM });

    const [X0, X1] = L.track_x;
    // big timecode area: left blank (tc_tl texture), with small frame readout beneath
    const [cx, cy, cw, ch] = L.tc_tl;
    const tcd = box(cx, cy, cw, ch, {}); tcd.id = 'tc_tl';
    const tcs = txt(0, ch / 2, '', { size: 18, color: BLUE, weight: 700, parent: tcd, cls: 'tc', ls: 0.2 });
    tcs.style.left = '1px'; tcs.id = 'tc_tl_text';
    txt(cx + 2, cy + ch + 2.5, '00000 (30.00 fps)', { size: 6.5, color: '#7d7d7d' });
    // search + switches
    box(cx + cw + 16, cy + 4, 128, 14, {}, 'field');
    icon('search', cx + cw + 26, cy + 11, 8, DIM);
    ['flow', 'draft3d', 'shy', 'frameblend', 'mblur', 'graph'].forEach((n, i) => icon(n, 316 + i * 20, cy + 11, 11, i === 5 ? '#a9a9a9' : '#a0a0a0'));

    // column header
    const hy = L.tl_colhead_y;
    const rowsTop = L.tl_rows[0][2];
    icon('eye', 12, hy + 2, 8, DIM); icon('speaker', 24, hy + 2, 7, DIM); icon('solo', 36, hy + 2, 5, DIM); icon('lock', 47, hy + 2, 7, DIM);
    icon('label', 65, hy, 8, DIM);
    txt(76, hy, '#', { size: 8.5, color: DIM });
    txt(104, hy, 'Layer Name', { size: 8.5, color: DIM });
    icon('shy', 226, hy, 8, DIM); icon('collapse', 238, hy, 8, DIM); icon('quality', 250, hy, 8, DIM); icon('fx', 262, hy, 9, DIM);
    txt(284, hy, 'Mode', { size: 8.5, color: DIM });
    txt(337, hy, 'T', { size: 8.5, color: DIM });
    txt(349, hy, 'TrkMat', { size: 8.5, color: DIM });
    txt(394, hy, 'Parent & Link', { size: 8.5, color: DIM });
    hline(x + 1, rowsTop - 1, X0 - 2, '#151515');

    // ruler
    const [rx, ry, rw, rh] = L.ruler;
    box(rx, ry, rw, rh, { background: '#262626' });
    const span = X1 - X0, dur = L.comp_duration, fps = TL.fps;
    const u = (ct) => X0 + span * ct / dur;
    const step = 5 / fps; // tick every 5 frames
    for (let k = 0; k * step <= dur + 1e-6; k++) {
      const ct = k * step, xx = u(ct);
      const isSec = Math.abs(ct - Math.round(ct)) < 1e-6, isHalf = Math.abs(ct * 2 - Math.round(ct * 2)) < 1e-6;
      const th2 = isSec ? 9 : isHalf ? 5 : 3;
      box(xx - 0.5, ry + rh - th2, 1, th2, { background: isSec ? '#9a9a9a' : '#5e5e5e' });
    }
    for (let s = 0; s <= dur; s++) {
      const label = s === 0 ? '0s' : String(s).padStart(2, '0') + 's';
      const xx = u(s);
      if (s === 0) txt(xx + 3, ry + 7, label, { size: 8, color: '#a8a8a8' });
      else if (s === dur) txt(xx - 3, ry + 7, label, { size: 8, color: '#a8a8a8', align: 'right' });
      else txt(xx, ry + 7, label, { size: 8, color: '#a8a8a8', align: 'center' });
    }
    // work area bar under the ruler
    box(X0, ry + rh + 3, span, 6, { background: '#3d3d3d', borderRadius: '1px' });
    box(X0, ry + rh + 3, 3, 6, { background: '#6a6a6a' }); box(X1 - 3, ry + rh + 3, 3, 6, { background: '#6a6a6a' });
    vline(X0 - 1, ry, y + h - ry - 22, '#111');
    // track area background
    box(X0, rowsTop, span, y + h - 23 - rowsTop, { background: '#1c1c1c' });
    box(X1, ry, x + w - 1 - X1, y + h - 23 - ry, { background: '#202020' });

    // rows
    const rows = L.tl_rows;
    rows.forEach(([label, kind, top, colour], i) => {
      const next = i + 1 < rows.length ? rows[i + 1][2] : top + L.tl_row_h;
      const rh2 = next - top, mid = top + rh2 / 2;
      hline(x + 1, next - 1, X0 - 2, '#1a1a1a');
      if (kind === 'layer') {
        const [num, glyph, name] = label.split(/\s{2,}/);
        icon('eye', 12, mid, 9, '#bdbdbd');
        icon('chevronDown', 55, mid, 7, '#9a9a9a').style.transform = num === '1' ? '' : 'rotate(-90deg)';
        box(61, mid - 4, 8, 8, { background: colour, borderRadius: '1px' });
        txt(74, mid, num, { size: 8.5, color: '#c4c4c4' });
        const ic = { 'T': 'textlayer', '★': 'star', '▣': 'footage', '■': 'solid' }[glyph] || 'solid';
        icon(ic, 91, mid, 10, ic === 'solid' ? '#e8e8e8' : '#c9c9c9');
        txt(104, mid, name, { size: 9, color: num === '1' ? HI : '#cdcdcd', weight: num === '1' ? 600 : 400 });
        icon(glyph === 'T' ? 'quality' : 'collapse', 238, mid, 8, '#9a9a9a');
        icon('quality', 250, mid, 8, '#9a9a9a');
        if (num === '1') icon('fx', 262, mid, 9, '#9a9a9a');
        dropdown(280, mid, 48, 'Normal');
        dropdown(346, mid, 38, 'None');
        icon('parent', 397, mid, 9, '#9a9a9a');
        dropdown(406, mid, 40, 'None');
        // coloured track bar across the whole track width
        box(X0, top + 2, span, rh2 - 4, { background: colour, borderRadius: '2px',
          backgroundImage: 'linear-gradient(rgba(255,255,255,0.10), rgba(0,0,0,0.10))' });
      } else if (kind === 'group') {
        icon('chevronDown', 96, mid, 7, '#9a9a9a');
        txt(106, mid, label, { size: 9, color: '#c4c4c4' });
        txt(284, mid, 'Reset', { size: 8.5, color: BLUE });
        box(X0, top, span, rh2, { background: '#191919' });
      } else {
        if (label === 'Position') {
          icon('keyprev', 24, mid, 8, '#bdbdbd'); icon('keydiamond', 35, mid, 8, '#bdbdbd'); icon('keynext', 46, mid, 8, '#bdbdbd');
        }
        icon('stopwatch', 112, mid, 9, label === 'Position' ? BLUE : '#a9a9a9');
        txt(122, mid, label, { size: 9, color: '#c4c4c4' });
        if (label === 'Scale') icon('link', 206, mid, 9, '#a9a9a9');
        txt(214, mid, label === 'Position' ? '960.0,540.0' : '100.0,100.0%', { size: 9, color: BLUE });
        box(X0, top, span, rh2, { background: '#151515' });
      }
      hline(X0, next - 1, span, '#121212');
    });

    // footer
    hline(x + 1, y + h - 22, w - 2, '#151515');
    const fy = y + h - 11;
    txt(12, fy, 'Frame Render Time  0ms', { size: 8, color: '#8a8a8a' });
    txt(290, fy, 'Toggle Switches / Modes', { size: 8, color: '#a8a8a8' });
    icon('mountainS', X0 + 10, fy, 9, '#7a7a7a');
    box(X0 + 22, fy - 1, 120, 2, { background: '#3a3a3a', borderRadius: '1px' });
    box(X0 + 60, fy - 4, 8, 8, { background: '#9a9a9a', borderRadius: '4px' });
    icon('mountainL', X0 + 154, fy, 11, '#7a7a7a');
  }

  // ------------------------------------------------------------------ API for render_ui.js
  const ACTIVE_TOOLS = ['Type', 'Rectangle', 'Pen'];
  window.setUIState = function (mode) {
    const active = mode === 'active';
    document.querySelectorAll('.cap[data-cap]').forEach((c) => {
      const n = c.dataset.cap;
      let on = false;
      if (n === 'Selection') on = !active;
      else if (ACTIVE_TOOLS.includes(n)) on = active;
      else if (n === 'preview:Play') on = active;
      c.classList.toggle('on', on);
    });
    document.getElementById('glowbar').classList.toggle('on', active);
    document.querySelectorAll('.glowrow').forEach((e) => e.classList.toggle('on', active));
  };
  window.setTimecode = function (comp, tl) {
    document.getElementById('tc_comp_text').textContent = comp;
    document.getElementById('tc_tl_text').textContent = tl;
  };
  window.measureUI = function () {
    const r = (e) => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; };
    const out = { caps: {}, preview: {} };
    document.querySelectorAll('.cap[data-cap]').forEach((c) => {
      const n = c.dataset.cap;
      if (n.startsWith('preview:')) out.preview[n.slice(8)] = r(c); else out.caps[n] = r(c);
    });
    out.glow_row = r(document.getElementById('glowbar'));
    out.comp_view = r(document.getElementById('comp_view'));
    out.tc_comp = r(document.getElementById('tc_comp'));
    out.tc_tl = r(document.getElementById('tc_tl'));
    return out;
  };
  await document.fonts.ready;
  window.UI_READY = true;
})();
