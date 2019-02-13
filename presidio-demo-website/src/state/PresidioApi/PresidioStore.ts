import { observable, action } from 'mobx';
import { FilterType } from './FilterType';
import { Api } from './Api';
import { FilterState, FieldTypeValue } from './FilterState';
import { IFilterType, IFieldTransformation, ITransformation, IAnalyzeResult } from './Interfaces';
import { INPUT_SEARCH_DELAY_MS, INPUT_DEFAULT_TEXT } from '../../settings';

export class PresidioStore {

  @observable filters: FilterType[] = [];
  @observable visibleFilters: string[] = [];
  @observable filterStates: FilterState[] = [];
  @observable pendingRequests = 0;
  @observable input: string = INPUT_DEFAULT_TEXT;

  @observable searchFieldType: string = '';
  @observable output: string = '';
  @observable analyzeResult: IAnalyzeResult | null = null;

  private _timeoutHandle: NodeJS.Timer | null = null;
  private api = new Api();

  constructor() {
    this.load();
  }

  @action async load() {
    const results = await this.api.load();

    this.filters = results.filters;
    this.visibleFilters = this.filters.map(filter => filter.name).sort();
    this.filterStates = this.filters.map(filter => new FilterState(filter.name));

    this.inputChangeCall(this.input);
  }

  @action toggleFilter(filterName: string) {
    const filterState = this.filterStates.find(fs => fs.name === filterName)!;
    filterState.active = !filterState.active;

    this.inputChange();
  }

  @action changeFilterType(filterName: string, value: string) {
    const filterState = this.filterStates.find(fs => fs.name === filterName)!;
    filterState.type = FieldTypeValue[value] as FieldTypeValue;

    this.inputChange();
  }

  @action searchFieldTypes(search: string) {
    this.searchFieldType = search;
    this.visibleFilters =
      this.filters.map(filter => filter.name).filter(filter => filter.toLowerCase().indexOf(search) >= 0).sort();
  }

  @action async inputChange(input?: string) {
    if (this._timeoutHandle !== null) {
      clearTimeout(this._timeoutHandle);
      this._timeoutHandle = null;
    }

    this._timeoutHandle = setTimeout(
      () => {
        this.inputChangeCall(input);
      },
      INPUT_SEARCH_DELAY_MS
    );
  }

  async inputChangeCall(input?: string) {

    this.input = input || this.input;
    if (!this.input) { return; }

    const activeFilters = this.filterStates.filter(f => f.active);
    const filterForApi: IFilterType[] = [];
    const fieldTypeTransformations: IFieldTransformation[] = [];

    // Adding active filter transformations
    activeFilters.forEach(activeFilter => {
      filterForApi.push({ name: activeFilter.name });

      let transformation: ITransformation | null = null;
      switch (activeFilter.type) {

        case FieldTypeValue.Redact:
          transformation = { redactValue: {} };
          break;

        case FieldTypeValue.Hash:
          transformation = { hashValue: {} };
          break;

        case FieldTypeValue.Replace:
          transformation = { replaceValue: { newValue: activeFilter.replaceWith } };
          break;

        case FieldTypeValue.Mask:
          transformation = {
            maskValue: {
              maskingCharacter: activeFilter.maskCharacter,
              charsToMask: activeFilter.maskCharsToMask,
              fromEnd: activeFilter.maskFromEnd
            }
          };
          break;

        case FieldTypeValue.FPE:
          transformation = {
            fPEValue: {
              key: activeFilter.key,
              tweak: activeFilter.tweak
            }
          };
          break;

        case FieldTypeValue.None:
          break;

        default:
          break;
      }

      if (transformation !== null) {
        fieldTypeTransformations.push({
          fields: [{ name: activeFilter.name }],
          transformation
        });
      }
    });

    const [anonimizedOutput, analyzeResult] =
      await Promise.all([
        this.api.anonimize(this.input, filterForApi, fieldTypeTransformations),
        this.api.analyze(this.input, filterForApi)
      ]);

    if (analyzeResult && anonimizedOutput) {
      this.output = anonimizedOutput.text;
      this.analyzeResult = analyzeResult;
    } else {
      this.output = '';
      this.analyzeResult = null;
    }
  }
}