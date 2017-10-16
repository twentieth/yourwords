from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class Email:
    __slots__ = ('_subject', '_sender', '_recipients', '_message')

    def __init__(self):
        self._subject = None
        self._sender = None
        self._recipients = []
        self._message = ''
        self._contenttype = 'html'

    def set_subject(self, subject):
        self._subject = subject
        return self

    def set_sender(self, sender):
        self._sender = sender
        return self

    def set_message(self, message):
        self._message = str(message)
        return self

    def set_recipients(self, recipients):
        if not isinstance(recipients, list):
            return self
        self._recipients = recipients
        return self

    def add_recipient(self, recipient):
        self._recipients.append(recipient)
        return self

    def set_contenttype(self, contenttype):
        if contenttype == 'text' or contenttype == 'html':
            self._contentype = contenttype
        else:
            self._contenttype = 'html'
        return self

    def send(self):
        if self._subject is None or self._sender is None or len(self._recipients) == 0:
            return None

        msg = EmailMultiAlternatives(self._subject, self._message,
                                     self._sender, self._recipients)
        msg.content_subtype = self._contenttype
        msg.send(fail_silently=True)
