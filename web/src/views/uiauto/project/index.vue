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
                onClick: handleEdit.bind(null, record),
              },
              {
                icon: 'ant-design:delete-outlined',
                type: 'button',
                color: 'error',
                placement: 'left',
                auth: ['user:delete'],
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
    <ProjectModal @register="registerDrawer" @success="handleSuccess" />
  </PageWrapper>
</template>
<script lang="ts">
  import { defineComponent, reactive } from 'vue';
  import { BasicTable, useTable, TableAction } from '/@/components/Table';
  import { useDrawer } from '/@/components/Drawer';
  import { PageWrapper } from '/@/components/Page';
  import { getList } from './api';
  import { columns, searchFormSchema } from './data';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { Space } from 'ant-design-vue';
  import ProjectModal from './ProjectDrawer.vue';
  export default defineComponent({
    name: 'Project',
    components: { BasicTable, TableAction, PageWrapper, Space, ProjectModal },
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
      function handleBulkDelete() {}
      function handleEdit(record: Recordable) {}
      function handleDelete(record: Recordable) {}
      function handleSuccess() {}
      return {
        t,
        registerTable,
        searchInfo,
        handleCreate,
        handleBulkDelete,
        handleEdit,
        handleDelete,
        registerDrawer,
        handleSuccess,
      };
    },
  });
</script>
