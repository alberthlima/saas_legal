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

const emit = defineEmits(["update:isDialogVisible", "approveSubscription"]);

const isLoading = ref(false);
const toast = useMaterializeToast();

const approveSubscription = async () => {
  try {
    isLoading.value = true;

    const response = await $api(
      `/subscription/${props.subscriptionSelected.id}/approve`,
      {
        method: "POST",
        onResponse({ response }) {
          if (response.status === 200) {
            toast.showSuccess(
              response._data.message || "Suscripción aprobada correctamente",
              "Éxito",
            );
            emit("update:isDialogVisible", false);
            emit("approveSubscription", props.subscriptionSelected.id);
          } else {
            toast.showError(
              response._data.message || "Error al aprobar la suscripción",
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
            icon="ri-check-double-line"
            size="64"
            color="success"
            class="mb-4"
          />
          <h4 class="text-h4 font-weight-bold mb-3">¿Aprobar Suscripción?</h4>
          <p class="text-h6 mb-2">{{ props.subscriptionSelected.name }}</p>
          <p class="text-body-1 text-medium-emphasis">
            Esta acción activará la suscripción por <b>30 días</b> a partir de
            hoy. ¿Deseas continuar?
          </p>
        </div>

        <VRow class="justify-center mt-4">
          <VCol cols="12" class="d-flex gap-3 justify-center">
            <VBtn
              color="success"
              class="px-8"
              :loading="isLoading"
              :disabled="isLoading"
              @click="approveSubscription"
            >
              <VIcon start icon="ri-checkbox-circle-line" />
              <span class="font-weight-bold">{{
                isLoading ? "Aprobando..." : "Sí, Aprobar"
              }}</span>
            </VBtn>

            <VBtn
              color="secondary"
              class="px-8"
              :disabled="isLoading"
              @click="onFormReset"
            >
              <VIcon start icon="ri-arrow-left-line" />
              <span class="font-weight-bold">Cancelar</span>
            </VBtn>
          </VCol>
        </VRow>
      </VCardText>
    </VCard>
  </VDialog>
</template>
