from __future__ import annotations

from dataclasses import dataclass
from functools import cache
import string

import pandas as pd
import gspread

from judge_gpt.auth import auth_gcloud


@dataclass
class GSSConfig:
    division: str
    key: str
    player_order: list[str]
    common_columns: list[str]
    scoring_items: list[str]
    template: str


class GSSReader:
    """
    APIだけじゃなく、WorkSheet自体に権限が必要かも？
    """

    def __init__(
        self, 
        config: dict
    ):
        self.gc = auth_gcloud(config["gcloud"])
        self.gss_conf: list[GSSConfig] = config["reader"]

    @property
    def sheets(self) -> list[GSSConfig]:
        return self.gss_conf

    @cache
    def get_worksheet(
        self, 
        division: str
    ) -> pd.DataFrame:
        """
        Google Spread SheetからWorkSheetを取得

        Parameters
        -----
        sheet_key: str
            Google Spread Sheetの識別子. URL内部に記載
        sheet_idx: int, default 0
            取得するSheetのindex
        """

        def rename_columns(df: pd.DataFrame):
            """
            重複しているカラム名を修正する
            {審査項目}__{選手名}に変換
            """
            cnt_scoring_items = {
                item: 0 for item in target_conf.scoring_items
            }
            columns_new = []
            for col in df.columns:
                if col in target_conf.scoring_items:
                    player_idx = cnt_scoring_items[col]
                    columns_new.append(f"{col}__{target_conf.player_order[player_idx]}")
    
                    cnt_scoring_items[col]+=1
                else:
                    columns_new.append(col)
            df.columns = columns_new
    
            return df

        target_conf_list = list(filter(lambda conf: conf.division == division, self.gss_conf))
        if len(target_conf_list) == 0:
            raise KeyError(f"{divisiob} is not found.")
        else:
            target_conf = target_conf_list[0]

        # worksheetの取得
        df = self.get_ws_as_df(target_conf.key)

        # カラム名の変更
        df = rename_columns(df)

        # 縦持ちに変換
        df = pd.concat([
            df[target_conf.common_columns + [f"{item}__{player}"for item in target_conf.scoring_items]].rename(
                columns={
                    f"{item}__{player}": item
                    for item in target_conf.scoring_items
                }
            ).assign(**{"選手": player})
            for player in target_conf.player_order
        ])
        
        return df, target_conf

    def get_ws_as_df(
        self,
        key: str,
        sheet_index: int=0,
    ):
        """
        google worksheetをpandasデータフレームとして配置
        """
        worksheet = self.gc.open_by_key(key).get_worksheet(sheet_index)

        # worksheet -> pandas
        ws_values = worksheet.get_values()
        df = pd.DataFrame(
            ws_values[1:],
            columns=ws_values[0],
        )

        return df

    def insert_dataframe_to_ws(
        self,
        ws: gspread.worksheet.Worksheet,
        df: pd.DataFrame,
        add_filter: bool=True,
        **insert_params,
    ):
        """
        dataframeをwsに入れる
        
        Parameters
        -----
        ws: gspread.worksheet.Worksheet
            データを入れるシート
        df: pd.DataFrame
            入力データ
        add_filter: bool, default True
            カラムにfilterを追加する
        **insert_params
            ws.append_rowsに与える引数
        """

        # 入力データの整形
        insert_values = [list(df.columns)] + df.values.tolist()

        # データをinsert
        ws.append_rows(
            insert_values,
            **insert_params,
        )

        if add_filter:
            filter_range = [
                ("" if idx < 26 else string.ascii_uppercase[idx//26 - 1]) 
                + string.ascii_uppercase[idx%26] 
                for idx, col in enumerate(df.columns)
            ]
            ws.set_basic_filter(
                f"{filter_range[0]}1:{filter_range[-1]}{len(insert_values)}"
            )
            
            
            
            
            
            
            
            
