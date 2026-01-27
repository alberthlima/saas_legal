<script setup>
const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  subscriptionSelected: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:isDialogVisible", "cancelSubscription"]);

const isLoading = ref(false);
const toast = useMaterializeToast();

const cancelSubscription = async () => {
  try {
    isLoading.value = true;

    const response = await $api(
      `/subscription/${props.subscriptionSelected.id}/cancel`,
      {
        method: "POST",
        onResponse({ response }) {
          if (response.status === 200) {
            toast.showSuccess(
              response._data.message || "Suscripción cancelada correctamente",
              "Éxito",
            );
            emit("update:isDialogVisible", false);
            emit("cancelSubscription", props.subscriptionSelected.id);
          } else {
            toast.showError(
              response._data.message || "Error al cancelar la suscripción",
              "Error",
            );
          }
        },
      },
    );
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
    <VCard class="pa-sm-8 pa-4">
      <DialogCloseBtn variant="text" size="default" @click="onFormReset" />

      <VCardText class="pt-5">
        <div class="text-center pb-6">
          <VIcon
            icon="ri-close-circle-line"
            size="64"
            color="error"
            class="mb-4"
          />
          <h4 class="text-h4 font-weight-bold mb-3">¿Cancelar Suscripción?</h4>
          <p class="text-h6 mb-2">{{ props.subscriptionSelected.name }}</p>
          <p class="text-body-1 text-medium-emphasis">
            ¿Estás seguro de que deseas cancelar esta suscripción? Esta acción
            desactivará el acceso del cliente.
          </p>
        </div>

        <VRow class="justify-center mt-4">
          <VCol cols="12" class="d-flex gap-3 justify-center">
            <VBtn
              color="error"
              class="px-8"
              :loading="isLoading"
              :disabled="isLoading"
              @click="cancelSubscription"
            >
              <VIcon start icon="ri-close-circle-line" />
              <span class="font-weight-bold">{{
                isLoading ? "Cancelando..." : "Sí, Cancelar"
              }}</span>
            </VBtn>

            <VBtn
              color="secondary"
              class="px-8"
              :disabled="isLoading"
              @click="onFormReset"
            >
              <VIcon start icon="ri-arrow-left-line" />
              <span class="font-weight-bold">Volver</span>
            </VBtn>
          </VCol>
        </VRow>
      </VCardText>
    </VCard>
  </VDialog>
</template>
