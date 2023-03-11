import Env from './next.config.js';
const isProd = process.env.NODE_ENV === 'production';

const setting = {
  isProd,
  basePath: Env.basePath,
  apiPath: process.env.NEXT_PUBLIC_LAMBDA_API_URL,
  title: "🧩 Let's make dataset! 🧩",
  waitingTime: 1000,
};

export default setting;
