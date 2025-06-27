
// Category の基本情報
export type CategoryBase = {
  name: string
  description: string
}

// 単一メニュー情報
export type MenuOut = {
  id: number
  category_id: number
  name: string
  price: number
  description: string
  search_text: string
  category: CategoryBase
}

// カテゴリごとのメニューグループ
export type MenuOut_GP = {
  category_id: number
  category_name: string
  menues: MenuOut[]
}

// カテゴリ情報
export type MenuCategory = {
  id: number
  name: string
  description: string
}
