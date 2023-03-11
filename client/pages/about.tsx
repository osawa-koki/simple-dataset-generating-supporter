import React from "react";
import { Alert } from "react-bootstrap";
import Layout from "../components/Layout";

export default function AboutPage() {
  return (
    <Layout>
      <div id="About">
        <h1>Here, About page.</h1>
        <hr />
        <div>
          <h2 className="mt-3">🐶 説明 🐶</h2>
          <p className="mt-3">
            機械学習用のデータセットを自作するためのサポートサイトです。<br />
            簡単に画像をお絵描きして、データセットを作成できます。<br />
            <br />
            このプログラムは「S3」「Lambda」「GitHub Actions」および「Next.js」を使用しています。<br />
            クラウド(SaaS)は偉大だ！<br />
            <br />
            出回っているデータセットではなく、自分で作成したデータセットを使って機械学習を行てみたい方におすすめです。<br />
            🐙🐙🐙
          </p>
          <Alert variant="info" className="mt-5">
            <h2>🔔 注意事項 🔔</h2>
            <hr />
            <h3>ユーザ名はできるだけ長く！</h3>
            <p>システムの簡素化のため、認証機能を実装していません。<br />他のユーザが勝手に登録した画像を削除することも可能な状態です。<br />ユーザ名はできるだけ長く、複雑なものにすることでそのような被害を防ぐことができます。</p>
            <hr />
            <h3>データは一時的に！</h3>
            このシステムでは、データを永続化させることを目的としていません。<br />データは一時的に保存され、一定期間経過すると自動的に削除されます。<br />データを永続化させたい場合は、自分でダウンロードしてください。<br />具体的には月曜日の午前9時にデータが削除されます。
            <hr />
            <h3>攻撃はしないで！</h3>
            大量の画像をアップロードすることで、このシステムに対する負荷を高めることができます。<br />WAF等の対策はしていないため、DoS系の攻撃をされるとシステムが簡単に落ちます。<br />攻撃をするのはやめてください。
            <hr />
            <h3>機密情報はアップしないで！</h3>
            このシステムは、機密情報をアップロードすることを目的としていません。<br />機密情報をアップロードすることで、その情報が漏洩する可能性があります。<br />機密情報をアップロードするのはやめてください。
          </Alert>
          <h2 className="mt-3">🐱 使い方 🐱</h2>
          <p className="mt-3">
            「ユーザ名」と「カテゴリ名」で画像を管理しています。<br />
            <br />
            ユーザ名は一種のトークンのようなもので、「ユーザID/パスワード」の機能を兼ねています。<br />
            <br />
            カテゴリ名は、画像を分類するためのものです。<br />
            例えば、「1」という画像データを作成する際にはカテゴリ名を「one」にすることで、<br />
            「1」の画像データとして管理することができます。<br />
          </p>
        </div>
      </div>
    </Layout>
  );
};
