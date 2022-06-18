import ReactDOM from 'react-dom/client';

import MessagesComponent from './MessagesComponent';

import './index.css'

const messegesEl = ReactDOM.createRoot(document.getElementById('messages'));
messegesEl.render(<MessagesComponent />);