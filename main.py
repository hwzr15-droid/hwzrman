from kivy.app import App
from kivy.uix.label import Label

class DebtApp(App):
    def build(self):
        return Label(text= وكالة عبدالرحمن مبارك\nAM , font_size= 32sp )

if __name__ ==  __main__ :
    DebtApp().run()
