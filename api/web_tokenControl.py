import aiosqlite
import secrets
import hashlib
from time import time as tTime
from api.setting import CURRENT_PATH
from os.path import join as path_join
from time import time
from api.db_control import SqliteControl


MAX_TOEKN_TIME = 1000*60*60*24

def getTime():
    return str(time()).replace('.','')[:13]

def token_gen(account):
    return hashlib.sha256(
        f"{account}{secrets.token_urlsafe()}".encode()
        ).hexdigest()

def check_token_time(token_time) -> bool:
    if int(getTime()) - int(token_time)>MAX_TOEKN_TIME:
        return False
    else:
        return True



class TokenControl:
    def __init__(self):
       self.DB_PATH = path_join(CURRENT_PATH,'../tokenControl.db')
       self.db = None

    async def init_db(self):
        self.db = SqliteControl()
        await self.db.set_path(self.DB_PATH)
        await self.db.update("""
            CREATE TABLE IF NOT EXISTS tokenInfo(
                account TEXT PRIMARY KEY,
                token TEXT,
                loginTime TEXT,
            )
        """)
        await self.db.close()

    async def __token_clear(self,account) -> None:
        await self.db.update("UPDATE tokenInfo SET token='' WHERE account=?",(account,))
        
    async def init_user(self,account):
        await self.db.update("INSERT INTO tokenInfo(account,token,loginTime) VALUES (%s,%s,%s)",(account,"",""))
    
    async def get_user_info(self,account) -> dict:
        res = await self.db.query_one("SELECT * FROM tokenInfo WHERE account=?",(account,))
        if res:
            return res
        else:
            await self.init_user(account)
            return await self.get_user_info(account)
    
    async def set_login(self,account) -> str:
        token = token_gen(account)
        await self.db.update("UPDATE tokenInfo SET token=?,loginTime=? WHERE account=?",(token,getTime(),account))
        return token

    async def check_login(self,account) -> dict|None:
        db = await aiosqlite.connect(self.DB_PATH)
        res = await db.execute("""
            SELECT * FROM tokenInfo WHERE account=?
        """,(account,))

        res = await res.fetchone()
        await db.close()
        if res:
            if check_token_time(res['loginTime']):
                return await self.get_user_info(account)
            else:
                self.__token_clear(account)
                return None
        else:
            await self.init_user(account)
            return None

