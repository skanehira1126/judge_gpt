from __future__ import annotations

import yaml
import json

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

    with open(response_schema, "r") as f:
        conf_response_schema = yaml.safe_load(f)

    return conf_judge, conf_response_schema
    
