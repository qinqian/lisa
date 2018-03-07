import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart # 3.0
from email.mime.text import MIMEText

#from email.Utils import COMMASPACE, formatdate
import datetime
from email import encoders

COMMASPACE = ', '


def send_localhost_mail(resultOpt, subject, to, html, attachment, server="localhost"):
    msg = MIMEMultipart('alternative')
    fro = 'lisa@cistrome.org'
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    #msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    if resultOpt == 'html':
        msg.attach( MIMEText(html, 'html') )
    else:
        import tempfile
        try:
           temp = tempfile.TemporaryFile()
           temp.write(attachment)
           temp.seek(0)
           part = MIMEBase('application', "octet-stream")
           part.set_payload( temp.read() )
           Encoders.encode_base64(part)
           part.add_header('Content-Disposition', 'attachment; filename="%s"'
                           % subject + ".xls")
           msg.attach(part)
        finally:
           temp.close()

    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()

