import * as React from 'react';
import { observer, inject } from 'mobx-react';
import { PresidioStore } from '../../state/PresidioApi';
import {
  Card,
  CardTitle,
  Divider,
  DataTable,
  TableHeader,
  TableBody,
  TableRow,
  TableColumn,
} from 'react-md';

interface IProps {
  presidioStore?: PresidioStore;
}

@inject('presidioStore')
@observer
export default class FindingsView extends React.Component<IProps> {

  presidioStore: PresidioStore;

  constructor(props: any) {
    super(props);

    this.presidioStore = this.props.presidioStore!;
  }

  render() {

    if (this.presidioStore.analyzeResult == null) {
      return (
        <Card>
          <CardTitle title="No Findings" subtitle="Presidio Analysis" />
          <Divider />
        </Card>
      );
    }

    return (
      <Card>
        <CardTitle title="Findings" subtitle="Presidio Analysis" />
        <Divider />
        <DataTable plain={true}>
          <TableHeader>
            <TableRow>
              <TableColumn>Field Type</TableColumn>
              <TableColumn>Score</TableColumn>
              <TableColumn>Text</TableColumn>
              <TableColumn>Start:End</TableColumn>
            </TableRow>
          </TableHeader>
          <TableBody>
            {this.presidioStore.analyzeResult.map((result, i) => (
              <TableRow key={i}>
                <TableColumn>{result.field.name}</TableColumn>
                <TableColumn>{result.score}</TableColumn>
                <TableColumn>{result.text}</TableColumn>
                <TableColumn>{result.location.start + ':' + result.location.end}</TableColumn>
              </TableRow>
            ))}
          </TableBody>
        </DataTable>
      </Card>
    );
  }
}