import { BasicColumn } from '/@/components/Table';
import { FormSchema } from '/@/components/Table';
import { useI18n } from '/@/hooks/web/useI18n';
import { h } from 'vue';
import { Tag } from 'ant-design-vue';
import { rules } from '/@/utils/helper/validator';
const { t } = useI18n();
export const columns: BasicColumn[] = [
  {
    title: t('common.pageobject.po_id'),
    dataIndex: 'po_id',
    width: 110,
  },
  {
    title: t('common.pageobject.name'),
    dataIndex: 'name',
    width: 110,
  },
  {
    title: t('common.pageobject.url'),
    dataIndex: 'url',
    width: 110,
  },
  {
    title: t('common.pageobject.locator'),
    dataIndex: 'locator',
    width: 110,
  },
  {
    title: t('common.pageobject.locator_type'),
    dataIndex: 'locator_type',
    width: 110,
  },
  {
    title: t('common.pageobject.create_time'),
    dataIndex: 'created_at',
    width: 180,
  },
];

export const searchFormSchema: FormSchema[] = [
  {
    field: 'name',
    label: t('common.pageobject.name'),
    component: 'Input',
    colProps: { span: 6 },
  },
];

export const pageobjectFormSchema: FormSchema[] = [
  {
    field: 'id',
    label: 'id',
    component: 'Input',
    show: false,
  },
  {
    field: 'po_id',
    label: 'po_id',
    component: 'Input',
    show: false,
  },
  {
    field: 'name',
    label: t('common.pageobject.name'),
    component: 'Input',
  },
  {
    field: 'url',
    label: t('common.pageobject.url'),
    component: 'Input',
  },
  {
    field: 'locator',
    label: t('common.pageobject.locator'),
    component: 'Input',
  },
  {
    field: 'locator_type',
    label: t('common.pageobject.locator_type'),
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
    field: 'created_at',
    label: 'created_at',
    component: 'Input',
    show: false,
  },
];
