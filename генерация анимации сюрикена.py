from PIL import Image

im = Image.open('data/shuriken.png')
size = 25
kol = 13
im.thumbnail((size, size))
res_im = Image.new('RGB', (size * kol, size), (255, 255, 255))
for i, angle in enumerate(range(0, 361, 30)):
    res_im.paste(im.rotate(angle), (i * size, 0))
res_im.save('data/move_shuriken.png', 'png')
