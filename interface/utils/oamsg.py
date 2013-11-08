#!/usr/local/services/python/bin/python
# -*- coding: utf-8 -*-

"""
TOF2.0 web service消息发送接口
powellli修改自mavisluo的messagehelper.py 
"""

import httplib 

port = 53041
serv_ip = '10.142.54.12'
host = 'ws.tof.oa.com'
uri = '/MessageService.svc?wsdl'
app_key = 'ea400b8cd7fa48eca0f1864c93a96155'

envelope_head = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:xsd="http://www.w3.org/1999/XMLSchema"
>
<SOAP-ENV:Header>
<Application_Context xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><AppKey xmlns="http://schemas.datacontract.org/2004/07/Tencent.OA.Framework.Context">%s</AppKey></Application_Context>
</SOAP-ENV:Header>
"""

envelope_mail_template = """<SOAP-ENV:Body>
<n2:SendMail xmlns:n2="http://tempuri.org/">
<n2:mail xmlns:n3="http://schemas.datacontract.org/2004/07/Tencent.OA.Framework.Messages.DataContract">
<n3:Attachments></n3:Attachments>
<n3:Bcc>%s</n3:Bcc>
<n3:BodyFormat>%s</n3:BodyFormat>
<n3:CC>%s</n3:CC>
<n3:Content>%s</n3:Content>
<n3:EmailType>%s</n3:EmailType>
<n3:From>%s</n3:From>
<n3:Location xsi:nil="true"></n3:Location>
<n3:Organizer xsi:nil="true"></n3:Organizer>
<n3:Priority>%s</n3:Priority>
<n3:Title>%s</n3:Title>
<n3:To>%s</n3:To>
</n2:mail>
</n2:SendMail>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>""" 

envelope_rtx_template = """<SOAP-ENV:Body>
<n2:SendRTX xmlns:n2="http://tempuri.org/">
<n2:message xmlns:n3="http://schemas.datacontract.org/2004/07/Tencent.OA.Framework.Messages.DataContract">
<n3:MsgInfo>%s</n3:MsgInfo>
<n3:Priority>%s</n3:Priority>
<n3:Receiver>%s</n3:Receiver>
<n3:Sender>%s</n3:Sender>
<n3:Title>%s</n3:Title>
</n2:message>
</n2:SendRTX>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>""" 

envelope_sms_template = """<SOAP-ENV:Body>
<n2:SendSMS xmlns:n2="http://tempuri.org/">
<n2:message xmlns:n3="http://schemas.datacontract.org/2004/07/Tencent.OA.Framework.Messages.DataContract">
<n3:MsgInfo>%s</n3:MsgInfo>
<n3:Priority>%s</n3:Priority>
<n3:Receiver>%s</n3:Receiver>
<n3:Sender>%s</n3:Sender>
</n2:message>
</n2:SendSMS>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>""" 

def safestr(obj, encoding='utf-8'):
    if isinstance(obj, unicode):
        return obj.encode(encoding)
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, (set, list, tuple)) or hasattr(obj, 'next'):
        return ';'.join([safestr(i) for i in obj])
    else:
        return str(obj)

def htmlquote(text):
    return text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace("'",'&apos;').replace('"','&quot;')

class OAMessage(object):
    def __init__(self, app_key=app_key, host=host, port=port, serv_ip=serv_ip, uri=uri): 
        self.app_key = app_key
        self.host = host
        self.port = port
        self.serv_ip = serv_ip
        self.uri = uri
        self.envelope_head = envelope_head % self.app_key

    def _send_data(self, data, method):
        http_conn = httplib.HTTP(self.serv_ip, self.port)
        http_conn.putrequest('POST', self.uri) 
        http_conn.putheader('Host', self.host) 
        http_conn.putheader('Content-Type', 'text/xml; charset="utf-8"') 
        http_conn.putheader('Content-Length', str(len(data)))
        http_conn.putheader('SOAPAction', 'http://tempuri.org/IMessageService/'+method) 
        http_conn.endheaders() 
        http_conn.send(data) 
        ret = http_conn.getreply() 
        #print http_conn.getfile().read()
        return ret

    def send_rtx(self, receiver, title, msginfo, sender='900', priority='Normal'):
        if priority not in ['Low', 'Normal', 'Hight']:
            priority = 'Low'
        receiver = safestr(receiver)
        sender = safestr(sender)
        receiver = safestr(receiver)
        title = safestr(title)
        msginfo = safestr(htmlquote(msginfo))
        msginfo = msginfo.replace('[', '(').replace(']', ')')

        envelope_rtx = envelope_rtx_template % (msginfo, priority, receiver, sender, title)
        envelope = self.envelope_head + envelope_rtx

        (status_code, message, reply_headers) = self._send_data(envelope, 'SendRTX')
        return status_code

    def send_mail(self, receiver, title, content, sender='oa-admin@tencent.com', priority='Normal', cc=[], bcc=[], is_html=True, mstype='SEND_TO_ENCHANGE'):
        if is_html:
            content = htmlquote(content)
        receiver = safestr(receiver)
        title = safestr(title)
        content = safestr(content)
        sender = safestr(sender)
        cc = safestr(cc)
        bcc = safestr(bcc)

        if mstype not in ['SEND_TO_INTERNET', 'SEND_TO_ENCHANGE', 'SEND_TO_MEETING']:
            mstype = 'SEND_TO_ENCHANGE'
        if priority not in ['Low', 'Normal', 'Hight']:
            priority = 'Low'

        text_format = 'Html' if is_html else 'Text'
        envelope_mail = envelope_mail_template % (bcc, text_format, cc, content, mstype, sender, priority, title, receiver)
        envelope = self.envelope_head + envelope_mail

        (status_code, message, reply_headers) = self._send_data(envelope, 'SendMail')
        return status_code

    def send_sms(self, receiver, msginfo, sender='900', priority='Normal'):
        sender = safestr(sender)
        receiver = safestr(receiver)
        msginfo = safestr(htmlquote(msginfo))
        if priority not in ['Low', 'Normal', 'Hight']:
            priority = 'Normal'

        envelope_sms = envelope_sms_template %(msginfo, priority, receiver, sender)
        envelope = self.envelope_head + envelope_sms
        
        (status_code, message, reply_headers) = self._send_data(envelope, 'SendSMS')
        return status_code

def help(exe):
    print exe, 'rtx receiver title content [sender [priority]]'
    print exe, 'sms receiver content [sender [priority]]'
    print exe, 'mail receiver title content [sender [priority [cc [bcc]]]]'

if __name__ == '__main__':
    import sys
    client = OAMessage()
    if len(sys.argv) < 2 or sys.argv[1] not in ('rtx', 'sms', 'mail'):
        help(sys.argv[0])
    else:
        try:
            print getattr(client, 'send_'+sys.argv[1])(*sys.argv[2:])
        except Exception, e:
            print 'parameters error!'
            help(sys.argv[0])
            raise e
