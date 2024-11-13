CREATE DATABASE VoiceAssistant;

USE VoiceAssistant;

CREATE TABLE users (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
    email TEXT(256),
    password_hash TEXT(256),
    is_active BOOLEAN,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE assistants (
	assistant_id INT AUTO_INCREMENT PRIMARY KEY,
    prompt MEDIUMTEXT,
    voice TEXT(128),
    user_id INT,
    created_at DATETIME,
    updated_at DATETIME,
    assistant_name TEXT(256),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE kndowledge (
    knowledge_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    uploaded_file LONGBLOB,
    file_name TEXT(256),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)

CREATE TABLE assistant_knowledge (
    knowledge_id INT,
    assistant_id INT,
    PRIMARY KEY (knowledge_id, assistant_id),
    FOREIGN KEY knowledge_id REFERENCES knowledge(knowledge_id),
    FOREIGN KEY assistant_id REFERENCES assistants(assistant_id)
)

CREATE TABLE telephony_providers (
	provider_id INT AUTO_INCREMENT PRIMARY KEY,
    provider_name TEXT(128)
);

CREATE TABLE phone_numbers (
	phone_number_id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number TEXT(32),
    account_sid TEXT,
    auth_token TEXT,
    user_id INT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
);

CREATE TABLE phone_number_providers (
	provider_id INT,
    phone_number_id INT,
    PRIMARY KEY (provider_id, phone_number_id),
    FOREIGN KEY (provider_id) REFERENCES telephony_providers(provider_id),
    FOREIGN KEY (phone_number_id) REFERENCES phone_numbers(phone_number_id)
);

CREATE TABLE campaigns (
	campaign_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    assistant_id INT,
    phone_number_id INT,
    campaign_type TEXT(64),
    start_time TIME,
    end_time TIME,
    max_recalls INT,
    recall_interval INT,
    campaign_status TEXT(32),
    uploaded_file LONGBLOB,
    created_at DATETIME,
    updated_at DATETIME,
    file_name TEXT(256),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (assistant_id) REFERENCES assistants(assistant_id),
    FOREIGN KEY (phone_number_id) REFERENCES phone_numbers(phone_number_id)
);

CREATE TABLE days_of_week (
	day_of_week_id INT AUTO_INCREMENT PRIMARY KEY,
    day_of_week TEXT(16)
);

CREATE TABLE campaign_days_of_week (
	day_of_week_id INT,
    campaign_id INT,
    PRIMARY KEY (day_of_week_id, campaign_id),
    FOREIGN KEY (day_of_week_id) REFERENCES days_of_week(day_of_week_id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

CREATE TABLE call_logs (
	call_id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT,
    assistant_id INT,
    client_id INT,
    call_tipe TEXT(32),
    start_datetime DATETIME,
    end_datetime DATETIME,
    duration_in_seconds INT,
    transcript TEXT,
    summary TEXT,
    success_score INT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (client_id) REFERENCES users(user_id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (assistant_id) REFERENCES assistants(assistant_id)
);

CREATE TABLE billing (
	billing_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    usage_units INT,
    usage_remains INT,
    paid BOOL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

