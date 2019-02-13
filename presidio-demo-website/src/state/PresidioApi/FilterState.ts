import { IFilterType } from './Interfaces';
import { observable } from 'mobx';

export enum FieldTypeValue {
  None,
  Hash,
  Redact,
  Replace,
  Mask,
  FPE
}

export class FilterState implements IFilterType {
  @observable name: string;
  @observable active: boolean = true;
  @observable type: FieldTypeValue = FieldTypeValue.Replace;

  @observable replaceWith: string = '';

  @observable maskCharacter: string = '*';
  @observable maskCharsToMask: number = 8;
  @observable maskFromEnd: boolean = false;

  @observable key: string = 'AAECAwQFBgcICQoLDA0ODw==';
  @observable tweak: string = 'MTIzNDU2Nw==';
  @observable decrypt: boolean = false;

  constructor(name: string) {
    this.name = name;
    this.replaceWith = `<${name}>`;
  }
}