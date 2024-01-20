import pandas as pd

def make_inputs_from_df(judge_df: pd.DataFrame) -> str:
    """
    スプレッドシートから取得した情報をLLMに入力するDataFrameにする.

    Parameters
    -----
    judge_df: pd.DataFrame
        審査結果のテーブル
    """
    
    context = """演者:{player}
難易度:{difficulty}
多彩性度：{variation}
操作安定度:{cleanliness}
演技構成度:{program_component}"""

    judge_result_list = []
    for idx, row in judge_df.iterrows():
        judge_result.append(context.format(
            player=row["演者"],
            difficulty=row["難易度"], 
            variation=row["多彩性度"],
            cleanliness=row["操作安定度"],
            program_component=row["演技構成"],
        ))

    return "\n".join(judge_result_list)
    