# judge_gpt

## 概要
ChatGPTを初めとしたLLMを利用して審査コメントを点数化するシステム.  
各選手の演技に対するコメントをもとに、評価基準に則り点数化する。

## 環境構築

1. ryeのinstall [参考](https://rye-up.com/guide/installation/)
2. `rye sync`の実行

## 審査システムの概要

審査コメントをGoogle Formで入力し、Spread SheetでPythonから読み込みChatGPT APIを利用する.

```mermaid
sequenceDiagram
    participant local as 端末
    participant judge as 審査員
    participant gf as Google Form
    participant gss as Google Spread Sheet
    participant api as ChatGPT API
    participant ui as ChatGPT UI

    loop 選手
        judge ->> gf: 審査コメントの入力
    end
    gf ->> gss: 審査コメントの入力

    loop 各審査員
        local ->>+ gss: 審査結果の参照
        gss ->>- local:  審査結果の返却

        local ->> local: 審査結果をChatGPT API用の文章に変換

        local ->>+ api: 審査
        api ->>- local: 審査結果
    end

    local ->> local: 審査結果を集計と集約
    local ->> gss: 審査結果を登録

    note over ui: コメントの要約はAPIでやるよりも元々ある程度プロンプトが<br>しっかりしているChatGPT UIの方が手間がかからず楽.
    local ->>+ ui: 採点項目ごとの全ての審査員のコメント
    ui ->>- local: 審査員全体のコメントの要約

```

## 設定
事前準備として以下の2点が必要

- PythonからGoogle Spread Sheetを利用するためにGCPにプロジェクトを作成する
- PythonからGPTを利用するためにOpenAIのAPI利用登録


### ファイルについて
審査実施のために必要なファイル

| ファイル名 | 説明 |
| :--- | :--- |
| `judge.yaml` | 審査について必要な情報を記載する |
| `response_schema.yaml` | ChatGPTのfunction Callingのためのスキーマを設定する |

#### judge.yaml

主項目
- gss: Google Spread Sheetに関する設定を記載
- chatgpt: ChatGPTに関する設定を記載

##### gss
| ファイル名 | 説明 |
| :--- | :--- |
| `gcloud` | gssをpythonで取得するために必要なgcloudの認証key |
| `gss_key` | google spread sheetの識別子. URLに含まれるランダムそうな文字列 |
| `output` | 審査結果を出力するスプレッドシートの識別子


##### chatgpt
| ファイル名 | 説明 |
| :--- | :--- |
| `secrets`| openai API接続のためのKey |
| `model` | 利用するGPTモデル |
| `seed` | chatgptの出力を生成するためのseed値
| `prompt_judge` | 審査についての説明用プロンプト |
| `prompt_summarize`| 審査元のコメントを要約するためのプロンプト |



#### `response_schema.yaml`
function callingの設定は[json schema](https://json-schema.org/learn/getting-started-step-by-step)を利用している.  
なので、基本的にはjson schemaを基にしつつフィールドの説明としてdescriptionを設定すればいい.  

独自のpromptでjsonを返却させることもできそうだけど、安定性と簡単のためにfunction callingを利用する.

各審査員ごとの結果を辞書として受け取り、それらを配列として出力させるようにする.



