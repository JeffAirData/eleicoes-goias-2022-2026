from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out = Path('publicacao/goias_dashboard_capa_premium_1200x630.png')
W, H = 1200, 630
img = Image.new('RGB', (W, H), '#F5F5F2')
img_draw = ImageDraw.Draw(img)

# left accent block
left = Image.new('RGBA', (520, 500), (0, 0, 0, 0))
ld = ImageDraw.Draw(left)
ld.rounded_rectangle((25, 60, 495, 500), radius=30, fill=(33, 23, 82, 255))
ld.ellipse((70, 110, 450, 470), fill=(62, 45, 146, 255))
ld.ellipse((120, 160, 400, 420), fill=(89, 69, 190, 170))
ld.ellipse((175, 215, 345, 385), fill=(145, 117, 255, 120))
for r in [200, 170, 140, 110]:
    ld.arc((250-r, 250-r, 250+r, 250+r), start=115, end=430, fill=(205, 205, 255, 120), width=2)
img.paste(left, (30, 70), left)

# header text
font_h = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 30)
font_s = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 20)
font_m = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 18)
img_draw.text((40, 24), 'Perfil do eleitorado de Goiás', fill='#1F2937', font=font_h)
img_draw.text((40, 62), 'Contexto territorial e demográfico municipal', fill='#4B5563', font=font_s)

# cards
card1 = Image.new('RGB', (220, 120), '#FFFFFF')
cd1 = ImageDraw.Draw(card1)
cd1.rounded_rectangle((0, 0, 220, 120), radius=16, fill='#FFFFFF', outline='#E5E7EB', width=2)
cd1.text((20, 18), 'Gênero', fill='#2F3A4A', font=font_m)
cd1.text((20, 46), '52%', fill='#2C3E50', font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 30))
cd1.rectangle((20, 88, 180, 106), fill='#C9EAD9')
img.paste(card1, (660, 110))

card2 = Image.new('RGB', (220, 120), '#FFFFFF')
cd2 = ImageDraw.Draw(card2)
cd2.rounded_rectangle((0, 0, 220, 120), radius=16, fill='#FFFFFF', outline='#E5E7EB', width=2)
cd2.text((20, 18), 'Jovens 16-29', fill='#2F3A4A', font=font_m)
cd2.text((20, 46), '41%', fill='#2C3E50', font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 30))
cd2.rectangle((20, 88, 160, 106), fill='#BFD6FA')
img.paste(card2, (900, 110))

# chart
chart = Image.new('RGB', (500, 220), '#FFFFFF')
cd = ImageDraw.Draw(chart)
cd.rounded_rectangle((0, 0, 500, 220), radius=18, fill='#FFFFFF', outline='#E5E7EB', width=2)
bars = [355, 310, 265, 220, 180, 140]
for i, b in enumerate(bars):
    x0 = 38 + i*68
    y0 = 170
    x1 = x0 + 50
    y1 = 170 - b
    cd.rounded_rectangle((x0, y1, x1, y0), radius=8, fill='#6657D7' if i % 2 == 0 else '#7EC7B2')
for idx, lab in enumerate(['A', 'B', 'C', 'D', 'E', 'F']):
    cd.text((52 + idx*68, 184), lab, fill='#4A4A4A', font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 14))
img.paste(chart, (620, 290))

# footer
img_draw.text((40, 590), 'Perfil municipal validado • leitura metodológica explícita • dados públicos', fill='#6B7280', font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 14))

img.save(out)
print('saved=', out, 'size=', img.size)
