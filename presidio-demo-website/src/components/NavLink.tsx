import * as React from 'react';
import { Link as RouterLink, Route } from 'react-router-dom';
import { FontIcon, ListItem } from 'react-md';

interface IProps {
  label: string;
  to: string;
  exact?: boolean;
  icon?: string;
}

export default class NavLink extends React.Component<IProps> {
  render() {

    const { label, to, exact, icon } = this.props;

    return (
      <Route path={to} exact={exact}>
        {({ match }) => {
          let leftIcon;
          if (icon) {
            leftIcon = <FontIcon>{icon}</FontIcon>;
          }

          return (
            <ListItem
              component={RouterLink}
              active={!!match}
              to={to}
              primaryText={label}
              leftIcon={leftIcon}
            />
          );
        }}
      </Route>
    );
  }
}