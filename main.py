# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
import sqlite3
import os
from datetime import datetime

Window.clearcolor = get_color_from_hex( #F5F5F5 )

DB_PATH = os.path.join(os.path.expanduser( ~ ),  debt_app.db )

KV =    
<RTLBox@BoxLayout>:
    orientation:  vertical 

<MyButton@Button>:
    background_normal:   
    background_color: 0.1, 0.14, 0.49, 1
    color: 1, 1, 1, 1
    font_size:  16sp 
    size_hint_y: None
    height:  48dp 

<MyInput@TextInput>:
    multiline: False
    size_hint_y: None
    height:  44dp 
    font_size:  16sp 
    padding: [10, 10]
   

Builder.load_string(KV)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(   CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        created_at TEXT
    )   )
    c.execute(   CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        type TEXT,
        amount REAL,
        note TEXT,
        date TEXT
    )   )
    conn.commit()
    conn.close()

def get_balance(client_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE client_id=? AND type= debt ", (client_id,))
    debts = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE client_id=? AND type= payment ", (client_id,))
    payments = c.fetchone()[0]
    conn.close()
    return debts - payments


class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name =  home 
        root = BoxLayout(orientation= vertical )

        # Header with AM background
        header = BoxLayout(orientation= vertical , size_hint_y=None, height=dp(100))
        with header.canvas.before:
            Color(0.1, 0.14, 0.49, 1)
            self.rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self._update_rect, size=self._update_rect)

        self.am_label = Label(
            text= AM ,
            font_size= 48sp ,
            color=(1, 1, 1, 0.15),
            bold=True,
        )
        header.add_widget(self.am_label)

        title = Label(
            text= وكالة عبدالرحمن مبارك ,
            font_size= 20sp ,
            color=(1, 1, 1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(30),
        )
        header.add_widget(title)

        sub = Label(
            text= محاسبة المديونية ,
            font_size= 14sp ,
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
            height=dp(25),
        )
        header.add_widget(sub)

        root.add_widget(header)

        self.scroll = ScrollView()
        self.list_box = BoxLayout(orientation= vertical , size_hint_y=None, spacing=dp(5), padding=dp(5))
        self.list_box.bind(minimum_height=self.list_box.setter( height ))
        self.scroll.add_widget(self.list_box)
        root.add_widget(self.scroll)

        btn_box = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5), padding=dp(5))
        btn_add = Button(text= إضافة عميل , background_normal=  , background_color=(0.1, 0.14, 0.49, 1), color=(1,1,1,1))
        btn_add.bind(on_release=lambda x: self.show_add_client())
        btn_box.add_widget(btn_add)
        btn_refresh = Button(text= تحديث , background_normal=  , background_color=(0.22, 0.29, 0.67, 1), color=(1,1,1,1))
        btn_refresh.bind(on_release=lambda x: self.load_clients())
        btn_box.add_widget(btn_refresh)
        root.add_widget(btn_box)

        self.add_widget(root)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_enter(self):
        self.load_clients()

    def load_clients(self):
        self.list_box.clear_widgets()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, name, phone FROM clients ORDER BY name")
        clients = c.fetchall()
        conn.close()

        if not clients:
            lbl = Label(text= لا يوجد عملاء بعد.\nاضغط "إضافة عميل" للبدء. , halign= center , size_hint_y=None, height=dp(100), color=(0.5, 0.5, 0.5, 1))
            self.list_box.add_widget(lbl)
            return

        for cid, name, phone in clients:
            balance = get_balance(cid)
            color = (0.18, 0.49, 0.20, 1) if balance >= 0 else (0.78, 0.16, 0.16, 1)
            btn = Button(
                text= %s\nالرصيد: %.2f  % (name, balance),
                size_hint_y=None,
                height=dp(70),
                background_normal=  ,
                background_color=(1, 1, 1, 1),
                color=color,
                halign= right ,
            )
            btn.bind(on_release=lambda x, c=cid, n=name: self.open_client(c, n))
            self.list_box.add_widget(btn)

    def open_client(self, cid, name):
        app = App.get_running_app()
        app.client_id = cid
        app.client_name = name
        app.root.current =  client 
        app.root.get_screen( client ).load_transactions()

    def show_add_client(self):
        box = BoxLayout(orientation= vertical , spacing=dp(10), padding=dp(10))
        name_in = TextInput(hint_text= اسم العميل , multiline=False, size_hint_y=None, height=dp(44))
        phone_in = TextInput(hint_text= رقم الهاتف (اختياري) , multiline=False, size_hint_y=None, height=dp(44))
        box.add_widget(name_in)
        box.add_widget(phone_in)

        popup = Popup(title= إضافة عميل جديد , content=box, size_hint=(0.9, 0.4))

        def save(instance):
            name = name_in.text.strip()
            phone = phone_in.text.strip()
            if not name:
                return
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO clients (name, phone, created_at) VALUES (?,?,?)",
                      (name, phone, datetime.now().strftime( %Y-%m-%d %H:%M )))
            conn.commit()
            conn.close()
            popup.dismiss()
            self.load_clients()

        btn_save = Button(text= حفظ , size_hint_y=None, height=dp(44), background_normal=  , background_color=(0.1, 0.14, 0.49, 1), color=(1,1,1,1))
        btn_save.bind(on_release=save)
        box.add_widget(btn_save)
        popup.open()


class ClientScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name =  client 
        root = BoxLayout(orientation= vertical )

        header = BoxLayout(orientation= vertical , size_hint_y=None, height=dp(90))
        with header.canvas.before:
            Color(0.1, 0.14, 0.49, 1)
            self.rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self._update_rect, size=self._update_rect)

        self.balance_label = Label(text=  , font_size= 18sp , color=(1, 1, 1, 1), bold=True)
        header.add_widget(self.balance_label)

        btn_back = Button(text= ← رجوع , size_hint=(None, None), size=(dp(80), dp(30)), pos_hint={ right : 1}, background_normal=  , background_color=(0.2, 0.2, 0.2, 0.5), color=(1,1,1,1))
        btn_back.bind(on_release=lambda x: self.go_back())
        header.add_widget(btn_back)

        root.add_widget(header)

        self.scroll = ScrollView()
        self.tx_box = BoxLayout(orientation= vertical , size_hint_y=None, spacing=dp(5), padding=dp(5))
        self.tx_box.bind(minimum_height=self.tx_box.setter( height ))
        self.scroll.add_widget(self.tx_box)
        root.add_widget(self.scroll)

        btn_box = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5), padding=dp(5))
        btn_debt = Button(text= تسجيل دين , background_normal=  , background_color=(0.78, 0.16, 0.16, 1), color=(1,1,1,1))
        btn_debt.bind(on_release=lambda x: self.show_add_tx( debt ))
        btn_box.add_widget(btn_debt)
        btn_pay = Button(text= تسجيل دفعة , background_normal=  , background_color=(0.18, 0.49, 0.20, 1), color=(1,1,1,1))
        btn_pay.bind(on_release=lambda x: self.show_add_tx( payment ))
        btn_box.add_widget(btn_pay)
        root.add_widget(btn_box)

        self.add_widget(root)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_back(self):
        App.get_running_app().root.current =  home 

    def load_transactions(self):
        self.tx_box.clear_widgets()
        app = App.get_running_app()
        cid = app.client_id
        if not cid:
            return
        balance = get_balance(cid)
        color = (0.18, 0.49, 0.20, 1) if balance >= 0 else (0.78, 0.16, 0.16, 1)
        self.balance_label.text =  %s - الرصيد: %.2f  % (app.client_name, balance)
        self.balance_label.color = color

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, type, amount, note, date FROM transactions WHERE client_id=? ORDER BY date DESC", (cid,))
        txs = c.fetchall()
        conn.close()

        for tid, ttype, amount, note, date in txs:
            label =  دين  if ttype ==  debt  else  دفعة 
            sign =  +  if ttype ==  debt  else  - 
            text =  %s: %s%.2f\n%s - %s  % (label, sign, amount, date, note or   )
            btn = Button(
                text=text,
                size_hint_y=None,
                height=dp(70),
                background_normal=  ,
                background_color=(1, 1, 1, 1),
                color=(0.2, 0.2, 0.2, 1),
                halign= right ,
            )
            btn.bind(on_release=lambda x, t=tid: self.delete_tx(t))
            self.tx_box.add_widget(btn)

    def show_add_tx(self, ttype):
        box = BoxLayout(orientation= vertical , spacing=dp(10), padding=dp(10))
        amount_in = TextInput(hint_text= المبلغ , input_filter= float , multiline=False, size_hint_y=None, height=dp(44))
        note_in = TextInput(hint_text= ملاحظة (اختياري) , multiline=False, size_hint_y=None, height=dp(44))
        date_in = TextInput(text=datetime.now().strftime( %Y-%m-%d ), multiline=False, size_hint_y=None, height=dp(44))
        box.add_widget(amount_in)
        box.add_widget(note_in)
        box.add_widget(date_in)

        title =  تسجيل دين  if ttype ==  debt  else  تسجيل دفعة 
        popup = Popup(title=title, content=box, size_hint=(0.9, 0.5))

        def save(instance):
            try:
                amount = float(amount_in.text)
            except:
                return
            app = App.get_running_app()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO transactions (client_id, type, amount, note, date) VALUES (?,?,?,?,?)",
                      (app.client_id, ttype, amount, note_in.text, date_in.text))
            conn.commit()
            conn.close()
            popup.dismiss()
            self.load_transactions()

        btn_save = Button(text= حفظ , size_hint_y=None, height=dp(44), background_normal=  , background_color=(0.1, 0.14, 0.49, 1), color=(1,1,1,1))
        btn_save.bind(on_release=save)
        box.add_widget(btn_save)
        popup.open()

    def delete_tx(self, tid):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE id=?", (tid,))
        conn.commit()
        conn.close()
        self.load_transactions()


class DebtApp(App):
    client_id = None
    client_name =   

    def build(self):
        self.title =  وكالة عبدالرحمن مبارك 
        init_db()
        sm = ScreenManager()
        sm.add_widget(HomeScreen())
        sm.add_widget(ClientScreen())
        return sm


if __name__ ==  __main__ :
    DebtApp().run()
