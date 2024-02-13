from __future__ import annotations

import json
from dataclasses import dataclass
from logging import getLogger

import openai
import pandas as pd
from tqdm.auto import tqdm

from judge_gpt.gss_reader import GSSConfig

logger = getLogger(__name__)


@dataclass
class ColumnInfo:
    judge: str
    player: str


class JudgeGPT:

    def __init__(
        self,
        model: str,
        conf_response_schema: dict,
        column_info: ColumnInfo,
        seed: int | None = None,
        temperature: float = 1.0,
        sep_player: str = "\n-----\n",
    ):
        """
        Parameters
        -----
        model: str
            審査に利用するOpenAIのモデル
        conf_response_schema: dict
            function callingに利用させる関数の定義
        column_info: ColumnInfo
            審査情報に必要なカラムの情報を管理すクラス
        seed: int, optional
            OpenAPIの関数で利用するシード値
        temperature: float
            OpenAPIの関数で利用するtemperture
        sep_player: str, default '\n-----\n'
            選手ごとの審査文字列を分ける文字列
        """

        self.client = openai.OpenAI()
        self.model = model
        self.seed = seed
        self.temperature = temperature
        self.conf_response_schema = conf_response_schema

        # logger
        logger.info("Setup Open AI Client")
        logger.info(f"Model name: {self.model}")
        logger.info(f"seed: {self.seed}")
        logger.info(f"temperature: {self.temperature}")

        # 審査文言まわり
        self.sep_player = sep_player
        self.column_info = column_info

    def make_prompt(
        self,
        judge_list: list,
        judge_result: pd.DataFrame,
        gss_conf: GSSConfig,
        system_prompt: str,
    ):
        """
        Parameteres
        -----
        judge_list: list
            審査員名の一覧
        judge_result: pd.DataFrame
            審査員結果のDataFrame
        """
        prompt_of_each_judge = {}

        logger.info("Start make prompts")
        for judge in judge_list:
            logger.info(f"judge_name is {judge}")
            judge_string = self.make_judge_prompt(
                judge_result.query(f"{self.column_info.judge} == '{judge}'"),
                gss_conf,
            )
            prompt = [
                {"role": "system", "content": system_prompt},
            ] + [
                {"role": "user", "content": judge_string},
            ]

            prompt_of_each_judge[judge] = prompt

        return prompt_of_each_judge

    def make_judge_prompt(
        self,
        judge_result: pd.DataFrame,
        gss_conf: GSSConfig,
    ) -> str:
        """
        審査項目ごとにGPTに投げるPromptを作成

        Parameters
        -----
        judge_result: pd.DataFrame
            Promptを作成するDataFrame
        gss_conf: GSSConfig
            審査項目などを格納しているConfigクラス
        include_player_name: bool, default True
            出力結果に選手名を含む
        include_judge_name: bool, default False
            出力結果に審査員を含む
        """
        judge_str_list = []
        for row in judge_result.itertuples():
            result_map = {
                scoring_item: getattr(row, scoring_item) for scoring_item in gss_conf.scoring_items
            }
            result_map[self.column_info.player] = getattr(row, self.column_info.player)
            judge_str_list.append(gss_conf.template.format(**result_map))

        return self.sep_player.join(judge_str_list)

    def call_chatgpt(
        self,
        prompts: dict[str, list],
    ) -> tuple[dict, pd.DataFrame]:
        """
        審査結果を作成する

        Parameters
        -----
        prompts: dict
            審査員ごとのpromptを格納した辞書

        Returns
        -----
        dict
            審査員ごとのOpenAIのAPIの返却結果
        pd.DataFrame
            OpenAIのAPIの返却結果をDataFrameに変換し結合したもの
        """

        def parse_response(arg_str: str) -> dict:
            """
            文字列を辞書として読み込む
            """
            try:
                judge_result = json.loads(arg_str)
            except:
                print("Parse Error. Try parse by eval()")
                with open("debug.txt", "a") as f:
                    f.write(arg_str)
                judge_result = eval(arg_str)

            return judge_result

        res_log = {}
        judge_result_all = []

        for judge, prompt in tqdm(prompts.items()):
            if judge in res_log.keys():
                continue
            res = self.client.chat.completions.create(
                model=self.model,
                messages=prompt,
                tools=[self.conf_response_schema],
                tool_choice="auto",
                seed=self.seed,
                temperature=self.temperature,
            )

            res_message = res.choices[0].message

            # tool callsの回数が場合によって異なる場合がある
            if res_message.tool_calls is None:
                raise RuntimeError("function is not called")
            n_called_function = len(res_message.tool_calls)
            if n_called_function >= 2:
                logger.warning(f"function is called {n_called_function} times.")

            # pandasのDataFrameとしてjsonを結合
            judge_result = pd.concat(
                [
                    pd.DataFrame(parse_response(tool_call.function.arguments)["judge_results"])
                    for tool_call in res_message.tool_calls
                ]
            )

            judge_result = judge_result.assign(
                judge=judge,
                total_points=judge_result[
                    ["difficulty", "variation", "refined", "performance"]
                ].sum(axis=1),
            )

            res_log[judge] = res_message
            judge_result_all.append(judge_result)

        return res_log, pd.concat(judge_result_all).reset_index(drop=True)
