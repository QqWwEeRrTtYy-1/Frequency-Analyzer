# https://pymorphy2.readthedocs.io/en/0.2/user/index.html
# кнопка сохранения непустого результата
# прогресс-бар
# сделать неактивным интерфейс во время анализа

import re
import pymorphy2  # pip install pymorphy2
from collections import Counter
import sys
import time
from charset_normalizer import CharsetNormalizerMatches as cnm
from interface import *
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtTest 


app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
ui.save_button.setVisible(False)

normal_word_list = []
ready_word_line_list = []


def main():
    ui.save_button.setVisible(True)
    ui.save_button.setEnabled(False) 
    ui.start.setEnabled(False)
    start_time = time.time()
    ui.message.clear()
    ui.message.addItem("Подождите, идет анализ текста.")
    QtTest.QTest.qWait(1) # обновить интерфейс
    print("Программа выполняется. Пожалуйста, подождите!")

    text_sou = source(source_file)
    ready_text = regular_text(text_sou)
    morphed_text = morphy_text(ready_text, ready_text)
    common_words_result = number_and_result(morphed_text)
    write_words(common_words_result)

    stop_time = round(time.time() - start_time, 2)
    ui.message.addItem(f"Анализ завершен за {stop_time} секунд")
    ui.save_button.setEnabled(True) 
    ui.start.setEnabled(True)
    ui.progressBar.setValue(0)

#ВЫБИРАЕМ ФАЙЛ
def choose_file():
    global source_file
    source_file = QFileDialog.getOpenFileName()[0]
    ui.file_path.setText(source_file)

#ОТКРЫВАЕМ ФАЙЛ-ИСТОЧНИК И ЗАПИСЫВАЕМ В ПЕРЕМЕННУЮ
def source(source_file_s):
    # TODO: file missing exception
    text_str = str(cnm.from_path(source_file_s).best().first())

    if len(text_str) == 0:
        ui.message.addItem("Файл оказался пустым!")
        ui.save_button.setVisible(False)

    return text_str

#ПРИВОДИМ ТЕКСТ К ОДНОМУ ВИДУ(РЕГУЛЯРКИ)
def regular_text(text_source):
    text_str = text_source.lower()
    text_str = re.sub("ё", "е", text_str)
    text_list = re.findall(r"[а-яё]+", text_str)

    return text_list

#ФИЛЬТРУЕМ ТЕКСТ, ОСТАВЛЯЯ ТОЛЬКО НУЖНЫЕ ЧАСТИ РЕЧИ
def morphy_text(reg_text, list_words):
    morph = pymorphy2.MorphAnalyzer()

    # задаем максимум для прогресс-бара
    progress_max_value = len(list_words)
    ui.progressBar.setMaximum(progress_max_value)
    progress_i = 0

    for word in reg_text:
        first_parse = morph.parse(word)[0]  # TODO: Parse с самым высоким Score
        if ui.checkbox_noun.isChecked():     
            if "NOUN" in first_parse.tag:
                normal_word_list.append(first_parse.normal_form)
        if ui.checkbox_adjective.isChecked():
            if "ADJF" or "ADJS" in first_parse.tag:
                normal_word_list.append(first_parse.normal_form)
        if ui.checkbox_verb.isChecked():
            if "VERB" in first_parse.tag:
                normal_word_list.append(first_parse.normal_form)

        # добавляем единицу к прогресс-бару
        QtTest.QTest.qWait(0)
        ui.progressBar.setValue(progress_i)
        progress_i += 1

    return normal_word_list

#БЕРЁМ САМЫЕ ПОВТОРЯЮЩИЕСЯ СЛОВА В КОЛЛИЧЕСТВЕ WORDS_NUMBER
def number_and_result(list_of_words):
    words_number = ui.spinBox.value()
    result = dict(Counter(list_of_words).most_common(words_number))

    return result

#ВЫВОДИМ СЛОВА НА LISTWIDGET И ДОБАВЛЯЕМ В ready_word_line_list
def write_words(common_words):
    for key, value in common_words.items():
        line = f"{key} : {value}"
        ui.listWidget.addItem(line)
        ready_word_line_list.append(line)

#СОХРАНЯЕМ ФАЙЛ
def save_file():
    save = QFileDialog.getSaveFileName(MainWindow, "result", '/', '.txt')[0]
    file = open(save, 'w')
    file.write("\n".join(ready_word_line_list))
    file.close()
    file_way = "Файл сохранён в " + str(save)
    ui.message.addItem(file_way) 

    
ui.choose_file.clicked.connect(choose_file)
ui.start.clicked.connect(main)
ui.save_button.clicked.connect(save_file)
sys.exit(app.exec_())