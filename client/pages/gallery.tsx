import React, { useContext, useEffect, useState } from "react";
import { Alert, Form } from "react-bootstrap";
import Layout from "../components/Layout";
import setting from "../setting";
import { DataContext } from "../src/DataContext";

import { is_valid_username as is_valid } from "../src/validate";

export default function GalleryPage() {

  const [keys, setKeys] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
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
            setKeys([]);
            return;
          }
          setKeys(data);
          const categories = data.keys.map((key: string) => key.split('/')[2]);
          setCategories(Array.from(new Set(categories)));
        });
    })();
  }, [sharedData.username]);

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
            <Form.Select>
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
      </div>
    </Layout>
  );
};
