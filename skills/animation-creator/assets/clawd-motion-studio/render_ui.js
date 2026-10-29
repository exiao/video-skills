#!/usr/bin/env node
// Regenerates every 2D texture from build/timeline.json.
//   node render_ui.js                      # everything
//   node render_ui.js --only ui,tc         # subset: ui | tc | comp | assets  (report is always rewritten)
//   node render_ui.js --no-json            # skip re-running timeline.py --json
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const puppeteer = require('puppeteer');

const ROOT = __dirname;
const P = (...a) => path.join(ROOT, ...a);
const CHROME = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const argv = process.argv.slice(2);
const onlyIdx = argv.indexOf('--only');
const ONLY = onlyIdx >= 0 ? argv[onlyIdx + 1].split(',') : ['ui', 'tc', 'comp', 'assets'];
const want = (k) => ONLY.includes(k);
const STATS_PATH = P('textures', 'render_stats.json');
const stats = fs.existsSync(STATS_PATH) ? JSON.parse(fs.readFileSync(STATS_PATH, 'utf8')) : {};
const pad4 = (n) => String(n).padStart(4, '0');
const dataUrl = (file) => 'data:image/png;base64,' + fs.readFileSync(file).toString('base64');
const writeDataUrl = (file, url) => fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
const now = () => Date.now();

async function main() {
  const T0 = now();
  fs.mkdirSync(P('build'), { recursive: true });
  if (!argv.includes('--no-json')) {
    execFileSync(P('.venv', 'bin', 'python'), [P('timeline.py'), '--json', P('build', 'timeline.json')], { stdio: 'inherit' });
  }
  const TLtext = fs.readFileSync(P('build', 'timeline.json'), 'utf8');
  const TL = JSON.parse(TLtext);
  const L = TL.layout, S = L.ui.scale;
  for (const d of ['textures', 'textures/comp', 'textures/tc_comp', 'textures/tc_tl']) fs.mkdirSync(P(d), { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: true,
    args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text', '--hide-scrollbars'],
  });
  const inject = async (page) => page.evaluateOnNewDocument(`window.TL = ${TLtext};`);

  // ---------------------------------------------------------------- comp/tools page (also used for diffs)
  const cp = await browser.newPage();
  await cp.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await inject(cp);
  await cp.goto('file://' + P('ui', 'comp.html'));
  await cp.waitForFunction('window.COMP_READY === true');
  stats.title_metrics = await cp.evaluate(() => window.initComp(window.TL));
  stats.comp_geom = await cp.evaluate(() => window.COMP.G);

  // ---------------------------------------------------------------- UI page
  let up = null;
  if (want('ui') || want('tc')) {
    up = await browser.newPage();
    await up.setViewport({ width: L.ui.w, height: L.ui.h, deviceScaleFactor: S });
    await inject(up);
    await up.goto('file://' + P('ui', 'ui.html'));
    await up.waitForFunction('window.UI_READY === true');
  }
  const shot = async (file, clip) => {
    const opt = { type: 'png', captureBeyondViewport: false };
    if (clip) opt.clip = { x: clip[0], y: clip[1], width: clip[2], height: clip[3] };
    fs.writeFileSync(file, Buffer.from(await up.screenshot(opt)));
  };

  if (want('ui')) {
    const t = now();
    await up.evaluate(() => { setUIState('base'); setTimecode('', ''); });
    await shot(P('textures', 'ui_base.png'));
    await up.evaluate(() => setUIState('active'));
    await shot(P('textures', 'ui_active.png'));
    const m = await up.evaluate(() => measureUI());
    await up.evaluate(() => setUIState('base'));
    // expected rects from timeline.json
    const exp = { caps: {}, preview: {} };
    for (const n of L.tool_order) { const [cx, cy] = L.tools[n]; exp.caps[n] = [cx - L.cap.w / 2, cy - L.cap.h / 2, L.cap.w, L.cap.h]; }
    for (const [n, [cx, cy]] of Object.entries(L.preview_buttons)) exp.preview[n] = [cx - L.preview_cap.w / 2, cy - L.preview_cap.h / 2, L.preview_cap.w, L.preview_cap.h];
    exp.glow_row = L.glow_row; exp.comp_view = L.comp_view; exp.tc_comp = L.tc_comp; exp.tc_tl = L.tc_tl;
    let maxDev = 0;
    const dev = (a, b) => { const d = Math.max(...a.map((v, i) => Math.abs(v - b[i]))); maxDev = Math.max(maxDev, d); return d; };
    const rects = [];
    for (const n of L.tool_order) rects.push(['cap ' + n, m.caps[n], exp.caps[n], dev(m.caps[n], exp.caps[n])]);
    for (const n of Object.keys(exp.preview)) rects.push(['preview ' + n, m.preview[n], exp.preview[n], dev(m.preview[n], exp.preview[n])]);
    for (const k of ['glow_row', 'comp_view', 'tc_comp', 'tc_tl']) rects.push([k, m[k], exp[k], dev(m[k], exp[k])]);
    stats.rects = rects; stats.rect_max_dev = maxDev;
    const allowed = [
      ['cap Selection', exp.caps.Selection], ['cap Type', exp.caps.Type], ['cap Rectangle', exp.caps.Rectangle],
      ['cap Pen', exp.caps.Pen], ['preview Play', exp.preview.Play], ['glow_row', exp.glow_row],
    ];
    // raw diff of the two screenshots (informational), then composite targets onto ui_base
    const raw = await cp.evaluate((a, b, s) => diffImages(a, b, s), dataUrl(P('textures', 'ui_base.png')), dataUrl(P('textures', 'ui_active.png')), S);
    stats.ui_diff_raw = raw;
    writeDataUrl(P('textures', 'ui_active.png'), await cp.evaluate((a, b, r) => compositeRegions(a, b, r),
      dataUrl(P('textures', 'ui_base.png')), dataUrl(P('textures', 'ui_active.png')), allowed.map(([, r]) => r.map((v) => v * S))));
    const d = await cp.evaluate((a, b, s) => diffImages(a, b, s), dataUrl(P('textures', 'ui_base.png')), dataUrl(P('textures', 'ui_active.png')), S);
    const inside = (b, r) => b[0] >= r[0] && b[1] >= r[1] && b[0] + b[2] <= r[0] + r[2] && b[1] + b[3] <= r[1] + r[3];
    stats.ui_diff = {
      changed_pixels: d.changed,
      boxes: d.boxes.map((b) => { const hit = allowed.find(([, r]) => inside(b, r)); return { ui: b, px: b.map((v) => v * S), region: hit ? hit[0] : 'UNEXPECTED' }; }),
    };
    // preview
    writeDataUrl(P('build', 'ui_preview.png'), await cp.evaluate((u) => downscale(u, 1920, 1080), dataUrl(P('textures', 'ui_base.png'))));
    stats.time_ui_s = (now() - t) / 1000;
    console.log('ui done', stats.time_ui_s, 's; max rect dev', maxDev, '; diff boxes', JSON.stringify(stats.ui_diff.boxes));
  }

  if (want('tc')) {
    const t = now();
    await up.evaluate(() => { setUIState('base'); setTimecode('', ''); });
    // background check: empty timecode crop must equal ui_base pixels
    const tmp = P('textures', '_tc_empty_check.png');
    const checks = {};
    for (const k of ['tc_comp', 'tc_tl']) {
      await shot(tmp, L[k]);
      checks[k] = await cp.evaluate((a, r, b) => compareCrop(a, r, b), dataUrl(P('textures', 'ui_base.png')), L[k].map((v) => v * S), dataUrl(tmp));
    }
    fs.unlinkSync(tmp);
    stats.tc_bg_check = checks;
    for (const f of TL.frames) {
      const tc = f.ui.timecode;
      await up.evaluate((s) => setTimecode(s, s), tc);
      await shot(P('textures', 'tc_comp', pad4(f.frame) + '.png'), L.tc_comp);
      await shot(P('textures', 'tc_tl', pad4(f.frame) + '.png'), L.tc_tl);
    }
    await up.evaluate(() => setTimecode('', ''));
    stats.time_tc_s = (now() - t) / 1000;
    console.log('tc done', stats.time_tc_s, 's', JSON.stringify(checks));
  }

  if (want('comp')) {
    const t = now();
    const edge = [];
    for (let i = 0; i < TL.frames.length; i++) {
      const [url, hits] = await cp.evaluate((k) => { renderFrame(k); return [COMP.canvas.toDataURL('image/png'), edgeHits()]; }, i);
      const cs = TL.frames[i].comp;
      if (hits && cs.particles < 0 && cs.flash <= 0.001) edge.push([TL.frames[i].frame, hits]);
      writeDataUrl(P('textures', 'comp', pad4(TL.frames[i].frame) + '.png'), url);
    }
    stats.time_comp_s = (now() - t) / 1000;
    stats.comp_edge_hits = edge;
    const items = [];
    for (let k = 0; k < 24; k++) {
      const tt = k * 0.5, fr = Math.round(tt * TL.fps) + 1;
      items.push({ url: dataUrl(P('textures', 'comp', pad4(fr) + '.png')), label: `t ${tt.toFixed(1)} s  f${fr}` });
    }
    writeDataUrl(P('build', 'comp_contact.png'), await cp.evaluate((it) => contactSheet(it, 6, 320, 180), items));
    console.log('comp done', stats.time_comp_s, 's');
  }

  if (want('assets')) {
    const card = await cp.evaluate(() => renderCard());
    writeDataUrl(P('textures', 'clawd_card.png'), card.url);
    delete card.url;
    stats.clawd_card = card;
    writeDataUrl(P('textures', 'glow_chip.png'), await cp.evaluate(() => renderChip()));
    console.log('assets done', JSON.stringify(card));
  }

  await browser.close();
  stats.notes = [
    '- Title width: lead asked for ~1440 px; fitted to 1370 px (Arial Black 114.9 px, x-stretch 1.05) because at 1440 px the KEY_POSES[0] (-250, +60) pose puts the glyphs ~19 px off the left edge. At 1370 px solid glyphs start at x = 25 at that pose; only the faint bloom tail (max ~30/255) reaches the edge.',
    '- Spark: 1.6x per lead (rays 147/128 px, tip to tip ~294 px). Ray base width scaled with it: 16 x 1.6 = 25.6 px (timeline SPARK_RAY_WIDTH_PX = 16 is the unscaled value). Centre moved up to (960, 290) so the bigger spark clears the bigger title (cap centre y 500).',
    '- Swoosh x 410..1510 (1100 px, ~80% of the title width), 14 px, around y 598. Subtitle centre y 680 (not 700) to sit under the swoosh like the reference, 0.5 em tracking per lead.',
    '- At the second keyframe pose (0, -120) the title overlaps the spark: correct AE logic (only layer 1 has Position keys), left as is.',
    '- ui_active.png = ui_base.png with the six target rects pasted from the active render (Chrome raster wobble otherwise shifted 1 device-px column inside the First cap). ui_active is saved RGBA (alpha all 255); ui_base is RGB.',
    '- Comp frames are RGBA PNGs with alpha 255 everywhere (opaque black BG).',
    '- No timeline.py changes required. Optional: if Blender wants the title width/spark geometry as data, add TITLE_WIDTH_PX = 1370, SPARK_RAY_LEN_PX = (147, 128), SPARK_CENTER = (960, 290), SWOOSH = (410, 1510, 598, 14), SUBTITLE_Y = 680 to timeline.py and have comp.js read them.',
  ];
  stats.last_run = { only: ONLY, total_s: (now() - T0) / 1000, date: new Date().toISOString() };
  fs.writeFileSync(STATS_PATH, JSON.stringify(stats, null, 1));
  writeReport(stats, TL);
  console.log('total', stats.last_run.total_s, 's');
}

function writeReport(st, TL) {
  const f = (a) => (a ? '[' + a.map((v) => +(+v).toFixed(2)).join(', ') + ']' : '-');
  const L = TL.layout;
  const lines = [];
  lines.push('# Texture report (2D layer)', '');
  lines.push('Generated by `render_ui.js` from `build/timeline.json`. Last run: ' + (st.last_run ? `${st.last_run.date}, --only ${st.last_run.only.join(',')}, ${st.last_run.total_s.toFixed(1)} s total` : '-'), '');
  lines.push('## Regenerate', '', '```sh', 'cd ' + ROOT,
    '.venv/bin/python timeline.py --json build/timeline.json   # render_ui.js also runs this unless --no-json',
    'node render_ui.js                 # ui + tc + comp + assets + contact sheets + this report',
    'node render_ui.js --only ui       # or tc | comp | assets (comma list)', '```', '');
  lines.push('## Render times', '',
    `- UI (base + active + measure + diff + preview): ${st.time_ui_s ?? '-'} s`,
    `- Timecodes (2 x 360 clipped screenshots): ${st.time_tc_s ?? '-'} s`,
    `- Comp frames (360 x 1920x1080 canvas exports): ${st.time_comp_s ?? '-'} s`, '');
  lines.push('## Outputs', '',
    '| file | size | notes |', '|---|---|---|',
    '| textures/ui_base.png | 3840x2160 | whole workspace, Selection active, comp_view pure #000, timecode rects blank |',
    '| textures/ui_active.png | 3840x2160 | Type/Rectangle/Pen caps + Play cap blue, Selection normal, fx Glow row selected |',
    '| textures/comp/0001..0360.png | 1920x1080 | frame N = timeline frames[N-1] (t = (N-1)/30) |',
    `| textures/tc_comp/0001..0360.png | ${L.tc_comp[2] * 3}x${L.tc_comp[3] * 3} | opaque, layout.tc_comp at 3x |`,
    `| textures/tc_tl/0001..0360.png | ${L.tc_tl[2] * 3}x${L.tc_tl[3] * 3} | opaque, layout.tc_tl at 3x |`,
    `| textures/clawd_card.png | ${st.clawd_card ? st.clawd_card.w + 'x' + st.clawd_card.h : '-'} | RGBA flat clawd, same drawClawd() as comp layer |`,
    '| textures/glow_chip.png | 512x192 | chip face |',
    '| build/comp_contact.png | 1920x816 | comp at t = 0, 0.5 .. 11.5 s |',
    '| build/ui_preview.png | 1920x1080 | ui_base downscaled |', '');
  lines.push('## DOM-measured rects vs timeline.json (UI px, [x, y, w, h])', '');
  lines.push(`Max deviation: **${st.rect_max_dev ?? '-'} UI px** (limit 0.5).`, '');
  lines.push('| element | measured | timeline.json | max dev |', '|---|---|---|---|');
  for (const [n, m, e, d] of st.rects || []) lines.push(`| ${n} | ${f(m)} | ${f(e)} | ${d} |`);
  lines.push('', 'Texture pixel rect = UI rect x 3 (e.g. comp_view = ' + f(L.comp_view.map((v) => v * 3)) + ' px in ui_*.png).', '');
  lines.push('## ui_base vs ui_active pixel diff', '');
  if (st.ui_diff) {
    lines.push(`Changed pixels: ${st.ui_diff.changed_pixels}. Connected changed regions (UI px; texture px = x3):`, '');
    lines.push('| region | UI box | texture px box |', '|---|---|---|');
    for (const b of st.ui_diff.boxes) lines.push(`| ${b.region} | ${f(b.ui)} | ${f(b.px)} |`);
    const bad = st.ui_diff.boxes.filter((b) => b.region === 'UNEXPECTED').length;
    if (st.ui_diff_raw) lines.push('', `Raw screenshot diff before compositing had ${st.ui_diff_raw.boxes.length} region(s) (Chrome raster wobble of ~1 device px column can appear in untouched icons); ui_active.png is therefore ui_base.png with only the six target rects pasted from the active render.`);
    lines.push('', bad ? `**${bad} region(s) outside the target rects!**` : 'Every changed pixel lies inside a target rect (Selection/Type/Rectangle/Pen caps, Play cap, glow_row); all other pixels are identical.');
  }
  lines.push('', '## Timecode textures', '');
  if (st.tc_bg_check) {
    for (const [k, v] of Object.entries(st.tc_bg_check)) lines.push(`- ${k}: empty-text render vs ui_base crop: ${v.diff} differing px (max channel delta ${v.maxd}), opaque: ${v.opaque}`);
    lines.push('- Text: blue #2d8ceb; tc_tl bold 18 CSS px (54 px in texture), tc_comp 9.5 CSS px; left aligned; string = frames[i].ui.timecode.');
  }
  lines.push('', '## clawd_card.png', '');
  if (st.clawd_card) {
    const c = st.clawd_card;
    lines.push(`- ${c.w}x${c.h} px, scale ${c.scale.toFixed(4)} card px per comp px (12 comp px transparent padding).`,
      `- Card covers comp rect ${f(c.comp_rect)} (x, y, w, h in 1920x1080 comp px), i.e. centred on (960, 540).`,
      `- Figure (nubs+legs bbox) in comp px ${f(c.figure_comp_rect)}; in card px ${f(c.figure_px_rect)}.`,
      `- Body rounded-rect in card px ${f(c.body_px_rect)}; body colour #D97757, legs #C7684A, eyes #141414.`,
      '- In UI px the card is ' + (c.comp_rect[2] * 0.25) + ' x ' + (c.comp_rect[3] * 0.25) + ' (comp px x 0.25), centred on layout comp centre (585, 233).');
  }
  lines.push('', '## Colours for Blender', '',
    '- Workspace bg #1b1b1b, panel #232323, header #2a2a2a, separators #111, text #b5b5b5, accent #2d8ceb.',
    '- Toolbar/preview keycap face (inactive) #2e2e2e with 1 px #3b3b3b border, radius 3 CSS px; active face #2d8ceb, white icon.',
    '- Toolbar row background #232323 (menubar strip #1f1f1f). Preview panel background #232323.',
    '- Glow row selected bar #2d8ceb (layout.glow_row), text white.',
    '- comp_view is pure #000 in both UI textures.', '');
  const g = st.comp_geom || {};
  if (st.title_metrics && g.title) lines.push('## Comp notes', '', `- Title: Arial Black ${st.title_metrics.size.toFixed(1)} px (cap ${st.title_metrics.cap.toFixed(1)} px), x-stretch ${g.title.sx}, skew ${g.title.skew} (~12 deg), fitted to ${g.title.width} comp px wide, cap centre (960 + title_dx, ${g.title.y} + title_dy); fill #fffaf4; typed in place, layout fixed as if full.`,
    `- Spark centre (${g.spark.x}, ${g.spark.y}), ${TL.comp.spark_rays} petal rays alternating ${g.spark.long}/${g.spark.short} px, base width ${TL.comp.spark_ray_width_px} x ${g.spark.wscale} = ${TL.comp.spark_ray_width_px * g.spark.wscale} px, ${g.spark.tip} px rounded tips; scaled by spark, rotated by spark_rot.`,
    `- Swoosh x ${g.swoosh.x0}..${g.swoosh.x1} around y ${g.swoosh.y}, ${g.swoosh.w} px, tapered both ends and at the pen tip. Subtitle ${TL.comp.subtitle} Arial Bold ${TL.comp.subtitle_px} px, ${g.subtitle.ls} em tracking, #f2a272, centre y ${g.subtitle.y}.`,
    '- Flat clawd: body 216x144 r16 #D97757, nubs 12x30, legs 4 x 20x30 #C7684A, eye slits 12x34 #141414; bbox 240x174 centred (960, 540); handles/bbox in layer colour #a99be0, anchor crosshair white.',
    `- Inside-frame check: frames whose 4 px border has any pixel > 60/255 (solid content; the faint glow halo, max ~30/255, may reach the left edge at the -250 px pose) (excluding Play particles/flash frames): ${st.comp_edge_hits ? (st.comp_edge_hits.length ? JSON.stringify(st.comp_edge_hits) : 'none') : '-'}.`,
    '- Glow: orange #ff8a3d silhouette bloom (~6/20/56 px blur, additive) over title, spark, swoosh, subtitle when glow > 0.', '');
  lines.push('## Deviations / requests', '', ...(st.notes || ['- none']), '');
  fs.writeFileSync(path.join(ROOT, 'build', 'texture_report.md'), lines.join('\n'));
}

main().catch((e) => { console.error(e); process.exit(1); });
