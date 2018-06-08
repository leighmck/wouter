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

import pytest

from wouter.router import message


class TestHello:
    def test_ctor(self):
        hello = message.Hello(realm='test', details={'roles': ['publisher', 'subscriber', 'caller', 'callee']})
        assert hello.type.value == 1

    def test_ctor_invalid_details(self):
        with pytest.raises(ValueError):
            message.Hello(realm='test', details={})

    def test_ctor_invalid_role(self):
        with pytest.raises(ValueError):
            message.Hello(realm='test', details={'roles': ['a']})

    def test_marshal(self):
        hello = message.Hello(realm='test', details={'roles': ['publisher', 'subscriber', 'caller', 'callee']})
        msg = hello.marshal()

        assert msg[0] == 1
        assert msg[1] == 'test'
        assert msg[2]['roles'] == ['publisher', 'subscriber', 'caller', 'callee']

    def test_unmarshal(self):
        msg = [1, 'test', {'roles': ['publisher', 'subscriber', 'caller', 'callee']}]
        hello = message.Hello.unmarshal(msg=msg)

        assert hello.type == message.Type.HELLO
        assert hello.realm == 'test'
        assert hello.details == {'roles': ['publisher', 'subscriber', 'caller', 'callee']}


class TestWelcome:
    def test_ctor(self):
        welcome = message.Welcome(session=0, details={'roles': ['broker', 'dealer']})
        assert welcome.type.value == 2

    def test_ctor_invalid_details(self):
        with pytest.raises(ValueError):
            message.Welcome(session=0, details={})

    def test_ctor_invalid_role(self):
        with pytest.raises(ValueError):
            message.Welcome(session=0, details={'roles': ['a']})

    def test_marshal(self):
        welcome = message.Welcome(session=0, details={'roles': ['broker', 'dealer']})
        msg = welcome.marshal()

        assert msg[0] == 2
        assert msg[1] == 0
        assert msg[2]['roles'] == ['broker', 'dealer']

    def test_unmarshal(self):
        msg = [2, 9129137332, {'roles': {'broker': {}}}]
        welcome = message.Welcome.unmarshal(msg=msg)

        assert welcome.type == message.Type.WELCOME
        assert welcome.session == 9129137332
        assert welcome.details == {'roles': {'broker': {}}}


class TestAbort:
    def test_ctor(self):
        abort = message.Abort(details={'message': 'The realm does not exist.'},
                              reason='wamp.error.no_such_realm')
        assert abort.type.value == 3

    def test_marshal(self):
        abort = message.Abort(details={'message': 'Received HELLO message after session was established.'},
                              reason='wamp.error.protocol_violation')
        msg = abort.marshal()

        assert msg[0] == 3
        assert msg[1] == {'message': 'Received HELLO message after session was established.'}
        assert msg[2] == 'wamp.error.protocol_violation'

    def test_unmarshal(self):
        msg = [3, {'message': 'Received WELCOME message after session was established.'},
               'wamp.error.protocol_violation']
        abort = message.Abort.unmarshal(msg=msg)

        assert abort.type == message.Type.ABORT
        assert abort.details == {'message': 'Received WELCOME message after session was established.'}
        assert abort.reason == 'wamp.error.protocol_violation'


class TestGoodbye:
    def test_ctor(self):
        goodbye = message.Goodbye(details={'message': 'The host is shutting down now.'},
                                  reason='wamp.close.system_shutdown')
        assert goodbye.type.value == 6

    def test_marshal(self):
        goodbye = message.Goodbye(details={},
                                  reason='wamp.close.goodbye_and_out')
        msg = goodbye.marshal()

        assert msg[0] == 6
        assert msg[1] == {}
        assert msg[2] == 'wamp.close.goodbye_and_out'

    def test_unmarshal(self):
        msg = [6, {}, 'wamp.close.goodbye_and_out']
        goodbye = message.Goodbye.unmarshal(msg=msg)

        assert goodbye.type == message.Type.GOODBYE
        assert goodbye.details == {}
        assert goodbye.reason == 'wamp.close.goodbye_and_out'


class TestError:
    def test_ctor(self):
        error = message.Error(request_type=message.Type.SUBSCRIBE,
                              request_id=713845233,
                              details={},
                              error='wamp.error.not_authorized')
        assert error.type.value == 8

    def test_marshal(self):
        error = message.Error(request_type=message.Type.SUBSCRIBE,
                              request_id=713845233,
                              details={},
                              error='wamp.error.not_authorized',
                              args=['a'],
                              kwargs={'a': 1})
        msg = error.marshal()

        assert len(msg) == 7
        assert msg[0] == 8
        assert msg[1] == 32
        assert msg[2] == 713845233
        assert msg[3] == {}
        assert msg[4] == 'wamp.error.not_authorized'
        assert msg[5] == ['a']
        assert msg[6] == {'a': 1}

    def test_unmarshal(self):
        msg = [8, 32, 713845233, {}, 'wamp.error.not_authorized', [1]]
        error = message.Error.unmarshal(msg=msg)

        assert error.type == message.Type.ERROR
        assert error.request_type == message.Type.SUBSCRIBE
        assert error.request_id == 713845233
        assert error.details == {}
        assert error.error == 'wamp.error.not_authorized'
        assert error.args == [1]


class TestPublish:
    def test_ctor(self):
        publish = message.Publish(request_id=239714735, options={}, topic='com.myapp.mytopic1')
        assert publish.type.value == 16

    def test_marshal(self):
        publish = message.Publish(request_id=239714735,
                                  options={},
                                  topic='com.myapp.mytopic1',
                                  args=['Hello, world!'])
        msg = publish.marshal()

        assert len(msg) == 5
        assert msg[0] == 16
        assert msg[1] == 239714735
        assert msg[2] == {}
        assert msg[3] == 'com.myapp.mytopic1'
        assert msg[4] == ['Hello, world!']

    def test_unmarshal(self):
        msg = [16, 239714735, {}, 'com.myapp.mytopic1', [], {'color': 'orange', 'sizes': [23, 42, 7]}]
        publish = message.Publish.unmarshal(msg=msg)

        assert publish.type == message.Type.PUBLISH
        assert publish.request_id == 239714735
        assert publish.options == {}
        assert publish.topic == 'com.myapp.mytopic1'
        assert publish.args == []
        assert publish.kwargs == {'color': 'orange', 'sizes': [23, 42, 7]}


class TestPublished:
    def test_ctor(self):
        published = message.Published(request_id=239714735, publication_id=4429313566)
        assert published.type.value == 17

    def test_marshal(self):
        published = message.Published(request_id=239714735, publication_id=4429313566)
        msg = published.marshal()

        assert msg[0] == 17
        assert msg[1] == 239714735
        assert msg[2] == 4429313566

    def test_unmarshal(self):
        msg = [17, 239714735, 4429313566]
        published = message.Published.unmarshal(msg=msg)

        assert published.type == message.Type.PUBLISHED
        assert published.request_id == 239714735
        assert published.publication_id == 4429313566


class TestSubscribe:
    def test_ctor(self):
        subscribe = message.Subscribe(request_id=713845233, options={}, topic='com.myapp.mytopic1')
        assert subscribe.type.value == 32

    def test_marshal(self):
        subscribe = message.Subscribe(request_id=713845233,
                                      options={},
                                      topic='com.myapp.mytopic1')
        msg = subscribe.marshal()

        assert len(msg) == 4
        assert msg[0] == 32
        assert msg[1] == 713845233
        assert msg[2] == {}
        assert msg[3] == 'com.myapp.mytopic1'

    def test_unmarshal(self):
        msg = [32, 713845233, {}, 'com.myapp.mytopic1']
        subscribe = message.Subscribe.unmarshal(msg=msg)

        assert subscribe.type == message.Type.SUBSCRIBE
        assert subscribe.request_id == 713845233
        assert subscribe.options == {}
        assert subscribe.topic == 'com.myapp.mytopic1'


class TestSubscribed:
    def test_ctor(self):
        subscribed = message.Subscribed(request_id=713845233, subscription_id=5512315355)
        assert subscribed.type.value == 33

    def test_marshal(self):
        subscribed = message.Subscribed(request_id=713845233, subscription_id=5512315355)
        msg = subscribed.marshal()

        assert msg[0] == 33
        assert msg[1] == 713845233
        assert msg[2] == 5512315355

    def test_unmarshal(self):
        msg = [33, 713845233, 5512315355]
        subscribed = message.Subscribed.unmarshal(msg=msg)

        assert subscribed.type == message.Type.SUBSCRIBED
        assert subscribed.request_id == 713845233
        assert subscribed.subscription_id == 5512315355


class TestUnsubscribe:
    def test_ctor(self):
        unsubscribe = message.Unsubscribe(request_id=85346237, subscription_id=5512315355)
        assert unsubscribe.type.value == 34

    def test_marshal(self):
        unsubscribe = message.Unsubscribe(request_id=85346237,
                                          subscription_id=5512315355)
        msg = unsubscribe.marshal()

        assert msg[0] == 34
        assert msg[1] == 85346237
        assert msg[2] == 5512315355

    def test_unmarshal(self):
        msg = [34, 85346237, 5512315355]
        subscribe = message.Unsubscribe.unmarshal(msg=msg)

        assert subscribe.type == message.Type.UNSUBSCRIBE
        assert subscribe.request_id == 85346237
        assert subscribe.subscription_id == 5512315355


class TestUnsubscribed:
    def test_ctor(self):
        unsubscribed = message.Unsubscribed(request_id=85346237)
        assert unsubscribed.type.value == 35

    def test_marshal(self):
        unsubscribed = message.Unsubscribed(request_id=85346237)
        msg = unsubscribed.marshal()

        assert msg[0] == 35
        assert msg[1] == 85346237

    def test_unmarshal(self):
        msg = [35, 85346237]
        unsubscribed = message.Unsubscribed.unmarshal(msg=msg)

        assert unsubscribed.type == message.Type.UNSUBSCRIBED
        assert unsubscribed.request_id == 85346237


class TestEvent:
    def test_ctor(self):
        event = message.Event(subscription_id=5512315355, publication_id=4429313566, details={})
        assert event.type.value == 36

    def test_marshal(self):
        event = message.Event(subscription_id=5512315355,
                              publication_id=4429313566,
                              details={},
                              args=['Hello, world!'])
        msg = event.marshal()

        assert len(msg) == 5
        assert msg[0] == 36
        assert msg[1] == 5512315355
        assert msg[2] == 4429313566
        assert msg[3] == {}
        assert msg[4] == ['Hello, world!']

    def test_unmarshal(self):
        msg = [36, 5512315355, 4429313566, {}, [], {'color': 'orange', 'sizes': [23, 42, 7]}]
        event = message.Event.unmarshal(msg=msg)

        assert event.type == message.Type.EVENT
        assert event.subscription_id == 5512315355
        assert event.publication_id == 4429313566
        assert event.details == {}
        assert event.args == []
        assert event.kwargs == {'color': 'orange', 'sizes': [23, 42, 7]}


class TestCall:
    def test_ctor(self):
        call = message.Call(request_id=7814135, options={}, procedure='com.myapp.ping')
        assert call.type.value == 48

    def test_marshal(self):
        call = message.Call(request_id=7814135,
                            options={},
                            procedure='com.myapp.echo',
                            args=['Hello, world!'])
        msg = call.marshal()

        assert len(msg) == 5
        assert msg[0] == 48
        assert msg[1] == 7814135
        assert msg[2] == {}
        assert msg[3] == 'com.myapp.echo'
        assert msg[4] == ['Hello, world!']

    def test_unmarshal(self):
        msg = [48, 7814135, {}, 'com.myapp.user.new', ['johnny'], {'firstname': 'John', 'surname': 'Doe'}]
        call = message.Call.unmarshal(msg=msg)

        assert call.type == message.Type.CALL
        assert call.request_id == 7814135
        assert call.options == {}
        assert call.procedure == 'com.myapp.user.new'
        assert call.args == ['johnny']
        assert call.kwargs == {'firstname': 'John', 'surname': 'Doe'}


class TestResult:
    def test_ctor(self):
        result = message.Result(request_id=7814135, details={})
        assert result.type.value == 50

    def test_marshal(self):
        result = message.Result(request_id=7814135,
                                details={},
                                args=['Hello, world!'])
        msg = result.marshal()

        assert len(msg) == 4
        assert msg[0] == 50
        assert msg[1] == 7814135
        assert msg[2] == {}
        assert msg[3] == ['Hello, world!']

    def test_unmarshal(self):
        msg = [50, 7814135, {}, [], {'userid': 123, 'karma': 10}]
        result = message.Result.unmarshal(msg=msg)

        assert result.type == message.Type.RESULT
        assert result.request_id == 7814135
        assert result.details == {}
        assert result.args == []
        assert result.kwargs == {'userid': 123, 'karma': 10}


class TestRegister:
    def test_ctor(self):
        register = message.Register(request_id=25349185, options={}, procedure='com.myapp.myprocedure1')
        assert register.type.value == 64

    def test_marshal(self):
        register = message.Register(request_id=25349185,
                                    options={},
                                    procedure='com.myapp.myprocedure1')
        msg = register.marshal()

        assert msg[0] == 64
        assert msg[1] == 25349185
        assert msg[2] == {}
        assert msg[3] == 'com.myapp.myprocedure1'

    def test_unmarshal(self):
        msg = [64, 25349185, {}, 'com.myapp.myprocedure1']
        register = message.Register.unmarshal(msg=msg)

        assert register.type == message.Type.REGISTER
        assert register.request_id == 25349185
        assert register.options == {}
        assert register.procedure == 'com.myapp.myprocedure1'


class TestRegistered:
    def test_ctor(self):
        registered = message.Registered(request_id=25349185, registration_id=2103333224)
        assert registered.type.value == 65

    def test_marshal(self):
        registered = message.Registered(request_id=25349185,
                                        registration_id=2103333224)
        msg = registered.marshal()

        assert msg[0] == 65
        assert msg[1] == 25349185
        assert msg[2] == 2103333224

    def test_unmarshal(self):
        msg = [65, 25349185, 2103333224]
        registered = message.Registered.unmarshal(msg=msg)

        assert registered.type == message.Type.REGISTERED
        assert registered.request_id == 25349185
        assert registered.registration_id == 2103333224


class TestUnregister:
    def test_ctor(self):
        unregister = message.Unregister(request_id=788923562, registration_id=2103333224)
        assert unregister.type.value == 66

    def test_marshal(self):
        unregister = message.Unregister(request_id=788923562,
                                        registration_id=2103333224)
        msg = unregister.marshal()

        assert msg[0] == 66
        assert msg[1] == 788923562
        assert msg[2] == 2103333224

    def test_unmarshal(self):
        msg = [66, 788923562, 2103333224]
        unregister = message.Unregister.unmarshal(msg=msg)

        assert unregister.type == message.Type.UNREGISTER
        assert unregister.request_id == 788923562
        assert unregister.registration_id == 2103333224


class TestUnregistered:
    def test_ctor(self):
        unregistered = message.Unregistered(request_id=788923562)
        assert unregistered.type.value == 67

    def test_marshal(self):
        unregistered = message.Unregistered(request_id=788923562)
        msg = unregistered.marshal()

        assert msg[0] == 67
        assert msg[1] == 788923562

    def test_unmarshal(self):
        msg = [67, 788923562]
        unregistered = message.Unregistered.unmarshal(msg=msg)

        assert unregistered.type == message.Type.UNREGISTERED
        assert unregistered.request_id == 788923562


class TestInvocation:
    def test_ctor(self):
        invocation = message.Invocation(request_id=6131533, registration_id=9823526, details={})
        assert invocation.type.value == 68

    def test_marshal(self):
        invocation = message.Invocation(request_id=6131533,
                                        registration_id=9823527,
                                        details={},
                                        args=['Hello, world!'])
        msg = invocation.marshal()

        assert len(msg) == 5
        assert msg[0] == 68
        assert msg[1] == 6131533
        assert msg[2] == 9823527
        assert msg[3] == {}
        assert msg[4] == ['Hello, world!']

    def test_unmarshal(self):
        msg = [68, 6131533, 9823529, {}, ['johnny'], {'firstname': 'John', 'surname': 'Doe'}]
        invocation = message.Invocation.unmarshal(msg=msg)

        assert invocation.type == message.Type.INVOCATION
        assert invocation.request_id == 6131533
        assert invocation.registration_id == 9823529
        assert invocation.details == {}
        assert invocation.args == ['johnny']
        assert invocation.kwargs == {'firstname': 'John', 'surname': 'Doe'}


class TestYield:
    def test_ctor(self):
        yield_ = message.Yield(request_id=6131533, options={})
        assert yield_.type.value == 70

    def test_marshal(self):
        yield_ = message.Yield(request_id=6131533,
                               options={},
                               args=['Hello, world!'])
        msg = yield_.marshal()

        assert len(msg) == 4
        assert msg[0] == 70
        assert msg[1] == 6131533
        assert msg[2] == {}
        assert msg[3] == ['Hello, world!']

    def test_unmarshal(self):
        msg = [70, 6131533, {}, [], {"userid": 123, "karma": 10}]
        yield_ = message.Yield.unmarshal(msg=msg)

        assert yield_.type == message.Type.YIELD
        assert yield_.request_id == 6131533
        assert yield_.options == {}
        assert yield_.args == []
        assert yield_.kwargs == {"userid": 123, "karma": 10}
