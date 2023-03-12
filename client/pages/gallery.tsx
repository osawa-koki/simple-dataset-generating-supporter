import React, { useContext, useEffect, useState } from "react";
import { Alert, Button, Form, Spinner } from "react-bootstrap";
import { BsFillTrash3Fill } from 'react-icons/bs';
import Layout from "../components/Layout";
import setting from "../setting";
import { DataContext } from "../src/DataContext";

import { is_valid_username as is_valid } from "../src/validate";

type ImageStruct = {
  key: string;
  image: string;
  deleting: boolean;
};

const image_fetch_limit = 3;

export default function GalleryPage() {

  const [keys, setKeys] = useState<string[]>([]);
  const [images, setImages] = useState<ImageStruct[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selected_category, setSelectedCategory] = useState<string>("");
  const [loeading, setLoading] = useState<boolean>(false);
  const [deleted, setDeleted] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { sharedData, setSharedData } = useContext(DataContext);

  const Delete = async (key: string) => {
    const new_images = images.map((image) => {
      if (image.key === key) {
        image.deleting = true;
      }
      return image;
    });
    setImages(new_images);
    await new Promise((resolve) => setTimeout(resolve, setting.smallWaitingTime));
    const guid = key.split('/')[3].replace('.png', '');
    fetch(`${setting.apiPath}/image/delete?user_id=${sharedData.username}&category=${selected_category}&guid=${guid}`, {
      method: 'DELETE',
    }).then(async (res) => {
      if (res.status === 200) {
        const new_images = images.filter((image) => image.key !== key);
        setImages(new_images);
        setDeleted(deleted.concat(key));
      } else {
        setError('画像の削除に失敗しました。');
      }
    });
  };

  const Download = () => {
    (async () => {
      fetch(`${setting.apiPath}/image/download/?user_id=${sharedData.username}&category=${selected_category}`)
        .then(async (res) => {
          if (res.status === 200) {
            return await res.json();
          } else {
            return null;
          }
        }
        ).then((data) => {
          if (data === null) {
            setError('画像データ一覧の取得に失敗しました。');
            return;
          }
          const zip_base64 = data.data;
          const zip = Buffer.from(zip_base64, 'base64');
          const blob = new Blob([zip], { type: 'application/zip' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${sharedData.username}_${selected_category}.zip`;
          a.click();
        });
    })();
  };

  const Load = () => {
    const target_keys = keys.filter((key) => key.split('/')[2] === selected_category);
    if (target_keys.length === 0) {
      return;
    }
    const new_keys = target_keys.filter((key) => !images.map((image) => image.key).includes(key));
    if (new_keys.length === 0) {
      return;
    }
    const guids_raw = new_keys.filter(a => !deleted.includes(a)).map((key) => key.split('/')[3].replace('.png', ''));
    const guids = guids_raw.slice(0, image_fetch_limit).join(',');
    (async () => {
      fetch(`${setting.apiPath}/image/fetch/?user_id=${sharedData.username}&category=${selected_category}&guids=${guids}`)
        .then(async (res) => {
          if (res.status === 200) {
            return await res.json();
          } else {
            return null;
          }
        }
        ).then((data) => {
          if (data === null) {
            setError('画像データ一覧の取得に失敗しました。');
            return;
          }
          data.images.forEach((image: ImageStruct) => {
            image.deleting = false;
          });
          setImages(images.concat(data.images));
        }
        );
    })();
  };

  useEffect(() => {
    if (sharedData.username === "") return;
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
    (async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, setting.smallWaitingTime));
      setImages([]);
      setError(null);
      // 対象のカテゴリの画像キーを取得
      const target_keys = keys.filter((key) => key.split('/')[2] === selected_category);
      if (target_keys.length === 0) {
        setLoading(false);
        return;
      };
      if (selected_category === "") {
        setLoading(false);
        return;
      };
      const guids = target_keys.map((key) => key.split('/')[3].replace('.png', '')).slice(0, image_fetch_limit).join(',');
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
              setLoading(false);
              return;
            }
            data.images.forEach((image: ImageStruct) => {
              image.deleting = false;
            });
            setImages(data.images as ImageStruct[]);
            setLoading(false);
          });
      })();
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
            <Alert variant="danger" className="mt-3">ユーザ名は半角英数字と記号(アンダースコアとハイフン)の3-16文字で入力してください。</Alert>
          )
        }
        {
          error !== null && (
            <Alert variant="danger" className="mt-3">{error}</Alert>
          )
        }
        {
          loeading ? (
            <div className="mt-3 d-flex justify-content-between">
              <Spinner animation="border" variant="primary" />
              <Spinner animation="border" variant="secondary" />
              <Spinner animation="border" variant="success" />
              <Spinner animation="border" variant="danger" />
              <Spinner animation="border" variant="warning" />
              <Spinner animation="border" variant="info" />
              <Spinner animation="border" variant="light" />
              <Spinner animation="border" variant="dark" />
            </div>
          ) : (
            <div>
            {
              images.length === 0 && selected_category !== "" ? (
                <Alert variant="info" className="mt-3">画像がありません。</Alert>
              ) : (
                <>
                  {
                    images.length !== 0 && <Button variant="primary" onClick={Download} className="mt-5 d-block m-auto">Download All</Button>
                  }
                  <div id="ImageDiv" className="mt-5">
                  {
                    images.map((image) => (
                      <div key={image.key} className={`image-box ${image.deleting ? "deleting" : ""}`}>
                        <img src={`data:image/png;base64,${image.image}`} alt={selected_category} className="img-thumbnail" />
                        <BsFillTrash3Fill onClick={() => {Delete(image.key)}} className="img-delete" />
                      </div>
                    ))
                  }
                </div>
                {
                  keys.filter((key) => key.split('/')[2] === selected_category).length - deleted.length > images.length && (
                    <Button variant="info" size="sm" onClick={Load} className="mt-5 d-block m-auto">Load More</Button>
                  )
                }
                </>
              )
            }
            </div>
          )
        }
      </div>
    </Layout>
  );
};
