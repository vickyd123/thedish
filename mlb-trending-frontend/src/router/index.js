import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/Home.vue'
import PlayerProfile from '../views/PlayerProfile.vue'

const routes = [
  { path: '/', name: 'HomePage', component: HomePage },
  { path: '/player/:player_id', name: 'PlayerProfile', component: PlayerProfile, props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
