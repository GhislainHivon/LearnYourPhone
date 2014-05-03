# encoding: utf-8

"""Main for the Learn Your Phone app"""

# To check :
# https://mail.python.org/pipermail/python-list/2008-February/494675.html

from __future__ import unicode_literals

import colorsys
from fractions import Fraction
import string

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.settings import SettingString
from kivy.uix.textinput import TextInput


SETTINGS_SECTION = "Learn your phone"
SETTINGS_KEY_PHONE = "number"
SETTINGS_KEY_SOUND = "sound"


def hue_to_rgba(hue):
    """Transform a hue into a rgba color. Saturation and value are fixed"""
    # Mostly inspired by https://mail.python.org/pipermail/python-list/2008-February/494675.html
    alpha = [1]
    return list(colorsys.hsv_to_rgb(hue, .5, 1)) + alpha


class ValidatingTextinput(TextInput):
    """A self validating textinput: refusing everything that is not  the expected text"""

    SUCCEED_EVENT = b'on_succeed'

    def __init__(self, **kwargs):
        self.expected_text = kwargs.pop("expecting")
        super(ValidatingTextinput, self).__init__(**kwargs)
        self.register_event_type(ValidatingTextinput.SUCCEED_EVENT)

    def insert_text(self, substring, from_undo=False):
        if substring == self.expected_text:
            value = super(ValidatingTextinput, self).insert_text(substring, from_undo)
            self.readonly = True
            self.dispatch(ValidatingTextinput.SUCCEED_EVENT, self)
            return value
        else:
            return super(ValidatingTextinput, self).insert_text("", from_undo)

    def on_succeed(self, instance):
        pass


class SettingsPhone(SettingString):
    """Only accept digit for phone number"""

    def on_textinput(self, instance, value):
        """To add some property to the textinput"""
        value.input_type = "number"

    def _validate(self, instance):
        self._dismiss()
        value = self.textinput.text.strip()
        if value.isdigit():
            self.value = value
        else:
            #The kivy way is to do nothing
            return


class LearnYourPhoneApp(App):
    """The app to learn your phone number"""

    needed_answers = None
    victory_sound = None
    replay_button = None
    _play_sound = None

    @property
    def spacer(self):
        return self.root.ids.spacer

    @property
    def answer_layout(self):
        return self.root.ids.answer_layout

    @property
    def hint_layout(self):
        return self.root.ids.hint_layout

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

    def add_answer_input(self, answer_digit, hue):
        answer_input = ValidatingTextinput(expecting=answer_digit,
                                          multiline=False,
                                          size_hint=(1, None),
                                          font_size=30,
                                          input_type = "number")

        answer_input.background_color = hue_to_rgba(hue)
        answer_input.bind(on_succeed=self.input_succeed)
        self.needed_answers.append(answer_input)
        self.answer_layout.add_widget(answer_input)

    def add_hint_uix(self, hint_digit, hue):
        hint_uix = Label(text=hint_digit,
                         size_hint=(None, None),
                         font_size=30)
        hint_uix.color = hue_to_rgba(hue)
        self.hint_layout.add_widget(hint_uix)

    def initialize_phone_guessing(self, phone_number):
        self.answer_layout.clear_widgets()
        self.hint_layout.clear_widgets()

        self.needed_answers = []

        if phone_number:
            self.spacer.text = "Guess your phone number"
            for answer_digit in phone_number:
                answer_hue = Fraction(int(answer_digit), len(string.digits))
                self.add_answer_input(answer_digit, answer_hue)

            for hint_digit in string.digits:
                hint_hue = Fraction(int(hint_digit), len(string.digits))
                self.add_hint_uix(hint_digit, hint_hue)
        else:
            self.spacer.text = "Please input your phone number in the settings."

    def initialize_from_config(self):
        self.play_sound = self.config.get(SETTINGS_SECTION, SETTINGS_KEY_SOUND)
        phone_number = self.config.get(SETTINGS_SECTION, SETTINGS_KEY_PHONE)
        self.initialize_phone_guessing(phone_number)

    def replay(self, _instance):
        self.initialize_from_config()
        self.replay_button = None

    def generate_replay_button(self):
        self.replay_button = Button(text="replay", size_hint=(None, None))
        self.replay_button.bind(on_press=self.replay)
        self.hint_layout.clear_widgets()
        self.hint_layout.add_widget(self.replay_button)

    def input_succeed(self, instance, _value):
        if instance in self.needed_answers:
            self.needed_answers.remove(instance)

        if not self.needed_answers:
            #Throw victory parade
            self.generate_replay_button()
            self.spacer.text = "You got your phone number right, yeah !"
            if self.play_sound and self.victory_sound:
                self.victory_sound.play()

    def build(self):
        self.initialize_from_config()
        self.victory_sound = SoundLoader.load('177120__rdholder__2dogsound-tadaa1-3s-2013jan31-cc-by-30-us.wav')
        return super(LearnYourPhoneApp, self).build()

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
