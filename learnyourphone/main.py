# encoding: utf-8

"""Main for the Learn Your Phone app"""

# To check :
# https://mail.python.org/pipermail/python-list/2008-February/494675.html
# And kivy accept hsv color
# http://kivy.org/docs/api-kivy.graphics.html#kivy.graphics.Color
from __future__ import unicode_literals

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.textinput import TextInput


SETTINGS_SECTION = "Learn your phone"
SETTINGS_KEY_PHONE = "number"


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
            self.readonly = True  # So the good text will not change
            self.dispatch(ValidatingTextinput.SUCCEED_EVENT, self)
            return value
        else:
            return super(ValidatingTextinput, self).insert_text("", from_undo)

    def on_succeed(self, instance):
        pass

class LearnYourPhoneApp(App):
    """The app to learn your phone number"""

    needed_answers = None
    victory_sound = None

    @property
    def spacer(self):
        return self.root.ids.spacer

    @property
    def answer_layout(self):
        return self.root.ids.answer_layout

    @property
    def hint_layout(self):
        return self.root.ids.hint_layout

    def input_succeed(self, instance, *args):
        print type(instance), instance
        print [(type(x), x) for x in args]
        if instance in self.needed_answers:
            self.needed_answers.remove(instance)

        if not self.needed_answers:
            #Throw victory parade
            if self.victory_sound:
                self.victory_sound.play()

    def initialize_phone_guessing(self, phone_number):
        self.answer_layout.clear_widgets()
        self.hint_layout.clear_widgets()

        self.needed_answers = []

        if phone_number:
            self.spacer.text = ""
            for digit in phone_number:
                #input_type=number, tel ?
                digit_input = ValidatingTextinput(expecting=digit,
                                                  multiline=False,
                                                  size_hint=(1, None),
                                                  font_size=22,
                                                  focus=True)
                self.needed_answers.append(digit_input)
                digit_input.bind(on_succeed=self.input_succeed)
                self.answer_layout.add_widget(digit_input)

        else:
            self.spacer.text = "Set the phone number in the settings."

    def build(self):
        phone_number = self.config.get(SETTINGS_SECTION, SETTINGS_KEY_PHONE)
        self.initialize_phone_guessing(phone_number)
        self.victory_sound = SoundLoader.load('177120__rdholder__2dogsound-tadaa1-3s-2013jan31-cc-by-30-us.wav')
        return super(LearnYourPhoneApp, self).build()

    def build_config(self, config):
        config.setdefaults(SETTINGS_SECTION,
                           {SETTINGS_KEY_PHONE: ""})
        return super(LearnYourPhoneApp, self).build_config(config)

    def build_settings(self, settings):
        jsondata = """[
                       {{"type": "string",
                         "title": "Phone number",
                         "desc": "The complete phone number you want to learn",
                         "section": "{section}",
                         "key": "{key}"
                       }}
                      ]""".format(section=SETTINGS_SECTION, key=SETTINGS_KEY_PHONE)
        settings.add_json_panel('Learn your phone', self.config, data=jsondata)
        return super(LearnYourPhoneApp, self).build_settings(settings)

    def on_config_change(self, config, section, key, value):
        if section == SETTINGS_SECTION and key == SETTINGS_KEY_PHONE:
            self.initialize_phone_guessing(value)
        return super(LearnYourPhoneApp, self).on_config_change(config, section, key, value)

if __name__ == '__main__':
    LearnYourPhoneApp().run()
