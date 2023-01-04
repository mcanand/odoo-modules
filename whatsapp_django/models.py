import json

import requests
from django.db import models


class Whatsapp(models.Model):

    is_active = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20)
    phone_number_id = models.CharField(max_length=20)
    app_id = models.CharField(max_length=25)
    app_secret = models.CharField(max_length=40)
    auth_token = models.TextField()
    graph_host_url = models.CharField(max_length=30, default="https://graph.facebook.com")
    api_version = models.CharField(max_length=5, default="v14.0")

    def save(self, *args, **kwargs):
        if self.is_active:
            qs = type(self).objects.filter(is_active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            qs.update(is_active=False)

        super(Whatsapp, self).save(*args, **kwargs)

    def get_auth_token(self):
        self.auth_token = ''
        self.save()

    def upload_image(self, img_path, retry=0):
        api_url = self.graph_host_url + "/" + self.api_version + "/" + self.phone_number_id + "/media"
        body = {'messaging_product': 'whatsapp'}
        files = [('file', ('invoice.jpg', open(img_path, 'rb'), 'image/jpeg'))]
        api_header = {'Authorization': 'Bearer %s' % self.auth_token}
        response = requests.post(url=api_url, headers=api_header, data=body, files=files, verify=False)
        if retry != 4:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                retry += 1
                self.get_auth_token()
                self.upload_image(retry)
        else:
            return False

    def send_text_message(self, recipient, message, retry=0):
        api_url = self.graph_host_url + "/" + self.api_version + "/" + self.phone_number_id + "/messages"
        api_header = {'Content-Type': 'application/json',
                      'Authorization': 'Bearer %s' % self.auth_token,
                      'Accept': 'application/json'}
        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        response = requests.post(url=api_url, headers=api_header, data=json.dumps(body))
        if retry != 4:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                retry += 1
                self.get_auth_token()
        else:
            return False

    def send_text_media_message(self, recipient, template, image_id, message_params, retry=0):
        api_url = self.graph_host_url + "/" + self.api_version + "/" + self.phone_number_id + "/messages"
        api_header = {'Content-Type': 'application/json',
                      'Authorization': 'Bearer %s' % self.auth_token,
                      'Accept': 'application/json'}
        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "template",
            "template": {
                "name": template['name'],
                "language": {
                    "code": template['lang_code']
                },
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "image",
                                "image": {
                                    "id": image_id
                                }
                            }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": msg_param['type'],
                                msg_param['type']: msg_param['value']
                            } for msg_param in message_params
                        ]
                    }
                ]
            }
        }
        response = requests.post(url=api_url, headers=api_header, data=json.dumps(body))
        print(response)
        print(response.json())
        if retry != 4:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                retry += 1
                self.get_auth_token()
        else:
            return False
