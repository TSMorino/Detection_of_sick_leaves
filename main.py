import os
import time
from flask import render_template, request, Flask, redirect, url_for
from yolov5.detect import parse_opt, main

app = Flask(__name__)


# 首页
@app.route('/')
def index():
    return render_template('index.html')


# 结果展示界面
@app.route('/result', methods=['GET', 'POST'])
def result():
    global img_path_1, img_path_2
    # 替换为模型路径，这里只展示一个模型，可以根据需要添加更多模型路径
    models = [r'D:\Work\Comprehensive_Practice\yolov5\yolov5s_未优化.pt',
              r'D:\Work\Comprehensive_Practice\yolov5\yolov5s_优化.pt']

    result = []  # 存储每个模型的运行结果
    model_name = ['yolov5s_未优化', 'yolov5s_已优化']  # 替换为模型的名字，用于在结果界面展示
    num_lines = []  # 存储每个模型结果的行数
    line_num = []  # 存储每个模型结果中每行最后一个数的列表
    avg_num = []  # 存储每个模型结果的平均置信度值
    project = [r'./static/image/Not_optimized/', r'./static/image/Optimized/']
    save_folders = ['./static/image/Not_optimized/labels', './static/image/Optimized/labels']  # 替换为labels的存储路径

    file = request.files.get('file')

    if file:
        upload_folder = 'yolov5/data/images'

        # 判断是否存在目标文件夹，不存在则创建新文件夹
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # 删除文件夹中已有的全部文件
        for file_name in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, file_name)
            os.remove(file_path)

        # 保存上传的文件到指定位置
        file.filename = "result.jpg"
        file.save(os.path.join(upload_folder, file.filename))
    else:
        return redirect(url_for('index'))

    # 对每个模型进行遍历
    for i, (model, project, save_folder) in enumerate(zip(models, project, save_folders)):

        if request.method == 'POST':
            # 删除原本存在的结果文件
            save_folders = ['./static/image/Not_optimized/labels', './static/image/Optimized/labels']  # 替换为labels的存储路径

            # 判断是否存在目标文件夹，不存在则创建新文件夹
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            # 获取文件夹中的所有文件并删除
            for file_name in os.listdir(save_folder):
                file_path = os.path.join(save_folder, file_name)
                os.remove(file_path)

            opt = parse_opt()
            opt.weights = model
            opt.project = project
            print(opt)
            main(opt)

            file_path = f"{project}/labels/result.txt"  # 替换为实际的文件路径

            # 打开存有标签数据的文本文件
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    lines = file.readlines()  # 读取所有行，按行添加值到lines列表中
            else:
                lines = []  # 文件不存在，将lines设置为空列表

            num_lines.append(len(lines))  # 获取行数

            # 判断结果是否为空
            if num_lines[i] != 0:
                result.append("存在病残叶")
            else:
                result.append("不存在病残叶")

            line_nums = []  # 存储每行最后一个数的列表

            for line in lines:
                values = line.strip().split()  # 去除换行符并按空格分隔每个值
                last_num = float(values[-1])  # 获取最后一个数，并转换为浮点型
                line_nums.append(last_num)

            line_num.append(line_nums)
            avg_num.append("{:.4f}".format(sum(line_nums) / num_lines[i]) if num_lines[i] != 0 else "-")  # 计算平均值并保留四位小数

            img_path_1 = "../static/image/Not_optimized/result.jpg"
            img_path_2 = "../static/image/Optimized/result.jpg"


    return render_template('upload.html', img_path_1=img_path_1, img_path_2=img_path_2,
                           variables=zip(model_name, result, num_lines, avg_num))


if __name__ == '__main__':
    app.run(debug=True, port=7249)
