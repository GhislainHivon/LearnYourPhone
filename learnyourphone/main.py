# encoding: utf-8

"""Main for the Learn Your Phone app"""

from __future__ import unicode_literals

from kivy.app import App

SETTINGS_SECTION = "Learn your phone"
SETTINGS_KEY_PHONE = "number"

class LearnYourPhoneApp(App):

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


if __name__ == '__main__':
    LearnYourPhoneApp().run()
