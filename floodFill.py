
# Input: 

# 1. x,y: starting point
# 2. d,e,f: the RGB color value of the main color for recognition (target color)
# 3. g,h,i: the RGB color value of the re-paint color (e.g, in contrast to target color )
# 4. image
# 5. pixelCount_threshold: define the pixel count for a target area
# 6. AllFiguretoFill:  the set of points that have not been checked


# Output: 

# 1. image
# 2. Possible_target_area: the set of points this is likely contains chars
# 3. pixelCount: the pixel count of the Possible_target_area
# 4. AllFiguretoFill




from colormath.color_objects import RGBColor



def floodFill(x,y, d,e,f, g,h,i, image, pixelCount_threshold,AllFiguretoFill):
    pixelCount = 0
    toFill = set()
    AlltoFill = set()
    alreadyfilled = set()
    Possible_target_area = set()
    toFill.add((x,y))
    AlltoFill.add((x,y))
    image = image.convert('RGB')

    xsize, ysize = image.size

    while (toFill):
        pixelCount+=1
        (x,y) = toFill.pop()
        alreadyfilled.add((x,y))
        Possible_target_area.add((x,y))

        (a,b,c) = image.getpixel((x,y))
     
        AllFiguretoFill.discard((x,y))
    
        if not (FindDeltaColor(a,b,c,d,e,f) < 50):
            continue
       
        if x != 0:
            if (x-1,y) not in alreadyfilled and (x-1,y) in AllFiguretoFill:
                toFill.add((x-1,y))
                AlltoFill.add((x-1,y))
        if y != 0:
            if (x,y-1) not in alreadyfilled and (x,y-1) in AllFiguretoFill:
                toFill.add((x,y-1))
                AlltoFill.add((x,y-1))
        if x != (xsize-1):
            if (x+1,y) not in alreadyfilled and (x+1,y) in AllFiguretoFill:
                toFill.add((x+1,y))
                AlltoFill.add((x+1,y))
        if y != (ysize-1):
            if (x,y+1) not in alreadyfilled and (x,y+1) in AllFiguretoFill:
                toFill.add((x,y+1))
                AlltoFill.add((x,y+1))
    if pixelCount < pixelCount_threshold and pixelCount > 1:
        while (AlltoFill):
          (x,y) = AlltoFill.pop()
          image.putpixel((x,y), (g,h,i))  # colord small area with other color
          Possible_target_area = set()
          Possible_target_area.add((x,y))
    return image, Possible_target_area, pixelCount,AllFiguretoFill


def FindDeltaColor(r1,g1,b1,r2,g2,b2):
    rgb1 = RGBColor(r1,g1,b1, rgb_type='sRGB')
    rgb2 = RGBColor(r2,g2,b2, rgb_type='sRGB')
    lab1 = rgb1.convert_to('lab', target_illuminant='D50')
    lab2 = rgb2.convert_to('lab', target_illuminant='D50')
    return lab1.delta_e(lab2, mode='cie1994')