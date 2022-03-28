import cv2
import mediapipe as mp
import time

import pyautogui

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=1,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0
xAvg = 0
yAvg = 0


while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    #print(results.multi_hand_landmarks)
    print(xAvg,yAvg)
    xAvg = 0
    yAvg = 0
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                #print(id,lm)
                h, w, c = img.shape
                cx, cy = int(lm.x *w), int(lm.y*h)
                #if id ==0:
                cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)
                xAvg = xAvg + cx
                yAvg = yAvg + cy

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            xAvg = xAvg / 20
            yAvg = yAvg / 20
            pyautogui.moveTo(-3*cx, 3*cy)
            #if xAvg < 160 and yAvg < 120:
            #    pyautogui.press('w')
            #elif xAvg < 160 and yAvg > 120:
            #    pyautogui.press('d')
            #elif xAvg > 480 and yAvg > 360:
            #    pyautogui.press('s')
            #elif xAvg > 480 and yAvg < 360:
            #    pyautogui.press('a')


    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    image = cv2.flip(img, 1)

    #cv2.putText(image,str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)

    #cv2.line(image, (0, 0), (160, 120), (255, 0, 0), 2, 0, None)
    #cv2.line(image, (640, 0), (480, 120), (255, 0, 0), 2, 0, None)
    #cv2.line(image, (0, 480), (160, 360), (255, 0, 0), 2, 0, None)
    #cv2.line(image, (640, 480), (480, 360), (255, 0, 0), 2, 0, None)
    #cv2.line(image, (160, 120), (480, 120), (0, 255, 0), 2, 0, None)
    #cv2.line(image, (480, 120), (480, 360), (0, 255, 0), 2, 0, None)
    #cv2.line(image, (480, 360), (160, 360), (0, 255, 0), 2, 0, None)
    #cv2.line(image, (160, 360), (160, 120), (0, 255, 0), 2, 0, None)
    # img is 640 wide
    # img is 480 tall



    cv2.imshow("Image", image)
    cv2.waitKey(1)
