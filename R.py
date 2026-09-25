import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLabel, QScrollArea)
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Window_R(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('График и аналитика')
        self.setGeometry(180, 80, 1150, 800)
        self.setMinimumSize(900, 620)
        tabs = QTabWidget(self)
        tabs.addTab(self._build_graph_tab(), 'Прибыль')
        tabs.addTab(self._build_analytics_tab(), 'Аналитика (ЛР4)')
        tabs.addTab(self._build_lab5_tab(), 'Сложные запросы (ЛР5)')
        tabs.addTab(self._build_lab6_tab(), 'Процедуры (ЛР6)')
        self.setCentralWidget(tabs)

    def _build_graph_tab(self):
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        figure = Figure()
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        axis = figure.add_subplot(111)
        axis.set_title('Прибыль')
        axis.set_xlabel('Время')
        axis.set_ylabel('Деньги')
        conn = sqlite3.connect('DataBase.db')
        cur = conn.cursor()
        cur.execute("SELECT O_DataEnd, O_Prise FROM Orde WHERE O_state == 1;")
        data = cur.fetchall()
        conn.close()
        dates = [row[0] for row in data]
        values = [row[1] for row in data]
        axis.plot(dates, values, label="Mark", marker="o")
        axis.tick_params(axis='x', rotation=45)
        figure.tight_layout()
        canvas.draw()
        return widget

    def _query_table(self, query):
        conn = sqlite3.connect('DataBase.db')
        cur = conn.cursor()
        cur.execute(query)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        conn.close()
        table = QTableWidget(len(rows), len(cols))
        table.setHorizontalHeaderLabels(cols)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(val)))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def _build_analytics_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel(
            'Задание 4.1. Максимальная и минимальная цена заказа (MIN, MAX c псевдонимами):'))
        layout.addWidget(self._query_table(
            "SELECT MIN(O_Prise) AS minimum, MAX(O_Prise) AS maximum FROM Orde"))
        layout.addWidget(QLabel(
            'Задание 4.2. Количество заказов по каждому статусу (COUNT + GROUP BY):'))
        layout.addWidget(self._query_table(
            "SELECT O_state, COUNT(*) AS kol_vo FROM Orde GROUP BY O_state"))
        layout.addWidget(QLabel('Уникальные значения (DISTINCT):'))
        layout.addWidget(self._query_table(
            "SELECT DISTINCT O_state FROM Orde"))
        layout.addWidget(QLabel('Сортировка по убыванию цены, первые 5 (ORDER BY + LIMIT):'))
        layout.addWidget(self._query_table(
            "SELECT O_Number, O_Num_C, O_NumCT, O_Num_W, O_Num_Ser, O_Prise "
            "FROM Orde ORDER BY O_Prise DESC LIMIT 5"))
        layout.addWidget(QLabel('Ограничение выборки, первые 5 заказов (LIMIT):'))
        layout.addWidget(self._query_table(
            "SELECT * FROM Orde LIMIT 5"))
        layout.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll

    def _build_lab5_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel(
            'Задание ЛР5.1. Многотабличный запрос (INNER JOIN трёх таблиц — '
            'клиент, заказ, сотрудник):'))
        layout.addWidget(self._query_table(
            "SELECT Client.C_Surname, Client.C_PhoneNumber, Orde.O_Number, "
            "Orde.O_Prise, Workers.W_Surname AS sotrudnik "
            "FROM Orde "
            "INNER JOIN Client ON Client.C_Surname = Orde.O_Num_C "
            "INNER JOIN Workers ON Workers.W_Surname = Orde.O_Num_W "
            "ORDER BY Orde.O_Prise DESC"))
        layout.addWidget(QLabel(
            'Задание ЛР5.2. Объединение с левой таблицей и подсчётом '
            '(LEFT JOIN + COUNT + GROUP BY):'))
        layout.addWidget(self._query_table(
            "SELECT Orde.O_Number, Orde.O_Num_C, COUNT(CT.CT_Number) AS kol_vo_tehniki "
            "FROM Orde LEFT JOIN CT ON CT.CT_Ordernumber = Orde.O_Number "
            "GROUP BY Orde.O_Number ORDER BY kol_vo_tehniki DESC"))
        layout.addWidget(QLabel(
            'Вложенный запрос 1 (скалярный): заказы дороже средней цены'))
        layout.addWidget(self._query_table(
            "SELECT O_Number, O_Num_C, O_Prise FROM Orde "
            "WHERE O_Prise > (SELECT AVG(O_Prise) FROM Orde)"))
        layout.addWidget(QLabel(
            'Вложенный запрос 2 (IN): клиенты с выполненными заказами'))
        layout.addWidget(self._query_table(
            "SELECT C_Number, C_Surname FROM Client "
            "WHERE C_Surname IN (SELECT O_Num_C FROM Orde WHERE O_state = '1')"))
        layout.addWidget(QLabel(
            'Вложенный запрос 3 (NOT EXISTS): услуги, которые не заказывались'))
        layout.addWidget(self._query_table(
            "SELECT S_Number, S_Name FROM Ser "
            "WHERE NOT EXISTS (SELECT 1 FROM Orde WHERE Orde.O_Num_Ser = Ser.S_Name)"))
        layout.addWidget(QLabel(
            'Вложенный запрос 4 (скалярный): самые дорогие заказы'))
        layout.addWidget(self._query_table(
            "SELECT O_Number, O_Num_C, O_Prise FROM Orde "
            "WHERE O_Prise = (SELECT MAX(O_Prise) FROM Orde)"))
        layout.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll

    def count_orders(self, surname):
        conn = sqlite3.connect('DataBase.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Orde WHERE O_Num_C = ?", (surname,))
        total = cur.fetchone()[0]
        conn.close()
        return total

    def total_price(self, surname):
        conn = sqlite3.connect('DataBase.db')
        cur = conn.cursor()
        cur.execute("SELECT SUM(O_Prise) FROM Orde WHERE O_Num_C = ?", (surname,))
        total = cur.fetchone()[0]
        conn.close()
        return total

    def copy_december(self):
        conn = sqlite3.connect('DataBase.db')
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS dekabr")
        cur.execute(
            "CREATE TABLE dekabr ("
            "O_Number INTEGER, O_Num_C TEXT, O_NumCT INTEGER, "
            "O_Num_W INTEGER, O_Num_Ser INTEGER, O_Prise INTEGER, "
            "O_DataEnd TEXT, O_state INTEGER)")
        cur.execute("SELECT * FROM Orde WHERE O_DataEnd LIKE '%.12.23'")
        for row in cur:
            conn.execute(
                "INSERT INTO dekabr VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                row)
        conn.commit()
        conn.close()

    def mark_expensive(self):
        conn = sqlite3.connect('DataBase.db')
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS dorogie")
        cur.execute(
            "CREATE TABLE dorogie ("
            "O_Number INTEGER, O_Num_C TEXT, O_Prise INTEGER)")
        cur.execute("SELECT O_Number, O_Num_C, O_Prise FROM Orde")
        for row in cur:
            if row[2] >= 3000:
                conn.execute(
                    "INSERT INTO dorogie VALUES (?, ?, ?)", row)
        conn.commit()
        conn.close()

    def _small_table(self, rows, cols):
        table = QTableWidget(len(rows), len(cols))
        table.setHorizontalHeaderLabels(cols)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(val)))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def _build_lab6_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(QLabel(
            'Процедура 1. Число заказов покупателя по фамилии '
            '(IN user_kod, OUT total):'
        ))
        layout.addWidget(self._small_table(
            [('Иванов', self.count_orders('Иванов'))],
            ['user_kod', 'total']))

        layout.addWidget(QLabel(
            'Процедура 2. Копирование заказов за декабрь 2023 г. '
            'в таблицу dekabr (с помощью курсора):'
        ))
        self.copy_december()
        layout.addWidget(self._query_table(
            "SELECT * FROM dekabr ORDER BY O_Number"))

        layout.addWidget(QLabel(
            'Процедура 3. Общая стоимость заказов покупателя '
            '(IN user_kod, OUT total_pr):'
        ))
        layout.addWidget(self._small_table(
            [('Иванов', self.total_price('Иванов'))],
            ['user_kod', 'total_pr']))

        layout.addWidget(QLabel(
            'Процедура 4. Отбор дорогих заказов (цена >= 3000) '
            'в таблицу dorogie (цикл по курсору + условие IF):'
        ))
        self.mark_expensive()
        layout.addWidget(self._query_table(
            "SELECT * FROM dorogie ORDER BY O_Number"))

        layout.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window_R()
    icon = QIcon('icon.png')
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())