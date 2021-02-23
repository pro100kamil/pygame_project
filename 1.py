from PIL import Image

img = Image.open('Back.png')
size = int(15 * 3), int(16 * 3)
# img.thumbnail(size)
img = img.resize(size)
# height = 64
# ratio = (width / float(img.size[0]))
# height = int((float(img.size[1]) * float(ratio)))
res_im = Image.new('RGB', size, (255, 255, 255))
res_im.paste(img, (0, 0))
res_im.save('Back1.png', 'png')
