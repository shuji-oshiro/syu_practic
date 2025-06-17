/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App
 */

// Composables
import { createApp } from 'vue'

// Components
import App from './App.vue'

// Plugins
import { registerPlugins } from '@/plugins'

// Styles
import 'unfonts.css'
import router from './router'

// アプリ作成
const app = createApp(App)

// プラグイン登録（router, vuetifyなど）
registerPlugins(app)

// アプリをマウント
app.mount('#app')
