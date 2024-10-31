import os.path as os_path
from configparser import ConfigParser

CURRENT_PATH = os_path.dirname(os_path.abspath(__file__))
SETTING_FILE_PATH = os_path.join(CURRENT_PATH,"../setting.ini")

__cf = ConfigParser()
__cf.read(os_path.join(CURRENT_PATH,SETTING_FILE_PATH),encoding="utf-8")

# DB
DB_CHOOSE = __cf.get("db","choose")
TABLE_SET = {
    'user':__cf.get("db","user_table"),
    'web': __cf.get("db","web_table")
}
# SQLITE
SQLITE_SET = {
    'user_db_path':__cf.get("sqlite","user_db_path"),
    'web_db_path':__cf.get("sqlite","web_db_path")
}
# MYSQL
MYSQL_SET = {
    'host' : __cf.get("mysql","host"),
    'port': __cf.get("mysql","port"),
    'account' : __cf.get("mysql","account"),
    'pswd' : __cf.get("mysql","password"),
    'db_name' : __cf.get("mysql","db_name")
}


REMOTE_API_TOKEN = __cf.get("token","api_token")

TIME_SET = {
    'start': __cf.get("timeSet","start"),  
    'end': __cf.get("timeSet","end")
}

MAIL_SET = {
    'admin':__cf.get("mail","admin_mail"),
    'account':__cf.get("mail","account"),
    'host': __cf.get("mail","host"),
    'token':__cf.get("mail","token")
}

ADMIN_ACCOUNT = MAIL_SET['admin'] if MAIL_SET['admin'] else "未设置"

ADDRESS_NAME = __cf.get("signInfo","address_name")

TIME_CHCECK_WAIT = int(__cf.get("timeSet","check_wait"))
TIME_SLEEP_WAIT = int(__cf.get("timeSet","sleep_wait"))

SIGN_MAX_TRY_TIMES = int(__cf.get("signInfo","times_max_try"))
FAIL_MAX_TRY_DAYS = int(__cf.get("signInfo","days_max_try"))
AYN_MAX_USERS = int(__cf.get("signInfo","ayn_max_users"))

MYSQL_INIT_SQL = f"""
    CREATE DATABASE IF NOT EXISTS {MYSQL_SET['db_name']};
"""

USER_DB_INIT_SQL = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_SET['user']} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account TEXT NOT NULL,
        pswd TEXT NOT NULL,
        email TEXT NOT NULL,
        coordinate TEXT NOT NULL,
        updateTime TEXT NOT NULL,
        signTime TEXT,
        success INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        failDays INTEGER DEFAULT 0
    );
'''
NOTICE_DB_INIT_SQL = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_SET['web']}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        time TEXT NOT NULL
    );
'''