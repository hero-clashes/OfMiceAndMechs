class AttrSpec(object):
    """
    dumy object behaving like an urwid attribute
    this is used to prevent crashes
    """

    def __init__(self, fg, bg):
        """
        store basic attriutes

        Parameters:
            fg: foreground color
            bg: background color
        """

        self.fg = fg
        self.bg = bg
