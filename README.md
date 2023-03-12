# simple-dataset-generating-supporter

🐀🐀🐀 機械学習のためのデータセットを簡単に生成するためのWEBサイトです。  

![成果物](./docs/img/fruit.gif)  

## 実行方法

本番環境へのデプロイは、GitHub Actionsを利用しています。  
以下のシークレットを設定してください。  

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION

`main`ブランチへプッシュすると、自動的にデプロイされます。  

---

開発環境は、以下のコマンドで実行できます。  

```shell
# クライアント
cd ./client
yarn install
yarn dev

# サーバ
cd ./server
sam build --use-container
sam local start-api
```

`.env.local`にAPI GatewayのURLを設定してください。  
`NEXT_PUBLIC_LAMBDA_API_URL=https://hogehoge.execute-api.ap-northeast-1.amazonaws.com/Prod`といった感じです。  

`.env.local`ファイルはGit管理対象外ですが、本番環境デプロイ時に自動で生成されるため、シークレットに登録する必要はありません。  
