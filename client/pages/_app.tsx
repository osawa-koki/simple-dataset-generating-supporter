import React, { useEffect } from 'react';
import { AppProps } from 'next/app';
import { useState } from 'react';

import 'bootstrap/dist/css/bootstrap.min.css';

import '../styles/styles.scss';
import '../styles/menu.scss';

import '../styles/index.scss';
import '../styles/about.scss';
import '../styles/canvas.scss';
import '../styles/gallery.scss';

import Head from 'next/head';

import setting from '../setting';
import { DataContext } from '../src/DataContext';
import SharedData from '../src/SharedData';

export default function MyApp({ Component, pageProps }: AppProps) {

  const [sharedData, setSharedData] = useState<SharedData>({
    username: '',
    category: '',
  });

  useEffect(() => {
    const username = localStorage.getItem('username');
    const category = localStorage.getItem('category');
    if (username !== null || category !== null) {
      setSharedData({
        username: username === null ? '' : username,
        category: category === null ? '' : category,
      });
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('username', sharedData.username);
    localStorage.setItem('category', sharedData.category);
  }, [sharedData.category, sharedData.username]);

  return (
    <>
      <Head>
        <meta charSet="utf-8" />
        <title>{setting.title}</title>
        <meta name="viewport" content="initial-scale=1.0, width=device-width" />
        <link rel="icon" type="image/png" href={`${setting.basePath}/favicon.ico`} />
      </Head>
      <DataContext.Provider value={{sharedData, setSharedData}}>
        <Component {...pageProps} />
      </DataContext.Provider>
    </>
  );
};
