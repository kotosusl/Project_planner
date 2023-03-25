import sys
import os
import datetime
import sqlite3
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QTableView, QPushButton, QLabel, QInputDialog
from PyQt5.QtWidgets import QTabWidget, QHBoxLayout, QGridLayout, QGroupBox, QVBoxLayout, QDateEdit, QFormLayout
from PyQt5.QtWidgets import QCalendarWidget, QTextEdit, QScrollArea, QComboBox, QCheckBox, QSpinBox, QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

# Условия на запуск программы на мониторах с высоким и обычным разрешением
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


# Самое первое диалоговое окно для выбора режима работы программы
class Choice_Of_Actions(QMainWindow):
    def __init__(self):
        super(Choice_Of_Actions, self).__init__()
        action, ok_pressed = QInputDialog.getItem(
            self, 'Выберете действие', 'Какие действия вы хотите совершить?',
            ('Изменить данные', 'Оценить проекты'), 0, False)
        if ok_pressed:
            if action == 'Изменить данные':
                action_change()  # Вход в режим изменения
            else:
                action_check()  # Вход в режим проверки
            self.close()
        else:
            self.close()
            exit()  # Выход из программы


def action_change():
    app = QApplication(sys.argv)
    change = Change()  # Запуск окна с режимом изменения
    change.show()
    change.showMaximized()  # Растягивание окна на весь экран
    sys.exit(app.exec_())


def action_check():
    app = QApplication(sys.argv)
    check = Check()  # Запуск окна с режимом проверки
    check.show()
    check.showMaximized()  # Растягивание окна на весь экран
    sys.exit(app.exec_())


class Change(QMainWindow, QWidget):  # Режим изменений
    def __init__(self):
        super(Change, self).__init__()
        self.initUI()

    def initUI(self):
        # Минимальный размер окна и заголовок
        self.setMinimumSize(600, 600)
        self.setWindowTitle('Database change')

        # Создание вкладок
        self.tabs = QTabWidget(self)
        self.tab_main = QWidget(self)
        self.tab2 = QWidget(self)
        self.tabs.addTab(self.tab_main, 'Проекты')
        self.tabs.addTab(self.tab2, 'Темы')

        # Изменение размера шрифта на 11
        font = QtGui.QFont()
        font.setPointSize(11)
        self.tabs.setFont(font)

        # Редактирование содержимого вкладки "Главная"
        self.tab_main_layout = QGridLayout()
        self.tab_main.setLayout(self.tab_main_layout)

        # Адаптация окна
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tabs)
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        # Подключение базы данных
        if os.path.isfile('Data_project_YL_MAIN.db'):
            self.db = QSqlDatabase.addDatabase('QSQLITE')
            self.db.setDatabaseName('Data_project_YL_MAIN.db')
        else:
            # Вывод окна ошибки
            app = QApplication(sys.argv)
            bad_exit = DatabaseNotFound()
            bad_exit.show()
            sys.exit(app.exec_())

        # Установка таблицы проектов
        self.project_model = QSqlTableModel(self)
        self.project_model.select()

        sqlquery = QSqlQuery('''SELECT project.id as "Номер", project.Date as "Дата",
                 project.Link as "Ссылка", 
                 project.Name as "Название", theme.theme as "Тема" FROM Project
                 inner join theme on project.id_theme = theme.id''', self.db)
        self.project_model.setQuery(sqlquery)

        # Отображение таблицы проектов
        self.project_view = QTableView(self)
        self.project_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.project_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.project_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.project_view.setModel(self.project_model)
        self.project_view.resize(300, 300)
        self.tab_main_layout.addWidget(self.project_view, 0, 0)

        # Создание области функций таблицы проектов

        self.project_function_tabs = FunctionTabs('project', self.db, self.project_model, self.project_view, None, None,
                                                  True, True, True, False,
                                                  *[True, True, False, True])
        self.tab_main_layout.addWidget(self.project_function_tabs.get_object(), 0, 1)

        # Вкладка тем
        self.tab2_layout = QGridLayout()
        self.theme_model = QSqlTableModel(self)
        self.theme_model.select()
        # Установка таблицы тем
        sqlquery = QSqlQuery('''SELECT theme.id as "Номер", theme.theme as "Тема",
                                         theme.date as "Срок",
                                         teachers.lastname as "Учитель", 
                                         subject.subject as "Предмет" FROM Theme
                                         inner join teachers on teachers.id = theme.id_teacher
                                         inner join subject on subject.id = theme.id_subject''', self.db)
        self.theme_model.setQuery(sqlquery)
        # Отображение таблицы тем
        self.theme_view = QTableView(self)
        self.theme_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.theme_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.theme_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.theme_view.setModel(self.theme_model)
        self.tab2_layout.addWidget(self.theme_view, 0, 0)
        # Создание области функций таблицы тем
        self.theme_function_tabs = FunctionTabs('theme', self.db, self.theme_model, self.theme_view, None, None, True,
                                                True, False, False,
                                                *[True, False, True, True])
        self.tab2_layout.addWidget(self.theme_function_tabs.get_object(), 0, 1)
        self.tab2.setLayout(self.tab2_layout)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:  # Закрытие окна
        self.db.close()
        self.project_model.clear()
        self.theme_model.clear()
        app.quit()
        self.close()

    def keyPressEvent(self, event):  # Закрытие окна по нажатию escape
        if event.key() == Qt.Key_Escape:
            self.close()


class SortedTab(QWidget):  # Определение вкладки сортировки
    def __init__(self, type, db, model, *args):
        super(SortedTab, self).__init__()
        # Установка интерфейса области сортировки
        self.students_list = []
        self.teacher_list = []
        self.db = db
        self.type = type
        self.table_model = model
        self.args = args
        self.main_sorted_layout = QVBoxLayout()
        self.scroll_area_sort = QScrollArea(self)
        self.scroll_area_sort.setMaximumWidth(420)
        self.scroll_area_sort.setMinimumWidth(420)
        self.scroll_area_sort.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_sort.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_sort.setWidgetResizable(True)
        self.main_sorted_widget = QWidget()
        self.main_sorted_widget.setLayout(self.main_sorted_layout)
        self.scroll_area_sort.setWidget(self.main_sorted_widget)

        # Определение нужных параметров сортировки
        if self.args[0]:
            self.main_sorted_layout.addWidget(self.init_date_group())
        if self.args[1]:
            self.main_sorted_layout.addWidget(self.init_students_group())
        if self.args[2]:
            self.main_sorted_layout.addWidget(self.init_teachers_group())
        if self.args[3]:
            self.main_sorted_layout.addWidget(self.init_theme_group())

    def init_date_group(self):  # Определение сортировки по дате сдачи
        self.date_group = QGroupBox('Дата сдачи')
        self.date_group.setMaximumSize(400, 300)
        self.date_group.setMinimumSize(400, 300)
        self.date_group_layout = QVBoxLayout()
        self.calendar = QCalendarWidget(self)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setMaximumDate(datetime.datetime.now().date())
        self.select_date = QDateEdit(self)
        self.select_date.setMaximumDate(datetime.datetime.now().date())
        self.select_date.setButtonSymbols(2)
        self.select_date.setDate(datetime.datetime.now().date())

        self.date_group.setLayout(self.date_group_layout)
        self.all_time = QCheckBox('За всё время', self)
        self.all_time.setCheckState(2)
        self.sorted_time = QPushButton('Применить', self)
        self.date_group_layout.addWidget(self.calendar)
        self.date_group_layout.addWidget(self.select_date)
        self.date_group_layout.addWidget(self.all_time)
        self.date_group_layout.addWidget(self.sorted_time)
        self.calendar.clicked['QDate'].connect(self.show_date_text)
        self.sorted_time.clicked.connect(self.set_table)
        return self.date_group

    def show_date_text(self):  # Связь даты в окне ввода и календаря
        date = self.calendar.selectedDate()
        self.select_date.setDate(date.toPyDate())

    def init_students_group(self):  # Определение сортировки по ученикам
        self.student_group = QGroupBox('Ученик')
        self.student_group.setMaximumSize(400, 260)
        self.student_group.setMinimumSize(400, 260)
        self.student_group_layout = QFormLayout()
        self.student_lastname_label = QLabel('Фамилия: ', self)
        self.student_lastname = QTextEdit('', self)
        self.student_name_label = QLabel('Имя: ', self)
        self.student_name = QTextEdit('', self)
        self.student_patronymic_label = QLabel('Отчество: ', self)
        self.student_patronymic = QTextEdit('', self)
        self.student_school_class_label = QLabel('Класс: ', self)
        self.student_school_class = QSpinBox(self)
        self.student_school_class.setMaximum(11)
        self.student_school_class.setMinimum(1)
        self.all_classes = QCheckBox('Все классы', self)
        self.all_classes.setCheckState(2)
        self.student_school_class.setDisabled(1)
        self.student_class_letter_label = QLabel('Буква класса: ', self)
        self.student_class_letter = QTextEdit('', self)
        self.sorted_students = QPushButton('Применить', self)
        self.students_list = [self.student_lastname, self.student_name, self.student_patronymic,
                              self.student_school_class, self.student_class_letter]
        for i in self.students_list:
            i.setMaximumHeight(32)
        self.student_group_layout.addRow(self.student_lastname_label, self.student_lastname)
        self.student_group_layout.addRow(self.student_name_label, self.student_name)
        self.student_group_layout.addRow(self.student_patronymic_label, self.student_patronymic)
        self.student_group_layout.addRow(self.student_school_class_label, self.student_school_class)
        self.student_group_layout.addRow(self.all_classes)
        self.student_group_layout.addRow(self.student_class_letter_label, self.student_class_letter)
        self.student_group_layout.addRow(self.sorted_students)
        self.student_group.setLayout(self.student_group_layout)
        self.sorted_students.clicked.connect(self.set_table)
        self.all_classes.clicked.connect(self.all_classes_click)
        return self.student_group

    def all_classes_click(self):  # Выбор сортировки по классам за всё время и обратно
        if self.all_classes.checkState() == 2:
            self.student_school_class.setDisabled(1)
        else:
            self.student_school_class.setDisabled(0)

    def init_teachers_group(self):  # Определение сортировки по учителям
        self.teacher_group = QGroupBox('Учитель')
        self.teacher_group_layout = QFormLayout()
        self.teacher_lastname_label = QLabel('Фамилия: ', self)
        self.teacher_lastname = QTextEdit('', self)
        self.teacher_name_label = QLabel('Имя: ', self)
        self.teacher_name = QTextEdit('', self)
        self.teacher_patronymic_label = QLabel('Отчество: ', self)
        self.teacher_patronymic = QTextEdit('', self)
        self.sorted_teachers = QPushButton('Применить', self)
        self.teacher_list = [self.teacher_lastname, self.teacher_name, self.teacher_patronymic]
        for i in self.teacher_list:
            i.setMaximumHeight(32)
        self.teacher_group_layout.addRow(self.teacher_lastname_label, self.teacher_lastname)
        self.teacher_group_layout.addRow(self.teacher_name_label, self.teacher_name)
        self.teacher_group_layout.addRow(self.teacher_patronymic_label, self.teacher_patronymic)
        self.teacher_group_layout.addRow(self.sorted_teachers)
        self.teacher_group.setLayout(self.teacher_group_layout)
        self.sorted_teachers.clicked.connect(self.set_table)
        return self.teacher_group

    def init_theme_group(self):  # Определение сортировки по темам
        self.theme_group = QGroupBox('Тема', self)
        self.theme_group_layout = QFormLayout()
        self.theme_name_label = QLabel('Тема: ')
        self.theme_name = QTextEdit('', self)
        self.theme_subject_label = QLabel('Предмет: ')
        self.theme_subject = QTextEdit('', self)
        for i in [self.theme_subject, self.theme_name]:
            i.setMaximumHeight(32)
        self.theme_group_layout.addRow(self.theme_name_label, self.theme_name)
        self.theme_group_layout.addRow(self.theme_subject_label, self.theme_subject)
        self.sorted_themes = QPushButton('Применить', self)
        self.theme_group.setLayout(self.theme_group_layout)
        self.theme_group_layout.addRow(self.sorted_themes)
        self.sorted_themes.clicked.connect(self.set_table)
        return self.theme_group

    def set_table(self):  # Генерирование отсортированной таблицы
        if self.type == 'project':
            sql = ['''SELECT project.id as "Номер", project.Date as "Дата",
                     project.Link as "Ссылка", 
                     project.Name as "Название", theme.theme as "Тема" FROM Project
                     inner join theme on project.id_theme = theme.id''']
        if self.type == 'theme':
            sql = ['''SELECT theme.id as "Номер", theme.theme as "Тема",
                                         theme.date as "Срок",
                                         teachers.lastname as "Учитель", 
                                         subject.subject as "Предмет" FROM Theme
                                         inner join subject on subject.id = theme.id_subject
                                         inner join teachers on teachers.id = theme.id_teacher''']
        # Сортировка по учителям
        if self.args[2]:
            append_sql = f''' and theme.id_teacher = (select teachers.id from teachers'''
            flag = False
            if any([p.toPlainText() for i, p in
                    enumerate([self.teacher_lastname, self.teacher_name, self.teacher_patronymic])]):
                sql_object_list = ['teachers.Lastname', 'teachers.Name', 'teachers.Patronymic']
                for i, name in enumerate([self.teacher_lastname, self.teacher_name, self.teacher_patronymic]):
                    if name.toPlainText():
                        if flag:
                            append_sql += f' AND {sql_object_list[i]} = "{name.toPlainText()}"'
                        else:
                            append_sql += f' WHERE {sql_object_list[i]} = "{name.toPlainText()}"'
                            flag = True
                append_sql += ')'
                sql.append(append_sql)

        if self.args[1]:
            append_sql = '''INNER JOIN student_project ON project.id = student_project.id_project 
            INNER JOIN student ON student_project.id_student = (select student.id'''
            flag = False
            # Сортировка по ученикам
            if any([p.toPlainText() for i, p in enumerate(self.students_list) if i != 3] +
                   [self.all_classes.checkState() == 0]):
                sql_object_list = ['student.Lastname', 'student.Name', 'student.Patronymic',
                                   'student.Class', 'student.Letter']
                for i, name in enumerate(self.students_list):
                    if i == 3:
                        if self.all_classes.checkState() == 0:
                            if flag:
                                append_sql += f' AND {sql_object_list[i]} = "{name.text()}"'
                            else:
                                append_sql += f' WHERE {sql_object_list[i]} = "{name.text()}"'
                                flag = True
                        continue
                    if name.toPlainText():
                        if flag:
                            append_sql += f' AND {sql_object_list[i]} = "{name.toPlainText()}"'
                        else:
                            append_sql += f' WHERE {sql_object_list[i]} = "{name.toPlainText()}"'
                            flag = True
                append_sql += ')'
                sql.append(append_sql)
        # Сортировка по теме
        if self.args[3]:
            if self.theme_subject.toPlainText():
                if self.type == 'project':
                    sql.insert(1, f''' and project.id_theme = 
                    (select theme.id where theme.id_subject = 
                    (select subject.id from Subject where subject.Subject = "{self.theme_subject.toPlainText()}"))''')
                elif self.type == 'theme':
                    sql.append(f''' where theme.id_subject = (select subject.id from subject 
                    where subject.subject = "{self.theme_subject.toPlainText()}")''')

            if self.theme_name.toPlainText():
                if self.type == 'project':
                    sql.insert(1, f''' and project.id_theme =
                     (select theme.id where theme.Theme = "{self.theme_name.toPlainText()}")''')
                elif self.type == 'theme':
                    sql.append(f' Where theme.theme == "{self.theme_name.toPlainText()}"')

            # Сортировка по предмету

        if self.args[0] and (self.args[3] and self.type == 'theme'):
            if self.all_time.checkState() == 0:
                sql.append(f' and {self.type}.Date = "{self.select_date.text()}"')
        elif self.args[0]:
            if self.all_time.checkState() == 0:
                sql.append(f' where {self.type}.Date = "{self.select_date.text()}"')

        sql.append(f' order by {self.type}.id')
        # Установка таблицы
        self.update_table = QSqlQuery('\n'.join(sql), self.db)
        self.table_model.setQuery(self.update_table)

    # Возврат объекта
    def get_object(self):
        return self.scroll_area_sort


class FunctionTabs(QWidget):  # Определение вкладок функций
    def __init__(self, f_type, db, model, table_view, presentation_tab, presentation_table, f_add, f_delete, f_reset,
                 f_check, *args):
        super(FunctionTabs, self).__init__()
        # Установка интерфейса вкладок функций
        self.table_model = model
        self.db = db
        self.type = f_type
        self.table_view = table_view
        self.presentation_tab = presentation_tab
        self.presentation_table = presentation_table
        self.connection = sqlite3.connect('Data_project_YL_MAIN.db')
        self.cursor = self.connection.cursor()
        self.functions = QTabWidget(self)
        self.functions.setMaximumWidth(445)
        self.functions.setMinimumWidth(445)

        # Установка вкладки поиска
        if self.type != 'presentation':
            self.f_find = QWidget(self)
            self.functions.addTab(self.f_find, 'Поиск')
            self.f_find_layout = QVBoxLayout()
            self.sotrted_tab = SortedTab(self.type, self.db, self.table_model, *args)
            self.f_find_layout.addWidget(self.sotrted_tab.get_object())
            self.f_find.setLayout(self.f_find_layout)
        # Установка определенных вкладок в зависимости от заданных параметров
        if f_add:
            self.functions.addTab(self.init_f_add(), 'Добавить')
        if f_delete:
            self.functions.addTab(self.init_f_delete(), 'Удалить')
        if f_reset:
            self.functions.addTab(self.init_f_reset(), 'Изменить')
        if f_check:
            self.functions.addTab(self.init_f_check(), 'Оценить')

    def init_f_add(self):  # Создание и установка вкладки добавления
        self.link = ''
        self.f_add_layout = QVBoxLayout()
        self.error_label_add = QLabel('', self)
        self.error_label_add.setMaximumHeight(35)
        self.f_add_layout.addWidget(self.error_label_add)
        # Если функция работает с таблицей проектов
        if self.type == 'project':
            # Определение интерфейса вкладки добавления для таблиц проектов
            self.add_name_group = QGroupBox('Основное')
            self.name_label = QLabel('Название:', self)
            self.name = QTextEdit('', self)
            self.name.setMaximumHeight(32)
            self.input_link = QPushButton('Закрузить проект', self)
            self.input_link.clicked.connect(self.open_dialog_project)
            self.check_input_link = QCheckBox('Проект', self)
            self.check_input_link.setDisabled(1)
            self.add_name_group_layout = QFormLayout()
            self.add_name_group_layout.addRow(self.name_label, self.name)
            self.add_name_group_layout.addRow(self.input_link, self.check_input_link)
            self.add_name_group.setLayout(self.add_name_group_layout)
            self.add_theme_group = QGroupBox('Тема', self)
            self.theme_label = QLabel('Выберите тему:', self)
            self.theme = QComboBox()
            self.connection = sqlite3.connect('Data_project_YL_MAIN.db')
            self.cursor = self.connection.cursor()
            self.theme.addItem('')
            self.theme.addItems(
                [p[0] for p in self.cursor.execute('select Theme from Theme order by Theme').fetchall()])
            self.add_theme_group_layout = QFormLayout()
            self.add_theme_group_layout.addRow(self.theme_label, self.theme)
            self.add_theme_group.setLayout(self.add_theme_group_layout)
            self.add_project_students_group = QGroupBox('Авторы')
            self.add_project_students_layout = QVBoxLayout()
            self.add_students_list = QTextEdit('', self)
            self.add_students_list.setDisabled(1)
            self.add_student_in_project = QPushButton('Добавить ученика', self)
            self.delete_students_in_project = QPushButton('Очистить', self)

            self.delete_students_in_project.clicked.connect(self.delete_students)
            self.add_student_in_project.clicked.connect(self.open_dialog_student)
            self.add_project_students_group.setLayout(self.add_project_students_layout)
            self.add_project_students_layout.addWidget(self.add_students_list)
            self.add_project_students_layout.addWidget(self.add_student_in_project)
            self.add_project_students_layout.addWidget(self.delete_students_in_project)

            self.f_add_layout.addWidget(self.add_name_group)
            self.f_add_layout.addWidget(self.add_theme_group)
            self.f_add_layout.addWidget(self.add_project_students_group)
            self.add_the_project_btn = QPushButton('Добавить проект', self)
            self.add_the_project_btn.setMinimumHeight(70)
            self.add_the_project_btn.clicked.connect(self.add_the_project)
            self.f_add_layout.addWidget(self.add_the_project_btn)

        # Если функция работает с таблицей презентаций
        elif self.type == 'presentation':
            # Определение интерфейса вкладки добавления для таблицы презентаций
            self.presentation_project_group = QGroupBox('Оценить проект с номером', self)
            self.presentation_project_group.setMaximumHeight(70)
            self.presentation_project_group_layout = QVBoxLayout()
            self.presentation_project_group.setLayout(self.presentation_project_group_layout)
            self.id_presentation = QTextEdit('', self)
            self.id_presentation.setMaximumHeight(32)
            self.presentation_project_group_layout.addWidget(self.id_presentation)
            self.presentation_add_group = QGroupBox('Данные', self)
            self.presentation_add_group.setMaximumHeight(200)
            self.presentation_add_group_layout = QFormLayout()
            self.presentation_add_group.setLayout(self.presentation_add_group_layout)
            self.score = QSpinBox()
            self.score_label = QLabel('Балл:', self)
            self.presentation_label = QLabel('Защита', self)
            self.presentation = QComboBox()
            self.presentation.addItems(['Да', 'Нет'])
            self.pres_teacher = QTextEdit('', self)
            self.pres_teacher.setMaximumHeight(33)
            self.pres_teacher.setDisabled(1)
            self.pres_teacher_label = QLabel('Проверяющий учитель:')
            self.add_presentation_teacher = QPushButton('Добавить учителя')
            self.presentation_add_group_layout.addRow(self.presentation_label, self.presentation)
            self.presentation_add_group_layout.addRow(self.score_label, self.score)
            self.presentation_add_group_layout.addRow(self.pres_teacher_label)
            self.presentation_add_group_layout.addRow(self.pres_teacher)
            self.presentation_add_group_layout.addRow(self.add_presentation_teacher)
            self.f_add_layout.addWidget(self.presentation_project_group)
            self.f_add_layout.addWidget(self.presentation_add_group)
            self.add_presentation_teacher.clicked.connect(self.open_dialog_teacher)
            self.add_presentation = QPushButton('Добавить оценку', self)
            self.f_add_layout.addWidget(self.add_presentation)
            self.add_presentation.clicked.connect(self.add_the_presentation)

        # Если функция работает с таблицей тем
        elif self.type == 'theme':
            # Определение интерфейса вкладки добавления для таблицы тем
            self.add_theme = QGroupBox('Тема')
            self.add_theme.setMaximumHeight(450)
            self.add_theme_layout = QFormLayout()
            self.add_theme.setLayout(self.add_theme_layout)
            self.name_theme_label = QLabel('Название темы:', self)
            self.name_theme = QTextEdit('', self)
            self.name_theme.setMaximumHeight(32)
            self.deadline_label = QLabel('Срок сдачи:', self)
            self.calendar = QCalendarWidget(self)
            self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
            self.calendar.setMinimumDate(datetime.datetime.now().date() + datetime.timedelta(days=1))
            self.deadline_date = QDateEdit(self)
            self.deadline_date.setButtonSymbols(2)
            self.deadline_date.setDate(datetime.datetime.now().date() + datetime.timedelta(days=1))
            self.deadline_date.setMinimumDate(datetime.datetime.now().date() + datetime.timedelta(days=1))
            self.calendar.clicked['QDate'].connect(self.show_date_text)
            self.add_theme_teacher = QTextEdit('', self)
            self.add_theme_teacher.setMaximumHeight(33)
            self.add_theme_teacher.setDisabled(1)
            self.add_theme_teacher_label = QLabel('Учитель, добавляющий тему:')
            self.add_theme_teacher_button = QPushButton('Добавить учителя')
            self.add_theme_layout.addRow(self.name_theme_label, self.name_theme)
            self.add_theme_layout.addRow(self.deadline_label)
            self.add_theme_layout.addRow(self.calendar)
            self.add_theme_layout.addRow(self.deadline_date)
            self.add_theme_layout.addRow(self.add_theme_teacher_label)
            self.add_theme_layout.addRow(self.add_theme_teacher)
            self.add_theme_layout.addRow(self.add_theme_teacher_button)
            self.add_theme_teacher_button.clicked.connect(self.open_dialog_teacher_add_theme)
            self.adding = QPushButton('Добавить тему', self)
            self.adding.setMinimumHeight(70)
            self.adding.clicked.connect(self.add_the_theme)
            self.add_theme_layout.addRow(self.adding)
            self.f_add_layout.addWidget(self.add_theme)

        self.add_scroll_area = QScrollArea(self)
        self.add_scroll_area.setLayout(self.f_add_layout)
        return self.add_scroll_area

    def add_the_theme(self):  # Добавление темы
        # Проверка корректности ввода
        if self.name_theme.toPlainText() and self.deadline_date.text() and self.add_theme_teacher.toPlainText():
            if self.name_theme.toPlainText() in self.cursor.execute('select theme.theme from theme'):
                self.error_label_add.setText('!Тема с таким названием уже существует!')
            else:  # Добавление темы в базу данных
                self.error_label_add.setText('')
                sql = f'''insert into theme(theme, date, id_teacher, id_subject) 
                values("{self.name_theme.toPlainText()}", "{self.deadline_date.text()}", 
                (select teachers.id from teachers 
                where teachers.lastname = "{self.add_theme_teacher.toPlainText().split()[0]}" 
                and teachers.name = "{self.add_theme_teacher.toPlainText().split()[1]}"
                and teachers.patronymic = "{self.add_theme_teacher.toPlainText().split()[2]}"), 
                (select subject_teacher.id_subject from subject_teacher 
                where subject_teacher.id_teacher in (select teachers.id from teachers where
                teachers.lastname = "{self.add_theme_teacher.toPlainText().split()[0]}" 
                and teachers.name = "{self.add_theme_teacher.toPlainText().split()[1]}"
                and teachers.patronymic = "{self.add_theme_teacher.toPlainText().split()[2]}")))'''
                self.update_table = QSqlQuery()
                self.update_table.exec(sql)
                self.set_update_table()
        else:  # Вывод ошибки
            self.error_label_add.setText('!Некорректное заполнение полей!')

    def open_dialog_teacher_add_theme(self):  # Выбор учителя
        list_teachers = self.cursor.execute(
            'select lastname, name, patronymic from teachers order by lastname, name').fetchall()
        self.add_theme_teacher_dialog, ok_press = QInputDialog.getItem(self, 'Выберете учителя', 'Кто задёт тему?',
                                                                       tuple([f'{p[0]} {p[1]} {p[2]}' for p in
                                                                              list_teachers]),
                                                                       0, False)
        if ok_press:
            self.add_theme_teacher.setText(self.add_theme_teacher_dialog)

    def show_date_text(self):  # Связь даты в окошке и календаря
        date = self.calendar.selectedDate()
        self.deadline_date.setDate(date.toPyDate())

    def add_the_presentation(self):  # Добавление оценки в базу данных
        # Проверка на корректность введённых данных
        if self.pres_teacher.toPlainText() and self.id_presentation.toPlainText().isdigit():
            if int(self.id_presentation.toPlainText()) in [p[0] for p in self.cursor.execute(
                    'select project.id from project').fetchall()]:
                # Добавление оценки в таблицу презентаций
                lastname, name, patronymic = self.pres_teacher.toPlainText().split()
                sql = f'''insert into presentation(presentation, score, id_teacher, id_project) 
                          values("{self.presentation.currentText()}", {int(self.score.text())}, 
                          (select teachers.id from teachers where teachers.name = "{name}"
                          and teachers.lastname = "{lastname}"
                          and teachers.patronymic = "{patronymic}"), {int(self.id_presentation.toPlainText())})'''
                self.update_table = QSqlQuery()
                self.update_table.exec(sql)
                self.error_label_add.setText('Запись успешно добавлена')
            else:  # Выводы ошибок
                self.error_label_add.setText('!Несуществующий номер проекта!')
        else:
            self.error_label_add.setText('!Некорректное заполнение полей!')

    def open_dialog_teacher(self):  # Выбор учителя
        list_teachers = self.cursor.execute(
            'select lastname, name, patronymic from teachers order by lastname, name').fetchall()
        self.presentation_teacher, ok_press = QInputDialog.getItem(self, 'Выберете проверяющего',
                                                                   'Кто оценивал проект?',
                                                                   tuple([f'{p[0]} {p[1]} {p[2]}' for p in
                                                                          list_teachers]),
                                                                   0, False)
        if ok_press:
            self.pres_teacher.setText(self.presentation_teacher)

    def open_dialog_project(self):  # Определение ссылки на проект
        self.link, ok_press = QFileDialog.getOpenFileName(self, 'Выберите проект', '', 'Все файлы (*)')
        if ok_press:
            self.check_input_link.setCheckState(2)
            self.check_input_link.setText('Проект ' + self.link.split('/')[-1])

    def open_dialog_student(self):  # Добавление авторов проекта
        list_students = self.cursor.execute(
            'select lastname, name, patronymic, class, letter from student order by class, letter, lastname').fetchall()
        self.add_student, ok_press = QInputDialog.getItem(self, 'Выберете автора', 'Кто работал над проектом?',
                                                          tuple([f'{p[0]} {p[1]} {p[2]} {p[3]}{p[4]}' for p in
                                                                 list_students]),
                                                          0, False)
        if ok_press:
            self.add_students_list.setText(self.add_students_list.toPlainText() + self.add_student + '\n')

    def delete_students(self):  # Очистка из списка авторов
        self.add_students_list.setText('')

    def add_the_project(self):  # Добавление проекта в таблицу проектов
        # Проверка на корректные введённые данные
        if self.name.toPlainText() and self.link and self.add_students_list.toPlainText() and self.theme.currentText():
            if self.name.toPlainText() in [p[0] for p in
                                           self.cursor.execute('select project.name from project').fetchall()]:
                self.error_label_add.setText('!Проект с таким названием уже существует!')
            elif self.link in [p[0] for p in self.cursor.execute('select project.link from project').fetchall()]:
                self.error_label_add.setText('!Этот проект уже добавлен!')
            else:
                # Добавление проекта в таблицу проектов в базе данных
                self.error_label_add.setText('')
                sql = f'''insert into project(name, link, date, id_theme) 
                values("{self.name.toPlainText()}", "{self.link}", 
                "{datetime.datetime.now().date().strftime("%d.%m.%Y")}", 
                (select theme.id from theme where theme.theme = "{self.theme.currentText()}"))'''
                self.update_table = QSqlQuery()
                self.update_table.exec(sql)
                for student in self.add_students_list.toPlainText().split('\n')[:-1]:
                    lastname, name, patronymic, class_number, letter = student.split()[:3] + [student.split()[3][:-1],
                                                                                              student.split()[3][-1]]
                    sql = f'''insert into student_project(id_project, id_student) 
                    values((select project.id from project where project.name = "{self.name.toPlainText()}"), 
                    (select student.id from student where student.lastname = "{lastname}"
                    and student.name = "{name}" and student.patronymic = "{patronymic}" and 
                    student.class = "{class_number}" and student.letter = "{letter}"))'''
                    self.update_table.exec(sql)

                self.set_update_table()
        else:
            self.error_label_add.setText('!Некорректное заполнение полей!')

    def init_f_delete(self):  # Создание и установка вкладки удаления
        self.error_label_delete = QLabel('', self)
        self.error_label_delete.setMaximumHeight(32)
        self.f_delete_scroll_area = QScrollArea(self)
        self.f_delete_layout = QVBoxLayout()
        self.f_delete_layout.addWidget(self.error_label_delete)
        self.f_delete_scroll_area.setLayout(self.f_delete_layout)
        self.id_delete = QTextEdit('', self)
        # Определение надписи зависимости от таблицы
        if self.type == 'project':
            self.id_delete_label = QLabel('Введите номер проекта, который нужно удалить:', self)
        elif self.type == 'theme':
            self.id_delete_label = QLabel('Введите номер темы, которую нужно удалить:', self)
        elif self.type == 'presentation':
            self.id_delete_label = QLabel('Введите номер оценки, которую нужно удалить:', self)
        self.id_delete.setMaximumHeight(32)
        self.id_delete_group = QGroupBox('Удалить по номеру', self)
        self.id_delete_group.setMaximumHeight(200)
        self.f_delete_layout.addWidget(self.id_delete_group)
        self.id_delete_button = QPushButton('Удалить', self)

        self.id_delete_group_layout = QVBoxLayout()
        self.id_delete_group_layout.addWidget(self.id_delete_label)
        self.id_delete_group_layout.addWidget(self.id_delete)
        self.id_delete_group_layout.addWidget(self.id_delete_button)
        self.id_delete_group.setLayout(self.id_delete_group_layout)
        self.clear_all = QPushButton('Очистить таблицу', self)
        self.f_delete_layout.addWidget(self.clear_all)
        self.clear_all.setMinimumHeight(60)
        self.id_delete_button.clicked.connect(self.delete_project)
        self.clear_all.clicked.connect(self.delete_all_table)
        self.table_view.clicked.connect(self.select_in_table_delete)

        return self.f_delete_scroll_area

    def select_in_table_delete(self):  # Автоматический ввод id в окно ввода по выбранному в таблице проекту
        self.id_delete.setText(str(self.table_view.currentIndex().siblingAtColumn(0).data()))

    def delete_project(self):  # Удаление проекта из базы данных
        # Проверка на корректность данных
        if self.id_delete.toPlainText().isdigit():
            if int(self.id_delete.toPlainText()) in [int(p[0]) for p in
                                                     self.cursor.execute(
                                                         f'select {self.type}.id from {self.type}').fetchall()]:
                # Удаление в зависимости от типа таблицы
                self.error_label_delete.setText('')
                if self.type == 'project':
                    label = 'проект'
                elif self.type == 'theme':
                    label = 'тему'
                elif self.type == 'presentation':
                    label = 'оценку'
                yes_or_no = QMessageBox.question(self, '',
                                                 f'''Вы действительно хотите удалить 
{label} номер {self.id_delete.toPlainText()}?''',
                                                 QMessageBox.Yes, QMessageBox.No)
                if yes_or_no == QMessageBox.Yes:
                    sql = f'delete from {self.type} where {self.type}.id = {int(self.id_delete.toPlainText())}'
                    self.update_table = QSqlQuery()
                    self.update_table.exec(sql)
                    if self.type == 'project':
                        sql = f'''delete from student_project 
                        where student_project.id_project = {int(self.id_delete.toPlainText())}'''
                        self.update_table.exec(sql)
                        sql = f'''delete from presentation 
                        where presentation.id_project = {int(self.id_delete.toPlainText())}'''
                        self.update_table.exec(sql)
                    elif self.type == 'theme':
                        sql = f'''delete from student_project 
where student_project.id_project = 
(select id from project where project.id_theme = {int(self.id_delete.toPlainText())})'''
                        self.update_table.exec(sql)
                        sql = f'''delete from presentation 
where presentation.id_project = (select id from project where project.id_theme = {int(self.id_delete.toPlainText())})'''
                        self.update_table.exec(sql)
                        sql = f'''delete from project
                        where project.id_theme = {int(self.id_delete.toPlainText())}'''
                        self.update_table.exec(sql)
                    self.set_update_table()
            else:  # Вывод ошибки при некорректном вводе
                self.error_label_delete.setText('!Некорректный номер!')
        else:
            self.error_label_delete.setText('!Некорректный номер!')

    def delete_all_table(self):  # Удаление всей таблицы
        yes_or_no = QMessageBox.question(self, '', 'Вы действительно хотите очистить всю таблицу?', QMessageBox.Yes,
                                         QMessageBox.No)
        if yes_or_no == QMessageBox.Yes:
            sql = f'delete from {self.type}'
            self.update_table = QSqlQuery()
            self.update_table.exec(sql)
            if self.type == 'project':
                sql = 'delete from student_project'
                self.update_table.exec(sql)
                sql = 'delete from presentation'
                self.update_table.exec(sql)
            elif self.type == 'theme':
                sql = 'delete from student_project where student_project.id_project = (select id from project)'
                self.update_table.exec(sql)
                sql = 'delete from presentation where presentation.id_project = (select id from project)'
                self.update_table.exec(sql)
                sql = 'delete from project'
                self.update_table.exec(sql)
            self.set_update_table()

    def set_update_table(self):  # Обновление таблицы
        if self.type == 'project':
            self.update_table = QSqlQuery('''SELECT project.id as "Номер", project.Date as "Дата",
                             project.Link as "Ссылка", 
                             project.Name as "Название", theme.theme as "Тема" FROM Project
                             inner join theme on project.id_theme = theme.id''', self.db)
        elif self.type == 'theme':
            self.update_table = QSqlQuery('''SELECT theme.id as "Номер", theme.theme as "Тема",
                                         theme.date as "Срок",
                                         teachers.lastname as "Учитель", 
                                         subject.subject as "Предмет" FROM Theme
                                         inner join teachers on teachers.id = theme.id_teacher
                                         inner join subject on subject.id = theme.id_subject''', self.db)
        self.table_model.setQuery(self.update_table)

    def init_f_check(self):  # Создание и установка вкладки оценки
        self.error_label_check = QLabel('', self)
        self.error_label_check.setMaximumHeight(50)
        self.f_check_scroll_area = QScrollArea(self)
        self.check_layout = QVBoxLayout()
        self.check_layout.addWidget(self.error_label_check)
        self.f_check_scroll_area.setLayout(self.check_layout)
        self.check_group = QGroupBox('Номер', self)
        self.check_group.setMaximumHeight(150)
        self.check_group_layout = QVBoxLayout()
        self.id_check = QTextEdit('', self)
        self.id_check.setMaximumHeight(32)
        self.id_check_label = QLabel('Введите номер проекта, который хотите оценить:', self)
        self.check_button = QPushButton('Оценить', self)
        self.check_group_layout.addWidget(self.id_check_label)
        self.check_group_layout.addWidget(self.id_check)
        self.check_group_layout.addWidget(self.check_button)
        self.check_group.setLayout(self.check_group_layout)
        self.check_layout.addWidget(self.check_group)
        self.open_project = QPushButton('Открыть проект', self)
        self.open_project.clicked.connect(self.open_the_project)
        self.check_layout.addWidget(self.open_project)
        self.table_view.clicked.connect(self.select_in_table_check)
        self.check_button.clicked.connect(self.presentation_active)

        return self.f_check_scroll_area

    def open_the_project(self):  # Открытие проекта
        # Проверка корректности данных
        if self.id_check.toPlainText().isdigit():
            if int(self.id_check.toPlainText()) in [p[0] for p in
                                                    self.cursor.execute('select project.id from project').fetchall()]:
                if os.path.isfile(self.cursor.execute(
                        f'''select project.link 
                        from project where project.id = {self.id_check.toPlainText()}''').fetchall()[0][0]):
                    # Открытие файла
                    self.error_label_check.setText('')
                    os.startfile(self.cursor.execute(
                        f'''select project.link from project where 
                        project.id = {self.id_check.toPlainText()}''').fetchall()[0][0])
                else:  # Вывод ошибок
                    self.error_label_check.setText('!Данный файл отсутствует на устройстве!')
            else:
                self.error_label_check.setText('!Некорректный номер!')
        else:
            self.error_label_check.setText('!Некорректный номер!')

    def presentation_active(self):  # Установка таблицы презентаций по проекту
        # Проверка на корректный ввод
        if self.id_check.toPlainText().isdigit():

            if int(self.id_check.toPlainText()) in [p[0] for p in
                                                    self.cursor.execute('select project.id from project').fetchall()]:
                # Установка на вкладке презентаций оценки выбранного проекта
                self.error_label_check.setText('')
                self.presentation_tab.setCurrentIndex(1)
                sql = f'''select presentation.id as "Номер", presentation.presentation as "Защита",
                          presentation.score as "Балл", teachers.lastname as "Проверяющий учитель", 
                          project.name as "Проект" from presentation 
                          inner join project on project.id = presentation.id_project
                          inner join teachers on teachers.id = presentation.id_teacher
                          where presentation.id_project = {int(self.id_check.toPlainText())}'''
                self.update_table = QSqlQuery(sql, self.db)
                self.presentation_table.setQuery(self.update_table)
            else:  # Вывод ошибки при некорректном вводе
                self.error_label_check.setText('!Данного номера не существует!')
        else:
            self.error_label_check.setText('!Некорректный номер!')

    def select_in_table_check(self):  # Автоматический ввод id в окно ввода по выбранному в таблице проекту
        self.id_check.setText(str(self.table_view.currentIndex().siblingAtColumn(0).data()))

    def init_f_reset(self):  # Создание и установка вкладки оценки
        self.error_label_reset = QLabel('', self)
        self.error_label_reset.setMaximumHeight(32)
        self.f_reset_scroll_area = QScrollArea(self)
        self.f_reset_layout = QVBoxLayout()
        self.f_reset_layout.addWidget(self.error_label_reset)
        self.f_reset_scroll_area.setLayout(self.f_reset_layout)
        self.id_reset = QTextEdit('', self)
        self.id_reset_label = QLabel('Введите номер проекта, который нужно изменить:', self)
        self.id_reset.setMaximumHeight(32)
        self.id_reset_group = QGroupBox('Номер', self)
        self.id_reset_group.setMaximumHeight(200)
        self.f_reset_layout.addWidget(self.id_reset_group)
        self.id_reset_button = QPushButton('Изменить', self)

        self.id_reset_group_layout = QVBoxLayout()
        self.id_reset_group_layout.addWidget(self.id_reset_label)
        self.id_reset_group_layout.addWidget(self.id_reset)
        self.id_reset_group_layout.addWidget(self.id_reset_button)
        self.id_reset_group.setLayout(self.id_reset_group_layout)
        self.id_reset_button.clicked.connect(self.reset_project)
        self.table_view.clicked.connect(self.select_in_table_reset)

        # Если функция работает с таблицей проектов
        if self.type == 'project':
            self.name_group_reset = QGroupBox('Изменить', self)
            self.name_label_reset = QLabel('Название:', self)
            self.name_reset = QTextEdit('', self)
            self.name_reset.setMaximumHeight(32)
            self.input_link_reset = QPushButton('Закрузить проект', self)
            self.input_link_reset.clicked.connect(self.open_dialog_project_reset)
            self.check_input_link_reset = QCheckBox('Проект', self)
            self.check_input_link_reset.setDisabled(1)
            self.name_group_layout_reset = QFormLayout()
            self.name_group_layout_reset.addRow(self.name_label_reset, self.name_reset)
            self.name_group_layout_reset.addRow(self.input_link_reset, self.check_input_link_reset)
            self.name_group_reset.setLayout(self.name_group_layout_reset)
            self.theme_label_reset = QLabel('Выберите тему:', self)
            self.theme_reset = QComboBox()
            self.theme_reset.addItem('')
            self.theme_reset.addItems(
                [p[0] for p in self.cursor.execute('select Theme from Theme order by Theme').fetchall()])
            self.name_group_layout_reset.addRow(self.theme_label_reset, self.theme_reset)
            self.reset_project_students_group = QGroupBox('Авторы')
            self.reset_project_students_layout = QVBoxLayout()
            self.reset_students_list = QTextEdit('', self)
            self.reset_students_list.setDisabled(1)
            self.reset_student_in_project = QPushButton('Добавить ученика', self)
            self.delete_students_in_project_reset = QPushButton('Очистить', self)
            self.reset_button = QPushButton('Применить', self)

            self.delete_students_in_project.clicked.connect(self.delete_students)
            self.reset_student_in_project.clicked.connect(self.open_dialog_student_reset)
            self.reset_project_students_group.setLayout(self.reset_project_students_layout)
            self.reset_project_students_layout.addWidget(self.reset_students_list)
            self.reset_project_students_layout.addWidget(self.reset_student_in_project)
            self.reset_project_students_layout.addWidget(self.delete_students_in_project_reset)
            self.name_group_layout_reset.addRow(self.reset_project_students_group)
            self.name_group_layout_reset.addRow(self.reset_button)
            self.reset_button.clicked.connect(self.reset_the_project)
            self.f_reset_layout.addWidget(self.name_group_reset)

        return self.f_reset_scroll_area

    def reset_project(self):  # Автоматический ввод данных окна id в соответствующие окна
        # Проверка на корректность введённый занных
        if self.id_reset.toPlainText().isdigit():
            if int(self.id_reset.toPlainText()) in [p[0] for p in
                                                    self.cursor.execute('select project.id from project').fetchall()]:
                # Распределение данных по окнам
                self.error_label_reset.setText('')
                self.link_reset = self.cursor.execute(
                    f'select project.link from project where project.id = {self.id_reset.toPlainText()}').fetchall()[0][
                    0]
                self.name_reset.setText(self.cursor.execute(
                    f'select project.name from project where project.id = {self.id_reset.toPlainText()}').fetchall()[0][
                                            0])
                self.theme_reset.setCurrentText(self.cursor.execute(
                    f'''select theme.theme from theme where 
                    theme.id = (select project.id_theme from 
                    project where project.id = {self.id_reset.toPlainText()})''').fetchall()[
                                                    0][0])
                self.check_input_link_reset.setText('Проект ' + self.cursor.execute(
                    f'select project.link from project where project.id = {self.id_reset.toPlainText()}').fetchall()[0][
                    0].split('/')[-1])
                self.reset_students_list.setText('\n'.join([f'{p[0]} {p[1]} {p[2]} {p[3]}{p[4]}' for p in
                                                            self.cursor.execute(f'''select lastname, name, patronymic,
                                                             class, letter 
                from student where student.id in (select student_project.id_student 
                from student_project where id_project = {self.id_reset.toPlainText()})''').fetchall()]) + '\n')

            else:  # Сообщения о некорректном вводе
                self.error_label_reset.setText('!Несуществующий номер!')
        else:
            self.error_label_reset.setText('!Некорректный номер!')

    def reset_the_project(self):  # Применение введённых изменений
        # Проверка на корректность данных
        if (self.name_reset.toPlainText() and self.link_reset and self.theme_reset.currentText()
                and self.reset_students_list.toPlainText()):
            # Изменение данных по id
            self.error_label_reset.setText('')
            print(self.theme_reset.currentText())
            sql = f'''update project set name = "{self.name_reset.toPlainText()}",
                      link = "{self.link_reset}", 
                      id_theme = (select theme.id from theme where theme.theme = "{self.theme_reset.currentText()}")
                      where id = {self.id_reset.toPlainText()}'''
            self.update_table = QSqlQuery()
            self.update_table.exec(sql)
            sql = f'''delete from student_project where id_project = {self.id_reset.toPlainText()}'''
            self.update_table.exec(sql)
            for student in self.reset_students_list.toPlainText().split('\n')[:-1]:
                lastname, name, patronymic, class_number, letter = student.split()[:3] + [student.split()[3][:-1],
                                                                                          student.split()[3][-1]]
                sql = f'''insert into student_project(id_project, id_student) 
                values((select project.id from project where project.name = "{self.name_reset.toPlainText()}"), 
                (select student.id from student where student.lastname = "{lastname}"
                and student.name = "{name}" and student.patronymic = "{patronymic}" and 
                student.class = "{class_number}" and student.letter = "{letter}"))'''
                self.update_table.exec(sql)
                self.set_update_table()
        else:  # Сообщение о некорректном вводе
            self.error_label_reset.setText('!Некорректное заполнение полей!')

    def open_dialog_project_reset(self):  # Переопределение ссылки на проект
        self.link_reset, ok_press = QFileDialog.getOpenFileName(self, 'Выберите проект', '', 'Все файлы (*)')
        if ok_press:
            self.check_input_link_reset.setCheckState(2)
            self.check_input_link_reset.setText('Проект ' + self.link_reset.split('/')[-1])

    def open_dialog_student_reset(self):  # Переопределение авторов проекта
        list_students = self.cursor.execute(
            'select lastname, name, patronymic, class, letter from student order by class, letter, lastname').fetchall()
        self.add_student_reset, ok_press = QInputDialog.getItem(self, 'Выберете автора', 'Кто работал над проектом?',
                                                                tuple([f'{p[0]} {p[1]} {p[2]} {p[3]}{p[4]}' for p in
                                                                       list_students]),
                                                                0, False)
        if ok_press:
            self.reset_students_list.setText(self.reset_students_list.toPlainText() + self.add_student_reset + '\n')

    def select_in_table_reset(self):  # Автоматический ввод id в окно ввода по выбранному в таблице проекту
        self.id_reset.setText(str(self.table_view.currentIndex().siblingAtColumn(0).data()))

    def get_object(self):  # Возврат объекта
        return self.functions

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.connection.close()
        self.close()


class Check(QMainWindow, QWidget):  # Режим оценки
    def __init__(self):
        super(Check, self).__init__()
        # Определение интерфейса
        self.setWindowTitle('Database check')
        self.setMinimumSize(600, 600)

        # Подключение базы данных
        if os.path.isfile('Data_project_YL_MAIN.db'):
            self.db = QSqlDatabase.addDatabase('QSQLITE')
            self.db.setDatabaseName('Data_project_YL_MAIN.db')
        else:
            # Вывод окна ошибки
            app = QApplication(sys.argv)
            bad_exit = DatabaseNotFound()
            bad_exit.show()
            sys.exit(app.exec_())

        # Установка модели таблицы проектов
        self.project_model = QSqlTableModel(self)
        self.project_model.select()

        sqlquery = QSqlQuery('''SELECT project.id as "Номер", project.Date as "Дата",
                         project.Link as "Ссылка", 
                         project.Name as "Название", theme.theme as "Тема" FROM Project
                         inner join theme on project.id_theme = theme.id''', self.db)
        self.project_model.setQuery(sqlquery)

        font = QtGui.QFont()
        font.setPointSize(11)
        self.tabs = QTabWidget(self)
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tabs)
        self.tab_main = QWidget(self)
        self.tab_presentation = QWidget(self)
        self.tabs.addTab(self.tab_main, 'Проекты')
        self.tabs.addTab(self.tab_presentation, 'Презентации')
        self.tabs.setCurrentIndex(0)
        self.tabs_main_layout = QGridLayout()
        self.tab_main.setLayout(self.tabs_main_layout)
        self.project_view = QTableView(self)
        self.project_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.project_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.project_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.project_view.setModel(self.project_model)
        self.project_view.resize(300, 300)

        self.tabs_main_layout.addWidget(self.project_view, 0, 0)
        self.presentation_model = QSqlTableModel(self)
        self.presentation_model.select()

        # Определение вкладок функций для таблицы проектов
        self.function_tabs_project = FunctionTabs('project', self.db, self.project_model, self.project_view, self.tabs,
                                                  self.presentation_model, False, False, False, True,
                                                  *[True, True, False, True])

        self.tabs_main_layout.addWidget(self.function_tabs_project.get_object(), 0, 1)
        self.tab_presentation_layout = QGridLayout()

        self.presentation_view = QTableView(self)
        self.presentation_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.presentation_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.presentation_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.presentation_view.setModel(self.presentation_model)
        # Определение вкладок функций для таблицы презентаций
        self.function_tabs_presentation = FunctionTabs('presentation', self.db, self.presentation_model,
                                                       self.presentation_view, self.tabs, None, True, True, False,
                                                       False,
                                                       *[True, True, True, True])
        self.tab_presentation.setLayout(self.tab_presentation_layout)
        self.tab_presentation_layout.addWidget(self.presentation_view, 0, 0)
        self.tab_presentation_layout.addWidget(self.function_tabs_presentation.get_object(), 0, 1)
        self.centralWidget = QWidget()
        self.centralWidget.setFont(font)
        self.centralWidget.setLayout(self.main_layout)
        self.setCentralWidget(self.centralWidget)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:  # Закрытие окна
        self.db.close()
        self.project_model.clear()
        self.presentation_model.clear()
        app.quit()
        self.close()

    def keyPressEvent(self, event):  # Закрытие окна при нажатии escape
        if event.key() == Qt.Key_Escape:
            self.close()


class DatabaseNotFound(QMainWindow, QWidget):  # Выход в случае невозможности подключения к базе данных
    def __init__(self):
        super(DatabaseNotFound, self).__init__()
        # Создание окна ошибки
        self.setGeometry(500, 500, 250, 50)
        self.setWindowTitle('Ошибка!')
        self.error_layout = QVBoxLayout()
        self.error_label = QLabel('База данных не найдена!', self)
        self.error_label.resize(self.sizeHint())
        self.error_layout.addWidget(self.error_label)
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.error_layout)
        self.setCentralWidget(self.centralWidget)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:  # Закрытие окна
        app.quit()
        self.close()

    def keyPressEvent(self, event):  # Закрытие при нажатии escape
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    # Запуск приложения
    app = QApplication(sys.argv)
    choice_window = Choice_Of_Actions()
    choice_window.show()
    sys.exit(app.exec_())
