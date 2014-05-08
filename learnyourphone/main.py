# encoding: utf-8

"""Main for the Learn Your Phone app"""

# To check :
# https://mail.python.org/pipermail/python-list/2008-February/494675.html

from __future__ import division
from __future__ import unicode_literals

import colorsys
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
from kivy.properties import (ListProperty, NumericProperty,
                             ObjectProperty, StringProperty)
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.settings import SettingString
from kivy.uix.scatter import Scatter


SETTINGS_SECTION = "Learn your phone"
SETTINGS_KEY_PHONE = "number"
SETTINGS_KEY_SOUND = "sound"


def hue_to_rgba(hue, alpha=1):
    """Transform a hue into a rgba color. Saturation and value are fixed"""
    # Mostly inspired by https://mail.python.org/pipermail/python-list/2008-February/494675.html  # pylint: disable=line-too-long
    rgb = list(colorsys.hsv_to_rgb(hue, .5, 1))
    rgb.append(alpha)
    return rgb


class MoveableDigit(Scatter):  # pylint: disable=too-many-public-methods
    """Show a digit (not enforce) to be move around."""
    color = ListProperty([1, 1, 1, 1])
    text = StringProperty("")
    font_size = NumericProperty(dp(12))


class AnswerBox(Label):  # pylint: disable=too-many-public-methods
    """A box-like label to validate if a MoveableDigit is in the correct
    place
    """
    background_color = ListProperty([0, 0, 0, 1])
    digit = StringProperty("")
    position = NumericProperty()
    phone_length = NumericProperty()
    current_answer = ObjectProperty()


class SettingsPhone(SettingString):  # pylint: disable=too-many-public-methods,too-many-ancestors
    """Only accept digit for phone number"""

    def on_textinput(self, _instance, value):  # pylint: disable=no-self-use
        """To add some property to the textinput"""
        value.input_type = "number"

    def _validate(self, _instance):
        """Ensure that the textinput.text containt only digits"""
        self._dismiss()
        value = self.textinput.text.strip()
        if value.isdigit():
            self.value = value
        else:
            #The kivy way is to do nothing
            return


class LearnYourPhoneApp(App):  # pylint: disable=too-many-public-methods
    """The app to learn your phone number"""

    digits = None
    answer_boxes = None
    phone_number = None

    victory_sound = None
    victory_callback = None
    in_victory = False

    replay_button = None
    _sound_enabled = None

    BASE_FONT_SIZE = 80

    @property
    def message(self):
        """The message widget"""
        return self.root.ids.message

    @property
    def answer_layout(self):
        """The answer_layout widget"""
        return self.root.ids.answer_layout

    @property
    def extra_layout(self):
        """The extra_layout widget"""
        return self.root.ids.extra_layout

    @property
    def sound_enabled(self):
        """If the app should play sound"""
        return self._sound_enabled

    @sound_enabled.setter
    def sound_enabled(self, value):
        """Try to convert value into a coherent bool"""
        if value is True:
            self._sound_enabled = True
        else:
            if isinstance(value, unicode):
                unicode_value = value
            else:
                unicode_value = unicode(value, errors="ignore")

            sound_settings_values = [u"0", u"1"]
            if unicode_value in sound_settings_values:
                enabled = bool(sound_settings_values.index(unicode_value))
                self._sound_enabled = enabled
            else:
                self._sound_enabled = bool(False)

    def add_digit_uix(self, digit, in_phone_position, uix_position):
        """Create a uix for the digit and put it on the answer_layout

        :param digit: the digit to show
        :type digit: unicode
        :param in_phone_position: the index of the digit in the phone number
        :param uix_position: the random index where to put the uix
        """
        relative_position = in_phone_position / len(self.phone_number)
        font_size = self.BASE_FONT_SIZE + in_phone_position * 2
        digit_uix = MoveableDigit(text=digit,
                                  font_size=font_size,
                                  color=hue_to_rgba(relative_position))
        pos_x = uix_position * self.answer_layout.width / len(self.phone_number)
        digit_uix.pos = [pos_x,
                         self.answer_layout.height / 5]
        digit_uix.bind(on_touch_up=self.validate_answers)  # pylint: disable=no-member
        self.digits.append(digit_uix)
        self.answer_layout.add_widget(digit_uix)

    def add_answer_box(self, digit, position):
        """Create an answer_box and puit it on the answer_layout

        :param digit: the digit to validate
        :param position: The index of the digit in the phone number
        """
        relative_position = position / len(self.phone_number)
        hue = hue_to_rgba(relative_position, alpha=.5)
        hint_uix = AnswerBox(digit=digit, position=position,
                             phone_length=len(self.phone_number),
                             font_size=self.BASE_FONT_SIZE,
                             background_color=hue,
                             pos_hint={"x": float(relative_position),
                                       "y": .5},
                             size_hint=[1 / len(self.phone_number), None])
        self.answer_boxes.append(hint_uix)
        self.answer_layout.add_widget(hint_uix)

    def initialize_phone_guessing(self, phone_number):
        """Initialize the screen to start a new game

        :param phone_number: The phone number for the game
        """
        self.digits = []
        self.answer_boxes = []
        self.answer_layout.clear_widgets()
        self.extra_layout.remove_widget(self.replay_button)
        Clock.unschedule(self.dancing)
        self.in_victory = False

        self.phone_number = phone_number

        if phone_number:
            self.message.text = "Reorder the digits to form your phone number"
            phone_length = len(phone_number)
            random_position = range(phone_length)
            random.shuffle(random_position)
            for position, digit in enumerate(phone_number):
                self.add_digit_uix(digit, position, random_position.pop())
                self.add_answer_box(digit, position)
        else:
            message = "Please input your phone number in the settings."
            self.message.text = message

    def initialize_from_config(self):
        """Start the game from information in the config"""
        self.sound_enabled = self.config.get(SETTINGS_SECTION,
                                             SETTINGS_KEY_SOUND)
        phone_number = self.config.get(SETTINGS_SECTION, SETTINGS_KEY_PHONE)
        self.initialize_phone_guessing(phone_number)

    def digit_in_bad_place(self, digit_uix):
        """Blink the digit_uix when it is now correctly place"""
        digit_uix.color = [1, 0, 0, 1]
        def reset_color(*_args):
            """Reset the color of the digit_uix"""
            # Recalculating the color to be sure to have to correct color
            hue = self.digits.index(digit_uix) / len(self.phone_number)
            digit_uix.color = hue_to_rgba(hue)
        Clock.schedule_once(reset_color, 2)

    def replay(self, _instance):
        """Restart the game"""
        self.initialize_from_config()

    def dancing(self, *_args):
        """Make the digits "dance" (move up and down) to celebrate the
        completion of the game.
        """
        for digit_uix in self.digits:
            step = digit_uix.height // 4
            move = random.randint(-step, step)
            digit_uix.y += move
            if digit_uix.y < 0:
                digit_uix.y = 0
            if digit_uix.top > digit_uix.parent.height:
                digit_uix.top = digit_uix.parent.height

    def victory(self, *_args):
        """Celebrate the victory of the player"""
        if self.sound_enabled and self.victory_sound:
            self.victory_sound.play()
        self.extra_layout.add_widget(self.replay_button)
        self.message.text = "You got your phone number right, yeah !"
        Clock.schedule_interval(self.dancing, 1)

    def validate_answers(self, instance, *_args):
        """Validate if instance is correctly place within a answer_box"""
        for answer_box in self.answer_boxes:
            if instance.collide_widget(answer_box):
                if (instance.text == answer_box.digit and
                        answer_box.current_answer is None):
                    instance.do_translation = False
                    answer_box.current_answer = instance
                    answer_box.background_color = [0, 0, 0, 1]
                    break
                if answer_box.current_answer is instance:
                    # Already answered...
                    break
                else:
                    self.digit_in_bad_place(instance)
                    break

        if all(digit_uix.do_translation == (False, False)
               for digit_uix in self.digits):
            if not self.in_victory:
                self.in_victory = True
                self.victory_callback()


    def build(self):
        """Build the screen"""
        self.replay_button = Button(size_hint=(.2, 1),
                                    text="Replay")
        self.replay_button.bind(on_press=self.replay)  # pylint: disable=no-member
        self.victory_sound = SoundLoader.load('177120__rdholder__2dogsound-tadaa1-3s-2013jan31-cc-by-30-us.wav')  # pylint: disable=line-too-long
        self.victory_callback = Clock.create_trigger(self.victory)
        return super(LearnYourPhoneApp, self).build()

    def on_start(self):
        """Delay the initialization of the game to be sure than the screen
        have already resized."""
        starting = super(LearnYourPhoneApp, self).on_start()
        Clock.schedule_once(lambda _dt: self.initialize_from_config(), 2.75)
        return starting

    def build_config(self, config):
        """Enable sound but without a phone"""
        config.setdefaults(SETTINGS_SECTION,
                           {SETTINGS_KEY_PHONE: "",
                            SETTINGS_KEY_SOUND: "1"})
        return super(LearnYourPhoneApp, self).build_config(config)

    def build_settings(self, settings):
        """Add settings for the phone number and sound"""
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
        settings.add_json_panel('Learn your phone',
                                self.config, data=jsondata)
        return super(LearnYourPhoneApp, self).build_settings(settings)

    def on_config_change(self, config, section, key, value):
        """When the phone number change, reinitialize the game"""
        if section == SETTINGS_SECTION:
            if key == SETTINGS_KEY_PHONE:
                self.initialize_phone_guessing(value)
            elif key == SETTINGS_KEY_SOUND:
                self.sound_enabled = value
        return super(LearnYourPhoneApp, self).on_config_change(config,
                                                               section,
                                                               key,
                                                               value)


if __name__ == '__main__':
    LearnYourPhoneApp().run()
