from PIL import Image

img = Image.open('Volume.png')
size = int(21 * 1.5), int(22 * 1.5)
# img.thumbnail((width, width))
img = img.resize(size)
# height = 64
# ratio = (width / float(img.size[0]))
# height = int((float(img.size[1]) * float(ratio)))
res_im = Image.new('RGB', size, (255, 255, 255))
res_im.paste(img, (0, 0))
res_im.save('Volume1.png', 'png')
