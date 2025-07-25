import { defHttp } from '/@/utils/http/axios';

enum DeptApi {
  prefix = '/runner/api/v1/task',
}

export const getList = (params) => {
  return defHttp.get({ url: DeptApi.prefix, params });
};

export const deleteItem = (id: number) => {
  return defHttp.delete({ url: DeptApi.prefix + '/' + id });
};
export const createOrUpdate = (params, isUpdate) => {
  if (isUpdate) {
    return defHttp.put({ url: DeptApi.prefix + '/' + params.id, params });
  } else {
    return defHttp.post({ url: DeptApi.prefix, params });
  }
};
