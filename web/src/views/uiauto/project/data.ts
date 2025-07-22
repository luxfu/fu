import { BasicColumn } from '/@/components/Table';
import { FormSchema } from '/@/components/Table';
import { useI18n } from '/@/hooks/web/useI18n';
import { h } from 'vue';
import { Tag } from 'ant-design-vue';
import { rules } from '/@/utils/helper/validator';
import { getList } from './api';
const { t } = useI18n();
export const columns: BasicColumn[] = [
  {
    title: t('common.project.name'),
    dataIndex: 'name',
    width: 110,
  },
  {
    title: t('common.project.status'),
    dataIndex: 'status',
    width: 110,
    customRender: ({ record }) => {
      const status = record.status;
      const enable = ~~status === 1;
      const color = enable ? 'success' : 'error';
      const text = enable ? t('common.enableText') : t('common.disableText');
      return h(Tag, { color: color }, () => text);
    },
  },
  {
    title: t('common.project.createTime'),
    dataIndex: 'create',
    width: 180,
  }
];

export const searchFormSchema: FormSchema[] = [
  {
    field: 'name',
    label: t('common.project.name'),
    component: 'Input',
    colProps: { span: 6 },
  },
  {
    field: 'status',
    label: t('common.project.status'),
    component: 'Select',
    componentProps: {
      options: [
        { label: t('common.enableText'), value: true },
        { label: t('common.disableText'), value: false },
      ],
    },
    colProps: { span: 6 },
  },
];

export const accountFormSchema: FormSchema[] = [
  {
    field: 'id',
    label: 'id',
    component: 'Input',
    show: false,
  },
  {
    field: 'password',
    label: 'password',
    component: 'Input',
    show: false,
  },
  {
    field: 'username',
    label: t('common.account.accountText'),
    component: 'Input',
    required: true,
  },
  {
    field: 'name',
    label: t('common.account.userNameText'),
    component: 'Input',
    required: true,
  },

  {
    field: 'mobile',
    label: t('common.account.mobileText'),
    component: 'Input',
    rules: rules.rule('phone', false),
  },
  {
    field: 'email',
    label: t('common.account.emailText'),
    component: 'Input',
    rules: rules.rule('email', false),
  },
  {
    label: t('common.account.userRoleText'),
    field: 'role',
    component: 'ApiSelect',
    componentProps: {
      api: getList,
      labelField: 'name',
      valueField: 'id',
      mode: 'multiple',
    },
    itemProps: { validateTrigger: 'blur' },
  },
  {
    label: t('common.account.userPostText'),
    field: 'post',
    component: 'ApiSelect',
    componentProps: {
      api: getList,
      labelField: 'name',
      valueField: 'id',
      mode: 'multiple',
    },
    itemProps: { validateTrigger: 'blur' },
  },
  {
    field: 'dept',
    label: t('common.account.userDeptText'),
    component: 'TreeSelect',
    componentProps: {
      fieldNames: {
        label: 'name',
        key: 'id',
        value: 'id',
      },
      getPopupContainer: () => document.body,
    },
  },
  {
    field: 'home_path',
    label: t('common.account.homePath'),
    component: 'DictSelect',
    componentProps: {
      dictCode: 'home_path',
    },
  },
  {
    field: 'gender',
    label: t('common.account.genderText'),
    component: 'RadioButtonGroup',
    defaultValue: 1,
    componentProps: {
      options: [
        { label: t('common.account.maleText'), value: 1 },
        { label: t('common.account.femaleText'), value: 0 },
      ],
    },
  },
  {
    field: 'status',
    label: t('common.statusText'),
    component: 'RadioButtonGroup',
    defaultValue: true,
    componentProps: {
      options: [
        { label: t('common.enableText'), value: true },
        { label: t('common.disableText'), value: false },
      ],
    },
    required: true,
  },

  {
    field: 'avatar',
    label: t('common.account.avatarText'),
    component: 'Input',
    slot: 'avatar',
  },
];
