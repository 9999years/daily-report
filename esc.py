def _escape(cmd):
    return '\x1b' + cmd

class Escape:
    def initialize(self, cmd, prefix=0x1b):
        self.prefix = prefix
        self.cmd = cmd

    def arg(self, txt, val):
        setattr(self, txt, val)

underline = Escape(0x2d)
underline.arg('off', 0x00)
underline.arg('on',  0x01)
underline.arg('on2', 0x02)
initialize = '\x40'
emph.on = '\x45\x00'
emph.off = '\x45\x01'
