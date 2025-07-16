import sqlite3
import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QAbstractItemView, QHeaderView, QFileDialog
from PyQt5.QtCore import pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices


# основное окно ппограммы
class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('ТРПО')
        uic.loadUi("ui/extra.ui", self)  # загрузка графического интерфейса из файла

        # Привязка событий к нажатиям кнопок
        self.searchButton.clicked.connect(self.search)
        self.addButton.clicked.connect(self.open_addForm)
        self.deleteButton.clicked.connect(self.delete)
        self.editButton.clicked.connect(self.open_editForm)

        self.materialLineEdit.returnPressed.connect(self.search)
        self.workTypeLineEdit.returnPressed.connect(self.search)
        self.authorLineEdit.returnPressed.connect(self.search)
        self.disciplineLineEdit.returnPressed.connect(self.search)
        self.groupLineEdit.returnPressed.connect(self.search)
        self.yearLineEdit.returnPressed.connect(self.search)
        self.storageLineEdit.returnPressed.connect(self.search)

        # Настройки таблицы

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.itemDoubleClicked.connect(self.on_item_double_click)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.itemClicked.connect(self.on_item_click)
        self.header = self.tableWidget.horizontalHeader()
        self.header.setSectionsClickable(False)
        self.header.setSectionResizeMode(QHeaderView.Stretch)
        self.header.setStretchLastSection(True)
        self.header.ResizeMode(QHeaderView.Stretch)
        self.select_data()

    def on_item_click(self, item):
        # Выбираем всю строку при клике на ячейку
        self.tableWidget.selectRow(item.row())

    def on_item_double_click(self, item):  # открытие файла при двойном клике
        column = item.column()
        if column == 8:
            file_path = self.tableWidget.item(item.row(), column).text()
            if os.path.exists(file_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            else:
                QMessageBox.warning(self, 'Ошибка', 'Файл не найден.')

    def select_data(self, query=""):  # выбор данных из бд

        con = sqlite3.connect("db/trpo.db")
        cur = con.cursor()
        headers = ["ID работы", "Название", "Тип работы", "Автор", "Группа", "Дисциплина", "Год публикации",
                   "Место хранения", "Файл"]

        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(9)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(headers)
        if query == "":
            query = """SELECT w.work_id, w.work_title, w.work_type, s.last_name || " " || s.first_name, s.[group], d.discipline_name, w.publication_date,
                        w.storage_location, w.file
                        FROM works w
                        JOIN students s ON w.student_id = s.student_id join disciplines d using(discipline_id)"""

        res = cur.execute(query).fetchall()

        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

        con.commit()

    def search(self):  # поиск работы в базе данных

        material = self.materialLineEdit.text().lower().capitalize()
        type = self.workTypeLineEdit.text().lower().capitalize()
        author = self.authorLineEdit.text().lower().title()
        discipline = self.disciplineLineEdit.text().lower().capitalize()
        year = self.yearLineEdit.text().lower().capitalize()
        group = self.groupLineEdit.text().upper()
        storage = self.storageLineEdit.text().capitalize()

        query = """SELECT work_id, work_title, work_type, last_name || " " ||first_name , s.[group], d.discipline_name, w.publication_date,
                        w.storage_location, w.file 
                    FROM works w join students s using (student_id) join disciplines d using (discipline_id) WHERE """
        conditions = []

        if material:
            conditions.append("work_title LIKE '%{}%'".format(material))
        if type:
            conditions.append("work_type LIKE '%{}%'".format(type))
        if author:
            if len(author.split()) == 1:
                conditions.append(f"first_name  LIKE '%{author}%' or last_name  LIKE '%{author}%'")
            if len(author.split()) == 2:
                name_parts = author.split()
                conditions.append(f"""first_name LIKE '%{name_parts[0]}%' AND last_name LIKE '%{name_parts[1]}%'
                                        or first_name LIKE '%{name_parts[1]}%' AND last_name LIKE '%{name_parts[0]}%'""")
        if discipline:
            conditions.append("discipline_id LIKE '%{}%'".format(discipline))
        if year:
            conditions.append("publication_date LIKE '%{}%'".format(year))
        if group:
            conditions.append(f"s.[group] like '%{group}%'")
        if storage:
            conditions.append(f"w.storage_location like '%{storage}%'")

        if conditions:
            query += " AND ".join(conditions)
        else:
            query = ""

        self.select_data(query)

    def open_editForm(self):
        selected_items = self.tableWidget.selectedItems()
        if selected_items:
            work_id = int(self.tableWidget.item(selected_items[0].row(), 0).text())
            title = self.tableWidget.item(selected_items[0].row(), 1).text()
            work_type = self.tableWidget.item(selected_items[0].row(), 2).text()
            author = self.tableWidget.item(selected_items[0].row(), 3).text()
            discipline = self.tableWidget.item(selected_items[0].row(), 5).text()
            year = self.tableWidget.item(selected_items[0].row(), 6).text()
            group = self.tableWidget.item(selected_items[0].row(), 4).text()
            storage = self.tableWidget.item(selected_items[0].row(), 7).text()
            fname = self.tableWidget.item(selected_items[0].row(), 8).text()

            self.edit_work_form = EditWorkForm()
            self.edit_work_form.set_data(title, work_type, author, discipline, year, group, storage, work_id,
                                         fname)  # Передача данных
            self.edit_work_form.work_edited.connect(self.edit_work)
            self.edit_work_form.show()
        else:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите строку для редактирования')

    def edit_work(self, title, type, author, discipline, year, group, storage, work_id, fname):
        con = sqlite3.connect("db/trpo.db")
        cur = con.cursor()

        author_first_name = author.split()[1]
        author_last_name = author.split()[0]
        check_student = f"""SELECT * FROM students WHERE first_name = '{author_first_name}' AND last_name = '{author_last_name}'"""
        res = len(cur.execute(check_student).fetchall())
        if res == 0:
            query = f"INSERT INTO students (first_name, last_name, [group]) VALUES ('{author_first_name}', '{author_last_name}', '{group}');"
            cur.execute(query)
            con.commit()

        check_discipline = f"""SELECT * FROM disciplines WHERE discipline_name = '{discipline}'"""
        res = len(cur.execute(check_discipline).fetchall())
        if res == 0:
            query = f"INSERT INTO disciplines (discipline_name) VALUES ('{discipline}');"
            cur.execute(query)

        work_query = """UPDATE works
                        SET work_title = ?, work_type = ?, student_id = (SELECT student_id FROM students WHERE first_name = ? AND last_name = ?),
                            discipline_id = (SELECT discipline_id FROM disciplines WHERE discipline_name = ?),
                            publication_date = ?, storage_location = ?, file = ?
                        WHERE work_id = ?;"""

        cur.execute(work_query,
                    (title, type, author_first_name, author_last_name, discipline, year, storage, fname, work_id))

        con.commit()

        self.select_data()

    def open_addForm(self):  # открытие окна добавления работы
        self.add_work_form = AddWorkForm()
        self.add_work_form.work_added.connect(self.add_work)
        self.add_work_form.show()

    def add_work(self, title, type, author, discipline, year, group, storage,
                 fname=""):  # добавление работы в базу данных
        con = sqlite3.connect("db/trpo.db")
        cur = con.cursor()

        author_first_name = author.split()[1]
        author_last_name = author.split()[0]
        check_student = f"""SELECT * FROM students WHERE first_name = '{author_first_name}' AND last_name = '{author_last_name}'"""
        res = len(cur.execute(check_student).fetchall())
        if res == 0:
            query = f"INSERT INTO students (first_name, last_name, [group]) VALUES ('{author_first_name}', '{author_last_name}', '{group}');"
            cur.execute(query)
            con.commit()

        check_discipline = f"""SELECT * FROM disciplines WHERE discipline_name = '{discipline}'"""
        res = len(cur.execute(check_discipline).fetchall())
        if res == 0:
            query = f"INSERT INTO disciplines (discipline_name) VALUES ('{discipline}');"
            cur.execute(query)

        with open(fname, 'rb') as file:
            blob_data = file.read()

        work_query = """INSERT INTO works (work_title, work_type, student_id, discipline_id, publication_date, storage_location, file)
                        SELECT ?, ?, s.student_id, d.discipline_id, ?, ?, ?
                        FROM students s, disciplines d
                        WHERE s.first_name = ? AND s.last_name = ? AND d.discipline_name = ?;"""

        cur.execute(work_query, (title, type, year, storage, fname, author_first_name, author_last_name, discipline))

        con.commit()

        self.select_data()

    def delete(self):  # Удаление работы из базы данных
        selected_items = self.tableWidget.selectedItems()
        if selected_items:
            selected_columns = {item.column() for item in selected_items}
            column_to_fetch = next(iter(selected_columns))
            for item in selected_items:
                if item.column() == column_to_fetch:
                    work_id = item.text()
                    break

            self.confirm_del = ConfirmDelete()
            self.confirm_del.confirm_deletion.connect(lambda confirm: self.process_deletion(confirm, work_id))
            self.confirm_del.show()
        else:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите строку для удаления')

    def process_deletion(self, confirm, work_id=""):
        if confirm:
            con = sqlite3.connect("db/trpo.db")
            cur = con.cursor()
            cur.execute(f"DELETE FROM works WHERE work_id = {work_id};")
            con.commit()
        self.select_data()


class EditWorkForm(QDialog):
    work_edited = pyqtSignal(str, str, str, str, str, str, str, int, str)  # cигнал для редактирования

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui/editForm.ui', self)

        self.btn_edit = self.findChild(QPushButton, 'btnSave')
        self.btn_cancel = self.findChild(QPushButton, 'btnCancel')
        self.btn_select_file = self.findChild(QPushButton, 'btnSelectFile')

        self.btn_edit.clicked.connect(self.edit_work)
        self.btn_cancel.clicked.connect(self.close)
        self.btn_select_file.clicked.connect(self.file_choose)

        self.line_title = self.findChild(QLineEdit, 'lineEditTitle')
        self.line_type = self.findChild(QLineEdit, 'lineEditType')
        self.line_author = self.findChild(QLineEdit, 'lineEditAuthor')
        self.line_discipline = self.findChild(QLineEdit, 'lineEditDiscipline')
        self.line_year = self.findChild(QLineEdit, 'lineEditYear')
        self.line_group = self.findChild(QLineEdit, 'lineEditGroup')
        self.line_storage = self.findChild(QLineEdit, 'lineEditStorage')

    def file_choose(self):  # выбор файла
        self.fname = QFileDialog.getOpenFileName(self)[0]

    def set_data(self, title, work_type, author, discipline, year, group, storage, work_id, fname):
        self.work_id = work_id
        # Заполнение виджетов формы данными из выбранной строки таблицы
        self.line_title.setText(title)
        self.line_type.setText(work_type)
        self.line_author.setText(author)
        self.line_discipline.setText(discipline)
        self.line_year.setText(year)
        self.line_group.setText(group)
        self.line_storage.setText(storage)
        self.fname = fname

    def edit_work(self):  # Метод для редактирования работы
        # Получение текста из полей формы

        title = self.line_title.text().capitalize().strip()
        work_type = self.line_type.text().capitalize().strip()
        author = self.line_author.text().title().strip()
        discipline = self.line_discipline.text().capitalize().strip()
        year = self.line_year.text().strip()
        group = self.line_group.text().upper().strip()
        storage = self.line_storage.text().capitalize()

        # Проверка заполнения всех полей
        if not all([title, work_type, author, discipline, year, group, storage]):
            QMessageBox.warning(self, 'Предупреждение', 'Заполните все поля.')
            return

        # Проверка наличия двух слов в поле автора
        if len(author.split()) != 2:
            QMessageBox.warning(self, 'Предупреждение', 'Введите имя и фамилию автора через пробел.')
            return

        # Отправка сигнала с данными для редактирования
        self.work_edited.emit(title, work_type, author, discipline, year, group, storage, self.work_id, self.fname)
        self.close()


# Окно добавления работы в базу данных
class AddWorkForm(QDialog):
    work_added = pyqtSignal(str, str, str, str, str, str, str, str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui/addWorkForm_style.ui', self)

        self.btn_add = self.findChild(QPushButton, 'btnAdd')
        self.btn_cancel = self.findChild(QPushButton, 'btnCancel')
        self.btn_select_file = self.findChild(QPushButton, 'btnSelectFile')

        self.btn_add.clicked.connect(self.add_work)
        self.btn_select_file.clicked.connect(self.file_choose)
        self.btn_cancel.clicked.connect(self.close)

        self.line_title = self.findChild(QLineEdit, 'lineEditTitle')
        self.line_type = self.findChild(QLineEdit, 'lineEditType')
        self.line_author = self.findChild(QLineEdit, 'lineEditAuthor')
        self.line_discipline = self.findChild(QLineEdit, 'lineEditDiscipline')
        self.line_year = self.findChild(QLineEdit, 'lineEditYear')
        self.line_group = self.findChild(QLineEdit, 'lineEditGroup')
        self.line_storage = self.findChild(QLineEdit, 'lineEditStorage')

    def file_choose(self):  # выбор файла
        self.fname = QFileDialog.getOpenFileName(self)[0]

    def add_work(self):  # добавление работы
        # Получаем текст из всех полей формы
        title = self.line_title.text().capitalize().strip()
        work_type = self.line_type.text().capitalize().strip()
        author = self.line_author.text().title().strip()
        discipline = self.line_discipline.text().capitalize().strip()
        year = self.line_year.text().strip()
        group = self.line_group.text().upper().strip()
        storage = self.line_storage.text().capitalize()

        # Проверяем, что все поля заполнены
        if not all([title, work_type, author, discipline, year, group, storage]) or not self.fname:
            QMessageBox.warning(self, 'Предупреждение', 'Заполните все поля.')
            return

        # Проверяем, что в поле автора введено два слова
        if len(author.split()) != 2:
            QMessageBox.warning(self, 'Предупреждение', 'Введите имя и фамилию автора через пробел.')
            return

        self.work_added.emit(title, work_type, author, discipline, year, group, storage, self.fname)
        self.close()


# Всплывающее окно для подтверждения удаления
class ConfirmDelete(QDialog):
    confirm_deletion = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        uic.loadUi('ui/confirmDelete.ui', self)
        self.btnYes.clicked.connect(self.on_yes_clicked)
        self.btnNo.clicked.connect(self.on_no_clicked)

    def on_yes_clicked(self):
        self.confirm_deletion.emit(True)
        self.accept()

    def on_no_clicked(self):
        self.confirm_deletion.emit(False)
        self.reject()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
