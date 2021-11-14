from disco.bot import Plugin
from disco.bot.plugin import register_plugin_base_class


class naPlugin(Plugin):
    # disco bug fix (Doesn't get name correctly overridding default __name__)
    @property
    def __name__(self):
        return self.__class__.__name__

    @property
    def name(self):
        return self.__class__.__name__.replace('Plugin', '').lower()


register_plugin_base_class(naPlugin)

