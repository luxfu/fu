<template>
  <BasicDrawer
    v-bind="$attrs"
    showFooter
    @register="registerModal"
    width="50%"
    :title="getTitle"
    @ok="handleSubmit"
  >
    <BasicForm @register="registerForm"> </BasicForm>
  </BasicDrawer>
</template>
<script lang="ts">
  import { defineComponent, ref, computed, unref } from 'vue';
  import { BasicDrawer, useDrawerInner } from '/@/components/Drawer';
  import { BasicForm, useForm } from '/@/components/Form/index';
  import { projectFormSchema } from './data';
  import { createOrUpdate } from './api';
  import { CropperAvatar } from '/@/components/Cropper';
  import { uploadApi } from '/@/api/sys/upload';
  import { useI18n } from '/@/hooks/web/useI18n';
  export default defineComponent({
    name: 'ProjectModal',
    components: { BasicDrawer, BasicForm, CropperAvatar },
    emits: ['success', 'register'],
    setup(_, { emit }) {
      const { t } = useI18n();
      const isUpdate = ref(true);
      const rowId = ref('');

      const [registerForm, { setFieldsValue, updateSchema, resetFields, validate }] = useForm({
        labelWidth: 100,
        schemas: projectFormSchema,
        showActionButtonGroup: false,
        baseColProps: { lg: 12, md: 24 },
      });

      const [registerModal, { setDrawerProps, closeDrawer }] = useDrawerInner(async (data) => {
        resetFields();
        setDrawerProps({ confirmLoading: false });
        isUpdate.value = !!data?.isUpdate;

        if (unref(isUpdate)) {
          rowId.value = data.record.id;
          setFieldsValue({
            ...data.record,
          });
        }
      });

      const getTitle = computed(() =>
        !unref(isUpdate) ? t('common.addText') : t('common.updateText'),
      );

      async function handleSubmit() {
        try {
          const values = await validate();
          setDrawerProps({ confirmLoading: true });
          // TODO custom api
          await createOrUpdate(values, unref(isUpdate));
          closeDrawer();
          emit('success', { isUpdate: unref(isUpdate), values: { ...values, id: rowId.value } });
        } finally {
          setDrawerProps({ confirmLoading: false });
        }
      }

      return { registerModal, registerForm, getTitle, handleSubmit, uploadApi };
    },
  });
</script>
