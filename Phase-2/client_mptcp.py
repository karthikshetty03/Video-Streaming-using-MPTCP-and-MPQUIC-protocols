import argparse, socket, cv2, utils
import numpy as np
from datetime import datetime
from make_vid import convert_frames_to_video

MAX_BYTES = 100000


class DataExceededError(Exception):
    pass


def startClient(host, port):
    # initialize connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_TCP, 42, 1)
    s.connect((host, port))

    counter = 0

    starttime = datetime.now()
    print("Starting Video Streaming at ", starttime)

    # Recieve frames and display it in real-time
    count = 0
    frame = None
    frameOld = None
    rows1, rows2 = -1, -1
    cols1, cols2 = -1, -1
    rows, cols = 0, 0
    pos_i, pos_j, pos_k = 0, 0, 0

    # Client side video streaming algorithm that recieves all the frames untill data is not empty
    while True:
        try:
            data_pos = 0
            data = s.recv(MAX_BYTES)
            if not data:
                break
            while data_pos < len(data):
                if frame is None:
                    if rows1 == -1:
                        rows1 = data[data_pos]
                        data_pos = data_pos + 1
                        if data_pos >= len(data):
                            raise DataExceededError
                    if rows2 == -1:
                        rows2 = data[data_pos]
                        data_pos = data_pos + 1
                        rows = (rows1 << 8) + rows2
                        if data_pos >= len(data):
                            raise DataExceededError
                    if cols1 == -1:
                        cols1 = data[data_pos]
                        data_pos = data_pos + 1
                        if data_pos >= len(data):
                            raise DataExceededError
                    if cols2 == -1:
                        cols2 = data[data_pos]
                        data_pos = data_pos + 1
                        cols = (cols1 << 8) + cols2
                        frame = np.zeros((rows, cols, 3), np.uint8)
                        if data_pos >= len(data):
                            raise DataExceededError
                frame[pos_i][pos_j][pos_k] = data[data_pos]
                data_pos = data_pos + 1
                pos_k = pos_k + 1
                if pos_k == 3:
                    pos_k = 0
                    pos_j = pos_j + 1
                    if pos_j == cols:
                        pos_j = 0
                        pos_i = pos_i + 1
                        if pos_i == rows:
                            pos_i = 0
                            frameOld = frame
                            count = count + 1
                            frame = None
                            rows1 = -1
                            rows2 = -1
                            cols1 = -1
                            cols2 = -1
                            rows = 0
                            cols = 0
                            cv2.imwrite(f"images/frame{counter}.jpg", frameOld)
                            counter += 1
                            cv2.imshow("Output", frameOld)
                            cv2.waitKey(1)
        except DataExceededError:
            pass
    endtime = datetime.now()
    print("Ending video streaming at ", endtime)
    print("Frame Received ", count)

    # convert recieved frames into a video file
    convert_frames_to_video("images/", "output.avi", 12.0)

    cv2.destroyAllWindows()
    s.close()
    print("connection closed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send and receive over MP-TCP")
    parser.add_argument(
        "host", help="interface the server listens at;" " host the client sends to"
    )
    parser.add_argument(
        "-p", metavar="PORT", type=int, default=6000, help="TCP port (default 6000)"
    )
    args = parser.parse_args()
    startClient(args.host, args.p)
