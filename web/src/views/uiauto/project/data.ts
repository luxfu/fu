import { BasicColumn } from '/@/components/Table';
import { FormSchema } from '/@/components/Table';
import { useI18n } from '/@/hooks/web/useI18n';
import { h } from 'vue';
import { Tag } from 'ant-design-vue';
import { rules } from '/@/utils/helper/validator';
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
    dataIndex: 'create_time',
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
        { label: t('common.enableText'), value: 1 },
        { label: t('common.disableText'), value: 0 },
      ],
    },
    colProps: { span: 6 },
  },
];

export const projectFormSchema: FormSchema[] = [
  {
    field: 'id',
    label: 'id',
    component: 'Input',
    show: false,
  },
  {
    field: 'name',
    label: t('common.project.name'),
    component: 'Input'
  },
  {
    field: 'status',
    label: t('common.project.status'),
    component: 'Select',
    defaultValue: 1,
    componentProps: {
      options: [
        { label: t('common.enableText'), value: 1 },
        { label: t('common.disableText'), value: 0 },
      ],
    },
    colProps: { span: 6 },
  },
];
