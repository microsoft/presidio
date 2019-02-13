import * as React from 'react';
import { Card, CardTitle, CardText } from 'react-md';

interface IState {
  str1: string;
  str2: string;
}

export default class Image extends React.Component<{}, IState> {

  state = {
    str1: 'None',
    str2: 'None'
  };

  getHelloWorld() {
    return this.state.str1 + ' ' + this.state.str2;
  }

  render() {
    return (
      <div className="md-grid">
        <Card className="md-cell md-cell--12">
          <CardTitle title="Soon to be available..." />
          <CardText>
            <p>This page will hold image anonymization</p>
          </CardText>
        </Card>
      </div>
    );
  }
}