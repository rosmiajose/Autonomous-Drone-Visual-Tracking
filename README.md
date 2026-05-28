# 🚁 Autonomous Visual Tracking System — DJI Tello + YOLOv8

> Real-time person detection and autonomous drone control using computer vision and deep learning.

---

## 📌 Project Overview

This project implements an **autonomous visual control system** on a DJI Tello drone. The drone detects and tracks a person in real time using a YOLOv8 object detection model, continuously adjusting its position to keep the target centered in frame — without any manual flight input.

This was developed as a **Master's final year project** in Automotive Embedded Systems at ESIGELEC, Rouen, France.

---

## Objectives

- Design and develop a **mobile robot platform with visual control**
- Implement **real-time object and person detection** on a live drone video stream
- Build a **closed-loop visual control system**: perception → decision → actuation
- Demonstrate **multi-sensor fusion** with camera as the primary sensor
- Achieve **autonomous target tracking** with obstacle awareness

---

## System Architecture

The system follows a classical embedded architecture with three distinct layers:

```
┌─────────────────────────────────────────────────────┐
│                  SENSING LAYER                      │
│         DJI Tello Front Camera (720p)               │
│         Live video stream over Wi-Fi / UDP          │
└─────────────────────┬───────────────────────────────┘
                      │ Video Frames
┌─────────────────────▼───────────────────────────────┐
│                PROCESSING LAYER                     │
│         Host PC running Python application          │
│         YOLOv8 inference engine (real-time)         │
│         Person detection → bounding box extraction  │
│         Control logic: frame error → movement cmd   │
└─────────────────────┬───────────────────────────────┘
                      │ UDP Movement Commands
┌─────────────────────▼───────────────────────────────┐
│                ACTUATION LAYER                      │
│         DJI Tello onboard flight controller         │
│         ESCs (Electronic Speed Controllers)         │
│         4x Brushless DC motors                      │
└─────────────────────────────────────────────────────┘
```

---

## Software Pipeline (Control Flow)

```
START
  │
  ├─► Import Libraries & Initialize DJI Tello SDK
  │
  ├─► Connect to Tello → Send Takeoff Command
  │
  ├─► Start Video Stream + Initialize Output File
  │
  ├─► Load YOLOv8 Model into Memory
  │
  └─► MAIN LOOP:
        │
        ├─► Get Latest Frame from Video Stream
        │
        ├─► Frame Available?
        │     ├── NO  → Print "No Frame Received" → Wait
        │     └── YES → Run YOLOv8 Inference on Frame
        │
        ├─► Detected Objects?
        │     └── YES → Track Detected Human
        │               Annotate Bounding Boxes on Frame
        │               Send Corrective Movement Commands to Drone
        │
        ├─► Tracking Duration Limit Reached?
        │     ├── NO  → Continue Loop
        │     └── YES → Land Drone
        │               Stop Video Recording
        │               Disconnect Tello
        │
        └─► END
```

---

## Technology Stack

| Component | Technology |
|---|---|
| Drone Platform | DJI Tello (Wi-Fi SDK) |
| Programming Language | Python 3 |
| Object Detection | YOLOv8 (Ultralytics) |
| Computer Vision | OpenCV |
| Drone Control Library | DJITelloPy |
| Communication Protocol | Wi-Fi / UDP |
| Processing | Multithreaded Python (frame capture + inference) |

---

## How The Visual Control Loop Works

The core of this project is a **perception-actuation closed loop**:

1. The drone's camera captures a frame
2. YOLOv8 processes the frame and returns a bounding box around any detected person
3. The center of the bounding box is calculated and compared to the center of the frame
4. The **positional error** (how far the person is from center) is used to generate corrective movement commands:
   - Person too far left → drone yaws left
   - Person too far right → drone yaws right
   - Person too small in frame (far away) → drone moves forward
   - Person too large in frame (close) → drone moves backward
5. Commands are sent to the Tello over UDP
6. The Tello's onboard ESCs execute the commands via motor speed adjustments
7. Loop repeats for the next frame

This is a form of **visual servoing** — controlling a robot's motion using visual feedback as the error signal.

---

## Hardware Specifications — DJI Tello

| Parameter | Specification |
|---|---|
| Weight | 80g |
| Max Flight Time | ~13 minutes |
| Camera | 720p HD, 30fps |
| Communication | Wi-Fi 802.11n (2.4 GHz) |
| SDK | Tello SDK 2.0 over UDP |
| Onboard Processor | Embedded flight controller |
| Actuation | 4x ESCs + brushless motors |
| Stabilization | IMU + barometer |

---

## Challenges & How We Addressed Them

### 1. Real-Time Processing Latency
**Problem:** YOLOv8 inference on CPU caused frame processing to drop to 10–15 FPS, meaning the control loop was reacting to frames already 100ms+ old.

**Solution:** Decoupled frame capture and inference into separate threads. The video buffer filled continuously while inference ran independently, reducing effective latency.

### 2. Battery Life Constraints
**Problem:** DJI Tello offers only ~13 minutes of flight time, severely limiting testing windows.

**Solution:** Developed and validated the detection pipeline on pre-recorded video first, then deployed to live flight only when logic was confirmed working.

### 3. Wireless Communication Latency
**Problem:** UDP commands sent over Wi-Fi introduced variable delay in the control loop, causing the drone to overshoot corrections.

**Solution:** Tuned movement command magnitudes and added dead-zone thresholds — small positional errors below a threshold did not trigger movement commands, preventing oscillation.

### 4. Detection Precision
**Problem:** YOLOv8 detection confidence dropped in low light, partial occlusion, and at large distances.

**Solution:** Used YOLOv8n (nano) variant for speed, with a confidence threshold filter to ignore low-confidence detections and prevent false positive tracking.

### 5. Payload Capacity
**Problem:** Tello's 80g weight limit meant no additional sensors could be mounted.

**Solution:** Relied entirely on the onboard camera as the sole sensor — demonstrating that a single-sensor visual control loop can be effective with the right processing pipeline.

---

## Results

- ✅ Successful real-time person detection at 15–30 FPS depending on scene complexity
- ✅ Autonomous person tracking with drone maintaining target in frame center
- ✅ Object and obstacle annotation on live video feed
- ✅ Controlled autonomous landing after defined tracking duration
- ✅ Full flight session recorded to video file for analysis

---

## Lessons Learned

- Practical implementation and SDK integration of the DJI Tello drone platform
- Real-time constraints in embedded vision systems — where the bottleneck actually is
- YOLOv8 model loading, inference optimization, and confidence threshold tuning
- Multithreaded Python architecture for parallel video capture and processing
- The impact of wireless communication latency on closed-loop control systems
- Importance of testing pipeline on recorded data before live hardware deployment

---

## Future Perspectives

- **Onboard inference:** Deploy a lightweight model (e.g. YOLOv8n with TensorRT) directly on an edge device mounted to the drone, eliminating Wi-Fi latency in the control loop
- **PID control:** Replace the simple threshold-based controller with a proper PID controller for smoother, more stable tracking
- **Multi-target tracking:** Extend to tracking multiple people simultaneously using DeepSORT or ByteTrack
- **Depth estimation:** Add monocular depth estimation to improve obstacle detection and distance-aware control
- **Model fine-tuning:** Fine-tune YOLOv8 on domain-specific data (specific lighting, indoor/outdoor environments) for higher precision

---

## References

- [DJI Tello SDK Documentation](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
- [Ultralytics YOLOv8 Documentation](https://docs.ultralytics.com/)
- [DJITelloPy Library](https://github.com/damiafuentes/DJITelloPy)
- [OpenCV Documentation](https://docs.opencv.org/)
