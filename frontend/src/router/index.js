import { createRouter, createWebHistory } from 'vue-router';
import userStore from '../store';

const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('../views/Home.vue')
    }
    , {
        path: '/index',
        name: 'index',
        redirect: to => {
            return { path: '/' }
        }
    }
    , {
        path: '/auth',
        name: 'auth',
        component: () => import('../views/Auth.vue')
    }
    , {
        path: '/profile',
        name: 'profile',
        component: () => import('../views/Profile.vue'),
        meta: { requiresAuth: true }
    },{
        path: '/guide',
        name: 'guide',
        component: () => import('../views/SignGuide.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/result',
        name:'resultPage',
        component: () => import('../views/RegResult.vue'),
        meta: { requiresAuth: true }
    }
]
const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const isLoginIn = userStore.getIsLogin;
    if (requiresAuth && !isLoginIn) {
        next('/auth');
    }  else {
        next();
    }
});

export default router;