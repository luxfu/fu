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
                icon: 'clarity:note-edit-line',
                color: 'primary',
                auth: ['user:update'],
                disabled: record.id === 1,
                onClick: handleEdit.bind(null, record),
              },
              {
                icon: 'ant-design:delete-outlined',
                type: 'button',
                color: 'error',
                placement: 'left',
                auth: ['user:delete'],
                disabled: record.id === 1,
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
  </PageWrapper>
</template>
<script lang="ts">
  import { defineComponent, reactive } from 'vue';
  import { BasicTable, useTable, TableAction } from '/@/components/Table';
  import { PageWrapper } from '/@/components/Page';
  import { getList } from './api';
  import { columns, searchFormSchema } from './data';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { Space, message } from 'ant-design-vue';
  export default defineComponent({
    name: 'Project',
    components: { BasicTable, TableAction, PageWrapper, Space },
    setup() {
      const { t } = useI18n();
      const searchInfo = reactive({});
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
      function handleBulkDelete() {}
      function handleEdit(record: Recordable) {}
      function handleDelete(record: Recordable) {}
      return {
        t,
        registerTable,
        searchInfo,
        handleCreate,
        handleBulkDelete,
        handleEdit,
        handleDelete,
      };
    },
  });
</script>
