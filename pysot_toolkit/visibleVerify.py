import os
import cv2
import numpy as np

# 指定图片路径
video_name = '0000000058_0000000000_1_629-681'
video_folder_parts = video_name.split('_')
video_begin_num = video_folder_parts[3].split('-')[0]
video_end_num = video_folder_parts[3].split('-')[1].split('.')[0]
video_folder_name = video_folder_parts[0] + '_' + video_folder_parts[1]
video_path = os.path.join('/media/cs303-2/DATA/hza/data/BirdSAI/conservation_drones_test_real/TestReal/images/', video_folder_name)
result_label_path = os.path.join('/tmp/pycharm_project_328/pysot_toolkit/results/BirdSAI/HCAT', video_name + '.txt')
groundtruth_path = os.path.join('/media/cs303-2/DATA/hza/data/BirdSAI/conservation_drones_test_real/TestReal/annotations/tracking/data_split_perfect_test', video_name,  'groundtruth_rect.txt')

def get_label_list(path):
    with open(path, 'r') as f:
        lines = [list(map(lambda x: int(float(x)), line.strip().split(','))) for line in f.readlines()]
    return lines



groundtruth_list = get_label_list(groundtruth_path)
result_label_list = get_label_list(result_label_path)

# 获取路径下的所有文件
current_image_num = 0
# 遍历所有图片
for i in range(int(video_begin_num), int(video_end_num) + 1):
    image_file_name = video_folder_name + '_{:010d}.jpg'.format(i)
    image_file_path = os.path.join(video_path, image_file_name)
    if os.path.exists(image_file_path):

        # 读取图片
        img = cv2.imread(image_file_path)

        # 假设你有一个名为get_groundtruth的函数，它可以返回groundtruth的坐标
        # 这个函数的返回值应该是一个包含四个元素的列表，分别是[x, y, width, height]
        groundtruth = groundtruth_list[current_image_num]
        result_label = result_label_list[current_image_num]
        current_image_num += 1
        # 画出groundtruth的范围
        cv2.rectangle(img, (groundtruth[0], groundtruth[1]),
                      (groundtruth[0] + groundtruth[2], groundtruth[1] + groundtruth[3]),
                      (0, 255, 0), 2)
        cv2.rectangle(img, (result_label[0], result_label[1]),
                      (result_label[0] + result_label[2], result_label[1] + result_label[3]),
                      (0, 0, 255), 2)
        # 显示图片
        cv2.imshow('Image', img)
        cv2.waitKey(0)

