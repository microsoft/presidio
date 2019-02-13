import * as React from 'react';
import { observer, inject } from 'mobx-react';
import { PresidioStore } from '../../state/PresidioApi';
import { List, ListItemControl, TextField } from 'react-md';
import FilterTypeEditor from './FilterTypeEditor';

import './filters.css';

interface IProps {
  presidioStore?: PresidioStore;
}

@inject('presidioStore')
@observer
export default class FiltersView extends React.Component<IProps> {

  presidioStore: PresidioStore;

  constructor(props: any) {
    super(props);

    this.presidioStore = this.props.presidioStore!;
  }

  onFilterActiveChange = (filterName: string): void => {
    this.presidioStore.toggleFilter(filterName);
  }

  onFilterTypeChange = (filterName: string, value: string): void => {
    this.presidioStore.changeFilterType(filterName, value);
  }

  onSearchFieldChange = (value: string): void => {
    this.presidioStore.searchFieldTypes(value);
  }

  render() {

    if (!this.presidioStore) { return null; }

    const { visibleFilters } = this.presidioStore;

    const listItems = [
      <ListItemControl
        key={-1}
        tileStyle={{ padding: 0, display: 'inline' }}
        primaryText=""
        primaryAction={(
          <TextField
            id="filter-field-types"
            label="Search Filters"
            paddedBlock={true}
            style={{ padding: '10px' }}
            value={this.presidioStore.searchFieldType}
            onChange={this.onSearchFieldChange}
          />
        )
        }
      />
    ];

    visibleFilters.forEach((filterName, idx) => {

      listItems.push((
        <ListItemControl
          key={idx}
          tileStyle={{ padding: 0, display: 'inline' }}
          primaryText=""
          primaryAction={<FilterTypeEditor filterName={filterName} />}
        />));
    });

    return (
      <List className="prs-nav-filters">
        {listItems}
      </List>
    );
  }
}