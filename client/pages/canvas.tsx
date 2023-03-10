import React, { useCallback, useEffect, useState } from "react";

import { Button, Alert, Form } from 'react-bootstrap';
import { fabric } from "fabric";
import Layout from "../components/Layout";

import { DataContext } from "../src/DataContext";
import setting from "../setting";

const CANVAS_NAME = 'MyCanvas';
const USER_ID_REGEX = /^[a-zA-Z0-9_-]{3,8}$/;
const CATEGORY_REGEX = /^[a-zA-Z0-9_-]{3,8}$/;
const is_valid = (username: string, category: string) => {
  return USER_ID_REGEX.test(username) && CATEGORY_REGEX.test(category);
}

export default function ContactPage() {

  const [canvas, setCanvas] = useState<any>(null);
  const { sharedData, setSharedData } = React.useContext(DataContext);

  useEffect(() => {
    const canvas = new fabric.Canvas(CANVAS_NAME);
    setCanvas(canvas);
  }, []);

  const Submit = useCallback(() => {
    if (canvas === null) return;
    const data = canvas.toDataURL("image/png").replace(/^data:image\/(png|jpg);base64,/, "");
    const username = sharedData.username;
    const category = sharedData.category;
    fetch(`${setting.apiPath}/image/upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data,
        username,
        category,
      }),
    }).then((res) => {
      if (res.status === 200) {
        alert('送信しました。');
      } else {
        alert('送信に失敗しました。');
      }
    });
  }, [canvas, sharedData]);

  const ClearCanvas = useCallback(() => {
    canvas.remove.apply(canvas, canvas.getObjects());
    canvas.backgroundColor = 'white';
  }, [canvas]);

  useEffect(() => {
    if (canvas === null) return;
    canvas.freeDrawingBrush = new fabric.PencilBrush(canvas);
    canvas.freeDrawingBrush.width = 10;
    canvas.freeDrawingBrush.color = "black";
    canvas.isDrawingMode = true;
    ClearCanvas();
  }, [ClearCanvas, canvas]);

  return (
    <Layout>
      <div id="Canvas">
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
            <Form.Control type="text" placeholder="Enter Category" value={sharedData.category} onInput={(e) => {
              setSharedData({
                ...sharedData,
                category: e.currentTarget.value,
              });
            }} />
          </Form.Group>
        </Form>
        {(is_valid(sharedData.username, sharedData.category) === false) && <Alert variant="danger" className="mt-3">ユーザ名とカテゴリは半角英数字と記号(アンダースコアとハイフン)の3-8文字で入力してください。</Alert>}
        <div id="CanvasWrapper" className="mt-5">
          <canvas id={CANVAS_NAME} width={300} height={300} />
        </div>
        <div className="mt-5 d-flex justify-content-center">
          <Button variant="primary" className="mx-3" disabled={is_valid(sharedData.username, sharedData.category) === false} onClick={Submit}>Submit 📨</Button>
          <Button variant="danger" className="mx-3" onClick={ClearCanvas}>Delete</Button>
        </div>
      </div>
    </Layout>
  );
};
