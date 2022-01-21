from dataclasses import dataclass
import itertools
import logging

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import database


class EmailClient:

    def __init__(self, smtp_server, port):
        context = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(smtp_server, port, context=context)

    def login(self, username, password) -> bool:
        self.fromaddr = username
        self.server.login(username, password)
        return True

    def send_email(self, toaddr, header, body) -> bool:
        msg = MIMEMultipart()
        msg['From'] = self.fromaddr
        msg['To'] = toaddr
        msg['Subject'] = header
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        server_sendmail = self.server.sendmail(self.fromaddr, toaddr, text)
        return True


class Accounts(database.SqliteData):
    def __init__(self):
        super().__init__()
        self.account_data = self.cur.execute(
            '''
            select username, password from accounts where status is NULL
            '''
        ).fetchall()
        self._iterable_accounts_data = iter(self.account_data)

    def __next__(self):
        return next(self._iterable_accounts_data)

    def __len__(self):
        return len(self.account_data)


class Targets(database.SqliteData):
    def __init__(self):
        super().__init__()
        self.target_data = self.cur.execute(
            '''
            select email from targets where status is NULL
            '''
        ).fetchall()
        self._iterable_target_data = iter(self.target_data)

    def __next__(self):
        return next(self._iterable_target_data)[0]

    def __len__(self):
        return len(self.target_data)


class Main:

    def __init__(self):
        self.data = database.SqliteData()
        self.header, self.body = self.data.cur.execute(
            '''
            select header, body from messages
            '''
        ).fetchone()

    def update_target_status(self, *args):
        self.data.cur.execute('update targets set status = ? where email = ?', args)
        self.data.con.commit()

    def update_account_status(self, *args):
        self.data.cur.execute('update accounts set status = ? where username = ?', args)
        self.data.con.commit()

    def __call__(self):
        c = 0
        targets = Targets()
        while c != len(targets):
            accounts = Accounts()
            for username, password in accounts.account_data:
                c += 1
                target = next(targets)
                print(username, password, target)
                email_client = EmailClient('smtp.gmail.com', 465)
                email_client.login(username, password)
                try:
                    send_email = email_client.send_email(target, self.header, self.body)
                    if send_email:
                        self.update_target_status(str(send_email), target)
                except Exception as error:
                    logging.exception(error)
                    self.update_account_status(str(error), username)


if __name__ == '__main__':
    main = Main()
    main()
