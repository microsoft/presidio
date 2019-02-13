import * as request from 'request-promise';
import { IFilterType, IAnonimizeResult, IAnalyzeResult } from './Interfaces';

import { API_FILTERS_URL, API_ANONIMIZE_URL, API_FINDINGS_URL } from '../../settings';

export interface IFilterResult {
  filters: IFilterType[];
}

export class Api {

  async load(): Promise<IFilterResult> {

    const data: string = await request(API_FILTERS_URL);

    return {
      filters: JSON.parse(data)
    };
  }

  async anonimize(input: string, filters: IFilterType[], transformations: any[]): Promise<IAnonimizeResult> {

    const data: IAnonimizeResult = await request({
      method: 'POST',
      uri: API_ANONIMIZE_URL,
      json: {
        text: input,
        analyzeTemplate: {
          fields: filters
        },
        anonymizeTemplate: {
          fieldTypeTransformations: transformations
        }
      }
    });

    return data;
  }

  async analyze(input: string, filters: IFilterType[]): Promise<IAnalyzeResult> {

    const data: IAnalyzeResult = await request({
      method: 'POST',
      uri: API_FINDINGS_URL,
      json: {
        text: input,
        analyzeTemplate: {
          fields: filters
        }
      }
    });

    return data;
  }
}