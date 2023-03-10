import React, { useEffect, useState } from "react";

import { Button, Alert, Form } from 'react-bootstrap';
import { fabric } from "fabric";
import Layout from "../components/Layout";

import { DataContext } from "../src/DataContext";

const CANVAS_NAME = 'MyCanvas';

export default function ContactPage() {

  const [canvas, setCanvas] = useState<any>(null);
  const { sharedData, setSharedData } = React.useContext(DataContext);

  const ClearCanvas = () => {
    canvas.remove.apply(canvas, canvas.getObjects());
    canvas.backgroundColor = 'white';
  }

  useEffect(() => {
    if (canvas === null) return;
    canvas.freeDrawingBrush = new fabric.PencilBrush(canvas);
    canvas.freeDrawingBrush.width=10;
    canvas.freeDrawingBrush.color="black";
    canvas.isDrawingMode = true;
    ClearCanvas();
  }, [canvas]);

  useEffect(() => {
    const canvas = new fabric.Canvas(CANVAS_NAME);
    setCanvas(canvas);
  }, []);

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
        <div id="CanvasWrapper" className="mt-5">
          <canvas id={CANVAS_NAME} width={300} height={300} />
        </div>
        <Button variant="primary" type="submit">
          Submit
        </Button>
      </div>
    </Layout>
  );
};
