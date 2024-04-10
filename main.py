import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog, QMessageBox, QLabel
from mainwindow import Ui_MainWindow

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np


class run_window(Ui_MainWindow):
    def __init__(self, MainWindow):
        super().__init__()
        self.setupUi(MainWindow)
        self.initUI()

        self.grid_diagram_area_layout = self.grid_diagram_area.layout()
        self.grid_diagram_area.setLayout(self.grid_diagram_area_layout)

        self.obstacle = {}
        self.obstacle_x_names = {}
        self.obstacle_y_names = {}

    # 函数功能与组件绑定
    def initUI(self):
        QtCore.QTimer.singleShot(0, self.draw_grid_diagram)

        self.spin_size_x.valueChanged.connect(self.set_range)
        self.spin_size_x.valueChanged.connect(self.draw_grid_diagram)
        self.spin_size_y.valueChanged.connect(self.set_range)
        self.spin_size_y.valueChanged.connect(self.draw_grid_diagram)

        self.spin_start_x.valueChanged.connect(self.draw_grid_diagram)
        self.spin_start_y.valueChanged.connect(self.draw_grid_diagram)

        self.spin_end_x.valueChanged.connect(self.draw_grid_diagram)
        self.spin_end_y.valueChanged.connect(self.draw_grid_diagram)

        self.spin_obstacle_num.valueChanged.connect(self.set_obstacle)
        self.search_button.clicked.connect(self.get_export_path)
        self.start_button.clicked.connect(self.start_calculate)

    def set_range(self):
        self.spin_start_x.setMaximum(self.spin_size_x.value())
        self.spin_start_y.setMaximum(self.spin_size_y.value())
        self.spin_end_x.setMaximum(self.spin_size_x.value())
        self.spin_end_y.setMaximum(self.spin_size_y.value())

        for name, pos in self.obstacle_x_names.items():
            pos.setMaximum(self.spin_size_x.value())
        for name, pos in self.obstacle_y_names.items():
            pos.setMaximum(self.spin_size_y.value())

    def draw_grid_diagram(self):
        # 清空布局已有的子部件
        while self.grid_diagram_area_layout.count():
            item = self.grid_diagram_area_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

                # 创建一个Matplotlib图形的Qt部件
        fig = Figure()
        canvas = FigureCanvas(fig)

        # 将画布添加到布局
        self.grid_diagram_area_layout.addWidget(canvas)

        # 获取网格大小和起始、结束点
        grid_size_x = self.spin_size_x.value()
        grid_size_y = self.spin_size_y.value()
        start_x = self.spin_start_x.value()
        start_y = self.spin_start_y.value()
        end_x = self.spin_end_x.value()
        end_y = self.spin_end_y.value()

        grid = np.zeros((grid_size_y, grid_size_x), dtype=int)

        colors = ['white', 'green', 'red', 'black', 'yellow']
        cmap = matplotlib.colors.ListedColormap(colors)
        norm = matplotlib.colors.Normalize(vmin=0, vmax=4)

        if start_x == end_x and start_y == end_y:
            try:
                if 1 <= start_x <= grid_size_x and 1 <= start_y <= grid_size_y:
                    grid[start_y - 1, start_x - 1] = 4
                else:
                    print(f"Start and end point ({start_x}, {start_y}) out of grid bounds.")
            except IndexError:
                print(f"IndexError: Start and end point ({start_x}, {start_y}) index error.")
        else:
            # 尝试填充开始和结束位置的单元格
            try:
                if 1 <= start_x <= grid_size_x and 1 <= start_y <= grid_size_y:
                    grid[start_y - 1, start_x - 1] = 1
                else:
                    print(f"Start point ({start_x}, {start_y}) out of grid bounds.")
            except IndexError:
                print(f"IndexError: Start point ({start_x}, {start_y}) index error.")

            try:
                if 1 <= end_x <= grid_size_x and 1 <= end_y <= grid_size_y:
                    grid[end_y - 1, end_x - 1] = 2
                else:
                    print(f"End point ({end_x}, {end_y}) out of grid bounds.")
            except IndexError:
                print(f"IndexError: End point ({end_x}, {end_y}) index error.")

            for name, pos in self.obstacle.items():
                print(pos)
                try:
                    if 1 <= pos[0] <= grid_size_x and 1 <= pos[1] <= grid_size_y:
                        if pos != [start_x, start_y]:
                            if pos != [end_x, end_y]:
                                grid[pos[1]-1, pos[0]-1] = 3
                            else:
                                self.label_warnmsg.setText(name + "与终点重合")
                        else:
                            self.label_warnmsg.setText(name + "与起点重合")
                    else:
                        self.label_warnmsg.setText(name + "超出网格范围")
                        print(f"obstacle ({pos[0]-1}, {pos[1]-1}) out of grid bounds.")
                except IndexError:
                    print(f"IndexError: obstacle ({pos[0]-1}, {pos[1]-1}) index error.")

        # 绘制网格
        ax = fig.add_subplot(111)
        ax.imshow(grid, cmap=cmap, norm=norm, interpolation='nearest', origin='lower',extent=[0, grid_size_x, 0, grid_size_y])  # extent设置确保颜色正确填充

        # 设置坐标轴范围
        ax.set_xlim(0, grid_size_x)
        ax.set_ylim(0, grid_size_y)

        # 设置网格线
        ax.set_xticks(np.arange(0, grid_size_x, 1))  # 网格线位于单元格边界上
        ax.set_yticks(np.arange(0, grid_size_y, 1))  # 网格线位于单元格边界上
        ax.grid(which="both", color="gray", linestyle='-', linewidth=0.5)

        # 隐藏坐标轴刻度标签
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # 刷新画布显示图形
        canvas.draw()

    def set_obstacle(self, value):
        layout = self.obstacle_pos_area.layout()
        # 如果layout为None，则创建一个新的布局
        if layout is None:
            layout = QtWidgets.QVBoxLayout(self.obstacle_pos_area)
        self.obstacle_pos_area.setLayout(layout)

        # 清空布局中已有的子部件
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 初始化障碍物spinboxes的字典
        self.obstacle = {}

        for obstacle_serial in range(1, value + 1):
            obstacle_name = f"obstacle{obstacle_serial}"

            # 增加label
            label = QtWidgets.QLabel(self.obstacle_pos_area)
            label.setObjectName(f"label_{obstacle_name}")
            label.setText(f"障碍物{obstacle_serial}(X,Y)")
            layout.addWidget(label)

            # 增加spinbox x轴
            spinbox_x = QtWidgets.QSpinBox(self.obstacle_pos_area)
            spinbox_x.setObjectName(f"spin_{obstacle_name}_x")
            spinbox_x.setMinimum(1)
            spinbox_x.setMaximum(self.spin_size_x.value())  # grid size x
            spinbox_x.valueChanged.connect(
                lambda val, obs=obstacle_name, axis='x': self.update_obstacle(obs, axis, val))
            spinbox_x.valueChanged.connect(self.draw_grid_diagram)
            layout.addWidget(spinbox_x)
            self.obstacle_x_names[f"spin_{obstacle_name}_x"] = spinbox_x

            # 增加spinbox y轴
            spinbox_y = QtWidgets.QSpinBox(self.obstacle_pos_area)
            spinbox_y.setObjectName(f"spin_{obstacle_name}_y")
            spinbox_y.setMinimum(1)
            spinbox_y.setMaximum(self.spin_size_y.value())  # grid size y
            spinbox_y.valueChanged.connect(
                lambda val, obs=obstacle_name, axis='y': self.update_obstacle(obs, axis, val))
            spinbox_y.valueChanged.connect(self.draw_grid_diagram)
            layout.addWidget(spinbox_y)
            self.obstacle_y_names[f"spin_{obstacle_name}_y"] = spinbox_y


    def update_obstacle(self, obstacle_name, axis, value):
        # 检查障碍物是否已经在字典中
        if obstacle_name not in self.obstacle:
            # 如果不在，则初始化一个空列表
            self.obstacle[obstacle_name] = [1, 1]
            # 根据坐标轴更新对应的值
        self.obstacle[obstacle_name][{'x': 0, 'y': 1}[axis]] = value
        # print(f"障碍物 {obstacle_name} 的 {axis} 坐标更新为: {value}")
        # print(self.obstacle)

    def get_export_path(self):
        # 获取保存文件路径
        file_dialog = QFileDialog()

        # 设置对话框标题和默认目录
        file_dialog.setWindowTitle("选择文件夹")
        file_dialog.setDirectory("/path/to/default/directory")

        # 打开文件夹选择对话框并获取用户选择的文件夹路径
        folder_path = file_dialog.getExistingDirectory()
        self.lineedit_export_path.setText(folder_path)
        app.exec_()

    def start_calculate(self):
        # 判断文件读取、保存路径是否正常，传入参数进行计算
        if not self.lineedit_export_path.text():
            QMessageBox.information(mainWindow, "错误", "未选择路径文件存储地址", QMessageBox.Yes)
        else:
            QMessageBox.information(mainWindow, "成功", "提交成功，正在计算结果", QMessageBox.Yes)
            # 以下为需要传入的参数
            return self.check_priority_1, self.check_priority_2, self.check_priority_3, self.check_priority_4


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    form = run_window(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
