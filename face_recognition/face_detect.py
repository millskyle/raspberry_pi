import cv2
import cv2.cv as cv
import getopt, sys
import uuid
import sys, math, Image

cascade_dir="/usr/local/share/OpenCV/haarcascades/"

def find_face_from_img(img):
   #convert
   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   gray = cv2.equalizeHist(gray)
   rects = cascade.detectMultiScale(img, scaleFactor=1.2, minNeighbors=3, minSize=(40, 40), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
   print 'found %d faces' % (len(rects))
   if len(rects) > 0:
      image_scale=1.0
      for x, y, w, h in rects:
   # the input to cv.HaarDetectObjects was resized, so scale the
   # bounding box of each face and convert it to two CvPoints
         pt1 = (int(x * image_scale), int(y * image_scale))
         pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
         face = img[y: y + h, x: x + w]
         face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
         face = cv2.equalizeHist(face)
         eyes = eyecascade.detectMultiScale(face, scaleFactor=1.2, minNeighbors=3, minSize=(3,3),flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
         if len(eyes)==2: #if two eyes aren't detected, throw away the face
            eye=[]
            for xx,yy,ww,hh in eyes:
               eye.append((int(xx+xx+ww)/2, int(yy+yy+hh)/2))
               pt1 = (int(xx), int(yy))
               pt2 = (int((xx + ww) ), int((yy + hh)))
         #      cv2.rectangle(face,pt1,pt2,(255,0,0))
               cv2.circle(face,((int(xx+xx+ww)/2, int(yy+yy+hh)/2)),4,255,-1)
            eye = [ min(eye), max(eye) ] #sort the eyes
            angle = math.atan2(eye[1][1] - eye[0][1], eye[1][0] - eye[0][0])
            rot = cv2.getRotationMatrix2D(eye[0], -angle, 1.0 )
            face = cv2.warpAffine(face, rot, (150,150))
            face = cv2.resize(face,(150,150), interpolation=cv.CV_INTER_CUBIC)
            cv2.imwrite("faces/" + str(uuid.uuid4()) + ".jpg",face)
def Distance(p1,p2):
  dx = p2[0] - p1[0]
  dy = p2[1] - p1[1]
  return math.sqrt(dx*dx+dy*dy)



#      cv2.imwrite("output.jpg",img)

if __name__ == '__main__':

   args, video_src = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])
   try: video_src = video_src[0]
   except: video_src = 0
   args = dict(args)


   face_cascade_name = cascade_dir+"haarcascade_frontalface_alt.xml";
   #eyes_cascade_name = cascade_dir+"haarcascade_eye_tree_eyeglasses.xml";
   eyes_cascade_name = cascade_dir+"haarcascade_eye.xml";


   cascade = cv2.CascadeClassifier(face_cascade_name)
   eyecascade = cv2.CascadeClassifier(eyes_cascade_name)

   c=cv2.VideoCapture(0)
   while(1):
      ret, frame = c.read()
      rects = find_face_from_img(frame)
      if 0xFF & cv2.waitKey(5) == 27:
         break

