import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Window_R(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('График')
        self.setGeometry(400, 400, 500, 500)
        # создаем виджет для графика
        graph_widget = QWidget(self)
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(graph_widget)
        figure = Figure()
        canvas = FigureCanvas(figure)
        graph_layout.addWidget(canvas)
        axis = figure.add_subplot(111)
        axis.set_title('Прибыль')
        axis.set_xlabel('Время')
        axis.set_ylabel('Деньги')
        # подключаемся к базе данных SQL
        conn = sqlite3.connect('DataBase.db')
        cur = conn.cursor()

        # выполняем запрос к базе данных для получения данных для графика
        cur.execute("SELECT O_DataEnd, O_Prise FROM Orde WHERE O_state == 1;")
        data = cur.fetchall()

        # закрываем соединение с базой данных
        conn.close()

        # создаем списки для дат и значений
        dates = [row[0] for row in data]
        values = [row[1] for row in data]

        # создаем график
        axis.plot(dates, values, label="Mark", marker="o")
        axis.tick_params(axis='x', rotation=45)
        figure.tight_layout()
        canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window_R()
    icon = QIcon('icon.png')
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())
