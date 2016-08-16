# Input: the directory of a series of images

# Output: a single concatenation image of all the images 

from PIL import Image


def concat_images(image_list):
    images = map(Image.open, image_list)
    widths, heights = zip(*(i.size for i in images))
    
    total_width = sum(widths)
    max_height = max(heights)
    
    new_im = Image.new('RGB', (total_width, max_height))
    pixdata = new_im.load()

    for y in xrange(new_im.size[1]):   # chage backgroud to white color
        for x in xrange(new_im.size[0]):         
                pixdata[x, y] = (255, 255, 255)
  
    x_offset = 0
    for im in images:
      new_im.paste(im, (x_offset,0))
      x_offset += im.size[0]
    return  new_im