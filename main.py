
from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import time
import pyautogui

app = Flask(__name__)

cap = cv2.VideoCapture(0)


def gen_frames():

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
        font = cv2.FONT_HERSHEY_SIMPLEX
        success, img = cap.read()

        # flip camera on X-axis
        img = cv2.flip(img, 1)

        if not success:
            break

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        # print(xAvg, yAvg)
        xAvg = 0
        yAvg = 0
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                lmList = []
                for id, lm in enumerate(handLms.landmark):
                    # print(id,lm)
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # if id ==0:
                    cv2.circle(img, (cx, cy), 3, (255, 0, 255), cv2.FILLED)
                    #xAvg = xAvg + cx
                    #yAvg = yAvg + cy
                    lmList.append([id, cx, cy])

                # CURSOR CODE STARTS HERE
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                #xAvg = xAvg / 20
                #yAvg = yAvg / 20
                #pyautogui.moveTo(3*xAvg, 3*yAvg)

                # CLICKING CODE STARTS HERE
                indexX = 0
                indexY = 0
                indexMid = 0
                handBottomX = 0
                handBottomY = 0
                pinkyX = 0
                pinkyY = 0
                fistWarning = "Fist!"
                for lms in lmList:
                    if lms[0] == 7:
                        indexX, indexY = lms[1], lms[2]
                        # cv2.circle(handsFrame, (lms[1], lms[2]), 15, (255, 0, 255), cv2.FILLED)
                    elif lms[0] == 5:
                        indexMid = lms[2]
                    # elif lms[0] == 11:
                    # middleY = lms[2]
                    # cv2.circle(handsFrame, (lms[1], lms[2]), 15, (255, 0, 255), cv2.FILLED)
                    # elif lms[0] == 15:
                    # ringY = lms[2]
                    # cv2.circle(handsFrame, (lms[1], lms[2]), 15, (255, 0, 255), cv2.FILLED)
                    elif lms[0] == 19:
                        pinkyX, pinkyY = lms[1], lms[2]
                        # cv2.circle(handsFrame, (lms[1], lms[2]), 15, (255, 0, 255), cv2.FILLED)
                    elif lms[0] == 0:
                        handBottomX, handBottomY = lms[1], lms[2]
                if (indexY < handBottomY) and (indexY > indexMid):
                    cv2.rectangle(imgRGB, (indexX, indexY), (pinkyX, handBottomY), (0, 0, 255), 2)
                    cv2.putText(imgRGB, fistWarning, (pinkyX + 2, indexY - 2), (font), .7,
                                (0, 0, 255), 1, cv2.LINE_4)
                    # print("Fist!!")

                    pyautogui.click()
                # if xAvg < 160 and yAvg < 120:
                #    pyautogui.press('w')
                # elif xAvg < 160 and yAvg > 120:
                #    pyautogui.press('d')
                # elif xAvg > 480 and yAvg > 360:
                #    pyautogui.press('s')
                # elif xAvg > 480 and yAvg < 360:
                #    pyautogui.press('a')

                pyautogui.moveTo(3 * handBottomX, (3 * handBottomY) - 200)
                # pyautogui.moveTo(handBottomX, handBottomY)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        #image = cv2.flip(img, 1)

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

        # cv2.imshow("Image", img)
        # cv2.waitKey(1)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
