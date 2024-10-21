import mysql.connector
import datetime

class Database:
    def __init__(self, host, user, password, database) -> None:
        self.connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database,
        )

        self.cursor = self.connection.cursor()

    def create_user(
        self,
        email: str,
        password_hash: str,
    ):
        add_user = ("INSERT INTO users"
                    "(email, password_hash, created_at, updated_at)"
                    "VALUES (%(email)s, %(password_hash)s, %(created_at)s, %(updated_at)s);")

        user_data = {
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.cursor.execute(add_user, user_data)
        self.connection.commit()

    def get_user(self, email):
        get_user = ("SELECT * FROM users WHERE email=%s;")

        self.cursor.execute(get_user, (email,))

        user = [{"id": user[0], "email": user[1]} for user in self.cursor][0]
        return user

    def create_assistant(
        self,
        user_id: int,
        prompt: str,
        voice: str,
    ):
        add_assistant = ("INSERT INTO assistants"
                        "(user_id, prompt, voice, created_at, updated_at)"
                        "VALUES (%(user_id)s, %(prompt)s, %(voice)s, %(created_at)s, %(updated_at)s)")
        
        assistant_data = {
            "user_id": user_id,
            "prompt": prompt,
            "voice": voice,
            "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.cursor.execute(add_assistant, assistant_data)
        self.connection.commit()

    def get_user_assistants(self, user_id):
        get_assistants = ("SELECT * FROM assistants WHERE user_id=%s")
        self.cursor.execute(get_assistants, (user_id,))
        assistants = [
            {
                "id": assistant[0],
                "prompt": assistant[1],
                "voice": assistant[2],
                "created_at": assistant[4],
                "updated_at": assistant[5],
            } for assistant in self.cursor
        ]
        return assistants
    
    def get_assistant(self, assistant_id):
        #testme
        get_assistants = ("SELECT * FROM assistants WHERE assistant_id=%s")
        self.cursor.execute(get_assistants, (assistant_id,))
        assistant = [
            {
                "id": assistant[0],
                "prompt": assistant[1],
                "voice": assistant[2],
                "created_at": assistant[4],
                "updated_at": assistant[5],
            } for assistant in self.cursor
        ][0]
        return assistant

    def create_campaign(
        self,
        user_id: int,
        assistant_id: int,
        phone_number_id: int,
        campaign_type: str,
        start_time: str,
        end_time: str,
        max_recalls: int,
        recall_interval: int,
        campaign_status: str,
    ):
        add_campaign = ("INSERT INTO campaigns"
                        "(user_id, assistant_id, phone_number_id, campaign_type, start_time, end_time, max_recalls, recall_interval, campaign_status)"
                        "VALUES (%(user_id)s, %(assistant_id)s, %(phone_number_id)s, %(campaign_type)s, %(start_time)s, %(end_time)s, %(max_recalls)s, %(recall_interval)s, %(campaign_status)s)")

        campaign_data = {
            "user_id": user_id,
            "assistant_id": assistant_id,
            "phone_number_id": phone_number_id,
            "campaign_type": campaign_type,
            "start_time": start_time,
            "end_time": end_time,
            "max_recalls": max_recalls,
            "recall_interval": recall_interval,
            "campaign_status": campaign_status,
            "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.cursor.execute(add_campaign, campaign_data)
        self.connection.commit()

    def get_user_campaigns(self, user_id):
        get_campaigns = ("SELECT * FROM campaigns WHERE user_id=%s")
        self.cursor.execute(get_campaigns, (user_id,))
        campaigns = [
            {
                "id": campaign[0],
                "type": campaign[4],
                "start_time": campaign[5],
                "end_time": campaign[6],
                "max_recalls": campaign[7],
                "recall_interval": campaign[8],
                "status": campaign[9],
                "created_at": campaign[10],
                "updated_at": campaign[11],
            } for campaign in self.cursor
        ]
        return campaigns
    
    def get_campaign(self, campaign_id):
        #testme
        #fixme возможно нужно возвращать и phone_number_id
        get_campaigns = ("SELECT * FROM campaigns WHERE campaign_id=%s")
        self.cursor.execute(get_campaigns, (campaign_id,))
        campaign = [
            {
                "id": campaign[0],
                "assistant_id": campaign[2],
                "type": campaign[4],
                "start_time": campaign[5],
                "end_time": campaign[6],
                "max_recalls": campaign[7],
                "recall_interval": campaign[8],
                "status": campaign[9],
                "created_at": campaign[10],
                "updated_at": campaign[11],
            } for campaign in self.cursor
        ][0]
        return campaign

    def create_phone_number(
            self,
            phone_number: str,
            user_id: int,
            account_sid: str,
            auth_token: str,
    ):
        add_phone_number = ("INSERT INTO phone_numbers"
                            "(phone_number, user_id, account_sid, auth_token, created_at, updated_at)"
                            "VALUES (%(phone_number)s, %(user_id)s, %(account_sid)s, %(auth_token)s, %(created_at)s, %(updated_at)s)")
        
        phone_number_data = {
            "phone_number": phone_number,
            "user_id": user_id,
            "account_sid": account_sid,
            "auth_token": auth_token,
            "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.cursor.execute(add_phone_number, phone_number_data)
        self.connection.commit()

    def get_user_phone_numbers(self,user_id):
        get_phone_numbers = ("SELECT * FROM phone_numbers WHERE user_id=%s")
        self.cursor.execute(get_phone_numbers, (user_id,))
        phone_numbers = [
            {
                "id": phone_number[0],
                "phone_number": phone_number[1],
                "account_sid": phone_number[2],
                "auth_token": phone_number[3],
                "created_at": phone_number[5],
                "updated_at": phone_number[6],
            } for phone_number in self.cursor
        ]
        return phone_numbers

    def close(self):
        self.connection.close()