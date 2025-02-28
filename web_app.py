from fastapi import FastAPI,Form
from fastapi.responses import HTMLResponse,JSONResponse,Response
from datetime import datetime,time,timedelta
from fastapi.staticfiles import StaticFiles
from api.setting import TIME_SET,REMOTE_API_TOKEN,DB_CHOOSE,ADMIN_ACCOUNT,ADDRESS_COORD,AMAP_SET
from api.mail_control import user_mail,reg_mail_gen
from api.db_control import getWebDBControl,getTime,getUserDBControl
import aiofiles
from pathlib import Path
import os
from api.core import wjcAccountSignTest
import uvicorn
#from log_setting import logger_set
from api.log_setting import logger
from api.web_regControl import RegControl

NOW_FILE_PATH = os.path.dirname(os.path.abspath(__file__))

#logger = logger_set('web')

app = FastAPI()
app.mount("/static", StaticFiles(directory="web_app/build/static"), name="static")

eDB = RegControl()

async def is_db_locked() -> bool:
    if DB_CHOOSE == 'mysql':
        # 如果选择Mysql作为数据库则不锁定
        return False

    # 获取当前时间
    now = datetime.now()
    # 增加1s的延迟
    now += timedelta(seconds=1)
    current_time = now.time()
    
    # 将时间区间转换为datetime.time对象
    start_time = time(hour=int(TIME_SET['start'].split(':')[0]), minute=int(TIME_SET['start'].split(':')[1]))
    end_time = time(hour=int(TIME_SET['end'].split(':')[0]), minute=int(TIME_SET['end'].split(':')[1]))

    if start_time <= current_time <= end_time:
        # 处于签到时间点，禁止数据库操作
        return True
    else:
        return False


@app.get('/',response_class=HTMLResponse)
async def index():
    async with aiofiles.open(Path(NOW_FILE_PATH+"/web_app/build/index.html"),encoding='utf-8') as f:
        return HTMLResponse(await f.read(),status_code=200)


@app.get('/favicon.ico')
async def get_favicon():
    async with aiofiles.open(Path(NOW_FILE_PATH+"/web_app/build/favicon.ico"),'rb') as f:
        return Response(await f.read(),media_type='image/x-icon')

@app.post('/checkAccount')
async def check_account(account:str=Form(),pswd:str=Form(),email:str=Form()):
    global eDB
    if(await is_db_locked()):
        logger.info(f'用户 {account} 尝试在非开放时间点注册')
        return JSONResponse({'code':'fail','msg':f'当前时间段 ({TIME_SET["start"]} - {TIME_SET["end"]}) 无法注册，请在非此时间段再重试'})
    
    await eDB.init_db()

    if(await eDB.check_user(account,pswd) or await wjcAccountSignTest(account,pswd)):
        emailVCode = None
        
        DB = await getUserDBControl()
        user_info = await DB.get_user_info(account)
        if user_info and user_info['email'] == email:
            # 跳过验证码
            DB.quit()
            await eDB.updata_user(account,pswd,email)
            await eDB.set_user_pass(account)
            return JSONResponse(content={'code':'ok','msg':'邮箱未改变，无需验证','info':{'update':True}})
        elif not await eDB.is_user_pass(account):
            last_sent_email = await eDB.is_vcode_sent(account)
            if last_sent_email:
                if last_sent_email == email:
                    return JSONResponse(content={'code':'ok','msg':'验证码已发送过，请检查你的邮箱'})
                else:
                    return JSONResponse(content={'code':'fail','msg':f'验证码已发送至 {last_sent_email}，请检测你邮箱是否填写正确，如要更换邮箱请等待10分钟后再试'})
        
        emailVCode = await eDB.updata_user(account,pswd,email)
        logger.info(f'用户 {account} 尝试注册或更新邮箱，邮箱验证码将发送至 {email}')
        res = await user_mail('自动签到注册邮箱验证码',f'你的验证码为(10分钟内有效)：{emailVCode}',email)
        if(res):
            logger.info(f'验证码发送至{email}')
            return JSONResponse(content={'code':'ok','msg':'验证码发送成功，请检查你的邮箱'})
        else:
            logger.error(f'验证码发送至{email} 失败')
            await eDB.updata_user(account,pswd,"")  # 置空邮箱信息
            return JSONResponse(content={'code':'fail','msg':'邮箱不存在或格式错误'})
    else:
        return JSONResponse(content={'code':'fail','msg':'账号或密码错误，如果你确定账号密码无误，请过段时间再重试'})

@app.post('/stopAccount')
async def cancel_reg(account:str=Form(),pswd:str=Form()):
    if(await is_db_locked()):
        logger.info(f'用户 {account} 尝试在非开放时间点取消签到注册')
       
        return JSONResponse({'code':'fail','msg':f'当前时间段 ({TIME_SET["start"]} - {TIME_SET["end"]}) 无法取消，请在非此时间段再重试'})
    DB = await getUserDBControl()
    if(await DB.is_user_exist(account) and await wjcAccountSignTest(account,pswd)):
        if await DB.deactive_user(account=account,ban_by_user=True):
            logger.info(f'用户 {account} 取消注册签到')
            await DB.quit()
            return JSONResponse(content={'code':'ok','msg':'取消注册成功'})
        else:
            logger.error(f'用户 {account} 取消注册签到失败')
            await DB.quit()
            return JSONResponse(content={'code':'fail','msg':'取消注册失败'})
    else:
        logger.error(f'用户 {account} 取消注册签到失败，未注册自动签到或账号密码错误')
        await DB.quit()
        return JSONResponse(content={'code':'fail','msg':'未注册自动签到或账号密码错误'})
@app.post('/emailCheck')
async def emailCheck(account:str=Form(),emailVCode:str=Form()):
    global eDB
    if(await is_db_locked()):
        return JSONResponse({'code':'fail','msg':f'当前时间段 ({TIME_SET["start"]} - {TIME_SET["end"]}) 无法注册，请在非此时间段再重试'})
    
    await eDB.init_db()

    if await eDB.check_email(account,emailVCode):
        logger.info(f'用户 {account} 邮箱验证成功')
        return JSONResponse(content={'code':'ok','msg':'邮箱验证成功！'})
    else:
        logger.error(f'用户 {account} 邮箱验证失败，验证码错误或已过期')
        return JSONResponse(content={'code':'fail','msg':'验证码错误或已过期！'})


@app.post('/submit')
async def submit(account:str=Form(),coordinate:str=Form(),position:str=Form(),distance:str=Form()):
    global eDB
    if(await is_db_locked()):
        return JSONResponse({'code':'fail','msg':f'当前时间段 ({TIME_SET["start"]} - {TIME_SET["end"]}) 无法注册，请在非此时间段再重试'})
    
    await eDB.init_db()

    if await eDB.is_user_pass(account):
        user_info = await eDB.finish_reg(account)
        DB = await getUserDBControl()
        await DB.add_user(account,user_info['pswd'],user_info['email'],coordinate,position,distance)
        await DB.quit()
        await user_mail('自动签到注册成功',await reg_mail_gen({'account':account,'email':user_info['email'],'coordinate':coordinate,'position':position,'distance':distance}),user_info['email'])
        logger.info(f'用户 {account} 注册成功')
        return JSONResponse(content={'code':'ok','msg':'注册成功'})
    else:
        logger.error(f'用户 {account} 注册失败，未通过验证')
        return JSONResponse(content={'code':'fail','msg':'当前账号未通过验证'})

@app.post('/login')
async def login(account:str=Form(),pswd:str=Form()):
    DB = await getUserDBControl()
    user_info = await DB.get_user_info(account)
    if user_info and pswd == user_info['pswd']:
        return JSONResponse(
            content={
                'code':'ok',
                'msg':'登录成功',
                'info':{
                    'account':user_info['account'],
                    'email':user_info['email']
                }
            }
        )
    else:
        return JSONResponse(content={'code':'fail','msg':'账号或密码错误'})


@app.get('/getSiteInfo')
async def get_site_info():
    """ 响应一些信息给前端 """
    DB = await getUserDBControl()
    nums = await DB.get_users_num()
    await DB.quit()
    return JSONResponse(content={'code':'ok','msg':'成功获取站点信息','info':{'admin':ADMIN_ACCOUNT,'nums':nums}})

@app.get('/noticeGet')
async def noticeGet():
    """
    用于获网站上的提醒信息
    """
    DB = await getWebDBControl()
    res = await DB.get_notice()
    await DB.quit()
    return JSONResponse(content=res)

@app.post('/noticePush')
async def noticePush(api_token:str=Form(),title:str=Form(),content:str=Form(),time:int=Form(),dayDelay:int=Form()):
    """
    用于向网站推送提醒信息

    time为通知的过期时间，为13位时间戳。time设置为0时以dayDelay为准延迟推送，单位为天数，会自动计算相应的time值

    :param api_token: API TOKEN
    :param title: 标题
    :param content: 内容
    :param time: 时间戳，单位为毫秒
    :param dayDelay: 延迟天数，单位为天
    :return: JSONResponse
    """
    if api_token != REMOTE_API_TOKEN:
        logger.error('用户尝试非法操作推送信息')
        return JSONResponse(content={'code':'fail','msg':'无权限操作'})
    
    if not title or not content:
        return JSONResponse(content={'code':'fail','msg':'标题或内容不能为空'})

    if not time and not dayDelay:
        return JSONResponse(content={'code':'fail','msg':'时间或延迟天数不能为空'})
    
    if not time and dayDelay:
        time = int(getTime()) + (dayDelay * 86400)*1000
    
    DB = await getWebDBControl()
    await DB.add_notice(title,content,time)
    await DB.quit()
    logger.info(f'推送提醒：{title}[{time}] \n {content}')
    return JSONResponse(content={'code':'ok','msg':'推送成功'})


@app.get('/checkAlive')
async def checkAlive():
    """ 响应一些信息给前端 """
    DB = await getUserDBControl()
    nums = await DB.get_users_num()
    await DB.quit()
    return JSONResponse(content={'code':'ok','msg':'成功获取站点信息','info':{'admin':ADMIN_ACCOUNT,'nums':nums}})


@app.get('/getAmap')
async def get_amap():
    return JSONResponse(content={
        'code':'ok',
        'msg':'成功获取高德地图信息',
        'info':{
            'key':AMAP_SET['key'],
            'code':AMAP_SET['code'],
            'longitude':ADDRESS_COORD['lgt'],
            'latitude':ADDRESS_COORD['lat']
            }
        }
    )


if __name__ == '__main__':
    uvicorn.run(app='web_app:app',host='0.0.0.0',port=8000,reload=True)
    #uvicorn.run(app='web_app:app',host='0.0.0.0',port=443,ssl_keyfile='/home/admin/certificate/certkey.key',ssl_certfile='/home/admin/certificate/certfile.cer')