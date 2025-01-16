from dotenv import load_dotenv
import mysql.connector
import datetime
import requests
import os

load_dotenv(override=True)

class Database:
    def __init__(self, host, user, password, database) -> None:
        self.connection_parameters = {
            "user": user,
            "password": password,
            "host": host,
            "database": database,
        }
        """self.connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database,
        )

        self.cursor = self.connection.cursor(buffered=True)"""

    def create_user(
        self,
        email: str,
        password_hash: str,
    ):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            add_user = ("INSERT INTO users"
                        "(email, password_hash, created_at, updated_at)"
                        "VALUES (%(email)s, %(password_hash)s, %(created_at)s, %(updated_at)s);")

            user_data = {
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

            cursor.execute(add_user, user_data)
            connection.commit()
            connection.close()

    def get_user(self, email):
         with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_user = ("SELECT * FROM users WHERE email=%s;")

            cursor.execute(get_user, (email,))

            user = [{"id": user[0], "email": user[1]} for user in cursor.fetchall()][0]
            connection.close()
            return user

    def create_openai_assistant(
        self,
        user_id: int,
        prompt: str,
        voice: str,
        assistant_name: str
    ):
         with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            add_assistant = ("INSERT INTO openai_agents"
                            "(user_id, prompt, voice, created_at, updated_at, assistant_name)"
                            "VALUES (%(user_id)s, %(prompt)s, %(voice)s, %(created_at)s, %(updated_at)s, %(assistant_name)s)")
            
            assistant_data = {
                "user_id": user_id,
                "prompt": prompt,
                "voice": voice,
                "assistant_name": assistant_name,
                "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

            cursor.execute(add_assistant, assistant_data)
            connection.commit()
            connection.close()

            return {
                "assistant_id": cursor.lastrowid,
                "prompt": prompt,
                "voice": voice,
                "assistant_name": assistant_name,
                "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
         
    def create_elevenlabs_assistant(
        self,
        user_id: int,
        assistant_name: str,
        elevenlabs_agent_id: str,
    ):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            add_assistant = ("INSERT INTO elevenlabs_agents"
                            "(user_id, created_at, updated_at, assistant_name, elevenlabs_agent_id)"
                            "VALUES (%(user_id)s, %(created_at)s, %(updated_at)s, %(assistant_name)s, %(elevenlabs_agent_id)s)")

            assistant_data = {
                "user_id": user_id,
                "assistant_name": assistant_name,
                "elevenlabs_agent_id": elevenlabs_agent_id,
                "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

            cursor.execute(add_assistant, assistant_data)
            connection.commit()
            connection.close()

            return {
                "assistant_id": cursor.lastrowid,
                "assistant_name": assistant_name,
                "elevenlabs_agent_id": elevenlabs_agent_id,
                "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

    def get_user_assistants(self, user_id):
        assistants = []
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_openai_assistants = ("SELECT * FROM openai_agents WHERE user_id=%s")
            cursor.execute(get_openai_assistants, (user_id,))
            openai_assistants = [
                {
                    "id": assistant[0],
                    "llm_provider": "openai",
                    "voice_provider": "openai",
                    "assistant_type": "openai-realtime",
                    "transcriber_provider": "openai",
                    "llm": "gpt-4o-realtime",
                    "tts_model": "gpt-4o-realtime",
                    "stt_model": "gpt-4o-realtime",
                    "prompt": assistant[1],
                    "voice": assistant[2],
                    "assistant_name": assistant[6],
                    "created_at": assistant[4],
                    "updated_at": assistant[5],
                } for assistant in cursor.fetchall()
            ]
            assistants.extend(openai_assistants)

            get_elevenlabs_assistants = ("SELECT * FROM elevenlabs_agents WHERE user_id=%s")
            cursor.execute(get_elevenlabs_assistants, (user_id,))
            elevenlabs_assistants = []
            for assistant in cursor.fetchall():
                elevenlabs_assistant = {
                        "id": assistant[0],
                        "created_at": assistant[1],
                        "updated_at": assistant[2],
                        "assistant_name": assistant[3],
                        "assistant_type": "elevenlabs",
                    }

                agent_info = requests.get(
                    f'https://api.elevenlabs.io/v1/convai/agents/{assistant[4]}',
                    headers={
                        'xi-api-key': os.getenv("ELEVENLABS_API_KEY")
                    }
                ).json()
                print(assistant[4], agent_info)
                elevenlabs_assistant["llm_provider"] = "openai"
                elevenlabs_assistant["voice_provider"] = "elevenlabs"
                elevenlabs_assistant["transcriber_provider"] = "elevenlabs"
                elevenlabs_assistant["llm"] = agent_info["conversation_config"]["prompt"]["llm"]
                elevenlabs_assistant["tts_model"] = agent_info["conversation_config"]["tts"]["model_id"]
                elevenlabs_assistant["stt_model"] = "elevenlabs-asr"
                elevenlabs_assistant["prompt"] = agent_info["conversation_config"]["prompt"]["prompt"]
                elevenlabs_assistant["voice"] = agent_info["conversation_config"]["tts"]["voice_id"] # convert id to name
                elevenlabs_assistants.append(elevenlabs_assistant)

            assistants.extend(elevenlabs_assistants)
            connection.close()

            return assistants

    def get_openai_assistant(self, assistant_id):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_assistants = ("SELECT * FROM openai_agents WHERE assistant_id=%s")
            cursor.execute(get_assistants, (assistant_id,))
            assistant = [
                {
                    "id": assistant[0],
                    "prompt": assistant[1],
                    "voice": assistant[2],
                    "assistant_name": assistant[6],
                    "created_at": assistant[4],
                    "updated_at": assistant[5],
                } for assistant in cursor.fetchall()
            ][0]
            connection.close()
            return assistant
         
    def delete_openai_assistant(
        self,
        assistant_id: int,
    ):
        remove_assistant = f"DELETE FROM openai_agents WHERE assistant_id={assistant_id}"
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            cursor.execute(remove_assistant)
            connection.commit()
            connection.close()

        return {"deleted.assistant_id": assistant_id}
    
    def update_openai_assistant(
        self,
        user_id: int,
        assistant_id: int,
        assistant_name: str,
        prompt: str,
        voice: str,
        uploaded_files: list[object],
    ):
        update_assistant_query = ("UPDATE openai_agents "
                                  "SET prompt=%(prompt)s, voice=%(voice)s, assistant_name=%(assistant_name)s, updated_at=%(updated_at)s "
                                  "WHERE assistant_id=%(assistant_id)s")
        assistant_data = {
            "assistant_id": assistant_id,
            "assistant_name": assistant_name,
            "prompt": prompt,
            "voice": voice,
            "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            cursor.execute(update_assistant_query, assistant_data)
            connection.commit()
            connection.close()

        existing_knowledge = self.get_assistant_knowledge(assistant_id=assistant_id)
        existing_knowledge_ids = [knowledge_item["knowledge_id"] for knowledge_item in existing_knowledge]
        knowledgebase = existing_knowledge
        for knowledge in uploaded_files:
            # maybe it's not more effective than just update knowledgebase entirely, deleting all old knowledge (especially for large number of files)
            if knowledge.knowledge_id in existing_knowledge_ids:
                continue

            new_knowledge = self.create_knowledge(
                user_id=user_id,
                file=knowledge.file,
                file_name=knowledge.file_name,
            )

            # rename key
            new_knowledge["knowledge_id"] = new_knowledge.pop("id")
            knowledgebase.append(new_knowledge)
            new_knowledge_id = new_knowledge["knowledge_id"]

            self.create_assistant_knowledge(
                assistant_id=assistant_id,
                knowledge_id=new_knowledge_id,
            )

        return {
            "assistant_data": assistant_data,
            "knowledgebase": knowledgebase,
        }
    
    def delete_assistant(
        self,
        assistant_id: int,
    ):
        assistant_knowledge = self.get_assistant_knowledge(assistant_id)
        delete_assistant_query = f"DELETE FROM assistants WHERE assistant_id={assistant_id}"
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            for knowledge in assistant_knowledge:
                cursor.execute(f"DELETE FROM assistant_knowledge WHERE knowledge_id={knowledge["knowledge_id"]}")
                cursor.execute(f"DELETE FROM knowledge WHERE knowledge_id={knowledge["knowledge_id"]}")

            cursor.execute(delete_assistant_query)
            connection.commit()
            connection.close()
        
        return {"delete.assistant_id": assistant_id}

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
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
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

            cursor.execute(add_campaign, campaign_data)
            connection.commit()
            connection.close()

            return {
                "id": cursor.lastrowid,
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
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_campaigns = ("SELECT * FROM campaigns WHERE user_id=%s")
            cursor.execute(get_campaigns, (user_id,))
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
                } for campaign in cursor.fetchall()
            ]
            connection.close()
            return campaigns
    
    def get_campaign(self, campaign_id):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_campaigns = ("SELECT * FROM campaigns WHERE campaign_id=%s")
            cursor.execute(get_campaigns, (campaign_id,))
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
                } for campaign in cursor.fetchall()
            ][0]
            return campaign
    
    def update_campaign(
        self,
        campaign_id: int,
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
        update_campaign_query = ("UPDATE campaigns "
                                 "SET assistant_id=%(assistant_id)s, phone_number_id=%(phone_number_id)s, campaign_type=%(campaign_type)s, start_time=%(start_time)s, end_time=%(end_time)s, max_recalls=%(max_recalls)s, recall_interval=%(recall_interval)s, campaign_status=%(campaign_status)s, uploaded_file=%(uploaded_file)s, file_name=%(file_name)s "
                                 "WHERE campaign_id=%(campaign_id)s")
        campaign_data = {
            "campaign_id": campaign_id,
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
        }

        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            cursor.execute(update_campaign_query, campaign_data)
            connection.commit()
            connection.close()

        return campaign_data  

    def delete_campaign(
        self,
        campaign_id: int,
    ):
        delete_campaign_query = f"DELETE FROM campaigns WHERE campaign_id={campaign_id}"
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True) 
            cursor.execute(delete_campaign_query)
            connection.commit()
            connection.close()
        
        return {"delete.campaignt_id": campaign_id}      

    def create_phone_number(
        self,
        phone_number: str,
        user_id: int,
        account_sid: str,
        auth_token: str,
    ):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
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

            cursor.execute(add_phone_number, phone_number_data)
            connection.commit()
            connection.close()

            return {
                "id": cursor.lastrowid,
                "phone_number": phone_number,
                "user_id": user_id,
                "account_sid": account_sid,
                "auth_token": auth_token,
                "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

    def get_user_phone_numbers(self, user_id):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_phone_numbers = ("SELECT * FROM phone_numbers WHERE user_id=%s")
            cursor.execute(get_phone_numbers, (user_id,))
            phone_numbers = [
                {
                    "id": phone_number[0],
                    "phone_number": phone_number[1],
                    "account_sid": phone_number[2],
                    "auth_token": phone_number[3],
                    "created_at": phone_number[5],
                    "updated_at": phone_number[6],
                } for phone_number in cursor.fetchall()
            ]
            connection.close()
            return phone_numbers
    
    def get_phone_number(self, phone_number_id: int):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_phone_number_by_id = ("SELECT * FROM phone_numbers WHERE phone_number_id=%s")
            cursor.execute(get_phone_number_by_id, (phone_number_id,))
            phone_number = [
                {
                    "id": phone_number[0],
                    "phone_number": phone_number[1],
                    "account_sid": phone_number[2],
                    "auth_token": phone_number[3],
                    "created_at": phone_number[5],
                    "updated_at": phone_number[6],
                } for phone_number in cursor.fetchall()
            ][0]
            connection.close()
            return phone_number
    
    def get_days_of_week(self):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_days_of_week_list = ("SELECT * FROM days_of_week")
            cursor.execute(get_days_of_week_list)
            days_of_week = [
                {
                    "id": day_of_week[0],
                    "day_of_week": day_of_week[1],
                } for day_of_week in cursor.fetchall()
            ]
            connection.close()
            return days_of_week

    def get_campaign_days_of_week(self, campaign_id: int):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_campaign_days_of_week_list = ("SELECT * FROM campaign_days_of_week WHERE campaign_id = %s")
            cursor.execute(get_campaign_days_of_week_list, (campaign_id,))
            days_of_week = [
                {
                    "day_of_week_id": day_of_week[0],
                    "campaign_id": day_of_week[1],
                } for day_of_week in cursor.fetchall()
            ]
            connection.close()
            return days_of_week

    def create_campaign_days_of_week(self, campaign_id: int, day_of_week_id: int):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            insert_campaign_days_of_week = (
                "INSERT INTO campaign_days_of_week"
                "(campaign_id, day_of_week_id)"
                "VALUES (%(campaign_id)s, %(day_of_week_id)s)"
            )

            campaign_days_of_week_data = {
                "campaign_id": campaign_id,
                "day_of_week_id": day_of_week_id,
            }

            cursor.execute(insert_campaign_days_of_week, campaign_days_of_week_data)
            connection.commit()
            connection.close()

            return campaign_days_of_week_data
    
    def create_knowledge(
        self,
        user_id: int,
        file: bytes,
        file_name: str,
    ):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            insert_knowledge = ("INSERT INTO knowledge"
                                "(uploaded_file, user_id, file_name)"
                                "VALUES (%(uploaded_file)s, %(user_id)s, %(file_name)s)")
            knowledge_data = {
                "user_id": user_id,
                "uploaded_file": file,
                "file_name": file_name,
            }
            cursor.execute(insert_knowledge, knowledge_data)
            connection.commit()
            connection.close()

            return {
                "id": cursor.lastrowid,
                "user_id": user_id,
                "uploaded_file": file,
                "file_name": file_name,
            }
        
    def get_user_knowledge(
        self,
        user_id,
    ):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            get_user_knowledge_list = ("SELECT * FROM knowledge WHERE user_id=%s")
            cursor.execute(get_user_knowledge_list, (user_id,))
            knowledge_list = [
                {
                    "id": knowledge[0],
                    "file": knowledge[2],
                    "file_name": knowledge[3],
                } for knowledge in cursor.fetchall()
            ]
            connection.close()
            return knowledge_list
    
    def create_assistant_knowledge(
        self,
        assistant_id: int,
        knowledge_id: int,
    ):
        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            insert_assistant_knowledge = ("INSERT INTO assistant_knowledge"
                                        "(assistant_id, knowledge_id)"
                                        "VALUES (%(assistant_id)s, %(knowledge_id)s)")
            knowledge_data = {
                "assistant_id": assistant_id,
                "knowledge_id": knowledge_id,
            }

            cursor.execute(insert_assistant_knowledge, knowledge_data)
            connection.commit()
            connection.close()

            return knowledge_data
        
    def get_assistant_knowledge(
            self,
            assistant_id: int
    ):
        get_assistant_knowledgebase_query = ("SELECT * " 
                                             "FROM assistant_knowledge "
                                             "INNER JOIN knowledge "
                                             "ON knowledge.knowledge_id=assistant_knowledge.knowledge_id "
                                            f"WHERE assistant_knowledge.assistant_id={assistant_id}")

        with mysql.connector.connect(**self.connection_parameters) as connection:
            cursor = connection.cursor(buffered=True)
            cursor.execute(get_assistant_knowledgebase_query)
            knowledgebase=[
                {
                    "knowledge_id": assistant_knowledge[0],
                    "assistant_id": assistant_knowledge[1],
                    "user_id": assistant_knowledge[3],
                    "uploaded_file": assistant_knowledge[4],
                    "file_name": assistant_knowledge[5],
                } for assistant_knowledge in cursor.fetchall()
            ]

            connection.close()

            return knowledgebase