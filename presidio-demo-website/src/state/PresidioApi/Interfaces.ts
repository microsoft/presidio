
export interface IFilterType {
  name: string;
}

export interface IAnonimizeResult {
  text: string;
}

export type ITransformation = {
  replaceValue: { newValue: string }
} | {
  maskValue: { maskingCharacter: string, charsToMask: number, fromEnd: boolean }
} | {
  redactValue: {}
} | {
  hashValue: {}
} | {
  fPEValue: { key: string, tweak: string }
};

export interface IFieldTransformation {
  fields: [{ name: string }];
  transformation: ITransformation;
}

export type IAnalyzeResult = [
  {
    text: string,
    field: {
      name: string
    },
    score: number,
    location: {
      start: number,
      end: number,
      length: number
    }
  }
];
