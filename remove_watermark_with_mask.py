import os
import time
import cv2
import glob
import numpy as np
import datetime
import boto3


def upload_file(file_name, bucket):
    """
    Function to upload a file to an S3 bucket
    """
    try:
        object_name = file_name
        s3_client = boto3.client('s3')
        response = s3_client.upload_file(file_name, bucket, object_name)
        print('[INFO] Connection established....')
        print('[INFO] Video uploaded....', response)
        return response
    except Exception as e:
        print('[FAILURE] Video Not uploaded....', e)


def video_to_frames(input_loc, output_loc):
    try:
        if os.path.exists(output_loc):
            pass
        else:
            os.mkdir(output_loc)
    except OSError:
        pass
    time_start = time.time()
    cap = cv2.VideoCapture(input_loc)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print("[INFO] Number of frames: ", video_length)
    count = 0
    print("[INFO] Converting video..\n")
    while cap.isOpened():
        ret, frame = cap.read()
        resize = cv2.resize(frame, (480, 848))
        cv2.imwrite(output_loc + "/%#05d.png" % (count + 1), resize)
        count = count + 1
        if (count > (video_length - 1)):
            time_end = time.time()
            cap.release()
            print("[SUCCESS] Done extracting frames.\n%d frames extracted" % count)
            print("[INFO] It took %d seconds forconversion." %
                  (time_end - time_start))
            break


def masking(output_loc):
    flags = cv2.INPAINT_TELEA
    images = glob.glob(output_loc + "/*png")
    if os.path.exists(output_loc + "/masked_img"):
        pass
    else:
        os.mkdir(output_loc + "/masked_img")
    count = 0
    for image in images:
        img = cv2.imread(image)
        # if True:
        # path shai kr iska ye vala masks/mask01.png
        mask = cv2.imread('/home/alervice/Desktop/masks/mask01.png')
        # else:
        #     mask = cv2.imread('masks/mask01.png')
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        output = cv2.inpaint(img, mask, 3, flags=flags)
        path = output_loc + "/masked_img"
        cv2.imwrite(path + "/%#05d.png" % (count + 1), output)
        count = count + 1
    cv2.waitKey(0)
    print("[SUCCESS] Done masking frames. %d frames Masked." % count)
    print('[INFO] Masking Completed....')


def frames_to_video(output_loc, frame_loc):
    img_array = []
    frames = glob.glob(f'{frame_loc}/masked_img/*.png')
    for frame in frames:
        img = cv2.imread(frame)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)
    getdatetime = datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%p")
    if os.path.exists(output_loc):
        full_path = f'{output_loc}/output{getdatetime}.avi'
    else:
        os.mkdir(output_loc)
        full_path = f'{output_loc}/output{getdatetime}.avi'

    out = cv2.VideoWriter(full_path,
                          cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    # os.remove(frame_loc)
    print(f'[INFO] Saved video at {full_path}....')
    return full_path




if __name__ == "__main__":
    input_loc = '/home/alervice/Desktop/input_videos/kanhaji.mp4'
    frame_loc = '/home/alervice/Desktop/frames'
    output_loc = '/home/alervice/Desktop/output_videos'
    bucket_name = ''
    try:
        print("[START] The video Watermark removal started...")
        video_to_frames(input_loc, frame_loc)
        print('[INFO] Masking Started....')
        masking(frame_loc)
        print("[INFO] Start achieveing video...")
        obj = frames_to_video(output_loc, frame_loc)
        print("[RESULT] The video was successfully Watermark removed...")
        # if obj:
        #     upload_file(obj, bucket_name)
        # else:
        #     print('File not exists')
    except Exception as e:
        print('[FAILURE] ERROR', e)
