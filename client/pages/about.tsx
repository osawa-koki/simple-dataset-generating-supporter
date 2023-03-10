import React from "react";
import Layout from "../components/Layout";

export default function AboutPage() {
  return (
    <Layout>
      <div id="About">
        <h1>Here, About page.</h1>
        <p className="mt-3">
          機械学習用のデータセットを自作するためのサポートサイトです。<br />
          簡単に画像をお絵描きして、データセットを作成できます。<br />
          <br />
          このプログラムは「S3」「Lambda」「GitHub Actions」および「Next.js」を使用しています。
        </p>
      </div>
    </Layout>
  );
};
