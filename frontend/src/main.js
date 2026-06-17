import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setupFetchInterceptor } from './services/fetch_interceptor'
import './registerServiceWorker'

// Install fetch interceptor BEFORE the app mounts so every LLM request
// automatically includes the user's X-User-LLM-* headers (if configured).
setupFetchInterceptor()

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')