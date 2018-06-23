import smtplib
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication



def send_email(alexa_resopnse, filename = None):
    From = "sg.alexa.updates@gmail.com"
    To = 'sourabh.iitg@gmail.com'
    passwd = "5gupdates"
    recipients = ['sourabh.iitg@gmail.com','sg.alexa.updates@gmail.com']

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(From, passwd)

    mns = 'value'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Alexa Updates"
    msg['From'] = From
    msg['To'] = ", ".join(recipients)
    #msg['Cc'] = 'cryptobarati@gmail.com, sourabh.iitg@gmail.com'

    body = alexa_resopnse


    msg.attach(MIMEText(body, "plain"))

    if filename :
        

        with open(filename, "rb") as fil :
            part = MIMEApplication(fil.read(),Name = basename(filename))

        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(filename)
        msg.attach(part)

    text = msg.as_string()
    server.sendmail(From, recipients,text )
    server.quit()
