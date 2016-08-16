
# OCR requires parameter tuning based on its image pattern.

# This project demonstrates how to use image pre-processing and then 
# utilize tesseract package to recognize captcha.

# The accuracy of the proposed method can achieve up to 80%, which is acceptable for many web applications.

# Feel free to give me any feedback. You can mailto: allan920693@yahoo.com.tw

# Yu-Jia Chen  02:01  2016/8/17


import pytesseract 
from PIL import Image, ImageEnhance, ImageFilter
import numpy
from collections import Counter
import floodFill
import cut_min_x_axis
import concat_images


    
    
def AllFiguretoFillInit(img): 
    TempFiguretoFill = set()
    xsize, ysize = img.size
    for i in range(xsize-1):
        for j in range(ysize-1):      
            TempFiguretoFill.add((i,j))
    return TempFiguretoFill


    
     
           
########## Assign Photo to solve and Initial Parameter  ##########

path = 'test.jpg'
target_color = "white"
image = Image.open(path)
xsize, ysize = image.size
scale = max(xsize, ysize)
smallscale = min(xsize, ysize)


answer_num = 5 # expected number of ouput alphabet
pixelCount_threshold_init = int(0.0025*xsize*ysize) # expected area of noise
pixelCount_threshold_varaition_number = 5
pixelCount_threshold_varaition_ratio = 0.2


############### Inital Photo Array  ############

global AllFiguretoFill
AllFiguretoFill = set()

for i in range(xsize-1):
    for j in range(ysize-1):      
        AllFiguretoFill.add((i,j))
#print AllFiguretoFill



############### Plaintext into Recognition  ############

text1 = pytesseract.image_to_string(image,config='-psm 9')  #-psm 7 = Treat the image as a single text line.
print 'Step1 Result:'  
print '\n'
print text1
print '\n'


###############  Function 1: Binary Map ############


step2_img = image
step2_img = step2_img.convert('RGBA')
pix = step2_img.load()
for y in range(step2_img.size[1]):
    for x in range(step2_img.size[0]):
        if pix[x, y][0] < 102 or pix[x, y][1] < 102 or pix[x, y][2] < 102:
            pix[x, y] = (0, 0, 0, 255)
           
        else:
            pix[x, y] = (255, 255, 255, 255)
           
            
step2_img.save('step2_img.jpg')
text2 = pytesseract.image_to_string(Image.open('step2_img.jpg'),config='-psm 9')  #-psm 7 = Treat the image as a single text line.


print 'Step2 Result:'  
print '\n'
print text2
print '\n'



###############  Function 2: bright and contrast filter  ############

step3_img = Image.open('step2_img.jpg')


step3_img = step3_img.filter(ImageFilter.MedianFilter())
enhancer = ImageEnhance.Contrast(step3_img)
step3_img = enhancer.enhance(10)

enhancer = ImageEnhance.Brightness(step3_img)
step3_img = enhancer.enhance(10)

step3_img = step3_img.convert('1')
step3_img.save('step3_img.jpg')
text3 = pytesseract.image_to_string(Image.open('step3_img.jpg'),config='-psm 9')  #-psm 7 = Treat the image as a single text line.


print 'Step 3 Result:'  
print '\n'
print text3
print '\n'




###############  Function 3 : Erase small pixel array by sliding window ############

step4_img = Image.open('step3_img.jpg')
step4_img = step4_img.convert('RGB')
x_w_scale, y_w_scale = step4_img.size
tilted_window_scale =int(max(x_w_scale, y_w_scale)*0.037)


pix = step4_img.load()
window_size_x = int(x_w_scale*0.027)# 2% of the max(width,length)
window_size_y = int(max(x_w_scale, y_w_scale)*0.027)# 2% of the max(width,length)

if target_color == "black":
    rgb_num=255
else:
    rgb_num=0  
    
for x in range(step4_img.size[0]): # cut vertical noise
    window_index = 0
    for window_index in range (step4_img.size[1]-window_size_y+1):
         if pix[x,window_index][0]==rgb_num and pix[x,window_index+window_size_y-1][0]==rgb_num:
            for i in range(window_size_y):
                pix[x,window_index+i] = (rgb_num, rgb_num, rgb_num)
                
for y in range(step4_img.size[1]): # cut horizontal noise
    window_index = 0
    for window_index in range (step4_img.size[0]-window_size_x+1):
         if pix[window_index,y][0]==rgb_num and pix[window_index+window_size_x-1,y][0]==rgb_num:
            for i in range(window_size_x):
                pix[window_index+i,y] = (rgb_num, rgb_num, rgb_num)               
 
for x in range(step4_img.size[0]): # left-to-right tilted line cutting
    window_index = 0
    while (x+tilted_window_scale) < step4_img.size[0] and (window_index+tilted_window_scale) < step4_img.size[1]:
        if pix[x,window_index][0]==rgb_num and pix[x+tilted_window_scale,window_index+tilted_window_scale][0]==rgb_num:
            for i in range (tilted_window_scale):
                pix[x+i,window_index+i] = (rgb_num, rgb_num, rgb_num)
                
        x+=1
        window_index+=1
        
for x in range(step4_img.size[0],0,-1): # left-to -right tilted line cutting
    window_index = y_w_scale
    while (x-tilted_window_scale) > 0 and (window_index-tilted_window_scale) > 0:
        if pix[x-1,window_index-1][0]==rgb_num and pix[x-tilted_window_scale,window_index-tilted_window_scale][0]==rgb_num:
            for i in range (tilted_window_scale):
                pix[x-i-1,window_index-i-1] = (rgb_num, rgb_num, rgb_num)
                
        x=x-1
        window_index=window_index-1       

for y in range(step4_img.size[1]): # Right-to-left tilted line cutting
    window_index = x_w_scale
    while (window_index-tilted_window_scale) > 0 and (y+tilted_window_scale) < step4_img.size[1]:
        if pix[window_index-1,y][0]==rgb_num and pix[window_index-tilted_window_scale,y+tilted_window_scale][0]==rgb_num:
            for i in range (tilted_window_scale):
                pix[window_index-i-1,y+i] = (rgb_num, rgb_num, rgb_num)
                
        y+=1
        window_index=window_index-1
        
for y in range(step4_img.size[1],0,-1): # Right-to-left tilted line cutting
    window_index = 0
    while (window_index+tilted_window_scale) < step4_img.size[0] and (y-tilted_window_scale) > 0:
        if pix[window_index,y-1][0]==rgb_num and pix[window_index+tilted_window_scale,y-tilted_window_scale][0]==rgb_num:
            for i in range (tilted_window_scale):
                pix[window_index+i,y-i-1] = (rgb_num, rgb_num, rgb_num)              
        y=y-1
        window_index=window_index+1        
               
step4_img.save('step4_img.jpg')




############### Cut Small Area & Extract target area & Noise area variation & Recognized by pytesseract  ############

S_pixel =  numpy.arange(1,1+pixelCount_threshold_varaition_ratio*pixelCount_threshold_varaition_number,pixelCount_threshold_varaition_ratio)
pixelCount_threshold_array = numpy.multiply(S_pixel,pixelCount_threshold_init )


text_final_mode5_min_x = []
text_final_mode6_min_x = []
text_final_mode7_min_x = []
text_final_mode8_min_x = []
text_final_mode9_min_x = []
text_final_min_x = []

text_final_mode5_max_x = []
text_final_mode6_max_x = []
text_final_mode7_max_x = []
text_final_mode8_max_x = []
text_final_mode9_max_x = []
text_final_max_x = []
new_text_final= [""for k in range(answer_num)]

target_count_array = []
Possible_target_area_array = []
Possible_target_area_array_combine = []
final_answer = [""for k in range(answer_num)]
Uncut_final_answer = [""for k in range(answer_num)]


target_x = []
min_x_reorderd_cutting_area_scale = []  # for cutting approriate sub figure
max_x_reorderd_cutting_area_scale = []  # for cutting approriate sub figure
min_x_reorderd_cutting_area_array = []
max_x_reorderd_cutting_area_array = []
all_img_dir_min_x = []
all_img_dir_max_x = []
sort_count_array = [ 0 for k in range(answer_num)]

img_min_x = [""for k in range(answer_num)]
img_max_x = [""for k in range(answer_num)]


if target_color == "black":
    target_rgb_num=0
    rgb_num=255
    
else:
    target_rgb_num=255
    rgb_num=0  
        

path = 'step4_img.jpg'
image = Image.open(path)



for pixelCount_threshold in pixelCount_threshold_array: 
    AllFiguretoFill = AllFiguretoFillInit(image)
    while (AllFiguretoFill):
        (x,y) = AllFiguretoFill.pop()
        newimage, Possible_target_area, areaCount, AllFiguretoFill = floodFill.floodFill(x,y,target_rgb_num,target_rgb_num,target_rgb_num,rgb_num,rgb_num,rgb_num,image,pixelCount_threshold,AllFiguretoFill) # Extract black color (0,0,0) and if the area is small: color white (255,255,255) 
        image = newimage.copy()

        Possible_target_area_array_combine.append([areaCount,Possible_target_area])
        if areaCount >= sort_count_array[0]:
            del(sort_count_array[0])
            sort_count_array.append(areaCount)
            sort_count_array = sorted(sort_count_array)             
    Possible_target_area_array_combine = sorted(Possible_target_area_array_combine) 
    seleted_list_target_area_array = Possible_target_area_array_combine[-answer_num:]
    Copy_list_target_area_array = seleted_list_target_area_array[:]
    


    for index in range(answer_num): # Find the min x axis and max x axis of each possible target area        
            tempset = set()
            new_temp_set = set()
            shift_temp_set = set()
            reshift_temp_set = set()
            tempset = Copy_list_target_area_array[index][1].copy()          
            a_min_x = min(tempset)[0]
            a_max_x = max(tempset)[0]
            a_min_y = 0
            a_max_y = 0 
            new_temp_set = tempset.copy()
            while (new_temp_set):
                (x,y) = new_temp_set.pop()
                if y > a_max_y: a_max_y = y
                if y < a_min_y: a_min_y = y   
            shift_temp_set = tempset.copy()        
            while (shift_temp_set): # reshift the area 
                (x,y) = shift_temp_set.pop()
                reshift_temp_set.add((x-a_min_x+1,y-a_min_y+1))                              
            target_x.append([[a_min_x,a_max_x],reshift_temp_set,[a_max_x-a_min_x,a_max_y-a_min_y]])
           
    
    sorted_min_x_list = sorted(range(len(target_x)), key=lambda i: target_x[i][0][0])[-answer_num:] 
    sorted_max_x_list = sorted(range(len(target_x)), key=lambda i: target_x[i][0][1])[-answer_num:]

    for index in sorted_min_x_list: # reorder the possible target area according to its min x axis 
        min_x_reorderd_cutting_area_array.append([target_x[index][0],target_x[index][1],target_x[index][2]])
    for index in sorted_max_x_list: # reorder the possible target area according to its max x axis 
        max_x_reorderd_cutting_area_array.append([target_x[index][0],target_x[index][1],target_x[index][2]])
       

      
    if (Possible_target_area_array_combine[-answer_num][0]  <  2*pixelCount_threshold_init) or (target_x[answer_num-1][2][0]>=int(scale*1.6/answer_num)): 
    # the last one is not target area, one of the top answer_num-1 target area is overlapped (we can only detect one-overlapped char)
    #  or the max area is too wide, we are unable to recognize
       to_seperate_mode = True        
       to_seperate_char_index_min_x = numpy.argmax(sorted_min_x_list)
       to_seperate_char_index_max_x = numpy.argmax(sorted_max_x_list)
       to_del_char_index_min_x = numpy.argmin(sorted_min_x_list)
       to_del_char_index_max_x = numpy.argmin(sorted_max_x_list)
    else:  to_seperate_mode = False  
    if Possible_target_area_array_combine[-answer_num+1][0]  <  2*pixelCount_threshold_init: # the last two are not target area, recommend not to make decision
       make_decision = False  
    else : make_decision = True  
            
    for image_index in range(answer_num): # create image for the cutting area
        
      
        
        temp_min_x_reorderd_cutting_area = min_x_reorderd_cutting_area_array[image_index][1].copy()
        temp_max_x_reorderd_cutting_area = max_x_reorderd_cutting_area_array[image_index][1].copy()
        
        img_x_scale_min_x = min_x_reorderd_cutting_area_array[image_index][2][0]+3
        img_y_scale_min_x = min_x_reorderd_cutting_area_array[image_index][2][1]+3
        img_x_scale_max_x = max_x_reorderd_cutting_area_array[image_index][2][0]+3
        img_y_scale_max_x = max_x_reorderd_cutting_area_array[image_index][2][1]+3
        
        new_cutting_img_min_x = numpy.zeros([img_y_scale_min_x,img_x_scale_min_x,3],dtype=numpy.uint8)
        new_cutting_img_min_x.fill(255) 
        
        new_cutting_img_max_x = numpy.zeros([img_y_scale_max_x,img_x_scale_max_x,3],dtype=numpy.uint8)
        new_cutting_img_max_x.fill(255) 
        
        img_min_x[image_index]  = Image.fromarray(new_cutting_img_min_x, 'RGB')
        img_max_x[image_index]  = Image.fromarray(new_cutting_img_max_x, 'RGB')
       
        
 
        
        while (temp_min_x_reorderd_cutting_area):
            (x,y) = temp_min_x_reorderd_cutting_area.pop()
            img_min_x[image_index].putpixel((x,y), (0,0,0)) 
            
        while (temp_max_x_reorderd_cutting_area):
            (x,y) = temp_max_x_reorderd_cutting_area.pop()
            img_max_x[image_index].putpixel((x,y), (0,0,0)) 
       
        img_min_x[image_index].save("min_x_cut_image_"+str(image_index)+".png")
        img_max_x[image_index].save("max_x_cut_image_"+str(image_index)+".png")
         
        all_img_dir_min_x.append("min_x_cut_image_"+str(image_index)+".png")
        all_img_dir_max_x.append("max_x_cut_image_"+str(image_index)+".png")
       
   
    reshape_min_x_img = concat_images.concat_images(all_img_dir_min_x)
    reshape_min_x_img.save("combine_min_x_cut_image.png")
    reshape_max_x_img = concat_images.concat_images(all_img_dir_max_x)
    reshape_max_x_img.save("combine_max_x_cut_image.png")

    temp_text_final_mode6_min_x = pytesseract.image_to_string(reshape_min_x_img,config='-psm 6 outputbase digits_and_letters')  #-psm 6 = Assume a single uniform block of text.  Use outputbase digits_and_letters
    #temp_text_final_mode6 = temp_text_final_mode6.replace(" ", "") # delete white space
    text_final_mode6_min_x.append(temp_text_final_mode6_min_x)
    text_final_min_x.append(temp_text_final_mode6_min_x)
    
    temp_text_final_mode7_min_x  = pytesseract.image_to_string(reshape_min_x_img,config='-psm 7 outputbase digits_and_letters')  #-psm 7 = Treat the image as a single text line.
    #temp_text_final_mode7 = temp_text_final_mode7.replace(" ", "") # delete white space
    text_final_mode7_min_x .append(temp_text_final_mode7_min_x )
    text_final_min_x .append(temp_text_final_mode7_min_x )
    
    temp_text_final_mode8_min_x  = pytesseract.image_to_string(reshape_min_x_img,config='-psm 8 outputbase digits_and_letters')  #-psm 8 = Treat the image as a single word.
    #temp_text_final_mode8 = temp_text_final_mode8.replace(" ", "") # delete white space
    text_final_mode8_min_x .append(temp_text_final_mode8_min_x )
    text_final_min_x .append(temp_text_final_mode8_min_x )
    

    temp_text_final_mode6_max_x = pytesseract.image_to_string(reshape_max_x_img,config='-psm 6 outputbase digits_and_letters')  #-psm 6 = Assume a single uniform block of text.  Use outputbase digits_and_letters
    #temp_text_final_mode6 = temp_text_final_mode6.replace(" ", "") # delete white space
    text_final_mode6_max_x.append(temp_text_final_mode6_max_x)
    text_final_max_x.append(temp_text_final_mode6_max_x)
    
    temp_text_final_mode7_max_x  = pytesseract.image_to_string(reshape_max_x_img,config='-psm 7 outputbase digits_and_letters')  #-psm 7 = Treat the image as a single text line.
    #temp_text_final_mode7 = temp_text_final_mode7.replace(" ", "") # delete white space
    text_final_mode7_max_x .append(temp_text_final_mode7_max_x )
    text_final_max_x .append(temp_text_final_mode7_max_x )
    
    temp_text_final_mode8_max_x  = pytesseract.image_to_string(reshape_max_x_img,config='-psm 8 outputbase digits_and_letters')  #-psm 8 = Treat the image as a single word.
    #temp_text_final_mode8 = temp_text_final_mode8.replace(" ", "") # delete white space
    text_final_mode8_max_x .append(temp_text_final_mode8_max_x )
    text_final_max_x .append(temp_text_final_mode8_max_x )
    


print 'Final Result 6:'  
print text_final_mode6_min_x
print text_final_mode6_max_x
print '\n'

print 'Final Result 7:'  
print text_final_mode7_min_x
print text_final_mode7_max_x
print '\n'

print 'Final Result 8:'  
print text_final_mode8_min_x
print text_final_mode8_max_x
print '\n'



text_final = text_final_mode6_min_x + text_final_mode6_max_x + text_final_mode7_min_x +text_final_mode7_max_x + text_final_mode8_min_x +text_final_mode8_max_x 



for word_index in range (0,answer_num):
    for answer_element in text_final:
        answer_element = answer_element.replace(" ", "")
        new_text_final[word_index] = answer_element
        if len(answer_element)> word_index:
            final_answer[word_index] = final_answer[word_index]+answer_element[word_index]
            final_answer[word_index] = final_answer[word_index].encode('ascii')
            final_answer[word_index] = final_answer[word_index].replace(" ", "")  #delete white space
    Uncut_final_answer[word_index] = Counter(final_answer[word_index]).most_common(3)

print 'Uncut Final Answer:'  
print final_answer
print '\n'


###### Single overlapped char Splitting   ########

text_final_char_array_min_x = [""for k in range(answer_num+2)]
text_final_char_array_max_x = [""for k in range(answer_num+2)]
image_index_min_x = 0
image_index_max_x = 0
new_text_final_char_array_min_x = [""for k in range(answer_num)]
new_text_final_char_array_max_x = [""for k in range(answer_num)]

for area_index in range (0,answer_num):
    
    temp_char_min_x=""

    temp_char_img_min_x = img_min_x[area_index].copy()

    
    if to_seperate_mode and area_index==to_del_char_index_min_x:  image_index_min_x=image_index_min_x+1  # delete non target char
    elif to_seperate_mode and area_index==to_seperate_char_index_min_x:
        cut_x_pix = cut_min_x_axis.cut_min_x_axis(temp_char_img_min_x,target_color) 
        temp_xsize, temp_ysize = temp_char_img_min_x.size  
        temp_img_left = temp_char_img_min_x.crop((0, 0, cut_x_pix, temp_ysize))
        temp_img_right = temp_char_img_min_x.crop((cut_x_pix , 0, temp_xsize, temp_ysize))
        
            
        char_6_min_x = pytesseract.image_to_string(temp_img_left,config='-psm 6 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_8_min_x = pytesseract.image_to_string(temp_img_left,config='-psm 8 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_9_min_x = pytesseract.image_to_string(temp_img_left,config='-psm 9 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_10_min_x = pytesseract.image_to_string(temp_img_left,config='-psm 10 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        temp_char_min_x = temp_char_min_x + char_6_min_x + char_8_min_x + char_9_min_x + char_10_min_x
        text_final_char_array_min_x[image_index_min_x]= text_final_char_array_min_x[image_index_min_x] + temp_char_min_x    
           
        char_6_min_x = pytesseract.image_to_string(temp_img_right,config='-psm 6 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_8_min_x = pytesseract.image_to_string(temp_img_right,config='-psm 8 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_9_min_x = pytesseract.image_to_string(temp_img_right,config='-psm 9 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_10_min_x = pytesseract.image_to_string(temp_img_right,config='-psm 10 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        temp_char_min_x = temp_char_min_x + char_6_min_x + char_8_min_x + char_9_min_x + char_10_min_x
        text_final_char_array_min_x[image_index_min_x+1]= text_final_char_array_min_x[image_index_min_x+1] + temp_char_min_x  
        
        image_index_min_x=image_index_min_x+2
    else:
        char_6_min_x = pytesseract.image_to_string(temp_char_img_min_x,config='-psm 6 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_8_min_x = pytesseract.image_to_string(temp_char_img_min_x,config='-psm 8 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_9_min_x = pytesseract.image_to_string(temp_char_img_min_x,config='-psm 9 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_10_min_x = pytesseract.image_to_string(temp_char_img_min_x,config='-psm 10 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        temp_char_min_x = temp_char_min_x + char_6_min_x + char_8_min_x + char_9_min_x + char_10_min_x
        text_final_char_array_min_x[image_index_min_x]= text_final_char_array_min_x[image_index_min_x] + temp_char_min_x
        image_index_min_x=image_index_min_x+1

for area_index in range (0,answer_num):

    temp_char_max_x=""
    temp_char_img_max_x = img_max_x[area_index].copy()
   
    if to_seperate_mode and area_index==to_del_char_index_max_x:  image_index_max_x=image_index_max_x+1  # delete non target char    
    elif to_seperate_mode and area_index==to_seperate_char_index_max_x:
        cut_x_pix = cut_min_x_axis(temp_char_img_max_x,target_color) 
        temp_xsize, temp_ysize = temp_char_img_max_x.size  
        temp_img_left = temp_char_img_max_x.crop((0, 0, cut_x_pix, temp_ysize))
        temp_img_right = temp_char_img_max_x.crop((cut_x_pix , 0, temp_xsize, temp_ysize))
       
        char_6_max_x = pytesseract.image_to_string(temp_img_left,config='-psm 6 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_8_max_x = pytesseract.image_to_string(temp_img_left,config='-psm 8 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_9_max_x = pytesseract.image_to_string(temp_img_left,config='-psm 9 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_10_max_x = pytesseract.image_to_string(temp_img_left,config='-psm 10 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        temp_char_max_x = temp_char_max_x + char_6_max_x + char_8_max_x + char_9_max_x + char_10_max_x
        text_final_char_array_max_x[image_index_max_x]= text_final_char_array_max_x[image_index_max_x] + temp_char_max_x    
           
        char_6_max_x = pytesseract.image_to_string(temp_img_right,config='-psm 6 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_8_max_x = pytesseract.image_to_string(temp_img_right,config='-psm 8 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_9_max_x = pytesseract.image_to_string(temp_img_right,config='-psm 9 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_10_max_x = pytesseract.image_to_string(temp_img_right,config='-psm 10 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        temp_char_max_x = temp_char_max_x + char_6_max_x + char_8_max_x + char_9_max_x + char_10_max_x
        text_final_char_array_max_x[image_index_max_x+1]= text_final_char_array_max_x[image_index_max_x+1] + temp_char_max_x  
        
        image_index_max_x=image_index_max_x+2
        
        
    else:
        char_6_max_x = pytesseract.image_to_string(temp_char_img_max_x,config='-psm 6 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_8_max_x = pytesseract.image_to_string(temp_char_img_max_x,config='-psm 8 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_9_max_x = pytesseract.image_to_string(temp_char_img_max_x,config='-psm 9 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_10_max_x = pytesseract.image_to_string(temp_char_img_max_x,config='-psm 10 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        temp_char_max_x = temp_char_max_x + char_6_max_x + char_8_max_x + char_9_max_x + char_10_max_x
        
        char_6_max_x = pytesseract.image_to_string(temp_char_img_max_x,config='-psm 6 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_8_max_x = pytesseract.image_to_string(temp_char_img_max_x,config='-psm 8 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_9_max_x = pytesseract.image_to_string(temp_char_img_max_x,config='-psm 9 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        char_10_max_x = pytesseract.image_to_string(temp_char_img_max_x,config='-psm 10 outputbase digits_and_letters')  #-psm = 8    Treat the image as a single word.        
        temp_char_max_x = temp_char_max_x + char_6_max_x + char_8_max_x + char_9_max_x + char_10_max_x

        text_final_char_array_max_x[image_index_max_x]= text_final_char_array_max_x[image_index_max_x] + temp_char_max_x
        image_index_max_x=image_index_max_x+1

while(text_final_char_array_min_x):
    char=text_final_char_array_min_x.pop()
    if char!="" and char!=" ": new_text_final_char_array_min_x.insert(0,char)
    
while(text_final_char_array_max_x):
    char=text_final_char_array_max_x.pop()
    if char!="" and char!=" ": new_text_final_char_array_max_x.insert(0,char)
            
        
        

##########  OutPut  ##########

if to_seperate_mode == True:  print 'It is hard' 
if make_decision==False: print 'Can I keep silent'
print '\n'
  

print 'Uncut Final Answer:'  
print final_answer
print '\n'


print 'Cut Final Answer:'  
print new_text_final_char_array_min_x
print new_text_final_char_array_max_x
print '\n'


##########  Combine both entire-image and splited-chart Result ##########


combine_array = [""for k in range(answer_num)]
combine_one_answer = [""for k in range(answer_num)]

weight_combine_array = [""for k in range(answer_num)]
weight_combine_one_answer = [""for k in range(answer_num)]

for index in range (0,answer_num):
    combine_array[index] = final_answer[index] + new_text_final_char_array_min_x[index]+ new_text_final_char_array_max_x[index]
    combine_one_answer[index] = Counter(combine_array[index]).most_common(3)
    
        
print 'Combine and Seclet one answer:'  
print combine_one_answer
print '\n'




for index in range (0,answer_num):
    if combine_one_answer[index] ==[]: combine_one_answer.remove(combine_one_answer[index]) 
        
    
    
output = ""
for index in range (0,len(combine_one_answer)):
     output = output + combine_one_answer[index][0][0]


print 'Answer:'  
print output
print '\n'
