import { useState,useEffect } from 'react';
import { TinyColor } from '@ctrl/tinycolor';
import { Form,message,Input,ConfigProvider,Button,Typography,Modal,Checkbox } from 'antd';
import { FireOutlined } from '@ant-design/icons';
import axios from 'axios';
const { Title,Link } = Typography;

export default function RegPage(props) {
    const colors1 = ['#6253E1', '#04BEFE'];
    const getHoverColors = (colors) =>
      colors.map((color) => new TinyColor(color).lighten(5).toString());
    const getActiveColors = (colors) =>
      colors.map((color) => new TinyColor(color).darken(5).toString());
  
    const [form] = Form.useForm();
    const [nowLoading,setNowLoading] = useState(false);
    const [isModalOpen,setModalOpen] = useState(true);
    const [cancelTask,setCancelTask] = useState(false);
    const [usersNum,setUsersNum] = useState("获取中");
    const [adminAccount,setAdminAccount] = useState("获取中");

    async function checkAccount(){
      setNowLoading(true);
      form.validateFields()
        .then((val)=>{
          const setStep = props.setStep;
          const setFormData = props.setFormData;
          if(!cancelTask){
            axios.post('/checkAccount',
              {
                account:val.account,
                pswd:val.pswd,
                email:val.email
              },{
                headers: {
                    'Content-Type': 'multipart/form-data'
                  }
              })
              .then((res)=>{
                if(res.data.code === 'ok'){
                  message.success(res.data.msg);
                  setFormData({
                    account:val.account,
                    pswd:val.pswd,
                    email:val.email
                  });
                  setStep(1);
                }else{
                  message.error(res.data.msg);
                }
                setNowLoading(false);
              }).catch((error)=>{
                setNowLoading(false);
                message.error("与服务器连接失败");
                console.log(error);
              })
          }else{
            axios.post('/stopAccount',
              {
                account:val.account,
                pswd:val.pswd
              },
              {
                headers: {
                    'Content-Type': 'multipart/form-data'
                  }
              })
              .then((res)=>{
                if(res.data.code === 'ok'){
                  message.success(res.data.msg);
                  setStep(20);
                }else{
                  message.error(res.data.msg);
                }
                setNowLoading(false);
              }).catch((error)=>{
                setNowLoading(false);
                message.error("与服务器连接失败");
                console.log(error);
              })
          }
        })
        .catch((err)=>{
          setNowLoading(false);
        });
    }
    
    useEffect(() => {
      axios.get('/getSiteInfo')
      .then(res=>{
        if(res.data.code === 'ok'){
          setUsersNum(res.data.info.nums);
          setAdminAccount(res.data.info.admin);
        }
      }).catch((error)=>{
        console.log(error);
      })
    },[]);

    return (
      <>
        <Title level={3}>填写账号</Title>
        <Form
          size='large'
          form={form}
        >
          <Form.Item
            label='账号'
            name='account'
            rules={[
              {
                required: true,
                message: '请输入正确的校芜优账号'
              },
              {
                min:11,
                max:11,
                message: '请输入正确的校芜优账号'
              }
            ]}
          >
            <Input placeholder='通常为你的学号'/>
          </Form.Item>
          <Form.Item
            label='密码'
            name='pswd'
            rules={[
              {
                required: true,
                message: '请输入正确的校芜优密码'
              }
            ]}
          >
            <Input.Password placeholder='推荐改成不常用密码后再填入' />
          </Form.Item>
          <Form.Item
            label='邮箱'
            name='email'
            rules={[
              {
                required: !cancelTask,
                message: '请输入邮箱，用于通知签到'
              },
              {
                pattern:/^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/,
                message:'请输入正确的邮箱'
              }
            ]}
          >
            <Input placeholder='推荐使用QQ邮箱' disabled={cancelTask}/>
          </Form.Item>
          <Form.Item>
            <Checkbox onChange={()=>{setCancelTask(!cancelTask);}}>取消自动签到请勾选！</Checkbox>
          </Form.Item>
          <Form.Item>
            <ConfigProvider
              theme={{
                components: {
                  Button: {
                    colorPrimary: `linear-gradient(135deg, ${colors1.join(', ')})`,
                    colorPrimaryHover: `linear-gradient(135deg, ${getHoverColors(colors1).join(', ')})`,
                    colorPrimaryActive: `linear-gradient(135deg, ${getActiveColors(colors1).join(', ')})`,
                    lineWidth: 0,
                  },
                },
              }}
            >
              
              <Button block
                  type="primary"
                  icon={<FireOutlined />}
                  onClick={() =>{checkAccount()}}
                  loading={nowLoading}
                >
                  注册or更新
              </Button>
            </ConfigProvider>
          </Form.Item>
        </Form>
        <Link onClick={()=>{setModalOpen(true)}}>这是什么？点我查看说明</Link>
        <span>项目开源地址：</span>
        <p>
            <a href='https://gitee.com/saucer216/wjc_auto_sign'><img src='https://gitee.com/saucer216/wjc_auto_sign/widgets/widget_5.svg?color=red' alt='Fork me on Gitee'></img></a>
            <a href='https://github.com/sz134055/wjc_auto_sign'><img src='https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png' width='50px' height='50px' alt='Fork me on GitHub'></img></a>
        </p>
        <Modal
          title="使用说明"
          open={isModalOpen}
          onOk={() => {setModalOpen(false)}}
          okText="我知道了"
          cancelButtonProps={{style:{display:'none'}}}
        >
          <Typography>
            <p>这是一个在线的，可为你在每晚自动签到的脚本程序。</p>
            <p>它绕过了一些不必要的步骤，因此可以帮你更快地完成签到，甚至在他人校芜优打开失败的情况下。</p>
            <p>你需要填写你的校芜优的账号与密码，以及一个用于接收签到信息的邮箱（很重要），程序会在签到失败的情况下向你发送邮件提醒。</p>
            <p>完成注册后，脚本会自动为你进行签到，你要做的只是关注下你的邮箱，确保签到成功即可。</p>
            <p style={{color:'red'}}>你的密码会明文存储，所以一定一定不要使用常用密码！</p>
            <p>当前站点搭建与管理员账号：<span style={{'font-weight':'bold'}}>{adminAccount}</span></p>
            <p style={{color:'red'}}>校芜优账户涉及到了你在校消费，若你担心账户安全，可下滑网页找到脚本开源地址，自行下载并搭建使用。</p>
            <p>受限于学校服务器性能以及注册用户数量，可能需要一定的时间才能帮你完成签到。当前总注册用户数：<span style={{'font-weight':'bold'}}>{usersNum}</span></p>
          </Typography>
        </Modal>
      </>
    );
}




