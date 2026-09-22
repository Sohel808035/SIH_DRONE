def parse_yolo(results):
    """
    Convert Ultralytics results into a common format.
    """

    detections = []

    names = results.names

    for box in results.boxes:

        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        detections.append({
            "class": names[cls_id],
            "confidence": conf,
            "box": [x1, y1, x2, y2]
        })

    return detections