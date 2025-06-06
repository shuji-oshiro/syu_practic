// 型定義
export interface Todo {
  title: string;
  email: string;
  done: boolean;
}

export interface TodoGetRequestBody {
  filter: string | undefined;
  user: string | undefined;
}


export interface EmailRequestBody {
  emailList: string;
}

export interface TodoAddRequestBody {
  title: string;
  emailList: string[];
}

export interface TodoToggleRequestBody {
  title: string;
  done: boolean;
  email: string;
}

export interface TodoDeleteRequestBody {
  title: string;
}

export interface TodoUpdateTitleRequestBody {
  oldTitle: string;
  newTitle: string;
}

export interface Send_Time_RequestBody{
  update_sendtime:string
}


import { z } from 'zod';

export const TodoAddSchema = z.object({
  title: z.string(),
  emailList: z.array(z.string())
});