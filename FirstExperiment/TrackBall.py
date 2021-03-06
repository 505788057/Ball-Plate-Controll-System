from imutils.video import VideoStream
import numpy as np
import argparse  # 是python的一个命令行解析包，用于编写可读性非常好的程序
import cv2
import imutils  # a python package is used as image processing.
import time
import kalman_new

'''
1. define the lower and upper boundaries of the "green" ball in the HSV color space
2. initialize the list of tracked points
3. allow the camera or video file to warm up
4. vs means video source.
'''

vs = cv2.VideoCapture(1, cv2.CAP_DSHOW)
vs.set(3, 1280)
vs.set(4, 720)
time.sleep(.5)

'''
1. vs.isOpened() if get the video, it will back the True continually.
2. vs.read() will reture two argument. The first is the situation whether vs gets the correct video source. The second
    is the matrix of the frame.
3. resize the frame.
4. 低通滤波器就是允许低频信号通过，在图像中边缘和噪点都相当于高频部分，所以低通滤波器用于去除噪点、平滑和模糊图像。
5. GaussianBlur() make noise cancellation.
'''
'''
1. 先利用二值化，将图片分成白色背景与黑色背景
2. 利用腐蚀与膨胀，去除白色背景与黑色背景中的噪声点
3. 利用 cv2.findContours(), 找到frame中的所有轮廓。
    -- 三个输入参数：输入图像（二值图像，黑色作为背景，白色作为目标），轮廓检索方式，轮廓近似方法。
    -- opencv2返回两个值：contours、hierarchy

'''
greenLower = (29, 86, 6)
greenUpper = (120, 255, 200)
while vs.isOpened():
    time.sleep(0.01)
    _, frame = vs.read()
    frame = frame[0:720, 280:1030]
    frame = imutils.resize(frame, width=720)

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask_before = cv2.inRange(hsv, greenLower, greenUpper)
    mask_erode = cv2.erode(mask_before, None, iterations=2)
    mask = cv2.dilate(mask_erode, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    a = cnts
    cnts = imutils.grab_contours(cnts)
    center = None

    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        center_float = (M["m10"] / M["m00"], M["m01"] / M["m00"])
        # a, b, c, d = kalman_new.kalman(np.mat(center_float[0]))
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

    # cv2.imshow('mask_before', mask_before)
    cv2.imshow('frame', frame)
    cv2.imshow('mask_before', mask_before)
    cv2.imshow('mask_erode', mask_erode)
    cv2.imshow('mask', mask)
    if cv2.waitKey(1) == ord('q'):
        break
vs.release()
cv2.destroyAllWindows()
