import { defineStore } from 'pinia'
import type { MenuOut } from '@/types/menuTypes'

// アプリケーションのナビゲーション状態を管理するストア
// 注文画面、注文履歴、メニューカテゴリの表示状態を管理
export const EventAppNavigation = defineStore('eventAppNavigation', {
  state: () => ({
    isNavigation: false,
    isOrder: false,
    isHistory: false,
    isMenuCategory: false
  }),

  actions: {
    triggerNavigation(target: string) {
      this.isNavigation = true
      this.isOrder = target === 'order'
      this.isHistory = target === 'history'
      this.isMenuCategory = target === 'category'
    }
  }
})

// 共通イベントストア
// エラー、情報、警告イベントを管理するためのストア
export const CommonEventStore = defineStore('eventOrder', {

  state: () => ({
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


export const UseEventStore = defineStore('event', {
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
  }
})
