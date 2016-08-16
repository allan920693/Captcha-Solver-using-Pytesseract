

# Input: 1. image and 2. the main color for recognition

# Output: the x_axis that contains least pixels with main color


def cut_min_x_axis(image,target_color):
    pix = image.load()
    temp_xsize, temp_ysize = image.size
    min_count_x_axis=0
    for x in range(int(0.25*temp_xsize),int(0.75*temp_xsize)): # find vertical cutting line
        count=0
        for y in range(0,temp_ysize-1):          
          if (pix[x,y] < (50,50,50) and target_color =="black") or (pix[x,y] > (200,200,200) and target_color =="white"):  
               count+=1
        if x==int(0.25*temp_xsize): min_count = count         
        if count < min_count: 
           min_count = count
           min_count_x_axis = x
    return  min_count_x_axis     