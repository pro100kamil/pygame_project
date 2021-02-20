from PIL import Image

im = Image.open('data/Chameleon/Idle3.png')

right_size = 38
kol = 13
cur_size = im.size[0] // kol

res_im = Image.new('RGB', (right_size * kol, right_size))
res_im.putalpha(0)

for i in range(1, kol + 1):
    one = im.crop((i * cur_size - right_size, 0, i * cur_size, right_size))
    res_im.paste(one, ((i - 1) * right_size, 0))

res_im.save('data/Chameleon/Idle.png')