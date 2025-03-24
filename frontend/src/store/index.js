import { defineStore } from 'pinia'

const userStore = defineStore('user', {
  state: () => ({
    email: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).email : '',
    account: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).account : '',
    loginTime: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).loginTime : 0,
    isNewReg: false
  }
  ),
  getters: {
    getEmail: (state) => state.email,
    getAccount: (state) => state.account,
    getLoginTime: (state) => state.loginTime,
    getIsLogin: (state) => {
      return Date.now() - state.loginTime <= 1000 * 60 * 60
    }
  },
  actions: {
    setEmail(value) { // ✅ 使用常规函数
      this.email = value
    },
    setAccount(value) {
      this.account = value
    },
    setLoginTime() {
      this.loginTime = Date.now()
    },
    setLogin(email, account) {
      this.email = email
      this.account = account
      this.loginTime = Date.now()
      localStorage.setItem('user', JSON.stringify({
        email,
        account,
        loginTime: this.loginTime
      }))
    }
  },
})

export default userStore;