import { defineStore } from 'pinia'
import type { MenuOut } from '@/types/menuTypes'

export const useEventStore = defineStore('event', {
  state: () => ({
    // 注文選択イベント
    menuSelectAction: {
      source: '',
      menu: null as MenuOut | null,
      timestamp: null as number | null
    },

    // メニューカテゴリ選択イベント
    selectCategoryAction: {
      source: '',
      categoryId: null as number | null,
      timestamp: null as number | null
    },

    //注文更新イベント
    updateOrderAction: {
      source: '',
      updateflg: true,
      timestamp: null as number | null
    },

    // CSVファイルよりメニューを一括で更新するイベント
    importMenusAction: {
      source: '',
      formData: null as FormData | null,
      timestamp: null as number | null
    },

    showNavigationAction: {
      source: '',
      target: null as string | null,
      timestamp: null as number | null
    },

    // エラーイベント
    lastError: {
      message: '',
      detail: '',
      code: null as number | null,
      timestamp: null as number | null,
      source: ''
    },
    // 情報イベント
    lastInfo: {
      message: '',
      detail: '',
      code: null as number | null,
      timestamp: null as number | null,
      source: ''
    },
    // 警告イベント
    lastWarning: {
      message: '',
      detail: '',
      code: null as number | null,
      timestamp: null as number | null,
      source: ''
    }

  }),

  actions: {
    triggerMenuSelectAction(menu: MenuOut | null, source = 'MenuList') {
      this.menuSelectAction = {
        source,
        menu,
        timestamp: Date.now()
      }
    },

    triggerSelectCategoryAction(categoryId: number, source = 'CategoryList') {
      this.selectCategoryAction = {
        source,
        categoryId,
        timestamp: Date.now()
      }
    },

    triggerUpdateOrderAction(source = 'FoodMenusList') {
      this.updateOrderAction = {
        source,
        updateflg: true,
        timestamp: Date.now()
      }
    }, 

    triggerImportMenusAction(formData: FormData, source = 'ImportMenus') {
      this.importMenusAction = {
        source,
        formData,
        timestamp: Date.now()
      }
    },

    triggerShowNavigationAction(target:string, source:string) {
      this.showNavigationAction = {
        source: source,
        target: target,
        timestamp: Date.now()
      }
    },

    reportError(message: string, detail: string = '', code: number = 2, source: string = 'EventStore') {
      this.lastError = {
        message,
        detail,
        source,
        code,
        timestamp: Date.now()
      }
    },
    reportInfo(message: string, detail: string = '', code: number = 0, source: string = 'EventStore') {
      this.lastInfo = {
        message,
        detail,
        source,
        code,
        timestamp: Date.now()
      }
    },
    reportWarning(message: string, detail: string = '', code: number = 1, source: string = 'EventStore') {
      this.lastWarning = {
        message,
        detail,
        source,
        code,
        timestamp: Date.now()
      }
    },
  }
})