import { createRouter, createWebHashHistory } from 'vue-router'

import ChatView from './views/ChatView.vue'
import HistoryView from './views/HistoryView.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: ChatView },
    { path: '/history', component: HistoryView },
    // unknown addresses go back to the chat
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})