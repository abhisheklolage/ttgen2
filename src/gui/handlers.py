#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

import gui


class BaseHandlers(object):
    def __init__(self, app, runtime_state):
        self.runtime_state = runtime_state
        self.application = app

    def close(self, *args):
        if gui.file_save.save_if_unsaved_changes(self.runtime_state):
            self.application.window.destroy()
