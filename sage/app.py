# -*- coding: utf-8 -*-
import sys
from twisted.python.rebuild import rebuild


class Apps(dict):
    """ Container of loaded apps """

    def reload(self, name):
        """ Try to fully rebuild an app """

        if name not in self:
            return False

        self[name] = rebuild(self[name])
