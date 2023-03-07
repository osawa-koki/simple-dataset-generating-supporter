# nextjs-template

🌰🌰🌰 Next.jsのテンプレートです。  
よく使用すると思われる`Bootstrap`と`SCSS`は既にインストールしてあります。  

## 実行方法

```shell
# モジュールのインストール
yarn

# 開発用実行
yarn dev

# ビルド
yarn build
```

## CI/CD

`GitHub Actions`を使用しています。  
`main`ブランチにマージされると自動でデプロイされます。  

## GitHubシークレットの設定

GitHub Actionsで使用するシークレットを設定します。  
これは、GitHubのリポジトリの`Settings`→`Secrets`から設定できます。  
Depricatedなパッケージを使用している場合にその旨を通知します。  

`Develop`ブランチでは自動でパッケージの更新を行います。  
これはマイナーバージョンの更新のみです。  

| シークレット名 | 説明 |
| --- | --- |
| SLACK_WEBHOOK_URL | SlackのWebhook URL |
