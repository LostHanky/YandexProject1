import sys
import io
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow

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
  <property name="baseSize">
   <size>
    <width>0</width>
    <height>0</height>
   </size>
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
         <widget class="QListWidget" name="listWidget_tracks">
          <property name="enabled">
           <bool>true</bool>
          </property>
         </widget>
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
        <item>
         <widget class="QListWidget" name="listWidget_2"/>
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
       <widget class="QPushButton" name="pushButton_Continue">
        <property name="text">
         <string>| |</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QPushButton" name="pushButton_Pause">
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
        f = io.StringIO(template)
        uic.loadUi(f, self)
        self.initUI()

    def initUI(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = Example()
    ex.show()

    sys.exit(app.exec())