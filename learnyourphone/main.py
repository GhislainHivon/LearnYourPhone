# encoding: utf-8

"""Main for the Learn Your Phone app"""

# To check :
# https://mail.python.org/pipermail/python-list/2008-February/494675.html
# And kivy accept hsv color
# http://kivy.org/docs/api-kivy.graphics.html#kivy.graphics.Color
from __future__ import unicode_literals

from kivy.app import App
from kivy.uix.textinput import TextInput

SETTINGS_SECTION = "Learn your phone"
SETTINGS_KEY_PHONE = "number"


class ValidatingTextinput(TextInput):
    """A self validating textinput: refusing everything that is not  the expected text"""

    def __init__(self, **kwargs):
        self.expected_text = kwargs.pop("expecting")
        super(ValidatingTextinput, self).__init__(**kwargs)

    def insert_text(self, substring, from_undo=False):
        if substring == self.expected_text:
            value = super(ValidatingTextinput, self).insert_text(substring, from_undo)
            self.readonly = True  # So the good text will not change
            return value
        else:
            return super(ValidatingTextinput, self).insert_text("", from_undo)


class LearnYourPhoneApp(App):
    """The app to learn your phone number"""

    @property
    def spacer(self):
        return self.root.ids.spacer

    @property
    def answer_layout(self):
        return self.root.ids.answer_layout

    @property
    def hint_layout(self):
        return self.root.ids.hint_layout

    def initialize_phone_guessing(self, phone_number):
        self.answer_layout.clear_widgets()
        self.hint_layout.clear_widgets()
        if phone_number:
            self.spacer.text = ""
            for digit in phone_number:
                #input_type=number, tel ?
                digit_input = ValidatingTextinput(expecting=digit,
                                                  multiline=False,
                                                  size_hint=(1, None),
                                                  font_size=22,
                                                  focus=True)
                self.answer_layout.add_widget(digit_input)

        else:
            self.spacer.text = "Set the phone number in the settings."

    def build(self):
        phone_number = self.config.get(SETTINGS_SECTION, SETTINGS_KEY_PHONE)
        self.initialize_phone_guessing(phone_number)
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
