# judge_gpt
ChatGPTによる評価コメントを利用した審査

## 環境構築

1. ryeのinstall [参考](https://rye-up.com/guide/installation/)
2. `rye sync`の実行

## 審査システムの概要

審査員の各選手に対するコメントを元に審査基準に沿って点数化する.
やり方はいろいろあるけども、今回は審査員はGoogleフォームを利用し審査結果を入力しgoogle spread sheetに連携される場合を考える.


```mermaid
sequenceDiagram
    participant local as 端末
    participant gss as Google Spread Sheet
    participant api as ChatGPT

    loop 各審査員
        local ->>+ gss: 審査結果の参照
        gss ->>- local:  審査結果の返却

        local ->> local: 審査結果をChatGPTに渡す文字列に変換

        local ->>+ api: 審査結果をPromptと共にChathGPTに渡す
        api ->>- local: 審査結果
    end

    local ->> local: 審査結果を集計と集約

    loop 各選手
        local ->>+ api: 採点項目ごとの全ての審査員のコメント
        api ->>- local: 審査員全体のコメントの要約
    end

    local ->> gss: 審査結果を登録
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
| `gss_ey` | google spread sheetの識別子. URLに含まれるランダムそうな文字列 |

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



