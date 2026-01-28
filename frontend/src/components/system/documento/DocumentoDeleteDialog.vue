<script setup>
const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  documentSelected: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:isDialogVisible", "deleteDocument"]);

const isLoading = ref(false);
const toast = useMaterializeToast();

const remove = async () => {
  try {
    isLoading.value = true;
    const response = await $api(`/document/${props.documentSelected.id}`, {
      method: "DELETE",
    });

    if (response.success) {
      toast.showSuccess(
        response.message || "Documento eliminado correctamente",
        "Éxito",
      );
      emit("update:isDialogVisible", false);
      emit("deleteDocument");
    } else {
      toast.showError(response.message || "Error al eliminar", "Error");
    }
  } catch (error) {
    toast.showError("Error al conectar con el servidor", "Error");
  } finally {
    isLoading.value = false;
  }
};

const onFormReset = () => {
  emit("update:isDialogVisible", false);
};

const dialogVisibleUpdate = (val) => {
  emit("update:isDialogVisible", val);
};
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 500"
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard class="pa-sm-11 pa-3">
      <DialogCloseBtn variant="text" size="default" @click="onFormReset" />

      <VCardText class="pt-5 text-center">
        <VIcon icon="ri-delete-bin-line" size="64" color="error" class="mb-3" />
        <h4 class="text-h4 font-weight-bold mb-2">Eliminar Documento</h4>
        <p class="text-body-1 mb-6">
          ¿Estás seguro de que deseas eliminar el documento <br />
          <span class="font-weight-bold"
            >"{{ props.documentSelected.name }}"</span
          >? <br />Esta acción se puede deshacer desde el administrador de base
          de datos.
        </p>

        <div class="d-flex justify-center gap-4">
          <VBtn
            color="error"
            class="px-8"
            :loading="isLoading"
            :disabled="isLoading"
            @click="remove"
          >
            <VIcon start icon="ri-delete-bin-fill" />
            <span class="font-weight-bold">Sí, Eliminar</span>
          </VBtn>

          <VBtn
            color="secondary"
            variant="tonal"
            class="px-8"
            :disabled="isLoading"
            @click="onFormReset"
          >
            Cancelar
          </VBtn>
        </div>
      </VCardText>
    </VCard>
  </VDialog>
</template>
