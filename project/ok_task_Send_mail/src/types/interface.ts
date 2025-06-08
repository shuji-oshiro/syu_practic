// 型定義
export interface Todo {
  title: string;
  email: string;
  done: boolean;
}

import { z } from 'zod';

export const TodoAddSchema = z.object({
  title: z.string(),
  emailList: z.array(z.string())
});

export const TodoGetSchema = z.object({
  filter: z.string().transform(val => val.trim() === '' ? undefined : val).optional(),
  user: z.string().transform(val => val.trim() === '' ? undefined : val).optional()
});

export const TodoUpdateSchema = z.object({
  title: z.string(),
  done: z.boolean(),
  email:z.string()

});

export const TodoTitleUpdateSchema = z.object({
  oldTitle: z.string().min(1),
  newTitle:z.string().min(1)
});

export const TodoDeleteSchema = z.object({
  title: z.string().min(1)
});

export const TodoSendTimeSchema = z.object({
  update_sendtime: z.string().regex(/^([01]\d|2[0-3]):[0-5]\d$/)
});