import cv2
import os
import sys
from tqdm import tqdm


def capture_slides_frame_diff(
    video_path, output_dir_path, frame_rate=1, MIN_PERCENT_THRESH=0.06, ELAPSED_FRAME_THRESH=85
):
    prev_frame = None
    curr_frame = None
    screenshots_count = 0
    capture_frame = False
    frame_elapsed = 0

    # Initialize kernel.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

    # Capture video frames
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Unable to open video file: ", video_path)
        sys.exit()

    success, first_frame = cap.read()
    frame_no = 1
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    prog_bar = tqdm(total=num_frames)

    print("Using frame differencing for Background Subtraction...")
    print("---" * 10)

    # The 1st frame should always be present in the output directory.
    # Hence capture and save the 1st frame.
    if success:
        # Convert frame to grayscale.
        first_frame_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

        prev_frame = first_frame_gray

        screenshots_count += 1

        filename = f"{screenshots_count:03}.jpg"
        out_file_path = os.path.join(output_dir_path, filename)

        # Save frame.
        cv2.imwrite(out_file_path, first_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        prog_bar.update(1)

    # Loop over subsequent frames.
    while cap.isOpened():
        ret, frame = cap.read()
        frame_no += 1

        if not ret:
            break
        if frame_no % frame_rate != 0:
            prog_bar.update(1)
            continue

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        curr_frame = frame_gray

        if (prev_frame is not None) and (curr_frame is not None):
            frame_diff = cv2.absdiff(curr_frame, prev_frame)
            _, frame_diff = cv2.threshold(frame_diff, 80, 255, cv2.THRESH_BINARY)

            # Perform dilation to capture motion.
            frame_diff = cv2.dilate(frame_diff, kernel)

            # Compute the percentage of non-zero pixels in the frame.
            p_non_zero = (cv2.countNonZero(frame_diff) / (1.0 * frame_gray.size)) * 100

            if p_non_zero >= MIN_PERCENT_THRESH and not capture_frame:
                capture_frame = True
            elif capture_frame:
                frame_elapsed += 1

            if frame_elapsed >= ELAPSED_FRAME_THRESH:
                capture_frame = False
                frame_elapsed = 0

                screenshots_count += 1

                filename = f"{screenshots_count:03}.jpg"
                out_file_path = os.path.join(output_dir_path, filename)

                cv2.imwrite(out_file_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                prog_bar.set_postfix_str(f"Total Screenshots: {screenshots_count}")

        prev_frame = curr_frame
        prog_bar.update(1)

    # Release progress bar and video capture object.
    prog_bar.close()
    cap.release()
