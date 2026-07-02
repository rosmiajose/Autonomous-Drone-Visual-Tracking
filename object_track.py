import cv2
from ultralytics import YOLO
from djitellopy import Tello
import time

def track_human(tello, bbox, frame_width, frame_height):
    center_x, center_y = bbox.xywh[0][:2]
    center_x, center_y = center_x.item(), center_y.item()

    offset_x = center_x - frame_width / 2
    offset_y = frame_height / 2 - center_y

    threshold_x = frame_width * 0.1
    threshold_y = frame_height * 0.1

    if abs(offset_x) > threshold_x:
        if offset_x > 0:
            tello.send_rc_control(20, 0, 0, 0)
        else:
            tello.send_rc_control(-20, 0, 0, 0)

    if abs(offset_y) > threshold_y:
        if offset_y > 0:
            tello.send_rc_control(0, 0, 30, 0)
        else:
            tello.send_rc_control(0, 0, -30, 0)

tello = Tello()
tello.connect()
print(f"Battery: {tello.get_battery()}%")

tello.takeoff()
time.sleep(2)
tello.streamon()

video_path = 'object_track.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_out = cv2.VideoWriter(video_path, fourcc, 20, (960,720), isColor=True)

model = YOLO('yolov8s.pt', task='detect')
frame_read = tello.get_frame_read(with_queue=False, max_queue_len=0)

tracking_duration = 60
start_time = time.time()

try:
    while True:
        frame = frame_read.frame

        if frame is not None:
            results = model(frame)
            annotated_frame = results[0].plot()

            for result in results:
                for bbox in result.boxes:
                    if bbox.cls == 0:
                        track_human(tello, bbox, frame.shape[1], frame.shape[0])

            video_out.write(annotated_frame)
            cv2.imshow("YOLOv8 Tello Drone Tracking", annotated_frame)

            elapsed_time = time.time() - start_time
            if elapsed_time > tracking_duration:
                print("Tracking duration elapsed. Landing the drone...")
                tello.land()
                break

            if cv2.waitKey(1) & 0xFF == ord("x"):
                print("Terminating script. Landing the drone...")
                tello.land()
                break
        else:
            print("No frame received")
            tello.streamoff()
            tello.streamon()
            time.sleep(2)

except Exception as e:
    print(f"An error occurred: {e}")
    tello.land()

finally:
    video_out.release()
    tello.end()
    cv2.destroyAllWindows()
