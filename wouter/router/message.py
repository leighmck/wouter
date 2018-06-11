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
import abc


@enum.unique
class Type(enum.Enum):
    HELLO = 1
    WELCOME = 2
    ABORT = 3
    GOODBYE = 6
    ERROR = 8
    PUBLISH = 16
    PUBLISHED = 17
    SUBSCRIBE = 32
    SUBSCRIBED = 33
    UNSUBSCRIBE = 34
    UNSUBSCRIBED = 35
    EVENT = 36
    CALL = 48
    RESULT = 50
    REGISTER = 64
    REGISTERED = 65
    UNREGISTER = 66
    UNREGISTERED = 67
    INVOCATION = 68
    YIELD = 70


class Message(abc.ABC):
    type = ...  # type: Type

    def __init__(self, type_: Type):
        self.type = type_

    @classmethod
    @abc.abstractmethod
    def unmarshal(cls, msg: list):
        pass

    @abc.abstractmethod
    def marshal(self) -> list:
        pass


class Hello(Message):
    realm = ...  # type: str
    details = ...  # type: dict

    def __init__(self, realm: str, details: dict):
        """
        Sent by a Client to initiate opening of a WAMP session to a Router attaching to a Realm.

        After the underlying transport has been established, the opening of a WAMP session is initiated by the Client
        sending a HELLO message to the Router.

        :param realm: Realm is a string identifying the realm this session should attach to.
        :param details: Details is a dictionary that allows the client to provide additional opening information. The
            client must announce the roles it supports via the 'roles' key. A role can be:
                - publisher
                - subscriber
                - caller
                - callee
            A Client can support any combination of the above roles but must support at least one role.
        """
        Message.__init__(self, type_=Type.HELLO)
        self.realm = realm

        if details.get('roles'):
            if all(r in ['publisher', 'subscriber', 'caller', 'callee'] for r in details['roles']):
                self.details = details
            else:
                raise ValueError('Invalid message roles')
        else:
            raise ValueError('Invalid message details')

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.HELLO.value:
            return cls(realm=msg[1], details=msg[2])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.realm, self.details]


class Welcome(Message):
    session = ...  # type: int
    details = ...  # type: dict

    def __init__(self, session: int, details: dict):
        """
        Sent by a Router to accept a Client. The WAMP session is now open.

        :param session: Session MUST be a randomly generated ID specific to the WAMP session. This applies for the
            lifetime of the session.
        :param details: Details is a dictionary that allows the router to provide additional information regarding the
            open session. The router must announce the roles it supports via the 'roles' key. A role can be:
                - broker
                - dealer
            A Router must support at least one role, and MAY support both roles.
        """
        Message.__init__(self, type_=Type.WELCOME)
        self.session = session

        if details.get('roles') and all(r in ['dealer', 'broker'] for r in details['roles']):
            self.details = details
        else:
            raise ValueError('Invalid message details')

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.WELCOME.value:
            return cls(session=msg[1], details=msg[2])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.session, self.details]


class Abort(Message):
    details = ...  # type: dict
    reason = ...  # type: str

    def __init__(self, details: dict, reason: str):
        """
        Both the Router and the Client may abort a WAMP session by sending an ABORT message.

        :param details: MUST be a dictionary that allows to provide additional, optional closing information.
        :param reason: MUST be an URI.
        """
        Message.__init__(self, type_=Type.ABORT)
        self.details = details
        self.reason = reason

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.ABORT.value:
            return cls(details=msg[1], reason=msg[2])
        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.details, self.reason]


class Goodbye(Message):
    details = ...  # type: dict
    reason = ...  # type: str

    def __init__(self, details: dict, reason: str):
        """
        Sent by a Peer to close a previously opened WAMP session. Must be echo'ed by the receiving Peer.

        :param details: MUST be a dictionary that allows to provide additional, optional closing information
        :param reason: MUST be an URI.
        """
        Message.__init__(self, type_=Type.GOODBYE)
        self.details = details
        self.reason = reason

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.GOODBYE.value:
            return cls(details=msg[1], reason=msg[2])
        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.details, self.reason]


class Error(Message):
    request_type = ...  # type: Type
    request_id = ...  # type: int
    details = ...  # type: dict
    error = ...  # type: str
    args = ...  # type: list
    kwargs = ...  # type: dict

    def __init__(self,
                 request_type: Type,
                 request_id: int,
                 details: dict,
                 error: str,
                 args: list = None,
                 kwargs: dict = None):
        """
        Error reply sent by a Peer as an error response to different kinds of requests.

        :param request_type: MUST be the TYPE of the original request.
        :param request_id: MUST be the ID from the original request.
        :param details: is a dictionary with additional error details.
        :param error: is an URI that identifies the error of why the request could not be fulfilled.
        :param args: is a list containing arbitrary, application defined, positional error information. This will be
            forwarded by the Dealer to the Caller that initiated the call.
        :param kwargs: is a dictionary containing arbitrary, application defined, keyword-based error information.
            This will be forwarded by the Dealer to the Caller that initiated the call.
        """
        Message.__init__(self, type_=Type.ERROR)
        self.request_type = request_type
        self.request_id = request_id
        self.details = details
        self.error = error
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.ERROR.value:
            if len(msg) > 6:
                return cls(request_type=Type(msg[1]), request_id=msg[2], details=msg[3], error=msg[4], args=msg[5],
                           kwargs=msg[6])
            elif len(msg) > 5:
                return cls(request_type=Type(msg[1]), request_id=msg[2], details=msg[3], error=msg[4], args=msg[5])
            elif len(msg) > 4:
                return cls(request_type=Type(msg[1]), request_id=msg[2], details=msg[3], error=msg[4])

    def marshal(self) -> list:
        if self.kwargs:
            return [self.type.value, self.request_type.value, self.request_id, self.details, self.error, self.args,
                    self.kwargs]
        elif self.args:
            return [self.type.value, self.request_type.value, self.request_id, self.details, self.error, self.args]
        else:
            return [self.type.value, self.request_type.value, self.request_id, self.details, self.error]


class Publish(Message):
    request_id = ...  # type: int
    options = ...  # type: dict
    topic = ...  # str
    args = ...  # type: list
    kwargs = ...  # type: dict

    def __init__(self, request_id: int, options: dict, topic: str, args: list = None, kwargs: dict = None):
        """
        Sent by a Publisher to a Broker to publish an event.

        :param request_id: is a random, ephemeral ID chosen by the Publisher and used to correlate the Broker's
            response with the request.
        :param options: is a dictionary that allows to provide additional publication request details in an extensible
            way. This is described further below.
        :param topic: is the topic published to.
        :param args: is a list of application-level event payload elements. The list may be of zero length.
        :param kwargs: is an optional dictionary containing application-level event payload, provided as keyword
            arguments. The dictionary may be empty.
        """
        Message.__init__(self, type_=Type.PUBLISH)
        self.request_id = request_id
        self.options = options
        self.topic = topic
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.PUBLISH.value:
            if len(msg) > 5:
                return cls(request_id=msg[1], options=msg[2], topic=msg[3], args=msg[4], kwargs=msg[5])
            elif len(msg) > 4:
                return cls(request_id=msg[1], options=msg[2], topic=msg[3], args=msg[4])
            elif len(msg) > 3:
                return cls(request_id=msg[1], options=msg[2], topic=msg[3])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        if self.kwargs:
            return [self.type.value, self.request_id, self.options, self.topic, self.args, self.kwargs]
        elif self.args:
            return [self.type.value, self.request_id, self.options, self.topic, self.args]
        else:
            return [self.type.value, self.request_id, self.options, self.topic]


class Published(Message):
    request_id = ...  # type: int
    publication_id = ...  # type: int

    def __init__(self, request_id: int, publication_id: int):
        """
        Acknowledge sent by a Broker to a Publisher for acknowledged publications.

        :param request_id: is the ID from the original publication request.
        :param publication_id: is a ID chosen by the Broker for the publication.
        """
        Message.__init__(self, type_=Type.PUBLISHED)
        self.request_id = request_id
        self.publication_id = publication_id

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.PUBLISHED.value:
            return cls(request_id=msg[1], publication_id=msg[2])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.request_id, self.publication_id]


class Subscribe(Message):
    request_id = ...  # type: int
    options = ...  # type: dict
    topic = ...  # type: str

    def __init__(self, request_id: int, options: dict, topic: str):
        """
        A Subscriber communicates its interest in a topic to a Broker by sending a SUBSCRIBE message:

        :param request_id: MUST be a random, ephemeral ID chosen by the Subscriber and used to correlate the Broker's
            response with the request.
        :param options: MUST be a dictionary that allows to provide additional subscription request details in a
            extensible way. This is described further below.
        :param topic: is the topic the Subscriber wants to subscribe to and MUST be an URI.
        """
        Message.__init__(self, type_=Type.SUBSCRIBE)
        self.request_id = request_id
        self.options = options
        self.topic = topic

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.SUBSCRIBE.value:
            return cls(request_id=msg[1], options=msg[2], topic=msg[3])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.request_id, self.options, self.topic]


class Subscribed(Message):
    """

    """
    request_id = ...  # type: int
    subscription_id = ...  # type: int

    def __init__(self, request_id: int, subscription_id: int):
        """
        If the Broker is able to fulfill and allow the subscription, it answers by sending a SUBSCRIBED message to the
        Subscriber

        :param request_id: MUST be the ID from the original request.
        :param subscription_id: MUST be an ID chosen by the Broker for the subscription.
        """
        Message.__init__(self, type_=Type.SUBSCRIBED)
        self.request_id = request_id
        self.subscription_id = subscription_id

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.SUBSCRIBED.value:
            return cls(request_id=msg[1], subscription_id=msg[2])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.request_id, self.subscription_id]


class Unsubscribe(Message):
    request_id = ...  # type: int
    subscription_id = ...  # type: int

    def __init__(self, request_id: int, subscription_id: int):
        """
        When a Subscriber is no longer interested in receiving events for a subscription it sends an UNSUBSCRIBE
        message.

        :param request_id: MUST be a random, ephemeral ID chosen by the Subscriber and used to correlate the Broker's
            response with the request.
        :param subscription_id: MUST be the ID for the subscription to unsubscribe from, originally handed out by the
            Broker to the Subscriber.
        """
        Message.__init__(self, type_=Type.UNSUBSCRIBE)
        self.request_id = request_id
        self.subscription_id = subscription_id

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.UNSUBSCRIBE.value:
            return cls(request_id=msg[1], subscription_id=msg[2])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.request_id, self.subscription_id]


class Unsubscribed(Message):
    request_id = ...  # type: int

    def __init__(self, request_id: int):
        """
        Upon successful unsubscription, the Broker sends an UNSUBSCRIBED message to the Subscriber.

        :param request_id: MUST be the ID from the original request.
        """
        Message.__init__(self, type_=Type.UNSUBSCRIBED)
        self.request_id = request_id

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.UNSUBSCRIBED.value:
            return cls(request_id=msg[1])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.request_id]


class Event(Message):
    subscription_id = ...  # type: int
    publication_id = ...  # type: int
    details = ...  # type: dict
    args = ...  # type: list
    kwargs = ...  # type: dict

    def __init__(self, subscription_id: int, publication_id: int, details: dict, args: list = None,
                 kwargs: dict = None):
        """
        When a publication is successful and a Broker dispatches the event, it determines a list of receivers for the
        event based on Subscribers for the topic published to and, possibly, other information in the event.

        Note that the Publisher of an event will never receive the published event even if the Publisher is also a
        Subscriber of the topic published to.

        :param subscription_id: is the ID for the subscription under which the Subscriber receives the event - the ID
            for the subscription originally handed out by the Broker to the Subscribe*.
        :param publication_id: is the ID of the publication of the published event.
        :param details: is a dictionary that allows the Broker to provide additional event details in a extensible way.
            This is described further below.
        :param args: is the application-level event payload that was provided with the original publication request.
        :param kwargs: is the application-level event payload that was provided with the original publication request.
        """
        Message.__init__(self, type_=Type.EVENT)
        self.subscription_id = subscription_id
        self.publication_id = publication_id
        self.details = details
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.EVENT.value:
            if len(msg) > 5:
                return cls(subscription_id=msg[1], publication_id=msg[2], details=msg[3], args=msg[4], kwargs=msg[5])
            elif len(msg) > 4:
                return cls(subscription_id=msg[1], publication_id=msg[2], details=msg[3], args=msg[4])
            elif len(msg) > 3:
                return cls(subscription_id=msg[1], publication_id=msg[2], details=msg[3])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        if self.kwargs:
            return [self.type.value, self.subscription_id, self.publication_id, self.details, self.args, self.kwargs]
        elif self.args:
            return [self.type.value, self.subscription_id, self.publication_id, self.details, self.args]
        else:
            return [self.type.value, self.subscription_id, self.publication_id, self.details]


class Call(Message):
    request_id = ...  # type: int
    options = ...  # type: dict
    procedure = ...  # type: str
    args = ...  # type: list
    kwargs = ...  # type: dict

    def __init__(self, request_id: int, options: dict, procedure: str, args: list = None, kwargs: dict = None):
        """
        When a Caller wishes to call a remote procedure, it sends a CALL message to a Dealer:

        :param request_id: is a random, ephemeral ID chosen by the Caller and used to correlate the Dealer's response
            with the request.
        :param options: is a dictionary that allows to provide additional call request details in an extensible way.
            This is described further below.
        :param procedure: is the URI of the procedure to be called.
        :param args: is a list of positional call arguments (each of arbitrary type). The list may be of zero length.
        :param kwargs: is a dictionary of keyword call arguments (each of arbitrary type). The dictionary may be empty.
        """
        Message.__init__(self, type_=Type.CALL)
        self.request_id = request_id
        self.options = options
        self.procedure = procedure
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.CALL.value:
            if len(msg) > 5:
                return cls(request_id=msg[1], options=msg[2], procedure=msg[3], args=msg[4], kwargs=msg[5])
            elif len(msg) > 4:
                return cls(request_id=msg[1], options=msg[2], procedure=msg[3], args=msg[4])
            elif len(msg) > 3:
                return cls(request_id=msg[1], options=msg[2], procedure=msg[3])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        if self.kwargs:
            return [self.type.value, self.request_id, self.options, self.procedure, self.args, self.kwargs]
        elif self.args:
            return [self.type.value, self.request_id, self.options, self.procedure, self.args]
        else:
            return [self.type.value, self.request_id, self.options, self.procedure]


class Result(Message):
    request_id = ...  # type: int
    details = ...  # type: dict
    args = ...  # type: list
    kwargs = ...  # type: dict

    def __init__(self, request_id: int, details: dict, args: list = None, kwargs: dict = None):
        """
        Result of a call as returned by Dealer to Caller.

        :param request_id: is the ID from the original call request.
        :param details: is a dictionary of additional details.
        :param args: is the original list of positional result elements as returned by the Callee.
        :param kwargs: is the original dictionary of keyword result elements as returned by the Callee.
        """
        Message.__init__(self, type_=Type.RESULT)
        self.request_id = request_id
        self.details = details
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.RESULT.value:
            if len(msg) > 4:
                return cls(request_id=msg[1], details=msg[2], args=msg[3], kwargs=msg[4])
            elif len(msg) > 3:
                return cls(request_id=msg[1], details=msg[2], args=msg[3])
            elif len(msg) > 2:
                return cls(request_id=msg[1], details=msg[2])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        if self.kwargs:
            return [self.type.value, self.request_id, self.details, self.args, self.kwargs]
        elif self.args:
            return [self.type.value, self.request_id, self.details, self.args]
        else:
            return [self.type.value, self.request_id, self.details]


class Register(Message):
    request_id = ...  # type: int
    options = ...  # type: dict
    procedure = ...  # type: str

    def __init__(self, request_id: int, options: dict, procedure: str):
        """
        A Callee announces the availability of an endpoint implementing a procedure with a Dealer by sending a REGISTER
        message:

        :param request_id: is a random, ephemeral ID chosen by the Callee and used to correlate the Dealer's response
            with the request.
        :param options: is a dictionary that allows to provide additional registration request details in a extensible
            way. This is described further below.
        :param procedure: is the procedure the Callee wants to register
        """
        Message.__init__(self, type_=Type.REGISTER)
        self.request_id = request_id
        self.options = options
        self.procedure = procedure

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.REGISTER.value:
            return cls(request_id=msg[1], options=msg[2], procedure=msg[3])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.request_id, self.options, self.procedure]


class Registered(Message):
    request_id = ...  # type: int
    registration_id = ...  # type: int

    def __init__(self, request_id: int, registration_id: int):
        """
        If the Dealer is able to fulfill and allowing the registration, it answers by sending a REGISTERED message to
        the Callee:

        :param request_id: is the ID from the original request.
        :param registration_id: is an ID chosen by the Dealer for the registration.
        """
        Message.__init__(self, type_=Type.REGISTERED)
        self.request_id = request_id
        self.registration_id = registration_id

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.REGISTERED.value:
            return cls(request_id=msg[1], registration_id=msg[2])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.request_id, self.registration_id]


class Unregister(Message):
    request_id = ...  # type: int
    registration_id = ...  # type: int

    def __init__(self, request_id: int, registration_id: int):
        """
        When a Callee is no longer willing to provide an implementation of the registered procedure, it sends an
        UNREGISTER message to the Dealer:

        :param request_id: is a random, ephemeral ID chosen by the Callee and used to correlate the Dealer's response
            with the request.
        :param registration_id: is the ID for the registration to revoke, originally handed out by the Dealer to the
            Callee.
        """
        Message.__init__(self, type_=Type.UNREGISTER)
        self.request_id = request_id
        self.registration_id = registration_id

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.UNREGISTER.value:
            return cls(request_id=msg[1], registration_id=msg[2])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.request_id, self.registration_id]


class Unregistered(Message):
    request_id = ...  # type: int

    def __init__(self, request_id: int):
        """
        Upon successful unregistration, the Dealer sends an UNREGISTERED message to the Callee:

        :param request_id: is the ID from the original request.
        """
        Message.__init__(self, type_=Type.UNREGISTERED)
        self.request_id = request_id

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.UNREGISTERED.value:
            return cls(request_id=msg[1])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        return [self.type.value, self.request_id]


class Invocation(Message):
    request_id = ...  # type: int
    registration_id = ...  # type: int
    details = ...  # type: dict
    args = ...  # type: list
    kwargs = ...  # type: dict

    def __init__(self, request_id: int, registration_id: int, details: dict, args: list = None,
                 kwargs: dict = None):
        """
        If the Dealer is able to fulfill (mediate) the call and it allows the call, it sends a INVOCATION message to
        the respective Callee implementing the procedure:

        :param request_id: is a random, ephemeral ID chosen by the Dealer and used to correlate the Callee's response
            with the request.
        :param registration_id: is the registration ID under which the procedure was registered at the Dealer.
        :param details: is a dictionary that allows to provide additional invocation request details in an extensible
            way. This is described further below.
        :param args: is the original list of positional call arguments as provided by the Caller.
        :param kwargs: is the original dictionary of keyword call arguments as provided by the Caller.
        """
        Message.__init__(self, type_=Type.INVOCATION)
        self.request_id = request_id
        self.registration_id = registration_id
        self.details = details
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.INVOCATION.value:
            if len(msg) > 5:
                return cls(request_id=msg[1], registration_id=msg[2], details=msg[3], args=msg[4], kwargs=msg[5])
            elif len(msg) > 4:
                return cls(request_id=msg[1], registration_id=msg[2], details=msg[3], args=msg[4])
            elif len(msg) > 3:
                return cls(request_id=msg[1], registration_id=msg[2], details=msg[3])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        if self.kwargs:
            return [self.type.value, self.request_id, self.registration_id, self.details, self.args, self.kwargs]
        elif self.args:
            return [self.type.value, self.request_id, self.registration_id, self.details, self.args]
        else:
            return [self.type.value, self.request_id, self.registration_id, self.details]


class Yield(Message):
    request_id = ...  # type: int
    options = ...  # type: dict
    args = ...  # type: list
    kwargs = ...  # type: dict

    def __init__(self, request_id: int, options: dict, args: list = None, kwargs: dict = None):
        """
        If the Callee is able to successfully process and finish the execution of the call, it answers by sending a
        YIELD message to the Dealer.

        :param request_id: is the ID from the original invocation request.
        :param options: is a dictionary that allows to provide additional options.
        :param args: is a list of positional result elements (each of arbitrary type). The list may be of zero length.
        :param kwargs: is a dictionary of keyword result elements (each of arbitrary type). The dictionary may be empty.
        """
        Message.__init__(self, type_=Type.YIELD)
        self.request_id = request_id
        self.options = options
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def unmarshal(cls, msg: list):
        if msg[0] == Type.YIELD.value:
            if len(msg) > 4:
                return cls(request_id=msg[1], options=msg[2], args=msg[3], kwargs=msg[4])
            elif len(msg) > 3:
                return cls(request_id=msg[1], options=msg[2], args=msg[3])
            elif len(msg) > 2:
                return cls(request_id=msg[1], options=msg[2])

        raise ValueError('Invalid message')

    def marshal(self) -> list:
        if self.kwargs:
            return [self.type.value, self.request_id, self.options, self.args, self.kwargs]
        elif self.args:
            return [self.type.value, self.request_id, self.options, self.args]
        else:
            return [self.type.value, self.request_id, self.options]
