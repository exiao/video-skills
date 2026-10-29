// Helper routines run inside the comp page by render_ui.js: assets, contact sheet, downscale, diffs.
(function () {
  const mk = (w, h) => { const k = document.createElement('canvas'); k.width = w; k.height = h; return k; };
  const load = (src) => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });

  // clawd_card.png: same drawClawd as the comp layer, 960 px wide, transparent, 12 comp-px padding.
  window.renderCard = function () {
    const { G, drawClawd } = window.COMP;
    const pad = 12, cw = G.figW + 2 * pad, ch = G.figH + 2 * pad;
    const k = 960 / cw, H = Math.round(ch * k);
    const c = mk(960, H), x = c.getContext('2d');
    drawClawd(x, 480, H / 2, k);
    return {
      url: c.toDataURL('image/png'), w: 960, h: H, scale: k,
      comp_rect: [960 - cw / 2, 540 - ch / 2, cw, ch],
      figure_comp_rect: [960 - G.figW / 2, 540 - G.figH / 2, G.figW, G.figH],
      figure_px_rect: [pad * k, pad * k, G.figW * k, G.figH * k],
      body_px_rect: [480 - G.body.w / 2 * k, H / 2 + (G.bodyDy - G.body.h / 2) * k, G.body.w * k, G.body.h * k],
    };
  };

  // glow_chip.png: 512x192 chip face.
  window.renderChip = function () {
    const c = mk(512, 192), x = c.getContext('2d');
    const { rr } = window.COMP;
    const g = x.createLinearGradient(0, 0, 0, 192);
    g.addColorStop(0, '#4aa6ff'); g.addColorStop(0.55, '#2d8ceb'); g.addColorStop(1, '#1b63bf');
    rr(x, 4, 4, 504, 184, 30); x.fillStyle = g; x.fill();
    x.lineWidth = 4; x.strokeStyle = 'rgba(180,220,255,0.85)'; x.stroke();
    // subtle top highlight
    x.save(); rr(x, 4, 4, 504, 184, 30); x.clip();
    const hg = x.createLinearGradient(0, 4, 0, 100);
    hg.addColorStop(0, 'rgba(255,255,255,0.32)'); hg.addColorStop(1, 'rgba(255,255,255,0)');
    x.fillStyle = hg; x.beginPath(); x.ellipse(256, 0, 300, 96, 0, 0, Math.PI * 2); x.fill();
    x.restore();
    // fx badge
    rr(x, 34, 40, 112, 112, 22); x.fillStyle = '#ffffff'; x.fill();
    x.fillStyle = '#1f72d6'; x.font = 'italic 700 76px Georgia, "Times New Roman", serif';
    x.textAlign = 'center'; x.textBaseline = 'alphabetic'; x.fillText('fx', 88, 122);
    // label
    x.fillStyle = '#ffffff'; x.font = '700 92px "SF Pro Display", -apple-system, "Helvetica Neue", Arial, sans-serif';
    x.textAlign = 'left'; x.shadowColor = 'rgba(0,30,80,0.35)'; x.shadowOffsetY = 3; x.shadowBlur = 6;
    x.fillText('Glow', 176, 128);
    return c.toDataURL('image/png');
  };

  // Paste rects (texture px) of `activeUrl` over `baseUrl`; guarantees all other pixels are identical.
  window.compositeRegions = async function (baseUrl, activeUrl, rects) {
    const a = await load(baseUrl), b = await load(activeUrl);
    const c = mk(a.width, a.height), x = c.getContext('2d');
    x.drawImage(a, 0, 0);
    for (const [rx, ry, rw, rh] of rects) { x.clearRect(rx, ry, rw, rh); x.drawImage(b, rx, ry, rw, rh, rx, ry, rw, rh); }
    return c.toDataURL('image/png');
  };

  window.contactSheet = async function (items, cols, tw, th) {
    const rows = Math.ceil(items.length / cols), lh = 24;
    const c = mk(cols * tw, rows * (th + lh)), x = c.getContext('2d');
    x.fillStyle = '#111'; x.fillRect(0, 0, c.width, c.height);
    for (let i = 0; i < items.length; i++) {
      const img = await load(items[i].url);
      const cx = (i % cols) * tw, cy = Math.floor(i / cols) * (th + lh);
      x.drawImage(img, cx + 1, cy + 1, tw - 2, th - 2);
      x.fillStyle = '#ddd'; x.font = '600 15px -apple-system, Helvetica, Arial'; x.textBaseline = 'middle';
      x.fillText(items[i].label, cx + 8, cy + th + lh / 2);
    }
    return c.toDataURL('image/png');
  };

  window.downscale = async function (url, w, h) {
    const img = await load(url);
    const c = mk(w, h), x = c.getContext('2d');
    x.imageSmoothingQuality = 'high'; x.drawImage(img, 0, 0, w, h);
    return c.toDataURL('image/png');
  };

  async function pixels(url) {
    const img = await load(url);
    const c = mk(img.width, img.height), x = c.getContext('2d');
    x.drawImage(img, 0, 0);
    return { w: img.width, h: img.height, d: x.getImageData(0, 0, img.width, img.height).data };
  }

  // Diff two equal-size images; returns connected changed regions (8-connected on the scale grid).
  window.diffImages = async function (aUrl, bUrl, scale) {
    const A = await pixels(aUrl), B = await pixels(bUrl);
    if (A.w !== B.w || A.h !== B.h) return { error: 'size mismatch', a: [A.w, A.h], b: [B.w, B.h] };
    const gw = Math.ceil(A.w / scale), gh = Math.ceil(A.h / scale);
    const grid = new Uint8Array(gw * gh);
    let changed = 0;
    for (let y = 0; y < A.h; y++) for (let x = 0; x < A.w; x++) {
      const i = (y * A.w + x) * 4;
      if (A.d[i] !== B.d[i] || A.d[i + 1] !== B.d[i + 1] || A.d[i + 2] !== B.d[i + 2] || A.d[i + 3] !== B.d[i + 3]) {
        changed++; grid[Math.floor(y / scale) * gw + Math.floor(x / scale)] = 1;
      }
    }
    const seen = new Uint8Array(gw * gh), boxes = [];
    for (let s = 0; s < gw * gh; s++) {
      if (!grid[s] || seen[s]) continue;
      let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1; const st = [s]; seen[s] = 1;
      while (st.length) {
        const p = st.pop(), px = p % gw, py = (p / gw) | 0;
        x0 = Math.min(x0, px); y0 = Math.min(y0, py); x1 = Math.max(x1, px); y1 = Math.max(y1, py);
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          const nx = px + dx, ny = py + dy;
          if (nx < 0 || ny < 0 || nx >= gw || ny >= gh) continue;
          const q = ny * gw + nx;
          if (grid[q] && !seen[q]) { seen[q] = 1; st.push(q); }
        }
      }
      boxes.push([x0, y0, x1 - x0 + 1, y1 - y0 + 1]);
    }
    return { changed, boxes };
  };

  // Compare a crop of a big image (rect in its pixels) to another image; returns differing pixel count.
  window.compareCrop = async function (bigUrl, rect, smallUrl) {
    const big = await pixels(bigUrl), small = await pixels(smallUrl);
    const [rx, ry, rw, rh] = rect;
    if (small.w !== rw || small.h !== rh) return { error: 'size', small: [small.w, small.h] };
    let diff = 0, maxd = 0;
    for (let y = 0; y < rh; y++) for (let x = 0; x < rw; x++) {
      const i = ((ry + y) * big.w + rx + x) * 4, j = (y * rw + x) * 4;
      let d = 0;
      for (let k = 0; k < 3; k++) d = Math.max(d, Math.abs(big.d[i + k] - small.d[j + k]));
      if (d) diff++; maxd = Math.max(maxd, d);
    }
    // opacity check
    let opaque = true;
    for (let j = 3; j < small.d.length; j += 4) if (small.d[j] !== 255) { opaque = false; break; }
    return { diff, maxd, opaque };
  };
})();
