import { defHttp } from "/@/utils/http/axios";

enum DeptApi  {
    prefix = "/runner/api/v1/project",
}

export const getList = (params) => {
  return defHttp.get({ url: DeptApi.prefix, params });
};