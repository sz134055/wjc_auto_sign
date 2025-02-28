import { defineStore } from 'pinia'

const userStore = defineStore('user', {
  state: () => {
    return {
      email: '',
      account: '',
      loginTime: 0,
      isLogin: false,
    }
  },
  getters: {
    getEmail: (state) => state.email,
    getAccount: (state) => state.account,
    getLoginTime: (state) => state.loginTime,
    getIsLogin: (state) => {
      const nowTime = Date.now()
      if (nowTime - state.loginTime > 1000 * 60 * 60) {
        state.isLogin = false
      } else {
        state.isLogin = true
      }
      return state.isLogin
    },
  },
  actions: {
    setEmail: (value) => {
      this.email = value
    },
    setAccount: (value) => {
      this.account = value
    },
    setLoginTime: () => {
      this.loginTime = Date.now()
    },
    setLogin: (email, account) => {
      this.email = email
      this.account = account
      this.loginTime = Date.now()
      this.isLogin = true
    },
  },
})

export default userStore;