import cv2

COLORS = {
    "fire": (0,0,255),          # Red
    "smoke": (180,180,180),     # Gray
    "flood": (255,0,0),         # Blue
    "landslide": (42,42,165),   # Brown
    "debris": (0,255,0),        # Green
    "person": (0,255,255)       # Yellow
}

def draw_detections(frame, detections):

    for det in detections:

        x1,y1,x2,y2 = det["box"]
        cls = det["class"]
        conf = det["confidence"]

        color = COLORS.get(cls,(255,255,255))

        cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)

        label = f"{cls} {conf:.2f}"

        cv2.putText(
            frame,
            label,
            (x1,max(20,y1-8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    return frame


if __name__ == "__main__":

    img = cv2.imread("../../datasets/final/test/images/fire_smoke_1.jpg")

    sample = [
        {"class":"fire","confidence":0.91,"box":[120,220,240,380]},
        {"class":"smoke","confidence":0.74,"box":[80,40,300,180]},
        {"class":"person","confidence":0.83,"box":[260,240,320,420]}
    ]

    out = draw_detections(img,sample)

    cv2.imshow("Multi Hazard",out)
    cv2.waitKey(0)