from __future__ import annotations

import os
import pathlib

import gspread
import openai


def set_openai_apikey_from_file(file_path: str | pathlib.Path):
    """
    OpenAI認証のためのKeyを環境変数に登録する

    Parameters
    -----
    file_path: str or pathlib.Path
        認証キーが記載されたファイルのパス
    """
    with open(file_path, "r") as f:
        key = f.read().strip()
        os.environ["OPENAI_API_KEY"] = key

    openai.api_key = os.environ["OPENAI_API_KEY"]


def auth_gcloud(file_path: str | pathlib.Path, relogin: bool = False) -> gspread.client.Client:
    """
    gcloudにログインする

    Parameters
    -----
    file_path: str, pathlib.Path
        gcloud認証のためのjson key
    relogin: bool
        ログイン時に生成されauthorized_user.jsonを再作成する
    """

    if relogin and pathlib.Path("authorized_user.json").exists():
        pathlib.Path("authorized_user.json").unlink()


    gc = gspread.oauth(
        credentials_filename=file_path,
        authorized_user_filename="authorized_user.json",
    )

    return gc
