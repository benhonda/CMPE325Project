# Learned from https://www.youtube.com/watch?v=8gPONnGIPgw

from flask import Flask, render_template, Response, request
import cv2
import numpy as np
import Tracker as htm
import time
import autopy

app = Flask(__name__)


def gen_frames():

    ##########################
    # wCam, hCam = 640, 480
    wCam, hCam = 1280, 720
    frameR = 100  # Frame Reduction
    smoothening = 7
    #########################

    pTime = 0
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = htm.handDetector(maxHands=1)
    wScr, hScr = autopy.screen.size()
    # print(wScr, hScr)

    while cap.isOpened():
        # 1. Find hand Landmarks
        success, img = cap.read()

        if not success:
            break

        # flip camera on X-axis
        img = cv2.flip(img, 1)

        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        # 2. Get the tip of the index and middle fingers
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            # print(x1, y1, x2, y2)

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)

        # 4. Only Index Finger : Moving Mode
        if len(fingers) > 0 and fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move Mouse
            # autopy.mouse.move(wScr - clocX, clocY)
            autopy.mouse.move(clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 8. Both Index and middle fingers are up : Clicking Mode
        if len(fingers) > 0 and fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print(length)
            # 10. Click mouse if distance short
            if length < 50:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                           15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
                time.sleep(0.5)
                
                

        # 11. Frame Rate
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)
        # 12. Display
        # cv2.imshow("Image", img)
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
        cv2.waitKey(1)


@app.route('/video_feed')
def video_feed():

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
