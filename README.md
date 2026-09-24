# Live Mask Detection

A Python webcam application that sends live camera frames to a Roboflow Workflow and displays mask-detection predictions. The project includes a Tkinter GUI, a terminal/OpenCV runner, and a camera test utility.

## Requirements

- Windows with a working webcam
- Python 3.10 or newer
- A Roboflow API key
- A published Roboflow Workflow configured for webcam image input

Tkinter is included with the standard Windows Python installer. If Python was installed without Tcl/Tk support, reinstall Python with the standard optional features enabled.

## Setup

1. Clone the repository and open its folder:

   ```powershell
   git clone https://github.com/RUTVIK-ZAPADIYA/mask_detection.git
   cd mask_detection
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Create a file named `.env` in the project folder:

   ```text
   ROBOFLOW_API_KEY=your_roboflow_api_key
   ```

The `.env` file is ignored by Git and must never be committed or shared publicly.

## Run the application

### GUI

```powershell
python mask_detection_gui.py
```

Or double-click `run_mask_detection.bat`. In the GUI, select **Start camera** to connect to the Roboflow Workflow and **Stop camera** to end the session.

### Terminal mode

```powershell
python live_camera.py
```

Press `Q` or `Esc` in the camera window to stop.

### Test the webcam

Use this before troubleshooting Roboflow connectivity:

```powershell
python camera_test.py
```

Press `Q` or `Esc` to close the test window.

## Roboflow configuration

The current code connects to:

- Workspace: `rutvik-zapadiya`
- Workflow: `custom-workflow`
- Image input: `image`
- API endpoint: `https://serverless.roboflow.com`

Update these values in `mask_detection_gui.py` and `live_camera.py` if your Roboflow project uses different settings.

## Troubleshooting

- **Missing API key:** Confirm `.env` is in the project root and contains `ROBOFLOW_API_KEY`.
- **Camera unavailable:** Check Windows camera permissions and close other applications using the webcam.
- **Workflow connection errors:** Confirm the API key, workspace, workflow name, and internet connection.
- **PowerShell activation blocked:** Run `Set-ExecutionPolicy -Scope Process Bypass` for the current terminal session, then activate the environment again.

## License

No license has been specified yet.