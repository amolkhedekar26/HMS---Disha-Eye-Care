import requests


class Fast2SMS:
    @staticmethod
    def send_sms(phone_number, message):
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = f"sender_id=Cghpet&message={message}&language=english&route=v3&numbers={phone_number}"
        headers = {
            'authorization': "mOFr6R4jAgj7qqrpYGs7U5LtDJ5SdUvC8rBrZqTxRndi2jZeCXTaS83Q2Kqd",
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
