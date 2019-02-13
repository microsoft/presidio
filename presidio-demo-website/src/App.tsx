import * as React from 'react';
import { Route, Switch } from 'react-router-dom';
import * as H from 'history';
import { NavigationDrawer, TabsContainer, Tab, Tabs } from 'react-md';
// import NavLink from './components/NavLink';
import FiltersView from './components/Filters';

import './App.css';

import Text from './pages/Text';
import Image from './pages/Image';
// import Page2 from './pages/Page2';
// import Page3 from './pages/Page3';

interface INavSettings {
  exact?: boolean;
  label: string;
  to: string;
  icon: string;
  component: React.ComponentClass;
}

const DEFAULT_TITLE = 'Welcome';
const navItems: INavSettings[] = [
  {
    exact: true,
    label: 'Text Anonymization',
    to: '/',
    icon: 'home',
    component: Text
  },
  {
    label: 'Image Anonymization',
    to: '/image',
    icon: 'bookmark',
    component: Image
  },
];

class App extends React.Component {

  getLocationTitle(location: H.Location): string {
    const currentPage = navItems.find(item => item.to === location.pathname);
    return currentPage && currentPage.label || DEFAULT_TITLE;
  }

  render() {

    // const navButtons = navItems.map(props => <NavLink {...props} key={props.to} />);

    const tabs = (
      <TabsContainer
        panelClassName="md-grid"
        colored={true}
        activeTabIndex={navItems.findIndex(i => window.location.pathname === i.to)}
        onTabChange={() => null}
      >
        <Tabs tabId="simple-tab">
          {
            navItems.map((props, idx) => (
              <Tab
                key={idx}
                label={props.label}
                onClick={() => window.location.replace(props.to)}
              />
            ))
          }
        </Tabs>
      </TabsContainer>
    );

    return (
      <Route
        render={({ location }) => (
          <NavigationDrawer
            drawerTitle="Presidio"
            toolbarTitle={this.getLocationTitle(location)}
            toolbarActions={tabs}
            navItems={[<FiltersView key={0} />]}
          >
            <Switch key={location.key}>
              {
                navItems.map(props => (
                  <Route
                    key={props.to}
                    exact={props.exact}
                    path={props.to}
                    location={location}
                    component={props.component}
                  />
                ))
              }
            </Switch>
          </NavigationDrawer>
        )}
      />
    );
  }
}

export default App;
