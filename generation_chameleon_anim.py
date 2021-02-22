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


# генерация анимации зелья
new = Image.new('RGB', (4 * 28, 32), (255, 255, 255))
new.putalpha(0)
kol = [1, 2, 3, 2]
size = 28
for k, i in enumerate(kol):
    im = Image.open('C:/Users/Эмиль/Desktop/Potions/p' + str(i) + '.png')
    im: Image.Image
    w, h = im.size
    print((w, h), (k * size + ((size - w) // 2), (32 - h) // 2))
    new.paste(im, (k * size + ((size - w) // 2), (32 - h) // 2))




new.save('../../Desktop/Potions/result.png')