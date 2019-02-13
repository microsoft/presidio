import * as React from 'react';
import { observer, inject } from 'mobx-react';
import { PresidioStore } from '../../state/PresidioApi';
import { Card, CardTitle, Divider, TextField } from 'react-md';

interface IProps {
  presidioStore?: PresidioStore;
}

@inject('presidioStore')
@observer
export default class InputEditor extends React.Component<IProps> {

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
        <CardTitle title="Input text" subtitle="" />
        <Divider />
        <TextField
          id="input-text"
          placeholder="Input Text"
          block={true}
          rows={4}
          paddedBlock={true}
          defaultValue={this.presidioStore.input}
          errorText="Max 1000 characters."
          onChange={this.onInputChanged}
        />
      </Card>
    );
  }
}