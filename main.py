"""## Setup"""
# This Python file uses the following encoding: utf-8
import sys
import os
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from pynput.keyboard import Key, Listener
import time
from statistics import mean
import sqlite3
import matplotlib.pyplot as plt
import math

"""## Utils"""
class Keyboard(QWidget):
    def __init__(self):
        super(Keyboard, self).__init__()
        self.loadUi()
        self.mainWin = self.children()[0]
        self.mainWin.pushButton.clicked.connect(self.addNewUser)
        self.mainWin.pushButton_3.clicked.connect(self.login)
        self.mainWin.pushButton_2.clicked.connect(self.endOfWritting)
        self.mainWin.pushButton_4.clicked.connect(self.resetAll)
        self.probableRatio = [17, 10, 5, 15, 4, 4, 1, 1, 1, 2]
        self.mode = ""
    
    def resetParameters(self):
        """
        reset user parameters
        """
        self.hold = False
        self.start_time_release = 0
        self.intervals_beetwen_keystrokes = []
        self.intervals_beetwen_press_release = []
        self.symbols = 0
        self.time_of_identification = 0
        self.time_correction = 0
        self.correction_start = True
        self.words = 0
        self.losses_from_correction = []
        self.deleted_keys = 0
        self.deleted_groups = 0
        self.max_without_correction = 0
        self.listener = Listener(
            on_press=self.on_press, on_release=self.on_release)

    def resetAll(self):
        """
        clear the text of all textBoxes
        """
        self.resetParameters()
        self.mainWin.plainTextEdit.clear()
        
        self.mainWin.textEdit.clear()
        self.mainWin.label_2.setText(
            'Witaj! Podaj nazwę użytkownika i wybierz zaloguj lub nowy użytkownik')
        self.mainWin.label_3.setText('Zgodność XX% z użytkownik YYYYYY.')

    def loadUi(self):
        """
        load GUI
        """
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

    def login(self):
        """
        log in to the system
        """
        self.mode = 'log'
        self.resetParameters()
        used = True
        records = self.selectFromDB()
        
        for row in records:
            if row[0] == self.mainWin.textEdit.toPlainText():
                used = False
                break
        if (self.mainWin.textEdit.toPlainText() != "" and used == False):
            self.mainWin.label.setText(
                "W Szczebrzeszynie chrząszcz brzmi w trzcinie. \nI Szczebrzeszyn z tego słynie.")
            self.mainWin.plainTextEdit.clear()
            self.mainWin.label_2.setText(
                "Przepisz tekst i zatwierdź przyciskiem")
            self.nick = self.mainWin.textEdit.toPlainText()
            self.listener.start()
        elif (used == True):
            self.mainWin.label_2.setText("Użytkownik nie istnieje")

    def addNewUser(self):
        """
        measurement of parameters for a new user
        """
        self.mode = 'new'
        used = False
        records = self.selectFromDB()
        for row in records:
            if row[0] == self.mainWin.textEdit.toPlainText():
                used = True
                break
        if (self.mainWin.textEdit.toPlainText() != "" and used == False):
            self.resetParameters()
            self.mainWin.label.setText(
                "W Szczebrzeszynie chrząszcz brzmi w trzcinie. \nI Szczebrzeszyn z tego słynie.")
            self.mainWin.plainTextEdit.clear()
            self.mainWin.label_2.setText(
                "Przepisz tekst i zatwierdź przyciskiem lub kliknij ESC")
            self.nick = self.mainWin.textEdit.toPlainText()
            self.listener.start()
        elif (used == True):
            self.mainWin.label_2.setText("Nazwa użytkownika jest zajęta")
        elif (self.mainWin.textEdit.toPlainText() == ""):
            self.mainWin.label_2.setText("Podaj nazwę użytkownika")

    def on_press(self, key):
        """
        listener - measurement of parameters 
        """
        self.time_of_identification

        if self.time_of_identification == 0:
            self.time_of_identification = time.time()

        self.hold

        if self.hold != True:  # checking holding the key
            print('{0} pressed'.format(key))
            global start_time_press
            start_time_press = time.time()

            if self.start_time_release != 0:
                self.intervals_beetwen_keystrokes.append(
                    time.time() - self.start_time_release)

            self.symbols
            self.symbols = self.symbols+1

        self.correction_start
        self.time_correction
        self.losses_from_correction
        self.deleted_keys
        self.deleted_groups
        self.max_without_correction
        if key != Key.backspace:
            self.max_without_correction = 1 + self.max_without_correction

        if key == Key.backspace:
            self.deleted_keys = 1 + self.deleted_keys
        if key == Key.backspace and self.correction_start == True:
            self.correction_start = True
        if key == Key.backspace and self.correction_start == True:
            self.time_correction = time.time()
            self.correction_start = False
        if self.correction_start == False and key != Key.backspace:
            self.losses_from_correction.append(
                time.time() - self.time_correction)
            self.correction_start = True
            self.deleted_groups = self.deleted_groups + 1
        self.hold = True

    def on_release(self, key):
        """
        listener - measurement of parameters 
        """
        print('{0} release'.format(key))
        self.hold
        self.hold = False
        self.start_time_release
        self.start_time_release = time.time()
        self.intervals_beetwen_press_release.append(
            time.time()-start_time_press)
        if key == Key.esc:
            self.endOfWritting()
            return False
        if key == Key.space:
            self.words
            self.words = self.words + 1

    def endOfWritting(self):
        """
        complete measure
        """
        if self.mode == 'new':
            self.listener.stop()
            self.time_of_identification
            self.time_of_identification = time.time() - self.time_of_identification
            self.insertIntoDB()
        if self.mode == 'log':
            self.listener.stop()
            self.time_of_identification
            self.time_of_identification = time.time() - self.time_of_identification
            con = sqlite3.connect('measurements.db')
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            rekord = cur.execute(
                "SELECT * FROM person WHERE login='" + self.nick + "'")
            for row in rekord:
                if row[0] == self.nick:
                    ide = self.testLoginSucess(row)
                    if ide > 80:
                        self.mainWin.label_3.setText(
                            'Zgodność '+str(round(ide, 2))+'% z użytkownik '+self.nick+'. Identyfikacja poprawna.')
                    else:
                        self.mainWin.label_3.setText(
                            'Zgodność '+str(round(ide, 2))+'% z użytkownik '+self.nick+'. Identyfikacja nieprawidłowa.')
            con.commit()
            cur.close()
            
    def insertIntoDB(self):
        """
        insert into database - measurements.db
        """
        minPause = min(self.intervals_beetwen_keystrokes)
        maxPause = max(self.intervals_beetwen_keystrokes)
        averagePause = mean(self.intervals_beetwen_keystrokes)
        averageHold = mean(self.intervals_beetwen_press_release)
        symbolPerMinute = self.symbols/self.time_of_identification*60
        wordsPerMinute = self.words/self.time_of_identification*60
        lossesFromCorrection = sum(self.losses_from_correction)
        deletedKeys = self.deleted_keys
        deletedGroups = self.deleted_groups
        maxWithoutCorrection = self.max_without_correction
        con = sqlite3.connect('measurements.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('INSERT INTO person VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (self.nick, minPause, maxPause, averagePause, averageHold,
                     symbolPerMinute, wordsPerMinute, lossesFromCorrection,
                     deletedKeys, deletedGroups, maxWithoutCorrection))
        con.commit()
        cur.close()
        self.mainWin.label_2.setText("Dodano Nowego użytkownika !")

    def testLoginSucess(self, dataFromBase):
        """
        calculation of the similarity coefficient
        :return: float probableResult/probableRatioSum: similarity coefficient
        """
        dataFromLog = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        dataFromLog[1] = min(self.intervals_beetwen_keystrokes)
        dataFromLog[2] = max(self.intervals_beetwen_keystrokes)
        dataFromLog[3] = mean(self.intervals_beetwen_keystrokes)
        dataFromLog[4] = mean(self.intervals_beetwen_press_release)
        dataFromLog[5] = self.symbols/self.time_of_identification*60
        dataFromLog[6] = self.words/self.time_of_identification*60
        dataFromLog[7] = sum(self.losses_from_correction)
        dataFromLog[8] = self.deleted_keys
        dataFromLog[9] = self.deleted_groups
        dataFromLog[10] = self.max_without_correction

        probable = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for key in range(0, len(dataFromLog)):
            if key != 0:
                if dataFromLog[key] == 0 and dataFromBase[key] == 0:
                    probable[key-1] = 1
                elif dataFromLog[key] == 0 or dataFromBase[key] == 0:
                    if dataFromLog[key] == 1 or dataFromBase[key] == 1:
                        probable[key-1] = 0.5
                    elif dataFromLog[key] == 2 or dataFromBase[key] == 2:
                        probable[key-1] = 0.25
                    elif dataFromLog[key] == 3 or dataFromBase[key] == 3:
                        probable[key-1] = 0.1
                    else:
                        probable[key-1] = 0
                else:
                    if dataFromLog[key] < dataFromBase[key]:
                        probable[key-1] = (dataFromLog[key]/dataFromBase[key])
                    else:
                        probable[key-1] = (dataFromBase[key]/dataFromLog[key])

       
        probable2Chart = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        probableResult = 0
        probableRatioSum = 0

        probable[0] = math.sqrt(probable[0])
        probable[1] = math.sqrt(probable[1])
        probable[2] = math.sqrt(probable[2])
        probable[5] = math.sqrt(probable[5])

        for key in range(0, len(probable)):
            probable2Chart[key] = probable[key]
            if probable2Chart[key] > 0.7:
                probable2Chart[key] = probable2Chart[key] + \
                    probable2Chart[key] * (1-probable2Chart[key])
            else:
                probable2Chart[key] = probable2Chart[key] - \
                    probable2Chart[key] * (1-probable2Chart[key])
            probable2Chart[key] = probable2Chart[key] * 100
            probableResult += probable2Chart[key]*self.probableRatio[key]
            probableRatioSum += self.probableRatio[key]
        wector = ['minPause', 'maxPause', 'averagePause', 'averageHold', 'symbolPerMinut',
                  'wordsPerMinute', 'lossesFromCorrection', 'deletedKeys', 'deletedGroups', 'maxWithoutCorrection']

        
        fig, ax = plt.subplots(figsize=(50, 25))
        
        
        # Set tick font size
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        	label.set_fontsize(10)
        	
        ax.bar(wector, probable2Chart)
        plt.ylabel('Podobieństwo [%]', fontsize=15)
        plt.show()

        

        return probableResult/probableRatioSum

    def selectFromDB(self):
        """
        Read all records from database 
        :return: rows: records
        """
        con = sqlite3.connect('measurements.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM person;')
        rows = cur.fetchall()
        cur.close()
        return rows

"""## Main"""
if __name__ == "__main__":
    app = QApplication([])
    widget = Keyboard()
    widget.show()
    sys.exit(app.exec_())
