import cv2


def main():
    # 0 normally means the default camera.
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError(
            "Could not open the webcam. Check camera permissions "
            "and close other programs using the camera."
        )

    print("Camera opened successfully.")
    print("Press Q or Esc to stop.")

    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read a frame from the camera.")
            break

        cv2.imshow("Camera Test", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
