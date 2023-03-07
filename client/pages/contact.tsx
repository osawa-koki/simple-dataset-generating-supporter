import React, { useState } from "react";

import { Button, Alert, Form } from 'react-bootstrap';
import Layout from "../components/Layout";

import { DataContext } from "../src/DataContext";

const mail_regex = new RegExp(/^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/);

export default function ContactPage() {

  const [count, setCount] = useState(0);
  const { sharedData, setSharedData } = React.useContext(DataContext);

  return (
    <Layout>
      <div id="Contact">
        <h1>Dummy Contact.</h1>
        <p className="mt-3">仮想DOMによってJSで管理しているデータを中心にHTMLを生成することができます。<br /><br />`AddEventListener`や`JQuery(&quot;***&quot;).on`なんて使いません。<br /><br />ちなみに、Next.js(React)は単方向バインディングであるため、HTMLをそのまま操作することはせずに、JSによるデータを操作することで描写するHTMLを制御します。<br /><br />この点がVue.jsやAngularと異なります。<br /><br />また、react-bootstrapによるBootstrapのサポートがあるため、簡単にBootstrapを導入できます。</p>
        <hr />
        <Alert variant="info">You cliecked { count } times 🤣🤣🤣</Alert>
        <Button variant="primary" onClick={() => {setCount(count + 1)}}>Click Me {((count % 3 === 0 && count !== 0) || /3/.test(count.toString()) ? '🤪' : '😀')}</Button>
        <hr />
        <Form.Group controlId="formBasicEmail" className="mt-3">
          <Form.Label>Email address</Form.Label>
          <Form.Control type="email" placeholder="Enter email" value={sharedData.email} onInput={(e) => {
            setSharedData({
              ...sharedData,
              email: (e.target as HTMLInputElement).value,
            });
          }} />
          <Form.Text>
            We&apos;ll never share your email with anyone else.
          </Form.Text>
        </Form.Group>
        {
          mail_regex.test(sharedData.email) ? (
            <Alert variant="success">Your email is valid.</Alert>
          ) : (
            <Alert variant="danger">Your email is invalid.</Alert>
          )
        }
      </div>
    </Layout>
  );
};
