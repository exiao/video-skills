"""Contact sheet: python tools_contact.py OUT.png COLS img1 img2 ... (labels from filenames)."""
import os
import sys

from PIL import Image, ImageDraw

out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = [Image.open(f).convert("RGB") for f in files]
w, h = ims[0].size
tw = 640 if w > 640 else w
th = int(h * tw / w)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * th), (0, 0, 0))
dr = ImageDraw.Draw(sheet)
for i, (im, f) in enumerate(zip(ims, files)):
    x, y = (i % cols) * tw, (i // cols) * th
    sheet.paste(im.resize((tw, th)), (x, y))
    dr.rectangle([x, y, x + 150, y + 18], fill=(0, 0, 0))
    dr.text((x + 4, y + 3), os.path.basename(f), fill=(255, 255, 0))
sheet.save(out)
print("wrote", out, sheet.size)
