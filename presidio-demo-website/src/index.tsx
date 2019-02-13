import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Provider } from 'mobx-react';
import App from './App';
import './index.css';
import * as WebFontLoader from 'webfontloader';
import { BrowserRouter as Router } from 'react-router-dom';
import { PresidioStore } from './state/PresidioApi';

WebFontLoader.load({
  google: {
    families: ['Roboto:300,400,500,700', 'Material Icons'],
  },
});

const presidioStore = new PresidioStore();

ReactDOM.render(
  <Provider presidioStore={presidioStore}>
    <Router><App /></Router>
  </Provider>,
  document.getElementById('root') as HTMLElement
);