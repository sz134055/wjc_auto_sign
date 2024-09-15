import { Flex,Steps,Typography,notification } from 'antd';
import { UserAddOutlined,RobotOutlined,EnvironmentOutlined,SmileOutlined } from '@ant-design/icons';
import { useState,useEffect } from 'react';
import RegPage from './RegPage';
import EmailCheckPage from './EmailCheckPage';
import SetCoordinatesPage from './SetCoordinatesPage';
import ResultPage from './ResultPage';
import CancelResultPage from './CancelResultPage'
import axios from 'axios';

const { Title } = Typography;

export default function RegisterForm() {
  const [nowSetp,setStep] = useState(0);
  const [formData,setFormData] = useState({
    account:'',
    pswd:'',
    email:'',
    coordinates:'',
    emailVCode:''
  });
  const [api, contextHolder] = notification.useNotification();
  
  useEffect(() => {
    axios.get('/noticeGet')
    .then(res => {
      console.log(res.data);
      if(Date.now() <= res.data.time){
        api.open({
          message: res.data.title,
          description:res.data.content,
          showProgress:true,
          pauseOnHover:true,
          placement:'top'
        });

      }
    }).catch((error)=>{
      console.log(error);
    })
  }, []);


  

  return (
    <Flex vertical
      justify='center'
      align='center'
      gap='small'
      >
        {contextHolder}
      <Title>Auto Sign</Title>
      <Steps 
        size='small'
        current={nowSetp}
        items={[
          {title:'填写账号信息',icon:<UserAddOutlined />},
          {title:'验证账号',icon:<RobotOutlined />},
          {title:'设置签到位置',icon:<EnvironmentOutlined />},
          {title:'完成注册',icon:<SmileOutlined />}
        ]}
      />
      <PageSwitch nowSetp={nowSetp} setStep={setStep} formData={formData} setFormData={setFormData}/>
    </Flex>
  );
}

function PageSwitch({nowSetp,setStep,formData,setFormData}){
  switch (nowSetp) {
    case 0:
      return <RegPage setStep={setStep} setFormData={setFormData}/>;
    case 1:
      return <EmailCheckPage setStep={setStep} formData={formData} setFormData={setFormData}/>;
    case 2:
      return <SetCoordinatesPage setStep={setStep} formData={formData} setFormData={setFormData}/>;
    case 3:
      return <ResultPage />;
    case 20:
      return <CancelResultPage />;
    default:
      return <RegPage setStep={setStep} setFormData={setFormData}/>;
  }
}











