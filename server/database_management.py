import mysql.connector
import datetime


class Database:
    def __init__(self, host, user, password, database) -> None:
        self.connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database,
            ssl_disabled=True,
        )

        self.cursor = self.connection.cursor(buffered=True)

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

        user = [{"id": user[0], "email": user[1]} for user in self.cursor.fetchall()][0]
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

        return {
            "assistant_id": self.cursor.lastrowid,
            "prompt": prompt,
            "voice": voice,
            "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    def get_user_assistants(self, user_id):
        #self.connection.reconnect()
        get_assistants = ("SELECT * FROM assistants WHERE user_id=%s")
        self.cursor.execute(get_assistants, (user_id,))
        assistants = [
            {
                "id": assistant[0],
                "prompt": assistant[1],
                "voice": assistant[2],
                "created_at": assistant[4],
                "updated_at": assistant[5],
            } for assistant in self.cursor.fetchall()
        ]
        return assistants
    
    def get_assistant(self, assistant_id):
        #self.connection.reconnect()
        get_assistants = ("SELECT * FROM assistants WHERE assistant_id=%s")
        self.cursor.execute(get_assistants, (assistant_id,))
        assistant = [
            {
                "id": assistant[0],
                "prompt": assistant[1],
                "voice": assistant[2],
                "created_at": assistant[4],
                "updated_at": assistant[5],
            } for assistant in self.cursor.fetchall()
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
        uploaded_file: bytes,
        file_name: str,
    ):
        add_campaign = ("INSERT INTO campaigns"
                        "(user_id, assistant_id, phone_number_id, campaign_type, start_time, end_time, max_recalls, recall_interval, campaign_status, uploaded_file, file_name)"
                        "VALUES (%(user_id)s, %(assistant_id)s, %(phone_number_id)s, %(campaign_type)s, %(start_time)s, %(end_time)s, %(max_recalls)s, %(recall_interval)s, %(campaign_status)s, %(uploaded_file)s, %(file_name)s)")
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
            "uploaded_file": uploaded_file,
            "file_name": file_name,
            "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.cursor.execute(add_campaign, campaign_data)
        self.connection.commit()

        return {
            "id": self.cursor.lastrowid,
            "user_id": user_id,
            "assistant_id": assistant_id,
            "phone_number_id": phone_number_id,
            "campaign_type": campaign_type,
            "start_time": start_time,
            "end_time": end_time,
            "max_recalls": max_recalls,
            "recall_interval": recall_interval,
            "campaign_status": campaign_status,
            "uploaded_file": uploaded_file,
            "file_name": file_name,
            "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    def get_user_campaigns(self, user_id):
        #self.connection.reconnect()
        get_campaigns = ("SELECT * FROM campaigns WHERE user_id=%s")
        self.cursor.execute(get_campaigns, (user_id,))
        campaigns = [
            {
                "id": campaign[0],
                "assistant_id": campaign[2],
                "phone_number_id": campaign[3],
                "type": campaign[4],
                "days_of_week": self.get_campaign_days_of_week(campaign[0]),
                "start_time": str(campaign[5]),
                "end_time": str(campaign[6]),
                "max_recalls": campaign[7],
                "recall_interval": campaign[8],
                "status": campaign[9],
                "uploaded_file": campaign[10],
                "file_name": campaign[13],
                "created_at": campaign[11],
                "updated_at": campaign[12],
            } for campaign in self.cursor.fetchall()
        ]
        return campaigns
    
    def get_campaign(self, campaign_id):
        #self.connection.reconnect()
        get_campaigns = ("SELECT * FROM campaigns WHERE campaign_id=%s")
        self.cursor.execute(get_campaigns, (campaign_id,))
        campaign = [
            {
                "id": campaign[0],
                "assistant_id": campaign[2],
                "phone_number_id": campaign[3],
                "type": campaign[4],
                "start_time": campaign[5],
                "end_time": campaign[6],
                "max_recalls": campaign[7],
                "recall_interval": campaign[8],
                "status": campaign[9],
                "uploaded_file": campaign[10],
                "file_name": campaign[13],
                "created_at": campaign[11],
                "updated_at": campaign[12],
            } for campaign in self.cursor.fetchall()
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

        return {
            "id": self.cursor.lastrowid,
            "phone_number": phone_number,
            "user_id": user_id,
            "account_sid": account_sid,
            "auth_token": auth_token,
            "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    def get_user_phone_numbers(self, user_id):
        #self.connection.reconnect()
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
            } for phone_number in self.cursor.fetchall()
        ]
        return phone_numbers
    
    def get_phone_number(self, phone_number_id: int):
        #self.connection.reconnect()
        get_phone_number_by_id = ("SELECT * FROM phone_numbers WHERE phone_number_id=%s")
        self.cursor.execute(get_phone_number_by_id, (phone_number_id,))
        phone_number = [
            {
                "id": phone_number[0],
                "phone_number": phone_number[1],
                "account_sid": phone_number[2],
                "auth_token": phone_number[3],
                "created_at": phone_number[5],
                "updated_at": phone_number[6],
            } for phone_number in self.cursor.fetchall()
        ][0]
        return phone_number
    
    def get_days_of_week(self):
        #self.connection.reconnect()
        get_days_of_week_list = ("SELECT * FROM days_of_week")
        self.cursor.execute(get_days_of_week_list)
        days_of_week = [
            {
                "id": day_of_week[0],
                "day_of_week": day_of_week[1],
            } for day_of_week in self.cursor.fetchall()
        ]
        return days_of_week

    def get_campaign_days_of_week(self, campaign_id: int):
        #self.connection.reconnect()
        get_campaign_days_of_week_list = ("SELECT * FROM campaign_days_of_week WHERE campaign_id = %s")
        self.cursor.execute(get_campaign_days_of_week_list, (campaign_id,))
        days_of_week = [
            {
                "day_of_week_id": day_of_week[0],
                "campaign_id": day_of_week[1],
            } for day_of_week in self.cursor.fetchall()
        ]
        return days_of_week

    def create_campaign_days_of_week(self, campaign_id: int, day_of_week_id: int):
        insert_campaign_days_of_week = (
            "INSERT INTO campaign_days_of_week"
            "(campaign_id, day_of_week_id)"
            "VALUES (%(campaign_id)s, %(day_of_week_id)s)"
        )

        campaign_days_of_week_data = {
            "campaign_id": campaign_id,
            "day_of_week_id": day_of_week_id,
        }

        self.cursor.execute(insert_campaign_days_of_week, campaign_days_of_week_data)
        self.connection.commit()

        return campaign_days_of_week_data
    
    def create_knowledge(
        self,
        user_id: int,
        file: bytes,
        file_name: str,
    ):
        insert_knowledge = ("INSERT INTO knowledge"
                            "(uploaded_file, user_id, file_name)"
                            "VALUES (%(uploaded_file)s, %(user_id)s, %(file_name)s)")
        knowledge_data = {
            "user_id": user_id,
            "uploaded_file": file,
            "file_name": file_name,
        }
        self.cursor.execute(insert_knowledge, knowledge_data)
        self.connection.commit()

        return {
            "id": self.cursor.lastrowid,
            "user_id": user_id,
            "uploaded_file": file,
            "file_name": file_name,
        }

    def get_user_knowledge(
        self,
        user_id,
    ):
        get_user_knowledge_list = ("SELECT * FROM knowledge WHERE user_id=%s")
        self.cursor.execute(get_user_knowledge_list, (user_id,))
        knowledge_list = [
            {
                "id": knowledge[0],
                "file": knowledge[2],
                "file_name": knowledge[3],
            } for knowledge in self.cursor.fetchall()
        ]
        return knowledge_list
    
    def create_assistant_knowledge(
        self,
        assistant_id: int,
        knowledge_id: int,
    ):
        insert_assistant_knowledge = ("INSERT INTO assistant_knowledge"
                                      "(assistant_id, knowledge_id)"
                                      "VALUES (%(assistant_id)s, %(knowledge_id)s)")
        knowledge_data = {
            "assistant_id": assistant_id,
            "knowledge_id": knowledge_id,
        }

        self.cursor.execute(insert_assistant_knowledge, knowledge_data)
        self.connection.commit()
        return knowledge_data

    def close(self):
        self.connection.close()