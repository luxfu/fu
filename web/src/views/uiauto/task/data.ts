import { BasicColumn } from '/@/components/Table';
import { FormSchema } from '/@/components/Table';
import { useI18n } from '/@/hooks/web/useI18n';
import { h } from 'vue';
import { Tag } from 'ant-design-vue';
import { rules } from '/@/utils/helper/validator';
const { t } = useI18n();
export const columns: BasicColumn[] = [
  {
    title: t('common.tasks.task_name'),
    dataIndex: 'task_name',
    width: 110,
  },
  {
    title: t('common.tasks.status'),
    dataIndex: 'status',
    width: 110,
    customRender: ({ record }) => {
      const status = record.status;
      return h(Tag, { color: status }, () => status);
    },
  },
  {
    title: t('common.tasks.report_url'),
    dataIndex: 'report_url',
    width: 110,
  },
  {
    title: t('common.tasks.start_time'),
    dataIndex: 'start_time',
    width: 180,
  },
  {
    title: t('common.tasks.end_time'),
    dataIndex: 'end_time',
    width: 180,
  },
  {
    title: t('common.tasks.executor'),
    dataIndex: 'executor',
    width: 180,
  },
];

export const searchFormSchema: FormSchema[] = [
  {
    field: 'name',
    label: t('common.tasks.task_name'),
    component: 'Input',
    colProps: { span: 6 },
  },
];

export const tasksFormSchema: FormSchema[] = [
  {
    field: 'id',
    label: 'id',
    component: 'Input',
    show: false,
  },
  {
    field: 'task_name',
    label: t('common.tasks.task_name'),
    component: 'Input',
  },
  {
    field: 'test_suite',
    label: t('common.tasks.test_suite'),
    component: 'Input',
  },
];
