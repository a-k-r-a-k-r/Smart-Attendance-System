import tkinter as tk
from cv2 import cv2
import time
import datetime as dt
from PIL import Image,ImageTk
import argparse
import numpy
import os
import pandas as pd

class App:    
    def __init__(self,window,video_source=0):
        self.window=window
        self.window.title("Smart Attendance System")
        self.window.config(bg="black")
        self.video_source=video_source
        self.ok=False
        
        self.vid=VideoCapture(self.video_source)
        self.canvas=tk.Canvas(window,width=self.vid.width,height=self.vid.height)
        self.canvas.grid(row=0,column=0,padx=20,pady=(20,0))
        self.timer=ElapsedTimeClock(self.window)

        self.button_frame=tk.Frame(self.window,bg="gray",width=self.vid.width)
        self.button_frame.grid(row=2,column=0,padx=10,pady=10)
        self.btn_snapshot=tk.Button(self.button_frame,text="Add Student",command=self.add_student)
        self.btn_snapshot.grid(row=0,column=0,ipadx=10)
        self.btn_snapshot=tk.Button(self.button_frame,text="Train Model",command=self.train_model)
        self.btn_snapshot.grid(row=0,column=1,ipadx=10)
        self.btn_snapshot=tk.Button(self.button_frame,text="Start Class",command=self.start_class)
        self.btn_snapshot.grid(row=0,column=2,ipadx=10)
        self.btn_snapshot=tk.Button(self.button_frame,text="Get Attendance",command=self.get_attendance)
        self.btn_snapshot.grid(row=0,column=3,ipadx=10)
        self.btn_snapshot=tk.Button(self.button_frame,text="Snapshot",command=self.snapshot)
        self.btn_snapshot.grid(row=0,column=4,ipadx=10)    
        self.btn_snapshot=tk.Button(self.button_frame,text="Start Recording",command=self.start_recording)
        self.btn_snapshot.grid(row=0,column=5,ipadx=10)
        self.btn_snapshot=tk.Button(self.button_frame,text="Stop Recording",command=self.stop_recording)
        self.btn_snapshot.grid(row=0,column=6,ipadx=10)
        self.btn_snapshot=tk.Button(self.button_frame,text="Quit",command=quit)
        self.btn_snapshot.grid(row=0,column=7,ipadx=10)
        self.window.iconbitmap("resources/icons/ai.ico")
        

        self.get_time()
        self.window.mainloop()


    def snapshot(self):
        ret,frame=self.vid.get_frame()
        if ret:
            path="snapshots/{}".format(str(dt.datetime.now().date()))
            if (not os.path.isdir(path)):
                os.mkdir(path)
            path="snapshots/{}/{}".format(str(dt.datetime.now().date()),subject_now)
            if (not os.path.isdir(path)):
                os.mkdir(path)
            cv2.imwrite(path+"/image"+time.strftime("%d-%m-%Y-%H-%M-%S")+".jpg",cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

    def start_recording(self):
        self.ok=True
        self.timer.start()


    def stop_recording(self):
        self.ok=False
        self.timer.stop()

    def update(self):
        self.delay=10
        ret,frame=self.vid.get_frame()
        if self.ok:
            self.vid.out.write(cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

        if ret:
            self.photo=ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0,0,image=self.photo,anchor=tk.NW)
            
        self.window.after(self.delay,self.update)

    def get_attendance(self):
        present_students=[]
        path="attendance/{}".format(str(dt.datetime.now().date()))
        if (not os.path.isdir(path)):
            os.mkdir(path)
        path="attendance/{}/{}".format(str(dt.datetime.now().date()),subject_now)
        if (not os.path.isdir(path)):
            os.mkdir(path)


        attendance_sheet=open(path+"/attendance_"+time.strftime("%d-%m-%Y-%H-%M-%S")+".txt","a")
        attendance_sheet.write("\nAttendance for "+ subject_now + "\n")
        attendance_sheet.write("Timestamp: " + str(dt.datetime.now()) + "\n-------------------------------------\n")
        for k,v in marking.items():
            if v>=100:
                present_students.append(k)
                attendance_sheet.write(k+"\n")
        attendance_sheet.close()
        attendance_display=tk.Toplevel()
        attendance_display.geometry("300x583+"+ str(self.window.winfo_x()+768) + "+" + str(self.window.winfo_y()))
        try:
            attendance_display.title("Attendance for "+ subject_now)
        except:
            attendance_display.title("Attendance Sheet")

        label=""
        for student in present_students:
            label=label+"\n"+student
        attendance_label=tk.Label(attendance_display,text=label)
        attendance_label.pack()
        




    def start_class(self):
        self.train_model()
        self.get_subject()
        self.update()

    def get_time(self):
        time_now=int(dt.datetime.now().strftime("%H"))
        if ((time_now <= 17) and (time_now >= 9)):
            if(time_now>=12):
                time_now=time_now%12
            self.get_subject()
        else:
            pass

            
    def get_subject(self):     
        global subject_now
        now=dt.datetime.today().weekday()  #0 for monday, 6 for sunday
        df = pd.read_excel("timetable/timetable.xlsx",engine='openpyxl')
        hour_now=int(dt.datetime.now().strftime("%H"))
        if (int(hour_now)>12):
            hour_now=hour_now%12
            session="{} to {}".format(int(hour_now),int(hour_now)+1)
        if (int(hour_now)==12):
            session="{} to 1".format(int(hour_now))
        today_timetable=df.iloc[now]
        subject_now=today_timetable[session]
        if (subject_now=='NIL'):
            subject_now="Free-time"
        self.check_subject=360000
            
        self.window.after(self.check_subject,self.get_subject)

    
    def add_student(self):
        self.student_data_window=tk.Toplevel()
        self.student_data_window.title("Add Student")
        self.student_data_window.geometry("300x200+"+ str(self.window.winfo_x()+768) + "+" + str(self.window.winfo_y()))
        self.name_label=tk.Label(self.student_data_window,text="Name")
        self.student_name=tk.Entry(self.student_data_window)
        self.enroll_label=tk.Label(self.student_data_window,text="Enroll no")
        self.student_enroll=tk.Entry(self.student_data_window)
        self.capture_pic=tk.Button(self.student_data_window,text="Capture",command=lambda: self.create_database())
        self.name_label.grid(row=0,column=0,padx=(40,10),pady=20)
        self.student_name.grid(row=0,column=1)
        self.enroll_label.grid(row=1,column=0,padx=(40,5),pady=20)
        self.student_enroll.grid(row=1,column=1)
        self.capture_pic.grid(row=2,column=0,columnspan=2,ipadx=30,ipady=10,padx=(40,0))


        
    def create_database(self):
        alg="haarfront.xml"
        haar=cv2.CascadeClassifier(alg)
        cam=cv2.VideoCapture(0)
        parent="students"
        folder=self.student_enroll.get()
        path=os.path.join(parent,folder)
        if not os.path.isdir(path):
            os.mkdir(path)
        (width,height)=(130,100)
        count=1
        while (count<=20):
            _,img=cam.read()
            grayImg=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces=haar.detectMultiScale(grayImg,1.3,4)
            for(x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                onlyFace=grayImg[y:y+h,x:x+w]
                resizeImg=cv2.resize(onlyFace,(width,height))
                cv2.imwrite("%s/%s.jpg"%(path,count),resizeImg)
                count+=1
            cv2.imshow("Make sure that your face is clearly visible",img)
            key=cv2.waitKey(1000)
            if key==27:
                break
        cam.release()
        cv2.destroyAllWindows()
        self.student_data_window.destroy()


    def train_model(self):
        global model,images,names,id,labels,haar_file,width,height
        haar_file="haarfront.xml"
        datasets='students'
        (images,labels,names,id)=([],[],{},0)
        for (subdir,dirs,files) in os.walk(datasets):
            for subdir in dirs:
                names[id]=subdir
                subjectpath=os.path.join(datasets,subdir)
                for filename in os.listdir(subjectpath):
                    path=subjectpath + '/' + filename
                    label=id
                    images.append(cv2.imread(path,0))
                    labels.append(int(label))
                id+=1
        (width,height)=(130,100)
        (images,labels)=[numpy.array(lis) for lis in [images,labels]]
        model=cv2.face.LBPHFaceRecognizer_create()
        model.train(images,labels)
        print("Training Completed")
        self.get_all_student_names()


    def get_all_student_names(self):
        global student_list
        global marking
        marking={}
        datasets='students'
        student_list=[]
        for (subdir,dirs,files) in os.walk(datasets):
            for subdir in dirs:
                student_list.append(subdir)
                marking[subdir]=0



class VideoCapture:
    def __init__(self,video_source=0):
        self.vid=cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open the video source",video_source)
        args=CommandLineParse().args
        VIDEO_TYPES={
            "avi":cv2.VideoWriter_fourcc(*'DIVX'),
            "mp4":cv2.VideoWriter_fourcc(*'DIVX')
        }
        
        self.fourcc=VIDEO_TYPES[args.type[0]]
        STD_DIMENSIONS={
            '480p':(640,480),
            '720p':(1280,720),
            '1080p':(1920,1080),
            '4k':(3840,2160)
        }

        res=STD_DIMENSIONS[args.res[0]]

        path="recordings/{}".format(str(dt.datetime.now().date()))
        if (not os.path.isdir(path)):
            os.mkdir(path)
        self.out=cv2.VideoWriter(path+"/"+args.name[0]+time.strftime("_%d-%m-%Y-%H-%M-%S")+'.'+args.type[0],self.fourcc,10,res)
        self.vid.set(3,res[0])
        self.vid.set(4,res[1])
        self.width,self.height=res
    

    def get_frame(self):
        
        if self.vid.isOpened():
            global faces,gray
            ret,frame=self.vid.read()

            face_cascade=cv2.CascadeClassifier(haar_file)

            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            
            faces=face_cascade.detectMultiScale(gray,1.3,4)
            for(x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,0),2)
                face=gray[y:y+h,x:x+w]
                face_resize=cv2.resize(face,(width,height))
                prediction=model.predict(face_resize)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0))
                if prediction[1]<80:
                    cv2.putText(frame,'%s-(%.2f)%%'%(names[prediction[0]],prediction[1]),(x-10,y-10),cv2.FONT_HERSHEY_PLAIN,2,(0,0,255),2)
                    self.mark_student(names[prediction[0]])
                else:
                    cv2.putText(frame,"Unknown Student",(x-10,y-10),cv2.FONT_HERSHEY_PLAIN,2,(0,0,255),2)
                    self.mark_student("unknown")

            if ret:
                return(ret,cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))
            else:
                return(ret,None)
        else:
            return(ret,None)

    def mark_student(self,name_stu):
        self.name=name_stu
        if (self.name in student_list):
            self.count_student(self.name)


    def count_student(self,stu_name):
        self.student=stu_name
        marking[stu_name]+=1




    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.out.release()
            cv2.destroyAllWindows()



class ElapsedTimeClock:
    def __init__(self,window):
        self.T=tk.Label(window,text="00:00:00",font=('times',20,'bold'),bg="black",fg="white")
        self.T.grid(row=1,column=0)
        self.elapsedTime=dt.datetime(1,1,1)
        self.running=0
        self.lastTime=''
        t=time.localtime()
        self.zeroTime=dt.timedelta(hours=t[3],minutes=t[4],seconds=t[5])


    def tick(self):
        self.now=dt.datetime(1,1,1).now()
        self.elapsedTime=self.now-self.zeroTime
        self.time2=self.elapsedTime.strftime('%H:%M:%S')
        if self.time2!=self.lastTime:
            self.lastTime=self.time2
            self.T.config(text=self.time2)

        self.upwin=self.T.after(100,self.tick)


    def start(self):
        if not self.running:
            self.zeroTime=dt.datetime(1,1,1).now()-self.elapsedTime
            self.tick()
            self.running=1


    def stop(self):
        if self.running:
            self.T.after_cancel(self.upwin)
            self.elapsedTime=dt.datetime(1,1,1).now()-self.zeroTime
            self.time2=self.elapsedTime
            self.running=0



class CommandLineParse:
    def __init__(self):
        parser=argparse.ArgumentParser(description="Smart Attendance System")
        parser.add_argument('--type',nargs=1,default=['avi'],type=str,help="To select video type")
        parser.add_argument('--res',nargs=1,default=['480p'],type=str,help="Resolution")
        parser.add_argument('--name',nargs=1,default=['Output'],type=str,help="Video name")

        self.args=parser.parse_args()



def main():
    App(tk.Tk())


main()