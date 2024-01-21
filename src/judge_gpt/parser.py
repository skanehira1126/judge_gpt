import pandas as pd


class JudgeGPTParser:
    def __init__(
        self,
        sep_player: str,
        eval_column_variable_map: dict,
        template: str,
        n_players: int,
        player_col: str = "選手",
        judge_col: str = "審査員",
    ):
        self.sep_player = sep_player
        self.eval_column_variable_map = eval_column_variable_map
        self.template = template
        self.n_players = n_players
        self.player_col = player_col
        self.judge_col = judge_col

    def make_inputs_of_each_judge(
        self, judge_result_df: pd.DataFrame
    ) -> dict[str, str]:
        """
        審査員ごとに審査結果をLLMに入力する文字列に変換する

        Parameters
        -----

        """
        judge_names = judge_result_df[self.judge_col].unique()

        judge_str_map = {
            judge: self.make_judge_str(
                judge_result_df[judge_result_df[self.judge_col] == judge]
            )
            for judge in judge_names
        }

        return judge_str_map

    def make_judge_str(self, judge_result_df: pd.DataFrame) -> str:
        """
        入力されたDataFrameをもとにLLM用の入力に変換する

        Parameters
        -----
        judge_result_df: pd.DataFrame
            審査結果のテーブル

        Returns
        -----
        str
            LLM入力用の文字列
        """

        # 審査対象が揃っているか確認
        n_players = len(judge_result_df[self.player_col].unique())
        if self.n_players != n_players:
            raise ValueError("There are missing player.")

        judge_str_list = []

        for idx, row in judge_result_df.iterrows():
            variables = {
                var: row[col] for col, var in self.eval_column_variable_map.items()
            }

            judge_str_list.append(self.template.format(**variables))

        return self.sep_player.join(judge_str_list)
