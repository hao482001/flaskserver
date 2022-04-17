from fileinput import filename
import cv2
from flask import Flask, flash, request, redirect
from werkzeug.utils import secure_filename
import os
import pytesseract
import json

app = Flask(__name__)

UPLOAD_FOLDER= '\\'

app.secret_key = "secrect_key"
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

ALLOWED_EXTENSIONS =set(['png','jpg','jpeg'])

@app.route('/get-license-plate', methods=['GET'])
def getLicensePlate():
    file = request.files['license-plate']
    if file.filename == '':
        flash('No file upload')
        return 'No file upload'
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        path = UPLOAD_FOLDER + file.filename
        img = cv2.imread(path)
        os.remove(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
        contours,h = cv2.findContours(thresh,1,2)
        largest_rectangle = [0,0]
        for cnt in contours:
            lenght = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, lenght, True)
            if len(approx)==4: 
                area = cv2.contourArea(cnt)
                if area > largest_rectangle[0]:
                    largest_rectangle = [cv2.contourArea(cnt), cnt, approx]
        x,y,w,h = cv2.boundingRect(largest_rectangle[1])
        image=img[y:y+h, x:x+w]
        cv2.drawContours(img,[largest_rectangle[1]],0,(0,255,0),8)
        cv2.drawContours(img,[largest_rectangle[1]],0,(255,255,255),18)
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\ADMIN\\AppData\\Local\\Tesseract-OCR\\tesseract.exe'
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3,3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        invert = 255 - opening
        data = pytesseract.image_to_string(invert, lang='eng', config='--psm 6')
        tam =""
        for char in data:
            if (ord(char)==46):
                if (len(tam)<=8):
                    tam += char
            if (ord(char)==45):
                tam += char
            if (char.isalnum()==True):
                tam += char                     
        data = tam
        return json.dumps({'license-plate':data})
    else:
        return 'no'
if __name__ == "__main__":
    app.run()