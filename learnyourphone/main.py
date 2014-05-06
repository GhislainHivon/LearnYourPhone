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


class SingleDigitTextinput(TextInput):
    """A TextInput refusing everything that is not the expected digit"""

    SUCCEED_EVENT = b'on_succeed'

    def __init__(self, **kwargs):
        self.expected_text = kwargs.pop("expecting")
        assert self.expected_text in string.digits, "Not a digit"
        assert len(self.expected_text) == 1, "Not a single digit"
        super(SingleDigitTextinput, self).__init__(**kwargs)
        self.register_event_type(SingleDigitTextinput.SUCCEED_EVENT)

    def insert_text(self, substring, from_undo=False):
        if substring == self.expected_text:
            value = super(SingleDigitTextinput, self).insert_text(substring, from_undo)
            self.readonly = True
            self.dispatch(SingleDigitTextinput.SUCCEED_EVENT, self)
            return value
        else:
            return super(SingleDigitTextinput, self).insert_text("", from_undo)

    def on_succeed(self, instance):
        pass


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

    def add_answer_input(self, answer_digit, real_position, place, phone_length):
        relative_hint = Fraction(real_position, phone_length)
        answer_input = SingleDigitTextinput(expecting=answer_digit,
                                            multiline=False,
                                            size_hint=[float(Fraction(1, phone_length)), .1 + relative_hint / 10],
                                            pos_hint={"x": float(Fraction(place, phone_length)),
                                                      "center_y": .1},
                                            font_size=40,
                                            input_type="number")

        answer_input.background_color = hue_to_rgba(relative_hint)
        answer_input.bind(on_succeed=self.input_succeed)
        self.needed_answers.append(answer_input)
        self.answer_layout.add_widget(answer_input)

    def initialize_phone_guessing(self, phone_number):
        self.answer_layout.clear_widgets()
        self.extra_layout.remove_widget(self.replay_button)

        self.needed_answers = []

        if phone_number:
            self.spacer.text = "Reorder the digits to form your phone number"
            how_many = len(phone_number)
            random_position = range(how_many)
            random.shuffle(random_position)
            for position, answer_digit in enumerate(phone_number):

                self.add_answer_input(answer_digit, position, random_position.pop(), how_many)
        else:
            self.spacer.text = "Please input your phone number in the settings."

    def initialize_from_config(self):
        self.play_sound = self.config.get(SETTINGS_SECTION, SETTINGS_KEY_SOUND)
        phone_number = self.config.get(SETTINGS_SECTION, SETTINGS_KEY_PHONE)
        self.initialize_phone_guessing(phone_number)

    def replay(self, _instance):
        self.initialize_from_config()

    def show_replay_button(self):
        self.extra_layout.add_widget(self.replay_button)

    def input_succeed(self, instance, _value):
        if instance in self.needed_answers:
            self.needed_answers.remove(instance)
            if self.play_sound and self.victory_sound:
                self.victory_sound.play()

        if not self.needed_answers:
            #Throw victory parade
            self.show_replay_button()
            self.spacer.text = "You got your phone number right, yeah !"


    def build(self):
        self.replay_button = Button(size_hint=(.2, 1),
                                    text="Replay")
        self.replay_button.bind(on_press=self.replay)
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
