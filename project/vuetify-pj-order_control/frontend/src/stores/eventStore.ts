import { defineStore } from 'pinia'
import { triggerRef } from 'vue'
import { tr } from 'vuetify/locale'
export const useEventStore = defineStore('event', {
  state: () => ({
    // 注文選択イベント
    menuAction: {
      source: '',
      menu: null as any,
      timestamp: null as number | null
    },

    // メニューカテゴリ選択イベント
    categoryAction: {
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

    // エラーイベント
    lastError: {
      message: '',
      code: null as number | null,
      timestamp: null as number | null
    }
  }),

  actions: {
    triggerMenuAction(menu: any, source = 'MenuList') {
      this.menuAction = {
        source,
        menu,
        timestamp: Date.now()
      }
    },

    triggerCategoryAction(categoryId: number, source = 'CategoryList') {
      this.categoryAction = {
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

    reportError(message: string, code: number) {
      this.lastError = {
        message,
        code,
        timestamp: Date.now()
      }
    }
  }
})