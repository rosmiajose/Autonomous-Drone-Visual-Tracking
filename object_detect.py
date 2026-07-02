import cv2
from ultralytics import YOLO
from djitellopy import Tello

tello = Tello()
tello.connect()
print(tello.get_battery())
tello.streamon()

video_path = 'object_detect.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_out = cv2.VideoWriter(video_path, fourcc, 20, (960,720), isColor=True)

model = YOLO('yolov8s.pt', task='detect')
frame_read = tello.get_frame_read(with_queue=False, max_queue_len=0)

while True:
    frame = frame_read.frame

    if frame is not None:
        results = model(frame)
        annotated_frame = results[0].plot()
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        video_out.write(annotated_frame)
        cv2.imshow("YOLOv8 Tello Drone Tracking", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("x"):
            break
    else:
        print("No frame received")

video_out.release()
tello.end()
cv2.destroyAllWindows()
