# encoding: utf-8

"""Main for the Learn Your Phone app"""

from __future__ import unicode_literals

from kivy.app import App

SETTINGS_SECTION = "Learn your phone"
SETTINGS_KEY_PHONE = "number"

class LearnYourPhoneApp(App):

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
            self.spacer.text = phone_number
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
