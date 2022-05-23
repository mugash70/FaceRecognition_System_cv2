import os
import sys
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
import cv2
import numpy as np
import datetime
import csv
import face_recognition
import resource
class input_ui(QDialog):
    def __init__(self): 
        super(input_ui, self).__init__()
        loadUi("./ui/input.ui",self)
        self.cam="0"
        self.logic=0
        self.startVideo(self.cam)
        # self.setStyleSheet('background-image:url(images/back3.jpg)')
        self.capture_btn.clicked.connect(self.saveImage)
    def saveImage(self):
        self.logic=2

    def startVideo(self, camera_name):
        try:
            if len(camera_name) == 1:
                self.capture = cv2.VideoCapture(int(camera_name),cv2.CAP_DSHOW)
            else:
                self.capture = cv2.VideoCapture(camera_name,cv2.CAP_DSHOW)
            self.timer = QTimer(self)  
            images = []
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.timer.timeout.connect(self.update_frame)  
            self.timer.start(10) 
        except Exception as e:
            pass
        
    def update_frame(self):
        ret, self.image = self.capture.read()
        self.displayImage(self.image, 1) 
        self.value=0
        if (self.logic==2):
            try:
                self.textname=self.name_input.text()
            except Exception as e:
                print(e)
            finally:
                if self.textname != '':
                    cv2.imwrite('C:/Users/MUGADA/Desktop/Final year Project/face_GUI/input/%s.JPG'%(self.textname), self.image)
                    self.logic=1
                    QMessageBox.about(self,"Success","Your Details are captured")
                else:
                    QMessageBox.about(self,"Error","Please input Name")
                    self.capture.release()
    def displayImage(self, image, window=1):
        image = cv2.resize(image, (640, 480))
        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.cap_label.setPixmap(QPixmap.fromImage(outImage))
            self.cap_label.setScaledContents(True)

     
class Capture_ui(QDialog):
    def __init__(self):
        super(Capture_ui, self).__init__()
        loadUi("./ui/detect.ui", self)
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.Date_Label.setText(current_time)

        self.image = None
        

    @pyqtSlot()  
    def startVideo(self, camera_name,classs):
        self.class_Name=classs
        if len(camera_name) == 1:
            	self.capture = cv2.VideoCapture(int(camera_name))
        else:
        	self.capture = cv2.VideoCapture(camera_name)
        self.timer = QTimer(self) 
        path = 'ImagesAttendance'
        if not os.path.exists(path):
            os.mkdir(path)
        images = []
        self.class_name = []
        self.encode_name = []
        self.TimeList1 = []
        self.TimeList2 = []
        attendance_list = os.listdir(path)
        for cl in attendance_list:
            cur_img = cv2.imread(f'{path}/{cl}')
            images.append(cur_img)
            self.class_name.append(os.path.splitext(cl)[0])
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(img)
            encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0]
            self.encode_name.append(encodes_cur_frame)
        self.timer.timeout.connect(self.update_frame)  
        self.timer.start(10)
    def face_rec_(self, frame, encode_name_known, class_name):
        # print(self.class_Name)
        def mark_attendance(name):
            with open(f'{self.class_Name}  Attendance.csv', 'a') as f:
                # myDataList = f.readlines()
                # nameList = []
                f.writelines(f'{self.class_Name}')
                # for line in myDataList:
                #     entry = line.split(',')
                #     nameList.append(entry[0])
                if (name != 'unknown student'):
                    # if name not in nameList:
                        date_time_string = datetime.datetime.now().strftime("%y/%m/%d")
                        time_in= datetime.datetime.now().strftime("%H:%M:%S")
                        f.writelines(f'\n{name},{date_time_string},{time_in}')
                        self.NameLabel.setText(name)
                        self.Time1 = datetime.datetime.now()

        faces_cur_frame = face_recognition.face_locations(frame)
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)
        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(encode_name_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_name_known, encodeFace)
            name = "unknown student"
            best_match_index = np.argmin(face_dis)
           
            if match[best_match_index]:
                name = class_name[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            mark_attendance(name)
        return frame

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.displayImage(self.image, self.encode_name, self.class_name, 1)

    def displayImage(self, image, encode_name, class_name, window=1):
        image = cv2.resize(image, (640, 480))
        try:
            image = self.face_rec_(image, encode_name, class_name)
        except Exception as e:
            print(e)
        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)
  
   
class next_1(QDialog):
    def __init__(self):
        super(next_1, self).__init__()
        loadUi("./ui/next.ui", self)
        self.det_btn.clicked.connect(self.get_name)
        
    @pyqtSlot()
    def get_name(self):
        self.classs=self.class_name.text()
        self.refreshAll()
        self.outputWindow_()

    def refreshAll(self):
        self.camera_name = "0"
    
    def outputWindow_(self):
        self.x = Capture_ui()
        self.x.show()
        self.hide()
        self.x.startVideo(self.camera_name,self.classs)
    
 
    # def detect(self):   
    #     self.refreshAll()
    #     self.outputWindow_()
        
class welcome(QDialog):
    def __init__(self):
        super(welcome, self).__init__()
        loadUi("./ui/welcome.ui", self)
        self._new_window = None
        self.camera_name = None
        self.cap.clicked.connect(self.open_cap)
        self.cap2.clicked.connect(self.output)
    
    def output(self):
        self.y = next_1()
        self.y.show()
        self.hide()

    def open_cap(self):
        self.ui = input_ui()
        self.ui.show()
        self.hide()
    

        


app = QApplication(sys.argv)
ux = welcome()
ux.show()
sys.exit(app.exec_())
