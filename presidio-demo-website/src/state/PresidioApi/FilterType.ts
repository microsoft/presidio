
import { IFilterType } from './Interfaces';
import { observable } from 'mobx';

export class FilterType implements IFilterType {
  @observable name: string;
}