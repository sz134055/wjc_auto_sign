import aiosqlite
import aiomysql
from time import time
from datetime import datetime
from api.setting import USER_DB_INIT_SQL,FAIL_MAX_TRY_DAYS,NOTICE_DB_INIT_SQL,DB_CHOOSE,TABLE_SET,SQLITE_SET,MYSQL_SET,MYSQL_INIT_SQL,AYN_MAX_USERS
from api.log_setting import logger
from typing import Iterable, Any, Optional, List


def getTime():
    return str(time()).replace('.','')[:13]

class DBControlBase:
    def __init__(self):
        self.coon = None
        self.sqlite_path = None
    async def set_path(self,db_path):
        self.db_path = db_path
    async def connect(self):
        raise NotImplementedError

    async def execute(self, sql:str, params = None):
        raise NotImplementedError
    async def query(self, sql:str, params = None):
        raise NotImplementedError

    async def query_one(self, sql:str, params = None):
        raise NotImplementedError
    
    async def update(self, sql:str, params = None):
        raise NotImplementedError

    async def close(self):
        if self.coon:
            await self.coon.close()
            self.coon = None

class MysqlControl(DBControlBase):
    def __init__(self):
        super().__init__()
        self.cur = None
    async def connect(self):
        self.coon = await aiomysql.connect(
            host=MYSQL_SET['host'],
            port=int(MYSQL_SET['port']), 
            user=MYSQL_SET['account'], 
            password=MYSQL_SET['pswd'], 
            charset='utf8mb4',
            cursorclass= aiomysql.cursors.DictCursor
        )
        self.cur = await self.coon.cursor()
        await self.execute(MYSQL_INIT_SQL)
        await self.coon.select_db(MYSQL_SET['db_name'])
        

    async def execute(self, sql:str, params = None):
        await self.cur.execute(sql,params)

    async def query(self, sql:str, params = None):
        await self.execute(sql,params)
        res = await self.cur.fetchall()
        return res

    async def query_one(self, sql:str, params = None):
        await self.execute(sql,params)
        res = await self.cur.fetchone()
        return res
    
    async def update(self, sql:str, params = None):
        res = await self.execute(sql,params)
        await self.coon.commit()
        return res
    
    async def close(self):
        if self.coon and not self.coon.closed:
            self.coon.close()


class SqliteControl(DBControlBase):
    def __init__(self):
        super().__init__()
        #self.coon = await self.connect()
    
    async def connect(self):
        if not self.db_path:
            raise Exception('未设置sqlite_path')
        self.coon = await aiosqlite.connect(self.db_path)
        self.coon.row_factory = aiosqlite.Row
        
    async def execute(self, sql:str, params = None):
        if not self.coon:
            await self.connect()
        sql = sql.replace(r'%s','?')    # sqlite3 对不支持 %s进行转换
        cur = await self.coon.execute(sql,params)
        return cur
        # NO STOP

    async def query(self, sql:str, params = None) -> List[dict]:
        cursor = await self.execute(sql,params)
        res = await cursor.fetchall()
        await self.close()
        return [dict(row) for row in res]

    async def query_one(self, sql:str, params = None) -> Optional[dict]:
        cursor = await self.execute(sql,params)
        res = await cursor.fetchone()
        await self.close()
        return dict(res) if res else None
    
    async def update(self, sql:str, params = None):
        await self.execute(sql,params)
        await self.coon.commit()
        await self.close()
        return None


class MysqlPoolControl(DBControlBase):
    def __init__(self):
        super().__init__()
        self.pool = None

    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host=MYSQL_SET['host'],
            port=int(MYSQL_SET['port']), 
            user=MYSQL_SET['account'], 
            password=MYSQL_SET['pswd'], 
            charset='utf8mb4',
            minsize=5,
            maxsize=AYN_MAX_USERS,
            cursorclass= aiomysql.cursors.DictCursor
        )

    async def getCurosr(self):
        conn = await self.pool.acquire()
        await conn.select_db(MYSQL_SET['db_name'])
        cur = await conn.cursor()
        return conn, cur

    async def execute(self, sql:str, params= None):
        conn, cur = await self.getCurosr()
        await conn.select_db(MYSQL_SET['db_name'])
        await cur.execute(sql, params)
        await cur.close()
        await self.pool.release(conn)

    async def query(self, sql: str, params = None):
        conn, cur = await self.getCurosr()
        await conn.select_db(MYSQL_SET['db_name'])
        await cur.execute(sql, params)
        res = await cur.fetchall()
        await cur.close()
        await self.pool.release(conn)
        return res

    async def query_one(self, sql: str, params = None):
        conn, cur = await self.getCurosr()
        await conn.select_db(MYSQL_SET['db_name'])
        await cur.execute(sql, params)
        res = await cur.fetchone()
        await cur.close()
        await self.pool.release(conn)
        return res

    async def update(self, sql: str, params = None):
        conn, cur = await self.getCurosr()
        await conn.select_db(MYSQL_SET['db_name'])
        await cur.execute(sql, params)
        await conn.commit()
        await cur.close()
        await self.pool.release(conn)
    
    async def close(self):
        self.pool.close()
        await self.pool.wait_closed()

class UserDBControl():
    SQLITE_PATH = SQLITE_SET['user_db_path']
    def __init__(self):
        self.db = None

    async def init_db(self,mysql_pool:bool=False):
        if mysql_pool or DB_CHOOSE == 'mysql':
            self.db = MysqlPoolControl()
            await self.db.connect()
            await self.db.update(USER_DB_INIT_SQL.replace("AUTOINCREMENT","AUTO_INCREMENT"))
        elif DB_CHOOSE == 'sqlite':
            self.db = SqliteControl()
            await self.db.set_path(self.SQLITE_PATH)
            await self.db.update(USER_DB_INIT_SQL)
            await self.db.close()
        # elif DB_CHOOSE == 'mysql':
        #     self.db = MysqlControl()
        #     await self.db.connect()
        #     await self.db.update(USER_DB_INIT_SQL.replace("AUTOINCREMENT","AUTO_INCREMENT"))
        
        else:
            raise ValueError("数据库选择参数错误，填写 sqlite 或 mysql")
        

    async def update_user(self, account:str, pswd:str, email:str, coordinate:str):
        """
        附带账号检查的账号更新

        若账号可查询，则以账号更新优先，更新剩余数据；若账号不可查，则以邮箱优先，更新剩余数据。
        传入数据至少要做到邮箱准确可查
        
        :param account: 账号
        :param pswd: 密码
        :param email: 邮箱
        :param coordinate: 签到坐标
        :return: None
        """
        db = self.db
        account_res = await db.query_one(f"SELECT * FROM {TABLE_SET['user']} WHERE account = %s", (account,))
        email_res = await db.query_one(f"SELECT * FROM {TABLE_SET['user']} WHERE email = %s", (email,))
        if account_res:
            await db.update(f"UPDATE {TABLE_SET['user']} SET pswd=%s,email=%s,coordinate=%s,updateTime=%s,failDays=0,active=1 WHERE account = %s", (pswd, email, coordinate,getTime(),account))
            logger.info(f"更新用户{account}信息成功[账号优先 {account}]")
            return {'code':'ok','msg':f"更新用户{account}信息成功[账号优先 {account}]"}
        elif email_res:
            await db.update(f"UPDATE {TABLE_SET['user']} SET account=%s,pswd=%s,coordinate=%s,updateTime=%s,failDays=0,active=1 WHERE email=%s", (account,pswd,coordinate,getTime(),email))
            logger.info(f"更新用户{account}信息成功[邮箱优先 {email}]")
            return {'code':'ok','msg':f"更新用户{account}信息成功[邮箱优先 {email}]"}
        else:
            logger.info(f"更新用户{account}信息失败[账号或邮箱不存在 {email}]")
            return {'code':'fail','msg':f"更新用户{account}信息失败[账号或邮箱不存在 {email}]"}

    async def add_user(self, account:str, pswd:str, email:str, coordinate:str):
        db = self.db
        account_res = await db.query_one(f"SELECT * FROM {TABLE_SET['user']} WHERE account = %s", (account,))
        email_res = await db.query_one(f"SELECT * FROM {TABLE_SET['user']} WHERE email = %s", (email,))
        if account_res or email_res:
            await self.update_user(account, pswd, email, coordinate)
            logger.info(f"添加或更新用户{account} 添加成功")
        else:
            await db.update(f"INSERT INTO {TABLE_SET['user']} (account,pswd,email,coordinate,updateTime,signTime,success,total,active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (account, pswd, email, coordinate, getTime(), '0', 0, 0,1))
            logger.info(f"添加或更新用户{account} 添加成功")
            return {'code':'ok','msg':'新用户{account} 添加成功'}
    

    async def check_user(self, account:str):
        """
        检查用户是否签到

        """
        db = self.db
        user_info = await db.query_one(f"SELECT * FROM {TABLE_SET['user']} WHERE account = %s", (account,))
        if user_info:
            lastSignTime = datetime.fromtimestamp(int(user_info['signTime']) / 1000.0).date()
            now_time = datetime.now().date()
            if lastSignTime == now_time:
                return {'code':'ok_signed','msg':'该用户已经签到','info':user_info}
            else:
                return {'code':'ok','msg':'该用户未签到','info':user_info}
        else:
            return {'code':'fail','msg':'用户不存在','info':None}
    

    async def is_user_exist(self,account:str) -> bool:
        """
        检查用户是否存在

        """
        db = self.db
        user_info = await db.query_one(f"SELECT * FROM {TABLE_SET['user']} WHERE account = %s", (account,))
        if user_info:
            return True
        else:
            return False

    async def user_try_add(self,account:str):
        db = self.db
        sign_info = await db.query_one(f"SELECT total FROM {TABLE_SET['user']} WHERE account = %s", (account,))
        await db.update(f"UPDATE {TABLE_SET['user']} SET total=%s WHERE account = %s", (sign_info['total']+1,account))
        logger.info(f"更新用户{account}签到次数成功")
        return {'code':'ok','msg':f"更新用户{account}签到次数成功"}

  
    async def user_sign(self, account:str):
        db = self.db
        sign_info = await db.query_one(f"SELECT success,total FROM {TABLE_SET['user']} WHERE account = %s", (account,))
        await db.update(f"UPDATE {TABLE_SET['user']} SET signTime=%s,success=%s,total=%s WHERE account = %s", (getTime(),sign_info['success']+1,sign_info['total']+1,account))
        logger.info(f"更新用户{account}签到状态成功")
        return {'code':'ok','msg':f"更新用户{account}签到状态成功"}
    

    async def get_users_info(self) -> dict:
        db = self.db
        users_info = await db.query(f"SELECT * FROM {TABLE_SET['user']}")
        return users_info
    

    async def deactive_user(self,account:str,ban_by_user:bool=False) -> bool:
        '''
        申请对签到失败或主动选择停用的用户，将其停用

        会自动判断是否符合禁用条件并做出相应的处理。
        :param account: 用户账号
        :return: 如果符合禁用条件，将会禁用并返回True，否则返回False
        '''
        db = self.db
        user_info = await db.query_one(f"SELECT * FROM {TABLE_SET['user']} WHERE account = %s", (account,))
        if user_info['active']==0:
            # 已经禁用用户
            return True
        elif user_info['failDays']>=FAIL_MAX_TRY_DAYS or ban_by_user:
            await db.update(f"UPDATE {TABLE_SET['user']} SET active=%s WHERE account = %s", (0,account))
            logger.info(f"用户{account}被禁用")
            return True
        else:
            return False

       
    async def user_fail_day_add(self,account:str):
        db = self.db
        fail_day = await db.query_one(f"SELECT failDays FROM {TABLE_SET['user']} WHERE account = %s", (account,))
        await db.update(f"UPDATE {TABLE_SET['user']} SET failDays=%s WHERE account = %s", (fail_day['failDays']+1,account))
        logger.info(f"用户{account}连续签到失败{fail_day['failDays']+1}天")

     
    async def reset_fail_day(self,account:str):
        db = self.db
        await db.update(f"UPDATE {TABLE_SET['user']} SET failDays=0 WHERE account = %s", (account,))
        logger.info(f"重置用户{account}连续签到失败天数")

    async def get_users_num(self) -> int:
        db = self.db
        nums = await db.query_one(f"SELECT COUNT(*) FROM {TABLE_SET['user']}")
        nums = nums['COUNT(*)']
        return nums

    async def quit(self):
        if self.db:
            await self.db.close()

class WebDBControl():
    SQLITE_PATH = SQLITE_SET['web_db_path']
    def __init__(self):
        self.db = None

    async def init_db(self,mysql_pool:bool=False):
        if mysql_pool or DB_CHOOSE == 'mysql':
            self.db = MysqlPoolControl()
            await self.db.connect()
            await self.db.update(USER_DB_INIT_SQL.replace("AUTOINCREMENT","AUTO_INCREMENT"))    # 语法区别修补
        elif DB_CHOOSE == 'sqlite':
            self.db = SqliteControl()
            await self.db.set_path(self.SQLITE_PATH)
            await self.db.update(NOTICE_DB_INIT_SQL)
            await self.db.close()
        # elif DB_CHOOSE == 'mysql':
        #     self.db = MysqlControl()
        #     await self.db.connect()
        #     await self.db.update(NOTICE_DB_INIT_SQL.replace("AUTOINCREMENT","AUTO_INCREMENT"))  
        
        else:
            raise ValueError("数据库选择参数错误，填写 sqlite 或 mysql")


    async def add_notice(self,title:str,content:str,time:str) -> dict:
        return await self.db.update( 
            f"INSERT INTO {TABLE_SET['web']}(title,content,time) VALUES(%s,%s,%s)",
            (title,content,time)
        )


    async def get_notice(self) -> dict:
        res = await self.db.query_one(f"SELECT * FROM {TABLE_SET['web']} ORDER BY id DESC LIMIT 1")
        if res:
            return {
                'title': res['title'],
                'content': res['content'],
                'time': int(res['time'])
            }
        return {}
    
    async def quit(self):
        if self.db:
            await self.db.close()
async def getUserDBControl(mysql_pool:bool=False):
    DB = UserDBControl()
    await DB.init_db(mysql_pool=mysql_pool)
    return DB

async def getWebDBControl(mysql_pool:bool=False):
    DB = WebDBControl()
    await DB.init_db(mysql_pool=mysql_pool)
    return DB


