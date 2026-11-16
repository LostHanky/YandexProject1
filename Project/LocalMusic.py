import os
import sys
import io
import sqlite3
import librosa
import numpy as np

from PyQt6 import uic
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog,
    QListWidgetItem, QMessageBox, QPushButton,
)
from mutagen import File as MutagenFile

DB_PATH = "database.db"

# интерфейс
template = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>751</width>
    <height>540</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout" name="verticalLayout">
    <item>
     <layout class="QHBoxLayout" name="horizontalLayout_2">
      <item>
       <widget class="QPushButton" name="pushButton_AllTracks">
        <property name="text">
         <string>Мои треки</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QPushButton" name="pushButton_Playlist">
        <property name="text">
         <string>Плейлисты</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QPushButton" name="pushButton_sort">
        <property name="text">
         <string>Сортировка по настроению</string>
        </property>
       </widget>
      </item>
     </layout>
    </item>
    <item>
     <widget class="QStackedWidget" name="stackedWidget">
      <property name="currentIndex">
       <number>0</number>
      </property>
      <widget class="QWidget" name="page">
       <layout class="QVBoxLayout" name="verticalLayout_3">
        <item>
         <widget class="QPushButton" name="pushButton_addTrack">
          <property name="text">
           <string>+   Добавить трек</string>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QPushButton" name="pushButton_deleteTrack">
          <property name="text">
           <string>- Удалить трек</string>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QListWidget" name="listWidget_tracks"/>
        </item>
       </layout>
      </widget>
      <widget class="QWidget" name="page_2">
       <layout class="QVBoxLayout" name="verticalLayout_2">
        <item>
         <widget class="QPushButton" name="pushButton">
          <property name="text">
           <string>+  Создать плейлист</string>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QListWidget" name="listWidget"/>
        </item>
       </layout>
      </widget>
      <widget class="QWidget" name="page_3">
       <layout class="QVBoxLayout" name="verticalLayout_4">
        <item>
         <widget class="QLabel" name="label">
          <property name="text">
           <string>Выберите настроение:</string>
          </property>
         </widget>
        </item>
       </layout>
      </widget>
     </widget>
    </item>     
    <item>
     <layout class="QHBoxLayout" name="horizontalLayout">
      <item>
       <widget class="QLabel" name="currentMusic">
        <property name="text">
         <string>None</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QPushButton" name="pushButton_10">
        <property name="text">
         <string>-10 сек</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QPushButton" name="pushButton_Pause">
        <property name="text">
         <string>| |</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QPushButton" name="pushButton_Play">
        <property name="text">
         <string>▶</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QPushButton" name="pushButton10">
        <property name="text">
         <string>+10 сек</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QSlider" name="volumeSlider">
        <property name="sizePolicy">
         <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
          <horstretch>0</horstretch>
          <verstretch>0</verstretch>
         </sizepolicy>
        </property>
        <property name="orientation">
         <enum>Qt::Orientation::Horizontal</enum>
        </property>
       </widget>
      </item>
     </layout>
    </item>
   </layout>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>751</width>
     <height>33</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>
'''


class Example(QMainWindow):
    def __init__(self):
        super().__init__()

        # грузим интерфейс
        f = io.StringIO(template)
        uic.loadUi(f, self)

        # плеер
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)

        # громкость от 0 до 100
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(70)
        self.audio.setVolume(0.7)

        # кнопки плеера
        self.pushButton_Play.clicked.connect(self.player.play)
        self.pushButton_Pause.clicked.connect(self.player.pause)
        self.pushButton_10.clicked.connect(self.nazad)
        self.pushButton10.clicked.connect(self.vpered)
        self.volumeSlider.valueChanged.connect(self.gromkost)

        # кнопки треков
        self.pushButton_addTrack.clicked.connect(self.add_track)
        self.pushButton_deleteTrack.clicked.connect(self.del_track)
        self.listWidget_tracks.itemClicked.connect(self.play_track)

        # вкладки
        self.pushButton_AllTracks.clicked.connect(self.show_all_tracks)
        # добавил лямбду тк в коннект нельзя засунуть аргумент функции, т.е. пришлось бы под каждый коннект создавать по отдельной функции где бы мы и ставили аргументы(ну номера вкладок)
        self.pushButton_Playlist.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.pushButton_sort.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        self.listWidget.addItem("Пока в разработке")

        # база
        self.create_table()
        self.load_tracks()

        self.moods = ["Энергичное", "Бодрое", "Нейтральное", "Грустное", "Спокойное", "Все"]
        self.build_mood_buttons()

    # бд

    def create_table(self):
        # создание таблицы
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                title TEXT,
                artist TEXT,
                duration INTEGER,
                plays INTEGER DEFAULT 0,
                mood TEXT DEFAULT 'Неизвестно'
            )
        """)
        conn.commit()
        conn.close()

    def load_tracks(self, mood=None):
        self.listWidget_tracks.clear()

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        if mood is None or mood == "Все":
            cur.execute("SELECT id, file_path, title, artist FROM tracks ORDER BY artist, title")
        else:
            cur.execute(
                "SELECT id, file_path, title, artist FROM tracks WHERE mood = ? ORDER BY artist, title",
                (mood,)
            )
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            track_id = row[0]
            path = row[1]
            title = row[2]
            artist = row[3]

            if not artist:
                artist = "Неизвестен"
            if not title:
                title = os.path.basename(path)

            text = artist + " — " + title

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, {
                "id": track_id,
                "path": path,
                "name": text
            })
            self.listWidget_tracks.addItem(item)

    def add_track(self):
        # открытие файла
        fname, _ = QFileDialog.getOpenFileName(
            self,
            "Выбери трек",
            "",
            "Аудио (*.mp3 *.wav *.flac *.ogg *.m4a);;Все файлы (*)"
        )
        if not fname:
            return

        try:
            # читаем теги с мутагеном
            audio = MutagenFile(fname)
            if audio is None:
                QMessageBox.warning(self, "Ошибка", "Не могу прочитать файл")
                return

            title = ""
            artist = ""
            if "title" in audio:
                title = str(audio["title"][0])
            if "artist" in audio:
                artist = str(audio["artist"][0])

            duration = 0
            if hasattr(audio, "info"):
                duration = int(audio.info.length * 1000)

            mood, bpm, centroid = self.get_mood(fname)

            # если пользователь добавит одно и тоже второй раз
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id FROM tracks WHERE file_path = ?", (fname,))
            if cur.fetchone() is not None:
                conn.close()
                QMessageBox.information(self, "Ошибка", "Трек уже добавлен")
                return

            # добавление в бд
            cur.execute(
                "INSERT INTO tracks (file_path, title, artist, duration, mood) VALUES (?, ?, ?, ?, ?)",
                (fname, title, artist, duration, mood)
            )
            conn.commit()
            conn.close()

            self.load_tracks()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def del_track(self):
        # берём выбранный элемент, сразу проверяем
        item = self.listWidget_tracks.currentItem()
        if item is None:
            QMessageBox.warning(self, "Ошибка", "Выберите трек")
            return

        info = item.data(Qt.ItemDataRole.UserRole)

        # спрашиваем точно ли удалять
        otvet = QMessageBox.question(
            self,
            "Удалить?",
            "Точно удалить '" + info["name"] + "'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if otvet != QMessageBox.StandardButton.Yes:
            return

        # удаление из бд
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM tracks WHERE id = ?", (info["id"],))
        conn.commit()
        conn.close()

        self.load_tracks()

    # настроение

    def get_mood(self, file_path):
        # прогружаем 30сек чтобы не ждать долго на длинных треках
        y, sr = librosa.load(file_path, sr=22050, mono=True, duration=15)

        # бпм
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(np.atleast_1d(tempo)[0])

        # герцовка
        centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

        # пороги настроения
        if bpm >= 120 and centroid >= 2000:
            mood = "Энергичное"
        elif bpm >= 120 and centroid < 2000:
            mood = "Бодрое"
        elif bpm < 90 and centroid < 1500:
            mood = "Спокойное"
        elif bpm < 90 and centroid >= 1500:
            mood = "Грустное"
        else:
            mood = "Нейтральное"

        return mood, bpm, centroid

    # строим кнопки в настроении
    def build_mood_buttons(self):
        for mood in self.moods:
            btn = QPushButton(mood)
            btn.setMinimumHeight(40)
            btn.clicked.connect(self.on_mood_clicked)
            self.verticalLayout_4.addWidget(btn)

    # принимаем кнопку и передаем в show_mood()
    def on_mood_clicked(self):
        btn = self.sender()
        self.show_mood(btn.text())

    # фильтрация по настроению
    def show_mood(self, mood):
        self.load_tracks(mood)
        self.stackedWidget.setCurrentIndex(0)

    # показывает все треки
    def show_all_tracks(self):
        self.load_tracks()
        self.stackedWidget.setCurrentIndex(0)

    # управление плеером

    def play_track(self, item):
        info = item.data(Qt.ItemDataRole.UserRole)
        if info is None:
            return

        url = QUrl.fromLocalFile(info["path"])
        self.player.setSource(url)
        self.player.play()

        self.currentMusic.setText(info["name"])

        # пока тоже нигде не используется, еще доделаю
        # +1 прослушивание
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE tracks SET plays = plays + 1 WHERE id = ?", (info["id"],))
        conn.commit()
        conn.close()

    def gromkost(self, value):
        self.audio.setVolume(value / 100)

    def vpered(self):
        self.player.setPosition(self.player.position() + 10000)

    def nazad(self):
        pos = self.player.position() - 10000
        if pos < 0:
            pos = 0
        self.player.setPosition(pos)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())