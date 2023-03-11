import React, { useContext, useEffect, useState } from "react";
import { Alert, Form } from "react-bootstrap";
import Layout from "../components/Layout";
import setting from "../setting";
import { DataContext } from "../src/DataContext";

import { is_valid_username as is_valid } from "../src/validate";

type ImageStruct = {
  key: string;
  image: string;
};

export default function GalleryPage() {

  const [keys, setKeys] = useState<string[]>([]);
  const [images, setImages] = useState<ImageStruct[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selected_category, setSelectedCategory] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const { sharedData, setSharedData } = useContext(DataContext);

  useEffect(() => {
    // 画像一覧を取得
    (async () => {
      fetch(`${setting.apiPath}/image/list/?user_id=${sharedData.username}`)
        .then(async (res) => {
          if (res.status === 200) {
            return await res.json();
          } else {
            return null;
          }
        })
        .then((data) => {
          if (data === null) {
            setError('画像キー一覧の取得に失敗しました。');
            setKeys([]);
            return;
          }
          setKeys(data.keys);
          const categories = data.keys.map((key: string) => key.split('/')[2]);
          setCategories(Array.from(new Set(categories)));
        });
    })();
  }, [sharedData.username]);

  useEffect(() => {
    setImages([]);
    setError(null);
    // 対象のカテゴリの画像キーを取得
    const target_keys = keys.filter((key) => key.split('/')[2] === selected_category);
    if (target_keys.length === 0) return;
    if (selected_category === "") return;
    const guids = target_keys.map((key) => key.split('/')[3].replace('.png', '')).join(',');
    (async () => {
      fetch(`${setting.apiPath}/image/fetch/?user_id=${sharedData.username}&category=${selected_category}&guids=${guids}`)
        .then(async (res) => {
          if (res.status === 200) {
            return await res.json();
          } else {
            return null;
          }
        })
        .then((data) => {
          if (data === null) {
            setError('画像データ一覧の取得に失敗しました。');
            setImages([]);
            return;
          }
          setImages(data.images as ImageStruct[]);
        });
    })();
  }, [keys, selected_category, sharedData.username]);

  return (
    <Layout>
      <div id="Gallery">
        <h1>🖼️ Gallery 🖼️</h1>
        <Form className="d-flex justify-content-between">
          <Form.Group className="w-50">
            <Form.Label>username</Form.Label>
            <Form.Control type="text" placeholder="Enter User Name" value={sharedData.username} onInput={(e) => {
              setSharedData({
                ...sharedData,
                username: e.currentTarget.value,
              });
            }} />
          </Form.Group>
          <Form.Group className="w-50">
            <Form.Label>category</Form.Label>
            <Form.Select value={selected_category} onInput={(e) => {
              setSelectedCategory(e.currentTarget.value);
            }}>
              <option value={""}>Select category...</option>
              {
                categories.map((category) => (
                  <option key={category} value={category}>{category}</option>
                ))
              }
            </Form.Select>
          </Form.Group>
        </Form>
        {
          is_valid(sharedData.username) === false && (
            <Alert variant="danger" className="mt-3">ユーザ名は半角英数字と記号(アンダースコアとハイフン)の3-8文字で入力してください。</Alert>
          )
        }
        {
          error !== null && (
            <Alert variant="danger" className="mt-3">{error}</Alert>
          )
        }
        {
          images.length === 0 && selected_category !== "" ? (
            <Alert variant="info" className="mt-3">画像がありません。</Alert>
          ) : (
            images.map((image) => (
              <img key={image.key} src={`data:image/png;base64,${image.image}`} alt={selected_category} className="img-thumbnail" />
            ))
          )
        }
      </div>
    </Layout>
  );
};
