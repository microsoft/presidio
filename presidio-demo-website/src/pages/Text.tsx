import * as React from 'react';
import InputEditor from '../components/InputEditor';
import OutputDisplay from '../components/OutputDisplay';
import FindingsView from '../components/Findings';
import { Grid, Cell } from 'react-md';

export default class Text extends React.Component {
    render() {
        return (
            <Grid className="home" noSpacing={true}>
                <Cell size={12}>
                    <Grid>
                        <Cell size={6}>
                            <InputEditor />
                        </Cell>
                        <Cell size={6}>
                            <OutputDisplay />
                        </Cell>
                    </Grid>
                </Cell>
                <Cell size={12}>
                    <Grid>
                        <Cell size={12}>
                            <FindingsView />
                        </Cell>
                    </Grid>
                </Cell>
            </Grid>
        );
    }
}
