# Third-party notices

DriveGuard Agent includes `dist/models/driver-monitor.onnx`, derived from the Soham YOLO11n model published in the [AlbatrossC Driver Monitoring System](https://github.com/AlbatrossC/Driver-Monitoring-System).

The source project documents the training dataset as “Driver Monitoring System v1” from Roboflow Universe under the Creative Commons Attribution 4.0 license. The model recognizes Distracted, Drinking, Drowsy, Eating, PhoneUse, SafeDriving, Seatbelt, and Smoking classes.

Browser inference uses ONNX Runtime Web. Face landmark inference uses Google MediaPipe Tasks Vision and the official Face Landmarker model.

These models are intended for educational demonstrations and prototypes. They have not been validated as an automotive-grade safety system.

