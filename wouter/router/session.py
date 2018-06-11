# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Leigh McKenzie
# All rights reserved.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import enum

from wouter.router import message


@enum.unique
class State(enum.Enum):
    CLOSED = 'closed'
    ESTABLISHING = 'establishing'
    FAILED = 'failed'
    ESTABLISHED = 'established'
    CHALLENGING = 'challenging'
    CLOSING = 'closing'
    SHUTTING_DOWN = 'shutting-down'


class Session:
    """
    establishment
     1. client hello
     2. client role and feature announcement
     3. router welcome
     4. router role and feature announcement
    """

    def __init__(self, websocket):
        self.state = State.CLOSED
        self.realm = ''
        self.publications = []
        self.subscriptions = []
        self.registrations = []
        self.requests = []
        self.roles = []

    def hello(self):
        pass

    def welcome(self):
        pass

    def abort(self):
        pass

    def goodbye(self):
        pass

    def error(self):
        pass
