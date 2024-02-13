from __future__ import annotations

import json
import pathlib

import yaml

from judge_gpt.gss_reader import GSSConfig


def read_conf(
    judge: str | pathlib.Path,
    response_schema: str | pathlib.Path,
) -> tuple[dict, dict]:
    """
    confファイルを読み込む

    Parameters
    -----
    judge: str, pathlib.Path
        審査に関する設定を記載したファイル
    response_schema: str, pathlib.Path
        function callingのためのschema設定ファイル

    Returns
    -----
    conf_judge: dict
    conf_response_schema: dict
    """

    with open(judge, "r") as f:
        conf_judge = yaml.safe_load(f)
        conf_judge["gss"]["reader"] = [
            GSSConfig(**division_info) for division_info in conf_judge["gss"]["reader"]
        ]
        divisions = [conf.division for conf in conf_judge["gss"]["reader"]]
        if len(divisions) != len(set(divisions)):
            raise ValueError("gss.reader has duplicate division")

    with open(response_schema, "r") as f:
        conf_response_schema = yaml.safe_load(f)

    return conf_judge, conf_response_schema
