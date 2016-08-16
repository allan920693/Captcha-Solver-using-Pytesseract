# Captcha-Solver-using-Pytesseract

This project shows how to use pytesseract package (OCR, Optical Character Recognition) to solve Captcha. 

OCR requires parameter tuning based on its image pattern.

We demonstrate how to use image pre-processing and then utilize tesseract package to recognize captcha.

The accuracy of proposed method can achieve up to 80%, which is acceptable for many web applications.

Feel free to give me any feedback. You can mailto: allan920693@yahoo.com.tw

                                            Yu-Jia Chen   Taiwan, 08/17/2016, 2:17 AM


# Step by Step

1.	Install tesseract 
    pip install pytesseract

2.	Install ImageMagick
    install colormath==1.0.8  

3. excute Main()


# How to Force tessdata to recognize digit only:

1. Creat or Open existing Config File in:

   tessdata/configs/digits:

2. Edit or Apply 

   tessedit_char_whitelist 0123456789  

3. Call Method

  pytesseract.image_to_string(image,config='-psm 9 outputbase digits')  


