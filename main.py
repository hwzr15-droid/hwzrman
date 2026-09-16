# -*- coding: utf-8 -*-
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import sqlite3
import os
from datetime import datetime

# ====== إعدادات الخلفية ======
Window.clearcolor = get_color_from_hex( #F5F5F5 )

# ====== قاعدة البيانات ======
DB_PATH = os.path.join(os.path.expanduser( ~ ),  debt_app.db )

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
        date TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )   )
    conn.commit()
    conn.close()

# ====== دالة مساعدة ======
def get_balance(client_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE client_id=? AND type= debt ", (client_id,))
    debts = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE client_id=? AND type= payment ", (client_id,))
    payments = c.fetchone()[0]
    conn.close()
    return debts - payments

# ====== الشاشة الرئيسية ======
class HomeScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name =  home 
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation= vertical )
        self.toolbar = MDTopAppBar(
            title= وكالة عبدالرحمن مبارك ,
            md_bg_color=get_color_from_hex( #1A237E ),
            specific_text_color=(1, 1, 1, 1),
            left_action_items=[[ menu , lambda x: None]],
        )
        layout.add_widget(self.toolbar)

        sub = MDLabel(
            text= محاسبة المديونية ,
            halign= center ,
            theme_text_color= Custom ,
            text_color=get_color_from_hex( #1A237E ),
            font_style= H6 ,
            size_hint_y=None,
            height=dp(40),
        )
        layout.add_widget(sub)

        self.scroll = MDScrollView()
        self.list_layout = MDList()
        self.scroll.add_widget(self.list_layout)
        layout.add_widget(self.scroll)

        buttons = MDBoxLayout(size_hint_y=None, height=dp(60), padding=dp(10), spacing=dp(10))
        btn_add = MDRaisedButton(text= إضافة عميل , md_bg_color=get_color_from_hex( #1A237E ))
        btn_add.bind(on_release=lambda x: self.app.show_add_client())
        buttons.add_widget(btn_add)

        btn_refresh = MDRaisedButton(text= تحديث , md_bg_color=get_color_from_hex( #3949AB ))
        btn_refresh.bind(on_release=lambda x: self.load_clients())
        buttons.add_widget(btn_refresh)

        layout.add_widget(buttons)
        self.add_widget(layout)

    @property
    def app(self):
        return MDApp.get_running_app()

    def load_clients(self):
        self.list_layout.clear_widgets()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, name, phone FROM clients ORDER BY name")
        clients = c.fetchall()
        conn.close()

        if not clients:
            self.list_layout.add_widget(MDLabel(
                text= لا يوجد عملاء بعد. اضغط "إضافة عميل" للبدء. ,
                halign= center ,
                theme_text_color= Custom ,
                text_color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(60),
            ))
            return

        for cid, name, phone in clients:
            balance = get_balance(cid)
            color =  #2E7D32  if balance >= 0 else  #C62828 
            item = TwoLineAvatarIconListItem(
                text=f {name} ,
                secondary_text=f الرصيد: {balance:.2f} ريال ,
            )
            item.add_widget(IconLeftWidget(icon= account-circle ))
            arrow = IconRightWidget(icon= chevron-left )
            arrow.bind(on_release=lambda x, c=cid, n=name: self.app.show_client(c, n))
            item.add_widget(arrow)
            item.bind(on_release=lambda x, c=cid, n=name: self.app.show_client(c, n))
            self.list_layout.add_widget(item)

    def on_enter(self):
        self.load_clients()

# ====== شاشة تفاصيل العميل ======
class ClientScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name =  client 
        self.client_id = None
        self.client_name =   
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation= vertical )
        self.toolbar = MDTopAppBar(
            title= تفاصيل العميل ,
            md_bg_color=get_color_from_hex( #1A237E ),
            specific_text_color=(1, 1, 1, 1),
            left_action_items=[[ arrow-right , lambda x: self.app.go_home()]],
        )
        layout.add_widget(self.toolbar)

        self.balance_label = MDLabel(
            text=  ,
            halign= center ,
            theme_text_color= Custom ,
            text_color=(0, 0, 0, 1),
            font_style= H6 ,
            size_hint_y=None,
            height=dp(60),
        )
        layout.add_widget(self.balance_label)

        self.scroll = MDScrollView()
        self.tx_layout = MDList()
        self.scroll.add_widget(self.tx_layout)
        layout.add_widget(self.scroll)

        buttons = MDBoxLayout(size_hint_y=None, height=dp(60), padding=dp(10), spacing=dp(10))
        btn_debt = MDRaisedButton(text= تسجيل دين , md_bg_color=get_color_from_hex( #C62828 ))
        btn_debt.bind(on_release=lambda x: self.app.show_add_transaction( debt ))
        buttons.add_widget(btn_debt)

        btn_pay = MDRaisedButton(text= تسجيل دفعة , md_bg_color=get_color_from_hex( #2E7D32 ))
        btn_pay.bind(on_release=lambda x: self.app.show_add_transaction( payment ))
        buttons.add_widget(btn_pay)

        layout.add_widget(buttons)
        self.add_widget(layout)

    @property
    def app(self):
        return MDApp.get_running_app()

    def load_transactions(self):
        self.tx_layout.clear_widgets()
        if not self.client_id:
            return
        balance = get_balance(self.client_id)
        color =  #2E7D32  if balance >= 0 else  #C62828 
        self.balance_label.text = f {self.client_name} - الرصيد: {balance:.2f} 
        self.balance_label.text_color = get_color_from_hex(color)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, type, amount, note, date FROM transactions WHERE client_id=? ORDER BY date DESC", (self.client_id,))
        txs = c.fetchall()
        conn.close()

        for tid, ttype, amount, note, date in txs:
            icon =  cash-plus  if ttype ==  debt  else  cash-check 
            label =  دين  if ttype ==  debt  else  دفعة 
            sign =  +  if ttype ==  debt  else  - 
            item = TwoLineAvatarIconListItem(
                text=f {label}: {sign}{amount:.2f} ,
                secondary_text=f {date} - {note or ""} ,
            )
            item.add_widget(IconLeftWidget(icon=icon))
            del_btn = IconRightWidget(icon= delete )
            del_btn.bind(on_release=lambda x, t=tid: self.app.delete_transaction(t))
            item.add_widget(del_btn)
            self.tx_layout.add_widget(item)

    def on_enter(self):
        self.load_transactions()

# ====== التطبيق ======
class DebtApp(MDApp):
    def build(self):
        self.title =  وكالة عبدالرحمن مبارك 
        self.theme_cls.primary_palette =  Indigo 
        self.theme_cls.theme_style =  Light 
        init_db()

        self.sm = MDScreenManager()
        self.home = HomeScreen()
        self.client = ClientScreen()
        self.sm.add_widget(self.home)
        self.sm.add_widget(self.client)
        return self.sm

    def go_home(self):
        self.sm.current =  home 

    def show_add_client(self):
        name_field = MDTextField(hint_text= اسم العميل , mode= rectangle )
        phone_field = MDTextField(hint_text= رقم الهاتف (اختياري) , mode= rectangle )
        content = MDBoxLayout(orientation= vertical , spacing=dp(10), size_hint_y=None, height=dp(150))
        content.add_widget(name_field)
        content.add_widget(phone_field)

        def save(instance):
            name = name_field.text.strip()
            phone = phone_field.text.strip()
            if not name:
                return
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO clients (name, phone, created_at) VALUES (?,?,?)",
                      (name, phone, datetime.now().strftime( %Y-%m-%d %H:%M )))
            conn.commit()
            conn.close()
            dialog.dismiss()
            self.home.load_clients()

        dialog = MDDialog(
            title= إضافة عميل جديد ,
            type= custom ,
            content_cls=content,
            buttons=[
                MDFlatButton(text= إلغاء , on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text= حفظ , on_release=save),
            ],
        )
        dialog.open()

    def show_client(self, client_id, client_name):
        self.client.client_id = client_id
        self.client.client_name = client_name
        self.client.load_transactions()
        self.sm.current =  client 

    def show_add_transaction(self, ttype):
        amount_field = MDTextField(hint_text= المبلغ , input_filter= float , mode= rectangle )
        note_field = MDTextField(hint_text= ملاحظة (اختياري) , mode= rectangle )
        date_field = MDTextField(text=datetime.now().strftime( %Y-%m-%d ), hint_text= التاريخ , mode= rectangle )
        content = MDBoxLayout(orientation= vertical , spacing=dp(10), size_hint_y=None, height=dp(200))
        content.add_widget(amount_field)
        content.add_widget(note_field)
        content.add_widget(date_field)

        title =  تسجيل دين  if ttype ==  debt  else  تسجيل دفعة 

        def save(instance):
            try:
                amount = float(amount_field.text)
            except:
                return
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO transactions (client_id, type, amount, note, date) VALUES (?,?,?,?,?)",
                      (self.client.client_id, ttype, amount, note_field.text, date_field.text))
            conn.commit()
            conn.close()
            dialog.dismiss()
            self.client.load_transactions()

        dialog = MDDialog(
            title=title,
            type= custom ,
            content_cls=content,
            buttons=[
                MDFlatButton(text= إلغاء , on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text= حفظ , on_release=save),
            ],
        )
        dialog.open()

    def delete_transaction(self, tid):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE id=?", (tid,))
        conn.commit()
        conn.close()
        self.client.load_transactions()

if __name__ ==  __main__ :
    DebtApp().run()
