import cv2
import glob
import os
from tqdm import tqdm
import shutil
import time

def walk_cases_folder(cases_folder):
    print("Path:", cases_folder)
    images_paths = sorted(glob.glob(os.path.join(cases_folder, "*.png")))
    frame_num = len(images_paths)
    fps = 5
    frame_array = []

    if frame_num > 5:
        print("frame_num", frame_num)
        dim = None

        print("Reading images ...")
        for i in tqdm(range(frame_num)):
            img = cv2.imread(images_paths[i])
            height, width, layers = img.shape
            dim = (width, height)
            frame_array.append(cv2.resize(img, dim, interpolation=cv2.INTER_AREA))

        # frame_array = frame_array*10
        time.sleep(0.01)
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        out = cv2.VideoWriter(os.path.join(cases_folder, "result.mp4"), fourcc, fps, dim, True)

        time.sleep(0.01)
        print("\nCreating video ...")
        for i in tqdm(range(len(frame_array))):
            out.write(frame_array[i])
        out.release()

        # for file in images_paths:
        #     os.remove(file)

        time.sleep(0.1)
    else:
        print("frame number ({}) too small, skip".format(frame_num))

def walk_experiment_folder(experiment_folder):
    for path in os.listdir(experiment_folder):
        path = os.path.join(experiment_folder, path)
        walk_cases_folder(path)

def walk_image_folder(image_folder):
    # # experiment = r"D:\Google Drive Insync\MA+code_yang\Code\CCGAN\Normal_GAN\images\12346789"
    # image_folder = r"D:\Google Drive Insync\MA+code_yang\Code\CCGAN\OCAE\images\10x10combis"

    for experiment in os.listdir(image_folder):
        experiment = os.path.join(image_folder, experiment)
        if os.path.isdir(experiment):
            walk_experiment_folder(experiment)

def crop_video(video_path):
    print(os.environ)
    print(os.environ["HOMEPATH"])
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')

    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        # get vcap property
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        rows = 924
        cols = 1445
        out = cv2.VideoWriter(r"D:\result.mp4", fourcc, fps, (cols, rows), True)

        while (True):
            ret, frame = cap.read()
            if frame is None:
                break
            # Our operations on the frame come here
            # temp = cv2.circle(frame, (1445, 924), 5, (255,0,0), 2)
            temp = frame[:rows, :cols, :]
            out.write(temp)
            # Display the resulting frame
            cv2.imshow('frame', temp)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        out.release()
        cap.release()
        cv2.destroyAllWindows()

    #

if __name__ == '__main__':
    walk_cases_folder(r"F:\recorded\0")
    # walk_experiment_folder(r"D:\Google Drive Insync\MA+code_yang\Code\CCGAN\OCAE_FMNIST\images\result2")
    # walk_image_folder(r"D:\Google Drive Insync\MA+code_yang\Code\CCGAN\OCAE_SVHN\images\result")
    # crop_video(r"D:\AKKA\example.mp4")