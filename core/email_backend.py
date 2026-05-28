# usuarios/email_backend.py
import ssl
from django.core.mail.backends.smtp import EmailBackend


class SSLEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        self.connection = self.connection_class(
            self.host, self.port,
            timeout=self.timeout,
        )
        if self.use_tls:
            self.connection.starttls(context=context)
            self.connection.ehlo()
        if self.username and self.password:
            self.connection.login(self.username, self.password)
        return True