import os
import base64
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import cv2
from dotenv import load_dotenv
from inference_sdk import InferenceConfiguration, InferenceHTTPClient
from inference_sdk.webrtc import StreamConfig, VideoMetadata, WebcamSource


class MaskDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Mask Detection")
        self.root.geometry("1000x760")
        self.root.minsize(720, 540)

        self.session = None
        self.worker = None
        self.frame_queue = queue.Queue(maxsize=1)
        self.running = False

        self.status = tk.StringVar(value="Camera stopped")
        self.prediction_text = tk.StringVar(value="No predictions yet")

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(30, self._show_latest_frame)

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        controls = ttk.Frame(self.root, padding=12)
        controls.grid(row=0, column=0, sticky="ew")

        self.start_button = ttk.Button(controls, text="Start camera", command=self.start)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(
            controls, text="Stop camera", command=self.stop, state="disabled"
        )
        self.stop_button.pack(side="left", padx=(8, 0))
        ttk.Label(controls, textvariable=self.status).pack(side="left", padx=16)

        self.video_label = ttk.Label(self.root, anchor="center", text="Press Start camera")
        self.video_label.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))

        prediction_frame = ttk.LabelFrame(self.root, text="Detections", padding=8)
        prediction_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        ttk.Label(prediction_frame, textvariable=self.prediction_text).pack(anchor="w")

    def start(self):
        if self.running:
            return

        load_dotenv()
        api_key = os.getenv("ROBOFLOW_API_KEY")
        if not api_key:
            messagebox.showerror(
                "Missing API key",
                "Add ROBOFLOW_API_KEY to the .env file, then start the camera again.",
            )
            return

        self.running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status.set("Connecting to Roboflow...")
        self.prediction_text.set("Waiting for predictions...")
        self.worker = threading.Thread(
            target=self._run_session, args=(api_key,), daemon=True
        )
        self.worker.start()

    def _run_session(self, api_key):
        try:
            client = InferenceHTTPClient(
                api_url="https://serverless.roboflow.com", api_key=api_key
            ).configure(InferenceConfiguration(api_key_transport="header"))

            camera = WebcamSource(resolution=(1280, 720))
            config = StreamConfig(
                stream_output=["output_image"], data_output=["predictions"]
            )
            session = client.webrtc.stream(
                source=camera,
                workspace="rutvik-zapadiya",
                workflow="custom-workflow",
                image_input="image",
                config=config,
            )
            self.session = session

            @session.on_frame
            def receive_frame(frame, metadata: VideoMetadata):
                if not self.running:
                    return
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
                try:
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    pass

            @session.on_data("predictions")
            def receive_predictions(result, metadata: VideoMetadata):
                if not isinstance(result, dict):
                    return
                detections = result.get("predictions", [])
                if not detections:
                    text = "No face detected"
                else:
                    text = ", ".join(
                        f"{item.get('class', 'unknown')} "
                        f"({float(item.get('confidence', 0)):.1%})"
                        for item in detections
                    )
                self.root.after(0, self.prediction_text.set, text)

            self.root.after(0, self.status.set, "Camera running")
            session.run()
        except Exception as error:
            if self.running:
                self.root.after(0, self._show_error, str(error))
        finally:
            self.session = None
            if self.running:
                self.root.after(0, self._session_finished)

    def _show_latest_frame(self):
        try:
            frame = self.frame_queue.get_nowait()
            success, encoded = cv2.imencode(".png", frame)
        except queue.Empty:
            frame = None
        except Exception as error:
            self.status.set(f"Frame error: {error}")
            frame = None

        if frame is not None and success:
            try:
                image_data = base64.b64encode(encoded.tobytes()).decode("ascii")
                image = tk.PhotoImage(data=image_data, format="png")
                self.video_label.configure(image=image, text="")
                self.video_label.image = image
            except Exception as error:
                self.status.set(f"Preview error: {error}")
        self.root.after(30, self._show_latest_frame)

    def _show_error(self, error):
        self.stop()
        messagebox.showerror("Mask detection stopped", error)

    def _session_finished(self):
        self.stop()

    def stop(self):
        self.running = False
        session = self.session
        self.session = None
        if session is not None:
            try:
                session.close()
            except Exception:
                pass
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status.set("Camera stopped")

    def close(self):
        self.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    MaskDetectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()