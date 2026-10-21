# DriveGuard Agent

基于视觉感知、时序分析与 Agent 决策的驾驶安全主动干预系统。项目不是单纯的 YOLO 检测页面，而是将摄像头画面转换为可追溯的驾驶风险事件，并完成提示音、语音干预和驾驶报告闭环。

## 已实现能力

- 闭眼与疲劳状态检测
- 低头、头部侧转与左右视线偏移检测
- 使用手机与抽烟行为检测
- 安全带佩戴状态估计
- 行为持续时间与连续帧确认
- 三级风险评分、提示音和高风险中文语音提醒
- 事件统计、驾驶安全评分与自然语言原因解释
- GPU 优先的人脸推理，以及异常时自动切换 CPU 后端

## AI 架构

系统采用三模型协同：

1. **YOLO11n-derived Driver Monitoring Model**：识别 Drowsy、Distracted、PhoneUse、Seatbelt、Smoking 等驾驶行为语义。
2. **MediaPipe Face Landmarker**：计算 EAR、头部俯仰/偏航、虹膜视线与低头几何特征。
3. **EfficientDet-Lite0 Object Detector**：提供独立的 `cell phone` 物体证据，用于手机与抽烟类别冲突裁决。

模型输出经过 Temporal Evidence Aggregation、Persistence Threshold、Consecutive-frame Confirmation 和加权风险决策后，才会形成正式事件。

## 在线演示

[DriveGuard Agent](https://driveguard-agent.westhi1l.chatgpt.site/)

## 本地运行

### 环境要求

- Node.js 18 或更高版本
- 最新版 Microsoft Edge 或 Google Chrome
- 可用摄像头
- 网络连接：ONNX 模型随仓库提供，但 MediaPipe 运行库及官方模型需要联网加载

### 启动

```bash
npm start
```

随后访问：

```text
http://127.0.0.1:4173/
```

浏览器摄像头通常只能在 HTTPS 或 `localhost/127.0.0.1` 安全上下文中使用，因此不要直接双击 `dist/index.html`。

## 使用流程

1. 点击“启动车内摄像头”并允许摄像头权限。
2. 正视前方约 4 秒，完成个人姿态和视线基线校准。
3. 系统开始实时分析驾驶行为。
4. 风险事件成立后，页面显示原因并播放提示音；高风险状态触发中文语音。
5. 驾驶结束后查看事件统计、安全评分与 Agent 解释。

## 项目结构

```text
dist/
  index.html                    前端与浏览器端推理逻辑
  models/driver-monitor.onnx    驾驶行为检测模型
docs/
  DriveGuard_Agent_项目说明书.pdf
  build_driveguard_report.py    说明书生成脚本
serve.mjs                       本地静态服务器
THIRD_PARTY_NOTICES.md          第三方模型与组件说明
```

## 真实性与安全边界

这是教育与产品原型，不是经过车规级验证的驾驶辅助系统。识别结果会受到光照、遮挡、摄像头位置、驾驶员外观和设备性能影响，不能替代驾驶员判断，也不能作为事故责任认定依据。

第三方模型和数据来源见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 开源许可

项目自有代码采用 [MIT License](LICENSE)。仓库中的第三方模型、数据来源和运行时组件不因 MIT License 而重新授权，仍须遵循 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 中列明的原始许可与署名要求。

