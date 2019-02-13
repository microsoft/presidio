import * as React from 'react';
import { observer, inject } from 'mobx-react';
import { PresidioStore } from '../../state/PresidioApi';
import { Card, CardTitle, Divider, TextField } from 'react-md';

interface IProps {
  presidioStore?: PresidioStore;
}

@inject('presidioStore')
@observer
export default class OutputDisplay extends React.Component<IProps> {

  presidioStore: PresidioStore;

  constructor(props: any) {
    super(props);

    this.presidioStore = this.props.presidioStore!;
  }

  onInputChanged = (text: string) => {
    this.presidioStore.inputChange(text);
  }

  render() {
    return (
      <Card>
        <CardTitle title="Anonymized text" subtitle="" />
        <Divider />
        <TextField
          id="email-body"
          placeholder="Body"
          block={true}
          rows={4}
          paddedBlock={true}
          value={this.presidioStore.output}
          onChange={() => null}
        />
      </Card>
    );
  }
}