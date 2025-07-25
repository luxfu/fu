<template>
  <PageWrapper dense contentFullHeight contentClass="flex">
    <BasicTable @register="registerTable" :searchInfo="searchInfo">
      <template #tableTitle>
        <Space style="height: 40px">
          <a-button
            type="primary"
            v-auth="['user:add']"
            preIcon="ant-design:plus-outlined"
            @click="handleCreate"
          >
            {{ t('common.addText') }}
          </a-button>
          <a-button
            type="error"
            v-auth="['user:delete']"
            preIcon="ant-design:delete-outlined"
            @click="handleBulkDelete"
          >
            {{ t('common.delText') }}
          </a-button>
        </Space>
      </template>
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <TableAction
            :actions="[
              {
                type: 'button',
                icon: 'ant-design:bug-filled',
                color: 'primary',
                auth: ['task:detail'],
                onClick: handleReport.bind(null, record),
              },
              {
                icon: 'ant-design:delete-outlined',
                type: 'button',
                color: 'error',
                placement: 'left',
                auth: ['task:delete'],
                popConfirm: {
                  title: t('common.delHintText'),
                  confirm: handleDelete.bind(null, record.id),
                },
              },
            ]"
          />
        </template>
      </template>
    </BasicTable>
    <TaskModal @register="registerDrawer" @success="handleSuccess" />
  </PageWrapper>
</template>
<script lang="ts">
  import { defineComponent, reactive } from 'vue';
  import { BasicTable, useTable, TableAction } from '/@/components/Table';
  import { useDrawer } from '/@/components/Drawer';
  import { PageWrapper } from '/@/components/Page';
  import { getList, deleteItem } from './api';
  import { columns, searchFormSchema } from './data';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { Space, message } from 'ant-design-vue';
  import TaskModal from './TaskDrawer.vue';
  export default defineComponent({
    name: 'Task',
    components: { BasicTable, TableAction, PageWrapper, Space, TaskModal },
    setup() {
      const { t } = useI18n();
      const searchInfo = reactive<Recordable>({});
      const [registerDrawer, { openDrawer }] = useDrawer();
      const [registerTable, { reload, updateTableDataRecord, getSelectRows }] = useTable({
        api: getList,
        rowKey: 'id',
        columns,
        formConfig: {
          labelWidth: 80,
          schemas: searchFormSchema,
          autoSubmitOnEnter: true,
        },
        useSearchForm: true,
        tableSetting: { fullScreen: true },
        showTableSetting: true,
        bordered: true,
        handleSearchInfoFn(info) {
          return info;
        },
        rowSelection: {
          type: 'checkbox',
          getCheckboxProps(record: Recordable) {
            // Demo: 第一行（id为0）的选择框禁用
            if (record.id === 1) {
              return { disabled: true };
            } else {
              return { disabled: false };
            }
          },
        },
        actionColumn: {
          width: 200,
          title: t('common.operationText'),
          dataIndex: 'action',
        },
      });
      function handleCreate() {
        openDrawer(true, {
          isUpdate: false,
        });
      }
      function handleSuccess() {}
      function handleBulkDelete() {}
      function handleReport(record: Recordable) {
        window.open(record.report_url);
      }
      async function handleDelete(id: number) {
        await deleteItem(id);
        message.success(t('common.successText'));
        await reload();
      }
      return {
        t,
        registerTable,
        searchInfo,
        handleCreate,
        handleReport,
        handleDelete,
        registerDrawer,
        handleSuccess,
        handleBulkDelete,
      };
    },
  });
</script>
