import os
import cv2
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient, InferenceConfiguration
from inference_sdk.webrtc import WebcamSource, StreamConfig, VideoMetadata


# Load API key from .env
load_dotenv()
API_KEY = os.getenv("ROBOFLOW_API_KEY")

if not API_KEY:
    raise RuntimeError("Add your real ROBOFLOW_API_KEY to the .env file.")


# Connect to Roboflow Cloud
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=API_KEY,
).configure(
    InferenceConfiguration(api_key_transport="header")
)


# Configure the webcam
# If this resolution causes an error, change this to WebcamSource()
camera = WebcamSource(resolution=(1280, 720))


# Receive the annotated image and prediction data
config = StreamConfig(
    stream_output=["output_image"],
    data_output=["predictions"],
)


# Connect the webcam to your published Workflow
session = client.webrtc.stream(
    source=camera,
    workspace="rutvik-zapadiya",
    workflow="custom-workflow",
    image_input="image",
    config=config,
)


@session.on_frame
def display_frame(frame, metadata: VideoMetadata):
    """Display the annotated frame returned by the Workflow."""

    cv2.imshow("Live Mask Detection - Press Q to stop", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or key == 27:
        session.close()


@session.on_data("predictions")
def display_predictions(result, metadata: VideoMetadata):
    """Print mask and nomask predictions in the terminal."""

    if not isinstance(result, dict):
        return

    detections = result.get("predictions", [])

    if not detections:
        print(f"Frame {metadata.frame_id}: no face detected")
        return

    messages = []

    for detection in detections:
        class_name = detection.get("class", "unknown")
        confidence = float(detection.get("confidence", 0))

        messages.append(
            f"{class_name} ({confidence:.1%})"
        )

    print(
        f"Frame {metadata.frame_id}: "
        + ", ".join(messages)
    )


print("Starting live mask detection...")
print("Press Q or Esc in the camera window to stop.")

try:
    session.run()

except KeyboardInterrupt:
    session.close()

finally:
    cv2.destroyAllWindows()

print("Camera stopped.")
