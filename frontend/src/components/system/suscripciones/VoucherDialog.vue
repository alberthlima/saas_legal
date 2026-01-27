<script setup>
const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  voucherUrl: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["update:isDialogVisible"]);

const onFormReset = () => {
  emit("update:isDialogVisible", false);
};

const dialogVisibleUpdate = (val) => {
  emit("update:isDialogVisible", val);
};
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 800"
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard title="Comprobante de Pago">
      <DialogCloseBtn variant="text" size="default" @click="onFormReset" />

      <VCardText class="d-flex justify-center pa-6">
        <VImg
          :src="props.voucherUrl"
          class="border rounded shadow-sm"
          max-height="600"
          contain
        />
      </VCardText>

      <VCardText class="text-center pb-6">
        <VBtn
          color="primary"
          variant="tonal"
          prepend-icon="ri-external-link-line"
          :href="props.voucherUrl"
          target="_blank"
        >
          Abrir en pestaña nueva
        </VBtn>
      </VCardText>
    </VCard>
  </VDialog>
</template>
