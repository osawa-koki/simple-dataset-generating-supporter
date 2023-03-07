import React from "react";
import Link from "next/link";
import Layout from "../components/Layout";
import pages from "../pages";
import setting from "../setting";

export default function Home() {
  return (
    <Layout menu={false} footer={false}>
      <div id='Index'>
        <h1>Hello Next.js 💓💓💓</h1>
        <img id='Logo' src={`${setting.basePath}/tako.png`} alt="Logo" />
        <div id="IndexLink">
        {
          pages.map((page, index: number) => {
            return (
              <Link key={index} href={page.path}>
                {page.name}
              </Link>
            )
          })
        }
        </div>
      </div>
    </Layout>
  );
};
