# encoding: utf-8

"""Main for the Learn Your Phone app"""

# To check :
# https://mail.python.org/pipermail/python-list/2008-February/494675.html

from __future__ import division
from __future__ import unicode_literals

import colorsys
from fractions import Fraction
import random
import string

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.settings import SettingString
from kivy.uix.scatter import Scatter
from kivy.uix.textinput import TextInput


SETTINGS_SECTION = "Learn your phone"
SETTINGS_KEY_PHONE = "number"
SETTINGS_KEY_SOUND = "sound"


def hue_to_rgba(hue):
    """Transform a hue into a rgba color. Saturation and value are fixed"""
    # Mostly inspired by https://mail.python.org/pipermail/python-list/2008-February/494675.html
    alpha = [1]
    return list(colorsys.hsv_to_rgb(hue, .5, 1)) + alpha


class MoveableDigit(Scatter):
    
    def __init__(self, **kwargs):
        text = kwargs.pop("text")
        font_size = kwargs.pop("font_size")
        color = kwargs.pop("color")
        super(MoveableDigit, self).__init__(**kwargs)
        self.ids.digit.text = text
        self.ids.digit.font_size = font_size
        self.ids.digit.color = color



class SettingsPhone(SettingString):
    """Only accept digit for phone number"""

    def on_textinput(self, _instance, value):
        """To add some property to the textinput"""
        value.input_type = "number"

    def _validate(self, _instance):
        self._dismiss()
        value = self.textinput.text.strip()
        if value.isdigit():
            self.value = value
        else:
            #The kivy way is to do nothing
            return


class LearnYourPhoneApp(App):
    """The app to learn your phone number"""

    digits = None

    victory_sound = None
    victory_callback = None
    in_victory = False

    replay_button = None
    _play_sound = None

    @property
    def message(self):
        return self.root.ids.message

    @property
    def answer_layout(self):
        return self.root.ids.answer_layout

    @property
    def extra_layout(self):
        return self.root.ids.extra_layout

    @property
    def play_sound(self):
        """If the app should play sound"""
        return self._play_sound

    @play_sound.setter
    def play_sound(self, value):
        if value is True:
            self._play_sound = True
        else:
            if isinstance(value, unicode):
                unicode_value = value
            else:
                unicode_value = unicode(value, errors="ignore")

            sound_settings_values = [u"0", u"1"]
            if unicode_value in sound_settings_values:
                self._play_sound = bool(sound_settings_values.index(unicode_value))
            else:
                self._play_sound = bool(False)

    def add_digit_uix(self, digit, real_position, place, phone_length):
        relative_hint = Fraction(real_position, phone_length)
        digit_uix = MoveableDigit(text=digit,
                                  font_size=70 + real_position * 2,
                                  color=hue_to_rgba(relative_hint))
        digit_uix.pos = [place * self.answer_layout.width / phone_length , 
                                                 self.answer_layout.height / 5]
        digit_uix.bind(on_touch_up=self.validate_answers)
        self.digits.append(digit_uix)
        self.answer_layout.add_widget(digit_uix)

    def initialize_phone_guessing(self, phone_number):
        self.digits = []
        self.answer_layout.clear_widgets()
        self.extra_layout.remove_widget(self.replay_button)
        Clock.unschedule(self.dancing)
        self.in_victory = False

        if phone_number:
            self.message.text = "Reorder the digits to form your phone number"
            how_many = len(phone_number)
            random_position = range(how_many)
            random.shuffle(random_position)
            for position, digit in enumerate(phone_number):
                self.add_digit_uix(digit, position, random_position.pop(), how_many)
        else:
            self.message.text = "Please input your phone number in the settings."

    def initialize_from_config(self):
        self.play_sound = self.config.get(SETTINGS_SECTION, SETTINGS_KEY_SOUND)
        phone_number = self.config.get(SETTINGS_SECTION, SETTINGS_KEY_PHONE)
        self.initialize_phone_guessing(phone_number)

    def replay(self, _instance):
        self.initialize_from_config()

    def dancing(self, *_args):
        for digit_uix in self.digits:
            move = random.randint(-digit_uix.height // 4, digit_uix.height // 4)
            digit_uix.y += move
            if digit_uix.y < 0:
                digit_uix.y = 0
            if digit_uix.top > digit_uix.parent.height:
                digit_uix.top = digit_uix.parent.height

    def victory(self, *_args):
        if self.play_sound and self.victory_sound:
            self.victory_sound.play()
        self.extra_layout.add_widget(self.replay_button)
        self.message.text = "You got your phone number right, yeah !"
        Clock.schedule_interval(self.dancing, .5)

    def validate_answers(self, instance, *_args):
        before = self.digits[0]
        for current in self.digits[1:]:
            if not before.x < current.x:
                return
            before = current
        if not self.in_victory:
            self.in_victory = True
            self.victory_callback()

    def build(self):
        self.replay_button = Button(size_hint=(.2, 1),
                                    text="Replay")
        self.replay_button.bind(on_press=self.replay)
        
        self.victory_sound = SoundLoader.load('177120__rdholder__2dogsound-tadaa1-3s-2013jan31-cc-by-30-us.wav')
        self.victory_callback = Clock.create_trigger(self.victory)
        return super(LearnYourPhoneApp, self).build()

    def on_start(self):
        starting = super(LearnYourPhoneApp, self).on_start()
        Clock.schedule_once(lambda dt: self.initialize_from_config(), 2.5)
        return starting

    def build_config(self, config):
        config.setdefaults(SETTINGS_SECTION,
                           {SETTINGS_KEY_PHONE: "",
                            SETTINGS_KEY_SOUND: "1"})
        return super(LearnYourPhoneApp, self).build_config(config)

    def build_settings(self, settings):
        jsondata = """[
                       {{"type": "phone",
                         "title": "Phone number",
                         "desc": "The complete phone number you want to learn (digit only)",
                         "section": "{section}",
                         "key": "{key_number}"
                       }},
                       {{"type": "bool",
                         "title": "Enable sound",
                         "section": "{section}",
                         "key": "{key_sound}",
                         "true": "auto"
                       }}
                      ]""".format(section=SETTINGS_SECTION,
                                  key_number=SETTINGS_KEY_PHONE,
                                  key_sound=SETTINGS_KEY_SOUND)
        settings.register_type("phone", SettingsPhone)
        settings.add_json_panel('Learn your phone', self.config, data=jsondata)
        return super(LearnYourPhoneApp, self).build_settings(settings)

    def on_config_change(self, config, section, key, value):
        if section == SETTINGS_SECTION:
            if key == SETTINGS_KEY_PHONE:
                self.initialize_phone_guessing(value)
            elif key == SETTINGS_KEY_SOUND:
                self.play_sound = value
        return super(LearnYourPhoneApp, self).on_config_change(config, section, key, value)


if __name__ == '__main__':
    LearnYourPhoneApp().run()
