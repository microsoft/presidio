import * as React from 'react';
import { observer, inject } from 'mobx-react';
import { PresidioStore, FieldTypeValue } from '../../state/PresidioApi';
import { SelectField, Checkbox, TextField } from 'react-md';

interface IProps {
  filterName: string;
  presidioStore?: PresidioStore;
}

const FILTER_TYPE_OPTIONS = [
  FieldTypeValue[FieldTypeValue.None],
  FieldTypeValue[FieldTypeValue.Hash],
  FieldTypeValue[FieldTypeValue.Replace],
  FieldTypeValue[FieldTypeValue.Redact],
  FieldTypeValue[FieldTypeValue.Mask],
  FieldTypeValue[FieldTypeValue.FPE]
];

@inject('presidioStore')
@observer
export default class FilterTypeEditor extends React.Component<IProps> {
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

  render() {

    const { filterName } = this.props;
    if (!this.presidioStore) { return null; }

    const { filterStates } = this.presidioStore;
    if (filterStates.length === 0) { return null; }

    const filterState = filterStates.find(fs => fs.name === filterName)!;

    return (
      <div className="md-grid" style={{ width: '100%', padding: 0, marginBottom: '-10px', marginTop: '-10px' }}>
        <Checkbox
          id={'filter-active-check-' + filterState.name}
          className="md-cell md-cell--8"
          name={filterName}
          label={filterName}
          checked={filterState.active}
          onChange={this.onFilterActiveChange.bind(this, filterName)}
        />
        <SelectField
          id={'filter-type-select-' + filterState.name}
          className="md-cell md-cell--4"
          menuItems={FILTER_TYPE_OPTIONS}
          position={SelectField.Positions.BOTTOM_RIGHT}
          simplifiedMenu={true}
          sameWidth={true}
          value={FieldTypeValue[filterState.type]}
          onChange={this.onFilterTypeChange.bind(this, filterName)}
        />

        {filterState.type === FieldTypeValue.Replace && (
          <div className="md-cell md-cell--12" style={{ padding: 0, marginTop: '-20px' }}>
            <div className="md-grid">
              <div className="md-cell md-cell--12">
                <TextField
                  id={'filter-replace-' + filterState.name}
                  label="Replace With"
                  value={filterState.replaceWith}
                  onChange={(value) => {
                    filterState.replaceWith = value.toString();
                    this.presidioStore.inputChange();
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {filterState.type === FieldTypeValue.Mask && (
          <div className="md-cell md-cell--12" style={{ padding: 0, marginTop: '-20px' }}>
            <div className="md-grid">
              <div className="md-cell md-cell--12">
                <TextField
                  id={'filter-mask-chars-' + filterState.name}
                  label="Masking character"
                  value={filterState.maskCharacter}
                  maxLength={1}
                  onChange={value => {
                    if (value.toString().length > 1) { return; }
                    filterState.maskCharacter = value.toString();
                    this.presidioStore.inputChange();
                  }}
                />
              </div>
              <div className="md-cell md-cell--12">
                <TextField
                  id={'filter-mask-ctm-' + filterState.name}
                  label="Characters to mask"
                  type="number"
                  value={filterState.maskCharsToMask}
                  onChange={value => {
                    filterState.maskCharsToMask = parseInt(value.toString(), 0);
                    this.presidioStore.inputChange();
                  }}
                />
              </div>
              <div className="md-cell md-cell--12">
                <Checkbox
                  id={'filter-mask-fromend-' + filterState.name}
                  name="mask-from-end"
                  label="Mask from end"
                  checked={filterState.maskFromEnd}
                  onChange={value => {
                    filterState.maskFromEnd = value;
                    this.presidioStore.inputChange();
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {filterState.type === FieldTypeValue.FPE && (
          <div className="md-cell md-cell--12" style={{ padding: 0, marginTop: '-20px' }}>
            <div className="md-grid">
              <div className="md-cell md-cell--12">
                <TextField
                  id={'filter-key-' + filterState.name}
                  label="Key (Base64 format)"
                  value={filterState.key}
                  maxLength={256}
                  onChange={value => {
                    if (value.toString().length > 1) { return; }
                    filterState.key = value.toString();
                    this.presidioStore.inputChange();
                  }}
                />
              </div>
              <div className="md-cell md-cell--12">
                <TextField
                  id={'filter-tweak-' + filterState.name}
                  label="Tweak (Base64 format)"
                  value={filterState.tweak}
                  maxLength={14}
                  onChange={value => {
                    if (value.toString().length > 1) { return; }
                    filterState.tweak = value.toString();
                    this.presidioStore.inputChange();
                  }}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }
}