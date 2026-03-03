import os
import hashlib
import random
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.graphics import Color, RoundedRectangle
from kivy.storage.jsonstore import JsonStore
from kivy.core.audio import SoundLoader

# --- הגדרות מערכת ---
Window.softinput_mode = "below_target"
store = JsonStore('user_session.json')
DB_URL = "https://triviaquizapp-8b15c-default-rtdb.firebaseio.com/"

def clean_text(text):
    if not text: return ""
    return str(text).replace('\\', '').replace('"', '').strip()

def fix(text):
    text = clean_text(text)
    try:
        words = text.split(' ')
        fixed_words = [word[::-1] if any('\u0590' <= char <= '\u05ff' for char in word) else word for word in words]
        return ' '.join(fixed_words[::-1])
    except: return text

FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'arial.ttf')
if os.path.exists(FONT_PATH):
    LabelBase.register(name='Hebrew', fn_regular=FONT_PATH)

# --- צבעים ---
BG_COLOR = (0.117, 0.117, 0.18, 1)
CARD_COLOR = (0.165, 0.165, 0.239, 1)
INPUT_BG = (0.227, 0.227, 0.302, 1)
BTN_GREEN = (0.298, 0.686, 0.314, 1)
BTN_BLUE = (0.129, 0.588, 0.953, 1)
BTN_EXIT = (1, 0.333, 0.333, 1)
BTN_ORANGE = (1, 0.596, 0, 1)
TEXT_GRAY = (0.73, 0.73, 0.73, 1)

Window.clearcolor = BG_COLOR

def hash_p(p):
    return hashlib.sha256((p + "TriviaPro2026").encode()).hexdigest()

class ModernButton(Button):
    def __init__(self, bg_color=BTN_GREEN, radius=[12], **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.font_name = 'Hebrew'
        self.bold = True
        self.my_bg_color = bg_color
        self.size_hint_y = None
        self.height = 60
        with self.canvas.before:
            Color(rgba=self.my_bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=lambda ins, v: setattr(self.rect, 'pos', v), size=lambda ins, v: setattr(self.rect, 'size', v))

class CardInput(BoxLayout):
    def __init__(self, label_text, is_password=False, **kwargs):
        super().__init__(orientation='vertical', spacing=5, size_hint_y=None, height=100, **kwargs)
        self.add_widget(Label(text=fix(label_text), font_name='Hebrew', color=TEXT_GRAY, size_hint_y=None, height=30, halign="right"))
        self.input = TextInput(password=is_password, multiline=False, background_color=INPUT_BG, foreground_color=(1, 1, 1, 1), font_name='Hebrew', font_size='18sp', padding=[15, 12], size_hint_y=None, height=55)
        self.add_widget(self.input)

# --- מסכים ---

class MenuScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        uname = App.get_running_app().current_user
        layout.add_widget(Label(text=fix("🎮 Trivia Quiz Game"), font_name='Hebrew', font_size='36sp', bold=True))
        if uname:
            layout.add_widget(Label(text=fix(f"שלום, {uname}"), font_name='Hebrew', color=BTN_BLUE, font_size='20sp'))
            layout.add_widget(ModernButton(text=fix("התחל משחק"), on_release=lambda x: setattr(self.manager, 'current', 'game')))
            layout.add_widget(ModernButton(text=fix("הפרופיל שלי"), bg_color=BTN_BLUE, on_release=lambda x: setattr(self.manager, 'current', 'profile')))
            layout.add_widget(ModernButton(text=fix("לוח תוצאות"), bg_color=BTN_ORANGE, on_release=lambda x: setattr(self.manager, 'current', 'score')))
            layout.add_widget(ModernButton(text=fix("התנתק"), bg_color=BTN_EXIT, on_release=self.logout))
        else:
            layout.add_widget(ModernButton(text=fix("התחברות"), on_release=lambda x: setattr(self.manager, 'current', 'login')))
            layout.add_widget(ModernButton(text=fix("הרשמה"), bg_color=BTN_BLUE, on_release=lambda x: setattr(self.manager, 'current', 'register')))
        layout.add_widget(ModernButton(text=fix("יציאה"), bg_color=(0.2, 0.2, 0.2, 1), on_release=lambda x: App.get_running_app().stop()))
        self.add_widget(layout)

    def logout(self, x):
        if store.exists('user'): store.delete('user')
        App.get_running_app().current_user = None
        self.on_enter()

class ProfileScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        uname = App.get_running_app().current_user
        layout.add_widget(Label(text=fix("👤 הפרופיל שלי"), font_name='Hebrew', font_size='32sp', bold=True))
        pts = 0
        try:
            res = requests.get(f"{DB_URL}users/{uname}.json", timeout=5).json()
            pts = float(res.get('points', 0)) if res else 0.0
        except: pass
        # תצוגה נקייה של הניקוד
        display_pts = int(pts) if pts == int(pts) else pts
        layout.add_widget(Label(text=fix(f"שם משתמש: {uname}"), font_name='Hebrew', font_size='22sp'))
        layout.add_widget(Label(text=fix(f"ניקוד כולל: {display_pts}"), font_name='Hebrew', font_size='26sp', color=BTN_ORANGE))
        layout.add_widget(ModernButton(text=fix("חזרה"), bg_color=(0.3, 0.3, 0.3, 1), on_release=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(layout)

class GameScreen(Screen):
    def on_enter(self):
        self.questions = self.fetch_qs()
        self.idx, self.score, self.timer_val = 0, 0.0, 15
        self.hint_used = False
        self.next_question()

    def play_sound(self, state):
        try:
            sound = SoundLoader.load(f"sounds/{state}.mp3")
            if sound: sound.play()
        except: pass

    def fetch_qs(self):
        try:
            res = requests.get(f"{DB_URL}questions.json", timeout=5).json()
            if res:
                qs = [{"q": v['q'], "a": v['a']} for v in res if v and 'q' in v]
                random.shuffle(qs); return qs[:10]
        except: pass
        return [{"q": "שגיאה בטעינה", "a": "---"}]

    def next_question(self):
        self.clear_widgets()
        if self.idx >= len(self.questions):
            self.save_score_and_exit('score'); return
        self.timer_val = 15
        self.hint_used = False
        q_data = self.questions[self.idx]
        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=10)
        header = BoxLayout(size_hint_y=None, height=40)
        header.add_widget(Label(text=fix(f"שאלה {self.idx + 1}/10"), font_name='Hebrew', bold=True))
        self.lbl_timer = Label(text=f"⏱️ {self.timer_val}", color=BTN_ORANGE, font_size='20sp', bold=True)
        header.add_widget(self.lbl_timer); self.layout.add_widget(header)
        q_card = AnchorLayout(size_hint_y=None, height=120)
        with q_card.canvas.before:
            Color(rgba=CARD_COLOR); self.rect = RoundedRectangle(pos=q_card.pos, size=q_card.size, radius=[15])
        q_card.bind(pos=lambda ins, v: setattr(self.rect, 'pos', v), size=lambda ins, v: setattr(self.rect, 'size', v))
        q_card.add_widget(Label(text=fix(q_data['q']), font_name='Hebrew', font_size='20sp', halign="center", text_size=(Window.width - 60, None)))
        self.layout.add_widget(q_card)
        self.feedback_lbl = Label(text="", font_name='Hebrew', font_size='16sp', size_hint_y=None, height=30)
        self.layout.add_widget(self.feedback_lbl)
        self.ans_in = TextInput(hint_text=fix("תשובה..."), multiline=False, size_hint_y=None, height=55, font_name='Hebrew', font_size='18sp')
        self.layout.add_widget(self.ans_in)
        self.btn_check = ModernButton(text=fix("בדוק"), on_release=self.check_answer)
        self.layout.add_widget(self.btn_check)
        self.btn_hint = ModernButton(text=fix("רמז (0.5- נק')"), bg_color=BTN_BLUE, height=45, on_release=self.use_hint)
        self.layout.add_widget(self.btn_hint)
        self.layout.add_widget(ModernButton(text=fix("פרוש ושמור"), bg_color=BTN_EXIT, height=45, on_release=lambda x: self.save_score_and_exit('menu')))
        self.add_widget(self.layout)
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def use_hint(self, x):
        if not self.hint_used:
            self.hint_used = True
            self.btn_hint.disabled = True # מניעת לחיצה כפולה
            ans_part = clean_text(self.questions[self.idx]['a']).split('/')[0]
            if ans_part:
                self.feedback_lbl.text = fix(f"רמז: האות הראשונה היא '{ans_part[0]}'")

    def update_timer(self, dt):
        self.timer_val -= 1
        self.lbl_timer.text = f"⏱️ {self.timer_val}"
        if self.timer_val <= 0: self.check_answer()

    def check_answer(self, *args):
        Clock.unschedule(self.timer_event)
        self.btn_check.disabled = True
        self.btn_hint.disabled = True
        raw_correct = clean_text(self.questions[self.idx]['a']).lower()
        correct_list = [a.strip() for a in raw_correct.split('/')]
        user_ans = self.ans_in.text.strip().lower()
        if user_ans in correct_list:
            pts = 0.5 if self.hint_used else 1.0
            self.score += pts
            self.feedback_lbl.text = fix(f"✅ נכון! (+{pts})"); self.feedback_lbl.color = BTN_GREEN
            self.play_sound("correct")
        else:
            self.feedback_lbl.text = fix(f"❌ טעות. התשובה: {correct_list[0]}"); self.feedback_lbl.color = BTN_EXIT
            self.play_sound("wrong")
        Clock.schedule_once(lambda dt: self.go_next(), 1.5)

    def go_next(self):
        self.idx += 1; self.next_question()

    def save_score_and_exit(self, next_screen):
        if hasattr(self, 'timer_event'): Clock.unschedule(self.timer_event)
        uname = App.get_running_app().current_user
        if uname and self.score > 0:
            try:
                res = requests.get(f"{DB_URL}users/{uname}.json", timeout=5).json()
                old_pts = float(res.get('points', 0)) if res else 0.0
                requests.patch(f"{DB_URL}users/{uname}.json", json={"points": old_pts + float(self.score)})
            except: pass
        self.manager.current = next_screen

class LoginScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        l = BoxLayout(orientation='vertical', padding=40, spacing=20)
        l.add_widget(Label(text=fix("🔑 התחברות"), font_name='Hebrew', font_size='32sp', bold=True))
        self.u_box = CardInput("שם משתמש")
        self.p_box = CardInput("סיסמה", is_password=True)
        self.msg = Label(text="", color=BTN_EXIT, font_name='Hebrew', size_hint_y=None, height=30)
        l.add_widget(self.u_box); l.add_widget(self.p_box); l.add_widget(self.msg)
        l.add_widget(ModernButton(text=fix("התחבר"), on_release=self.do_login))
        l.add_widget(ModernButton(text=fix("חזרה"), bg_color=(0.3, 0.3, 0.3, 1), on_release=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(l)

    def do_login(self, x):
        u, p = self.u_box.input.text.strip(), self.p_box.input.text.strip()
        try:
            res = requests.get(f"{DB_URL}users/{u}.json", timeout=5).json()
            if res and res.get("password") == hash_p(p):
                store.put('user', name=u)
                App.get_running_app().current_user = u
                self.manager.current = 'menu'
            else: self.msg.text = fix("פרטים שגויים")
        except: self.msg.text = fix("שגיאת תקשורת")

class ScoreScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=35, spacing=12)
        layout.add_widget(Label(text=fix("🏆 לוח תוצאות"), font_name='Hebrew', font_size='32sp', bold=True))
        try:
            users = requests.get(f"{DB_URL}users.json", timeout=5).json()
            if users:
                sorted_u = sorted(users.items(), key=lambda x: x[1].get('points', 0) if isinstance(x[1], dict) else 0, reverse=True)
                for i, (name, data) in enumerate(sorted_u[:5], 1):
                    pts = float(data.get('points', 0)) if isinstance(data, dict) else 0.0
                    display_pts = int(pts) if pts == int(pts) else pts
                    layout.add_widget(Label(text=fix(f"{i}. {name} - {display_pts}"), font_name='Hebrew'))
        except: pass
        layout.add_widget(ModernButton(text=fix("חזרה"), bg_color=(0.3, 0.3, 0.3, 1), on_release=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(layout)

class RegisterScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        l = BoxLayout(orientation='vertical', padding=40, spacing=20)
        l.add_widget(Label(text=fix("📝 הרשמה"), font_name='Hebrew', font_size='32sp', bold=True))
        self.u_box = CardInput("שם משתמש")
        self.p_box = CardInput("סיסמה", is_password=True)
        self.msg = Label(text="", color=BTN_GREEN, font_name='Hebrew', size_hint_y=None, height=30)
        l.add_widget(self.u_box); l.add_widget(self.p_box); l.add_widget(self.msg)
        l.add_widget(ModernButton(text=fix("הירשם"), bg_color=BTN_BLUE, on_release=self.do_reg))
        l.add_widget(ModernButton(text=fix("חזרה"), bg_color=(0.3, 0.3, 0.3, 1), on_release=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(l)

    def do_reg(self, x):
        u, p = self.u_box.input.text.strip(), self.p_box.input.text.strip()
        if len(u) < 2 or len(p) < 4: self.msg.text = fix("קצר מדי"); return
        try:
            requests.put(f"{DB_URL}users/{u}.json", json={"password": hash_p(p), "points": 0}, timeout=5)
            self.msg.text = fix("נרשמת בהצלחה!"); Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'menu'), 1.5)
        except: self.msg.text = fix("שגיאה")

class TriviaApp(App):
    current_user = None
    def build(self):
        if store.exists('user'): self.current_user = store.get('user')['name']
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ScoreScreen(name='score'))
        sm.add_widget(ProfileScreen(name='profile'))
        return sm

if __name__ == '__main__':
    TriviaApp().run()