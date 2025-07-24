import { BasicColumn } from '/@/components/Table';
import { FormSchema } from '/@/components/Table';
import { useI18n } from '/@/hooks/web/useI18n';
import { h } from 'vue';
import { Tag } from 'ant-design-vue';
import { rules } from '/@/utils/helper/validator';
const { t } = useI18n();
export const columns: BasicColumn[] = [
  {
    title: t('common.case.url'),
    dataIndex: 'url',
    width: 110,
  },
  {
    title: t('common.case.url_override'),
    dataIndex: 'url_override',
    width: 110,
  },
  {
    title: t('common.case.po_id'),
    dataIndex: 'po',
    width: 110,
  },
  {
    title: t('common.case.action_type'),
    dataIndex: 'action_type',
    width: 110,
  },
  {
    title: t('common.case.action_value'),
    dataIndex: 'action_value',
    width: 110,
  },
  {
    title: t('common.case.order'),
    dataIndex: 'order',
    width: 110,
  },
  {
    title: t('common.case.assert_type'),
    dataIndex: 'assert_type',
    width: 110,
  },
  {
    title: t('common.case.assert_expression'),
    dataIndex: 'assert_expression',
    width: 110,
  },
];

export const searchFormSchema: FormSchema[] = [
  {
    field: 'url',
    label: t('common.case.url'),
    component: 'Input',
    colProps: { span: 6 },
  },
];

export const caseFormSchema: FormSchema[] = [
  {
    field: 'id',
    label: 'id',
    component: 'Input',
    show: false,
  },
  {
    field: 'po',
    label: 'po',
    component: 'Input',
    show: false,
  },
  {
    field: 'url',
    label: t('common.case.url'),
    component: 'Input',
  },
  {
    field: 'custom_locator',
    label: t('common.case.custom_locator'),
    component: 'Input',
  },
  {
    field: 'custom_locator_type',
    label: t('common.case.custom_locator_type'),
    component: 'Select',
    componentProps: {
      options: [
        { label: t('common.pageobject.by_id'), value: 'id' },
        { label: t('common.pageobject.by_css'), value: 'css' },
        { label: t('common.pageobject.by_xpath'), value: 'xpath' },
      ],
    },
    colProps: { span: 6 },
  },
  {
    field: 'action',
    label: t('common.case.action_type'),
    component: 'Select',
    componentProps: {
      options: [
        { label: 'input', value: 'input' },
        { label: 'hover', value: 'hover' },
      ],
    },
  },
  {
    field: 'action_value',
    label: t('common.case.action_value'),
    component: 'Input',
  },
  {
    field: 'assert_type',
    label: t('common.case.assert_type'),
    component: 'Input',
  },
  {
    field: 'assert_expression',
    label: t('common.case.assert_expression'),
    component: 'Input',
  },
];
