import aiosqlite
import random
from time import time as tTime
from api.setting import CURRENT_PATH
from os.path import join as path_join
async def emailVCodeGen() -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


class RegControl:
    def __init__(self):
       self.DB_PATH = path_join(CURRENT_PATH,'../regControl.db')

    async def init_db(self):
        db = await aiosqlite.connect(self.DB_PATH)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS regInfo(
                account TEXT PRIMARY KEY,
                pswd TEXT,
                email TEXT,
                emailVCode TEXT,
                emailVCodeTime TEXT,
                isPass INTEGER DEFAULT 0
            )
        """)
        await db.commit()
        await db.close()
    
    async def init_user(self,account,pswd,email) -> str:
        emailVCode = await emailVCodeGen()
        db = await aiosqlite.connect(self.DB_PATH)
        await db.execute("INSERT INTO regInfo VALUES (?,?,?,?,?,?)",(account,pswd,email,emailVCode,str(int(tTime())),0))
        await db.commit()
        await db.close()
        return emailVCode
    
    async def check_user(self,account,pswd) -> bool:
        db = await aiosqlite.connect(self.DB_PATH)
        cursor = await db.execute("SELECT * FROM regInfo WHERE account=? AND pswd=?",(account,pswd))
        result = await cursor.fetchone()
        await db.close()
        if result is None:
            return False
        else:
            return True
        
    async def check_email(self,account,emailVCode) -> bool:
        db = await aiosqlite.connect(self.DB_PATH)
        cursor = await db.execute("SELECT * FROM regInfo WHERE account=?",(account,))
        result = await cursor.fetchone()
        if result is None:
            await db.close()
            return False
        elif result[3] == emailVCode and ((int(tTime()) - int(result[4]))<=60*10):
            await db.execute("UPDATE regInfo SET isPass=1 WHERE account=?",(account,))
            await db.commit()
            await db.close()
            return True
        
    async def is_user_pass(self,account) -> bool:
        db = await aiosqlite.connect(self.DB_PATH)
        cursor = await db.execute("SELECT * FROM regInfo WHERE account=?",(account,))
        result = await cursor.fetchone()
        await db.close()
        if result is None:
            return False
        else:
            return result[5] == 1
        
    async def updata_user(self,account,pswd,email) -> str:
        db = await aiosqlite.connect(self.DB_PATH)
        cursor = await db.execute("SELECT * FROM regInfo WHERE account=?",(account,))
        res = await cursor.fetchone()
        if res is None:
            await db.close()
            return await self.init_user(account,pswd,email)
        else:
            emailVCode = await emailVCodeGen()
            await db.execute("UPDATE regInfo SET pswd=?,email=?,emailVCode=?,emailVCodeTime=? WHERE account=?",(pswd,email,emailVCode,str(int(tTime())),account))
            await db.commit()
            await db.close()
            return emailVCode
    
    async def finish_reg(self,account) -> dict:
        db = await aiosqlite.connect(self.DB_PATH)
        cursor = await db.execute("SELECT * FROM regInfo WHERE account=?",(account,))
        res = await cursor.fetchone()
        if res is None:
            await db.close()
            return None
        else:
            await db.execute("DELETE FROM regInfo WHERE account=?",(account,))
            await db.commit()
            await db.close()
            return {
                'account':res[0],
                'pswd':res[1],
                'email':res[2],
                'emailVCode':res[3],
                'emailVCodeTime':res[4],
                'isPass':res[5]
            }
        
    async def is_vcode_sent(self,account) -> str:
        """
        检测邮箱验证码是否成功发送

        :return: str 发送过且未过期则响应发送至的邮箱
        """
        db = await aiosqlite.connect(self.DB_PATH)
        cursor = await db.execute("SELECT emailVCodeTime,email FROM regInfo WHERE account=?",(account,))
        res = await cursor.fetchone()
        if res and ((int(tTime()) - int(res[0])) <= 60*10):
            return res[1]
        else:
            return ""