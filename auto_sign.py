from api.core import WJC
from api.setting import TIME_SET, SIGN_MAX_TRY_TIMES,TIME_SLEEP_WAIT,AYN_MAX_USERS
from queue import Queue
from datetime import datetime,time,date,timedelta
from api.db_control import getUserDBControl, getUserLogDBControl
from api import mail_control
import asyncio
from api.log_setting import logger
from time import time as time_t

class AutoSign:
    def __init__(self):
        self.q_user = Queue()
        self.q_fail_user = Queue()
        self.user_db = None
        self.user_log_db = None
        self.__semaphore = asyncio.Semaphore(AYN_MAX_USERS)     # 瞬时签到人数限制

    async def __error_msg_gen(self,content:str) -> str:
        if '请登录' in content or '需要登录才能进去系统' in content:
            return '账号密码可能错误'
        else:
            __info = content.split('body')
            if len(__info) == 3:
                return __info[1]
        return '未知错误'

    async def sign(self,account, pswd,coordinate,position,distance,email,fail_try:bool=False):
        # 瞬时签到人数限制
        self.__semaphore.acquire()
        await self._sign(account, pswd,coordinate,email,position,distance,fail_try)
        self.__semaphore.release()

    @logger.catch
    async def _sign(self,account, pswd,coordinate,email,position,distance,fail_try:bool=False):
        wjc = WJC(account, pswd)
        db = self.user_db
        info = {'code':'fail','msg':'未能签到'}
        try:
            info = await wjc.login()
            if info['code'] == 'fail':
                logger.error(f"[{account}]登录失败")
                raise Exception
            info = await wjc.getSignTask()
            if info['code'] == 'fail':
                logger.error(f"[{account}]获取签到信息失败")
                raise Exception
            # 对已签到的用户将不会再进行签到
            if not info['info']['aaData'][0]['QDSJ']:
                info = await wjc.sign(coordinate,info['info']['aaData'][0]['DM'],info['info']['aaData'][0]['SJDM'],position,distance)
            else:
                info = {'code':'ok','msg':f'[{account}]已存在签到记录，将不会签到'}
                logger.info(info['msg'])

            if info['code'] == 'ok':
                logger.info(f"{account} 签到成功")
                # 为节省邮箱发送次数，不再对成功签到的用户发送通知邮件
                #mail_content = await mail_control.user_mail_gen(f"签到成功",f"{account} 签到成功",str(info['info']))
                # await mail_control.user_mail('签到成功',mail_content,email)
                
                await db.user_sign(account)
                await self.user_log_db.add_log(
                    {
                        'account':account,
                        'email':email,
                        'coordinate':coordinate,
                        'position':position,
                    },
                    "",True
                )
            else:
                raise Exception
        except Exception as e:
            logger.error(f"[{account}]签到失败")
            if not fail_try:
                self.q_fail_user.put({
                    'account':account,
                    'pswd':pswd,
                    'coordinate':coordinate,
                    'email':email,
                    'position':position,
                    'distance':distance,
                    'info':str(info),
                    'times_try':1
                })
            await db.user_try_add(account)
            await self.user_log_db.add_log(
                {
                    'account':account,
                    'email':email,
                    'coordinate':coordinate,
                    'position':position,
                },
                "",False
            )
        return info 

    async def __sign_task_queue(self) -> None:
        db = self.user_db
        data = await db.get_users_info()
        logger.info(f"加载用户 {len(data)} 个")
        for u in data:
            if u['active'] and (await db.check_user(u['account']))['code'] == 'ok':
                # active 0 跳过该用户
                u_info = {
                    'account':u['account'],
                    'pswd':u['pswd'],
                    'coordinate':u['coordinate'],
                    'email':u['email'],
                    'position':u['position'],
                    'distance':u['distance']
                }
                self.q_user.put(u_info)
        logger.info(f"待签到用户数 {self.q_user.qsize()} 个")

    async def sign_task_create(self) -> list:
        await self.__sign_task_queue()
        task_list = []
        while not self.q_user.empty():
            user = self.q_user.get()
            task_list.append(asyncio.create_task(self.sign(user['account'],user['pswd'],user['coordinate'],user['position'],user['distance'],user['email'])))
            self.q_user.task_done()
        res = await asyncio.gather(*task_list)
        return res

    @logger.catch
    async def __fail_user_sign(self) -> None:
        # 重试队列不使用正常队列的瞬时并发形式
        db = self.user_db
        logger.info('重试队列开始')
        q_bad_list = Queue()    # 失败通知队列

        while not self.q_fail_user.empty():
            user = self.q_fail_user.get()
            self.q_fail_user.task_done()
            while user['times_try'] < SIGN_MAX_TRY_TIMES:
                # 只会在此重试SIGN_MAX_TRY_TIMES-1次
                logger.info(f"[{user['account']}]第 {user['times_try']+1} 次重试开始")
                info = await self._sign(user['account'],user['pswd'],user['coordinate'],user['email'],user['position'],user['distance'],fail_try=True)
                if info['code'] == 'ok':
                    # 签到成功的用户将不会被放到失败通知队列
                    break
                user['times_try'] +=1
                if user['times_try'] >= SIGN_MAX_TRY_TIMES:
                    q_bad_list.put(user)
            logger.info(f"[{user['account']}]重试结束")
            
        logger.info('重试队列结束')

        while not q_bad_list.empty():
            user = q_bad_list.get()
            mail_content = await mail_control.user_mail_gen('签到失败', '请检查账号密码等信息是否正确', await self.__error_msg_gen(user['info']))
            await mail_control.user_mail('签到失败', mail_content, user['email'])
            q_bad_list.task_done()
            logger.info(f"[{user['account']}]发送签到失败信息成功")

            # 添加失败天数
            await db.user_fail_day_add(user['account'])

            # 尝试封禁失败用户
            if await db.deactive_user(user['account']):
                mail_content = await mail_control.ban_mail_gen(str(user['account']))
                await mail_control.user_mail('自动签到停止', mail_content, user['email'])
            
                logger.info(f"[{user['account']}]发送账号禁用成功")

    async def time_check(self):
        while True:
            while True:
                logger.info('时间检查开始')
                # 获取当前时间
                now = datetime.now()
                current_time = now.time()

                # 将时间区间转换为datetime.time对象
                start_time = time(hour=int(TIME_SET['start'].split(':')[0]), minute=int(TIME_SET['start'].split(':')[1]))
                end_time = time(hour=int(TIME_SET['end'].split(':')[0]), minute=int(TIME_SET['end'].split(':')[1]))

                if start_time <= current_time <= end_time:
                    # 仅在开始签到时连接数据库，并在完成签到后退出，防止因长时间等待导致数据库断连引发后续问题
                    self.user_db = await getUserDBControl(mysql_pool=True)
                    self.user_log_db = await getUserLogDBControl()
                    logger.info('签到开始')
                    job_start_time = time_t()    # 耗时计时器起点
                    await self.sign_task_create()
                    await self.__fail_user_sign()
                    job_end_time = time_t()      # 耗时计时器终点
                    logger.info('签到结束，开始发送管理员邮件')
                    db = self.user_db
                    users_info = await db.get_users_info()
                    info = []
                    for user in users_info:
                        info.append({
                            'account':user['account'],
                            'status':'是' if (await db.check_user(user['account']))['code'] == 'ok_signed' else '否',
                            'success':user['success'],
                            'total':user['total'],
                            'active':user['active'],
                        })
                    mail_content = await mail_control.admin_mail_gen(info)
                    await mail_control.admin_mail('签到状态', mail_content)
                    # 退出数据库
                    if self.user_db:
                        await self.user_db.quit()  
                        self.user_db = None
                    if self.user_log_db:
                        await self.user_log_db.quit()
                        self.user_log_db = None
                    break
                else:
                    TIME_CHCECK_WAIT = int(datetime.combine(date.today(),start_time).timestamp()-now.timestamp())
                    if TIME_CHCECK_WAIT <0:
                        # 冗余10秒
                        TIME_CHCECK_WAIT = int((datetime.combine(date.today() + timedelta(days=1), time(20, 0))-datetime.now()).total_seconds())-10
                    if TIME_CHCECK_WAIT == 0:
                        TIME_CHCECK_WAIT +=1
                    logger.info(f'未到签到开始时间，等待{TIME_CHCECK_WAIT}秒后重新开始签到')
                    await asyncio.sleep(TIME_CHCECK_WAIT)
                    continue
            
            logger.info(f'签到结束，总耗时: {(job_end_time-job_start_time):.2f} 秒，等待{TIME_SLEEP_WAIT}')
            await asyncio.sleep(TIME_SLEEP_WAIT)

    async def __aliyun_run(self):
        # 仅在开始签到时连接数据库，并在完成签到后退出，防止因长时间等待导致数据库断连引发后续问题
        self.user_db = await getUserDBControl(mysql_pool=True)
        self.user_log_db = await getUserLogDBControl()
        logger.info('签到开始')
        job_start_time = time_t()    # 耗时计时器起点
        await self.sign_task_create()
        await self.__fail_user_sign()
        job_end_time = time_t()      # 耗时计时器终点
        logger.info('签到结束，开始发送管理员邮件')
        db = self.user_db
        users_info = await db.get_users_info()
        info = []
        for user in users_info:
            info.append({
                'account':user['account'],
                'status':'是' if (await db.check_user(user['account']))['code'] == 'ok_signed' else '否',
                'success':user['success'],
                'total':user['total'],
                'active':user['active'],
            })
        mail_content = await mail_control.admin_mail_gen(info)
        await mail_control.admin_mail('签到状态', mail_content)
        # 退出数据库
        if self.user_db:
            await self.user_db.quit()  
            self.user_db = None
        if self.user_log_db:
            await self.user_log_db.quit()
            self.user_log_db = None
        logger.info(f'签到结束，总耗时: {(job_end_time-job_start_time):.2f} 秒，等待{TIME_SLEEP_WAIT}')
    
    @logger.catch
    def aliyun_run(self):
        asyncio.run(self.__aliyun_run())

    @logger.catch
    def run(self):
        asyncio.run(self.time_check())

if __name__ == '__main__':
    auto_sign = AutoSign()
    auto_sign.run()

                
