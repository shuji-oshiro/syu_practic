
import pandas as pd
import numpy as np
import unittest

class Sampledata:
    def __init__(self):
        pass
    
    @classmethod  
    def CreateSalesData(cls) -> pd.DataFrame:
        # データ型定義
        DIC_AS_TYPES = {
            't_code': 'int64',   # 10種類の一意な値
            'l_code': 'int64',   # 5種類の一意な値
            'i_code': 'int64',   # 40種類の一意な値
            'day': 'int64',      # 2024年1月～2025年3月末のランダムな日付（yyyymmdd形式）
            'kind': 'int64',     # 0 = 通常, 1 = 返品
            'amount': 'int64',   # 売上金額
            'count': 'int64',    # 売上数量
        }
        
        # データ数
        num_samples = 1000
        
        # 一意なコードを作成
        t_codes = np.arange(1001, 1011)  # 10種類のt_code
        t_names = [f"チェーン{i}" for i in range(1, 11)]  # 例：チェーン1, チェーン2...
        
        l_codes = np.arange(201, 206)  # 5種類のl_code
        l_names = ["食パンライン", "菓子パンライン", "サンドイッチライン", "デニッシュライン", "その他"]
        
        i_codes = np.arange(10001, 10041)  # 40種類のi_code
        i_names = [
            "オリジナル食パン", "チョコパン", "カレーパン", "クリームパン", "メロンパン",
            "クロワッサン", "あんぱん", "フレンチトースト", "ロールパン", "バゲット",
            "デニッシュ", "アップルパイ", "ジャムパン", "シナモンロール", "コッペパン",
            "フォカッチャ", "ナン", "パニーニ", "バターロール", "マフィン",
            "クイニーアマン", "スコーン", "ベーグル", "ピタパン", "ホットドッグパン",
            "プレッツェル", "ダッチブレッド", "グリッシーニ", "カンパーニュ", "ブリオッシュ",
            "ザルツシュタンゲン", "チャバタ", "エピ", "フーガス", "ツォップ",
            "バルケット", "パンオショコラ", "ブレッチェン", "ライ麦パン", "トルティーヤ"
        ]
        
        
        # 日付（2024年1月1日～2025年3月31日）の範囲を作成
        date_range = pd.date_range(start="2024-01-01", end="2025-03-31")
        days = date_range.strftime('%Y%m%d').astype(int)  # yyyymmdd形式に変換
        
        # ランダムデータを生成
        np.random.seed(42)  # 乱数の再現性を確保
        
        df = pd.DataFrame({
            't_code': np.random.choice(t_codes, num_samples),
            'l_code': np.random.choice(l_codes, num_samples),
            'i_code': np.random.choice(i_codes, num_samples),
            'day': np.random.choice(days, num_samples),
            'kind': np.random.choice([0, 1], num_samples, p=[0.95, 0.05]),  # 返品は5%
            'amount': np.random.randint(1000, 50000, num_samples),  # 売上金額（1,000円～50,000円）
            'count': np.random.randint(1, 200, num_samples),  # 売上数量（1～200個）
        })
        
        df_item = pd.DataFrame({"i_code": i_codes, "i_name": i_names})
        
        df_sales = df.merge(df_item, on='i_code', how='left')
        
        # t_code, l_code に対応する名称の DataFrame を作成
        df_t_name = pd.DataFrame({'t_code': t_codes, 't_name': t_names})
        df_l_name = pd.DataFrame({'l_code': l_codes, 'l_name': l_names})
        
        # データ型を適用
        df = df.astype(DIC_AS_TYPES)
        
        return df_sales, df_t_name, df_l_name
   

if __name__ == "__main__": unittest.main()
pass

    