import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from '@/App.vue'
import router from '@/router/index'

import '@/styles/tokens.css'
import '@/styles/base.css'
import '@/styles/a11y.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
