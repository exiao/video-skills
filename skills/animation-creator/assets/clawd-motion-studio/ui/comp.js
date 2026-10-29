// Main Comp canvas (1920x1080). renderFrame(index) draws TL.frames[index].comp deterministically.
// All timing/state comes from build/timeline.json; constants below are drawing geometry only.
(function () {
  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');
  const W = 1920, H = 1080, CX = 960, CY = 540;
  let TL = null;

  // ------------------------------------------------------------ geometry (comp px)
  const G = {
    // flat clawd.png layer; figure bbox (nubs + legs) is centred on the given point
    body: { w: 216, h: 144, r: 16 },            // 12 x 8 proportion
    nub: { w: 12, h: 30, dy: -4 },               // side nubs, vertical offset from body centre
    legs: { w: 20, h: 30, xs: [-86, -46, 46, 86] },
    eye: { w: 12, h: 34, dx: 48, dy: -14 },
    figW: 240, figH: 174, bodyDy: -15,           // body centre = bbox centre + bodyDy
    title: { y: 500, width: 1370, sx: 1.05, skew: 0.21 },   // 1370: widest that keeps the -250 px pose inside
    spark: { x: 960, y: 290, long: 147, short: 128, wscale: 1.6, tip: 6.5 },  // 1.6x per lead revision
    swoosh: { x0: 410, x1: 1510, y: 598, w: 14 },
    subtitle: { y: 680, ls: 0.5 },
    glowColor: '#ff8a3d',
  };

  // ------------------------------------------------------------ seeded random
  function rng(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));

  // ------------------------------------------------------------ clawd
  function rr(c, x, y, w, h, r) {
    c.beginPath();
    c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r);
    c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath();
  }
  // Draw the flat front-view Clawd with its bbox centred at (cx, cy), scale s.
  function drawClawd(c, cx, cy, s, color) {
    const col = color || '#D97757';
    c.save();
    c.translate(cx, cy); c.scale(s, s); c.translate(0, G.bodyDy);
    const { w, h, r } = G.body;
    c.fillStyle = '#C7684A';
    for (const lx of G.legs.xs) { rr(c, lx - G.legs.w / 2, h / 2 - 8, G.legs.w, G.legs.h + 8, 3); c.fill(); }
    c.fillStyle = col;
    for (const sgn of [-1, 1]) {
      const nx = sgn < 0 ? -w / 2 - G.nub.w : w / 2 - 6;
      rr(c, nx, G.nub.dy - G.nub.h / 2, G.nub.w + 6, G.nub.h, 4); c.fill();
    }
    rr(c, -w / 2, -h / 2, w, h, r); c.fill();
    c.fillStyle = '#141414';
    for (const sgn of [-1, 1]) { rr(c, sgn * G.eye.dx - G.eye.w / 2, G.eye.dy - G.eye.h / 2, G.eye.w, G.eye.h, 3); c.fill(); }
    c.restore();
  }

  function drawHandles(c, s) {
    const col = '#a99be0';
    const hw = (G.figW / 2 + 8) * s, hh = (G.figH / 2 + 8) * s;
    c.save();
    c.strokeStyle = col; c.lineWidth = 2;
    c.strokeRect(CX - hw, CY - hh, hw * 2, hh * 2);
    const pts = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]];
    for (const [px, py] of pts) {
      const x = CX + px * hw, y = CY + py * hh;
      c.fillStyle = col; c.fillRect(x - 6, y - 6, 12, 12);
      c.strokeStyle = '#1b1b2b'; c.lineWidth = 1.5; c.strokeRect(x - 6, y - 6, 12, 12);
    }
    // anchor point crosshair
    c.strokeStyle = '#ffffff'; c.lineWidth = 2;
    c.beginPath(); c.arc(CX, CY, 8, 0, Math.PI * 2); c.stroke();
    c.beginPath(); c.moveTo(CX - 16, CY); c.lineTo(CX + 16, CY); c.moveTo(CX, CY - 16); c.lineTo(CX, CY + 16); c.stroke();
    c.restore();
  }

  function drawRipples(c, list) {
    c.save();
    for (const p of list) {
      for (const [lag, a] of [[0, 0.75], [0.18, 0.4]]) {
        const q = clamp(p - lag);
        if (q <= 0) continue;
        c.strokeStyle = `rgba(255,186,150,${a * (1 - q)})`;
        c.lineWidth = 9 * (1 - q) + 1.5;
        c.beginPath(); c.arc(CX, CY, 150 + 300 * q, 0, Math.PI * 2); c.stroke();
      }
    }
    c.restore();
  }

  // ------------------------------------------------------------ cracks (seeded once)
  const CRACKS = (function () {
    const R = rng(20260219);
    const n = 15, cracks = [];
    for (let i = 0; i < n; i++) {
      let a = (i / n) * Math.PI * 2 + (R() - 0.5) * 0.3;
      const len = 300 + R() * 360;
      const pts = [[0, 0]];
      let r = 0;
      while (r < len) {
        r += 34 + R() * 40;
        a += (R() - 0.5) * 0.16;
        pts.push([Math.cos(a) * Math.min(r, len), Math.sin(a) * Math.min(r, len) * 0.92, Math.min(r, len)]);
      }
      cracks.push({ pts, len });
    }
    const links = [];
    for (const ring of [105, 215, 340]) {
      for (let i = 0; i < n; i++) {
        if (R() < 0.35) continue;
        links.push([i, (i + 1) % n, ring * (0.9 + R() * 0.2)]);
      }
    }
    const wedges = [];
    for (let i = 0; i < n; i++) if (R() < 0.5) wedges.push([i, (i + 1) % n, 0.35 + R() * 0.35]);
    return { cracks, links, wedges };
  })();
  function crackPoint(cr, r) {
    const p = cr.pts;
    for (let k = 1; k < p.length; k++) {
      if (p[k][2] >= r) {
        const r0 = p[k - 1][2] || 0, f = (r - r0) / Math.max(1e-6, p[k][2] - r0);
        return [p[k - 1][0] + (p[k][0] - p[k - 1][0]) * f, p[k - 1][1] + (p[k][1] - p[k - 1][1]) * f];
      }
    }
    return [p[p.length - 1][0], p[p.length - 1][1]];
  }
  function drawCracks(c, alpha, grow) {
    if (alpha <= 0 || grow <= 0) return;
    c.save(); c.translate(CX, CY);
    c.lineJoin = 'round'; c.lineCap = 'round';
    // translucent shards between cracks
    for (const [i, j, f] of CRACKS.wedges) {
      const a = crackPoint(CRACKS.cracks[i], CRACKS.cracks[i].len * f * grow);
      const b = crackPoint(CRACKS.cracks[j], CRACKS.cracks[j].len * f * 0.8 * grow);
      c.fillStyle = `rgba(220,235,255,${0.07 * alpha})`;
      c.beginPath(); c.moveTo(0, 0); c.lineTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.closePath(); c.fill();
    }
    for (const pass of [{ w: 8, a: 0.10 }, { w: 2.6, a: 0.9 }]) {
      c.strokeStyle = `rgba(235,242,255,${pass.a * alpha})`;
      for (const cr of CRACKS.cracks) {
        const lim = cr.len * grow;
        c.lineWidth = pass.w;
        c.beginPath(); c.moveTo(0, 0);
        for (let k = 1; k < cr.pts.length; k++) {
          if (cr.pts[k][2] > lim) { const q = crackPoint(cr, lim); c.lineTo(q[0], q[1]); break; }
          c.lineTo(cr.pts[k][0], cr.pts[k][1]);
        }
        c.stroke();
      }
      c.lineWidth = pass.w * 0.7;
      for (const [i, j, r] of CRACKS.links) {
        if (r > Math.min(CRACKS.cracks[i].len, CRACKS.cracks[j].len) * grow) continue;
        const a = crackPoint(CRACKS.cracks[i], r), b = crackPoint(CRACKS.cracks[j], r * 1.04);
        const mx = (a[0] + b[0]) / 2 * 0.97, my = (a[1] + b[1]) / 2 * 0.97;
        c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(mx, my); c.lineTo(b[0], b[1]); c.stroke();
      }
    }
    // impact ring + centre
    c.strokeStyle = `rgba(235,242,255,${0.45 * alpha})`; c.lineWidth = 3;
    c.beginPath(); c.ellipse(0, 0, 240 * grow, 220 * grow, 0, 0, Math.PI * 2); c.stroke();
    c.fillStyle = `rgba(255,255,255,${0.8 * alpha})`;
    c.beginPath(); c.arc(0, 0, 10 * grow, 0, Math.PI * 2); c.fill();
    c.restore();
  }

  // ------------------------------------------------------------ title / spark / swoosh / subtitle
  let titleMetrics = null;
  function titleSetup(c) {
    c.save();
    c.font = '900 100px "Arial Black"';
    const w100 = c.measureText(TL.comp.title).width;
    c.restore();
    const size = 100 * G.title.width / (w100 * G.title.sx);
    titleMetrics = { size, cap: 0.716 * size, font: `900 ${size.toFixed(3)}px "Arial Black"` };
  }
  function drawTitle(c, st, t, glow) {
    const n = st.letters;
    if (n <= 0 && !st.cursor) return;
    const m = titleMetrics, text = TL.comp.title;
    c.save();
    c.translate(CX + st.title_dx, G.title.y + st.title_dy);
    c.transform(G.title.sx, 0, -G.title.skew, 1, 0, 0);
    c.font = m.font; c.textBaseline = 'alphabetic'; c.textAlign = 'left';
    const full = c.measureText(text).width, x0 = -full / 2, base = m.cap / 2;
    const typed = text.slice(0, n);
    c.fillStyle = '#fffaf4';
    if (n > 0) c.fillText(typed, x0, base);
    if (st.cursor) {
      const typing = n < text.length;
      const blink = typing || Math.floor(t * 4) % 2 === 0;
      if (blink) {
        const cx = x0 + (n > 0 ? c.measureText(typed).width : 0) + 10;
        c.fillStyle = '#ffffff';
        c.fillRect(cx, base - m.cap - 12, 7, m.cap + 22);
      }
    }
    c.restore();
  }
  function drawSpark(c, s, rot) {
    if (s <= 0) return;
    const S = G.spark;
    c.save();
    c.translate(S.x, S.y); c.rotate(rot); c.scale(s, s);
    const grad = c.createRadialGradient(0, 0, 4, 0, 0, S.long);
    grad.addColorStop(0, '#ffc08a'); grad.addColorStop(0.45, '#f59152'); grad.addColorStop(1, '#e8743b');
    c.fillStyle = grad;
    const n = TL.comp.spark_rays, bw = TL.comp.spark_ray_width_px * S.wscale / 2;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2, L = i % 2 ? S.short : S.long, tw = S.tip / 2;
      c.save(); c.rotate(a);
      c.beginPath();
      c.moveTo(6, -bw);
      c.bezierCurveTo(L * 0.35, -bw * 1.0, L * 0.7, -bw * 0.55, L - tw, -tw);
      c.arc(L - tw, 0, tw, -Math.PI / 2, Math.PI / 2);
      c.bezierCurveTo(L * 0.7, bw * 0.55, L * 0.35, bw * 1.0, 6, bw);
      c.closePath(); c.fill();
      c.restore();
    }
    c.beginPath(); c.arc(0, 0, 20, 0, Math.PI * 2); c.fill();
    c.restore();
  }
  function swooshPoint(s) {
    const S = G.swoosh;
    const x = S.x0 + (S.x1 - S.x0) * s;
    const y = S.y + 14 * Math.sin(2 * Math.PI * s - 0.5) - 16 * s + 8;
    return [x, y];
  }
  function drawSwoosh(c, p) {
    if (p <= 0) return;
    const N = 160, left = [], right = [];
    for (let k = 0; k <= N; k++) {
      const s = (k / N) * p;
      const [x, y] = swooshPoint(s);
      const [x2, y2] = swooshPoint(s + 0.002);
      const dx = x2 - x, dy = y2 - y, l = Math.hypot(dx, dy) || 1;
      const nx = -dy / l, ny = dx / l;
      // tapered at both ends of the full stroke, and at the pen tip while drawing
      let w = G.swoosh.w / 2 * Math.pow(Math.sin(Math.PI * clamp(s, 0.0001, 0.9999)), 0.55);
      w *= clamp(0.45 + (p - s) / 0.05 * 0.55, 0, 1);
      w = Math.max(w, 0.6);
      left.push([x + nx * w, y + ny * w]); right.push([x - nx * w, y - ny * w]);
    }
    const g = c.createLinearGradient(G.swoosh.x0, 0, G.swoosh.x1, 0);
    g.addColorStop(0, '#f29a5e'); g.addColorStop(1, '#ee7f45');
    c.save(); c.fillStyle = g;
    c.beginPath(); c.moveTo(left[0][0], left[0][1]);
    for (const q of left) c.lineTo(q[0], q[1]);
    for (let k = right.length - 1; k >= 0; k--) c.lineTo(right[k][0], right[k][1]);
    c.closePath(); c.fill();
    c.restore();
  }
  function drawSubtitle(c, s) {
    if (s <= 0) return;
    const px = TL.comp.subtitle_px, ls = px * G.subtitle.ls;
    c.save();
    c.translate(CX, G.subtitle.y); c.scale(s, s);
    c.globalAlpha = clamp(s);
    c.font = `700 ${px}px Arial`; c.letterSpacing = ls + 'px';
    c.textBaseline = 'alphabetic'; c.textAlign = 'left';
    const w = c.measureText(TL.comp.subtitle).width - ls;
    c.fillStyle = '#f2a272';
    c.fillText(TL.comp.subtitle, -w / 2, 0.716 * px / 2);
    c.restore();
  }

  // ------------------------------------------------------------ glow / shimmer / particles
  const fx = document.createElement('canvas'); fx.width = W; fx.height = H;
  const fxc = fx.getContext('2d');
  const mk = (w, h) => { const k = document.createElement('canvas'); k.width = w; k.height = h; return k; };
  const half = mk(W / 2, H / 2), quarter = mk(W / 4, H / 4), blurA = mk(W / 2, H / 2), blurB = mk(W / 4, H / 4), blurC = mk(W / 4, H / 4);
  function silhouette(dst, src) {
    const d = dst.getContext('2d');
    d.save(); d.globalCompositeOperation = 'copy'; d.drawImage(src, 0, 0, dst.width, dst.height);
    d.globalCompositeOperation = 'source-in'; d.fillStyle = G.glowColor; d.fillRect(0, 0, dst.width, dst.height); d.restore();
  }
  function blurInto(dst, src, px) {
    const d = dst.getContext('2d');
    d.save(); d.clearRect(0, 0, dst.width, dst.height); d.filter = `blur(${px}px)`; d.drawImage(src, 0, 0); d.restore();
  }
  function drawBloom(c, glow) {
    silhouette(half, fx); silhouette(quarter, fx);
    blurInto(blurA, half, 3);      // ~6 px
    blurInto(blurB, quarter, 5);   // ~20 px
    blurInto(blurC, quarter, 14);  // ~56 px
    c.save(); c.globalCompositeOperation = 'lighter';
    c.globalAlpha = 0.55 * glow; c.drawImage(blurC, 0, 0, W, H);
    c.globalAlpha = 0.65 * glow; c.drawImage(blurB, 0, 0, W, H);
    c.globalAlpha = 0.50 * glow; c.drawImage(blurA, 0, 0, W, H);
    c.restore();
  }
  const SPARKLES = (function () {
    const R = rng(777), out = [];
    for (let i = 0; i < 30; i++) out.push({ x: 360 + R() * 1200, y: 290 + R() * 460, s: 10 + R() * 18, ph: R() * 6.283, sp: 10 + R() * 10 });
    return out;
  })();
  function star4(c, x, y, s) {
    c.beginPath();
    c.moveTo(x, y - s); c.quadraticCurveTo(x, y, x + s, y); c.quadraticCurveTo(x, y, x, y + s);
    c.quadraticCurveTo(x, y, x - s, y); c.quadraticCurveTo(x, y, x, y - s); c.closePath(); c.fill();
  }
  function drawShimmer(c, amt, t) {
    if (amt <= 0) return;
    c.save(); c.globalCompositeOperation = 'lighter';
    for (const p of SPARKLES) {
      const tw = Math.max(0, Math.sin(p.ph + t * p.sp));
      if (tw <= 0.05) continue;
      c.fillStyle = `rgba(255,236,200,${amt * tw})`;
      star4(c, p.x, p.y, p.s * (0.6 + 0.4 * tw));
    }
    c.restore();
  }
  const PARTS = (function () {
    const R = rng(4242), out = [];
    const cols = ['#ff9a4a', '#ffd27a', '#ff7a35', '#ffb36b'];
    for (let i = 0; i < 120; i++) out.push({ a: R() * Math.PI * 2, v: 500 + R() * 1100, w: 2.5 + R() * 3, c: cols[Math.floor(R() * cols.length)], d: R() * 0.12, r0: 20 + R() * 60 });
    return out;
  })();
  function drawParticles(c, age) {
    if (age < 0) return;
    const k = 2.4, life = 1.8;
    c.save(); c.globalCompositeOperation = 'lighter'; c.lineCap = 'round';
    for (const p of PARTS) {
      const a2 = age - p.d;
      if (a2 <= 0) continue;
      const fade = Math.pow(clamp(1 - a2 / (life - p.d)), 1.3);
      if (fade <= 0) continue;
      const dist = p.r0 + p.v / k * (1 - Math.exp(-k * a2));
      const vel = p.v * Math.exp(-k * a2);
      const len = Math.max(8, vel * 0.055);
      const dx = Math.cos(p.a), dy = Math.sin(p.a);
      const hx = 960 + dx * dist, hy = 520 + dy * dist + 90 * a2 * a2;
      c.strokeStyle = p.c; c.globalAlpha = fade; c.lineWidth = p.w * (0.5 + 0.5 * fade);
      c.beginPath(); c.moveTo(hx - dx * len, hy - dy * len); c.lineTo(hx, hy); c.stroke();
    }
    c.restore();
  }

  // ------------------------------------------------------------ frame
  function drawComp(c, st, t) {
    c.save();
    c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1; c.filter = 'none';
    c.fillStyle = '#000'; c.fillRect(0, 0, W, H);
    if (st.ripples && st.ripples.length) drawRipples(c, st.ripples);
    const s = 1 + 0.12 * st.knock;
    if (st.flat_clawd) drawClawd(c, CX, CY, s);
    if (st.handles) drawHandles(c, s);
    // glowable layers into fx
    fxc.clearRect(0, 0, W, H);
    drawSpark(fxc, st.spark, st.spark_rot);
    drawSwoosh(fxc, st.swoosh);
    drawTitle(fxc, st, t, st.glow);
    drawSubtitle(fxc, st.subtitle);
    if (st.glow > 0) drawBloom(c, st.glow);
    c.drawImage(fx, 0, 0);
    drawShimmer(c, st.shimmer, t);
    drawParticles(c, st.particles);
    drawCracks(c, st.cracks, st.crack_grow);
    if (st.flash > 0) { c.fillStyle = `rgba(255,255,255,${0.85 * st.flash})`; c.fillRect(0, 0, W, H); }
    c.restore();
  }

  window.renderFrame = function (index) {
    const f = TL.frames[index];
    drawComp(ctx, f.comp, f.t);
    return f.frame;
  };
  // Count non-black pixels in a 4 px border of the current frame (inside-frame check).
  window.edgeHits = function () {
    let n = 0;
    for (const [x, y, w, h] of [[0, 0, W, 4], [0, H - 4, W, 4], [0, 0, 4, H], [W - 4, 0, 4, H]]) {
      const d = ctx.getImageData(x, y, w, h).data;
      for (let i = 0; i < d.length; i += 4) if (d[i] > 60 || d[i + 1] > 60 || d[i + 2] > 60) n++;
    }
    return n;
  };
  window.COMP = { drawClawd, G, rr, canvas, ctx };
  window.initComp = async function (tl) {
    TL = tl || window.TL || await (await fetch('../build/timeline.json')).json();
    await document.fonts.load('900 100px "Arial Black"');
    await document.fonts.load('700 78px Arial');
    titleSetup(ctx);
    window.COMP_READY = true;
    return titleMetrics;
  };
  if (window.TL) window.initComp(window.TL);
})();
