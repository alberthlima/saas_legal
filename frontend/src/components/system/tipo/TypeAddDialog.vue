<script setup>
// Importar los validadores compartidos
import { requiredValidator } from "@/utils/validators";

const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
});

//definicion de variables
const emit = defineEmits(["update:isDialogVisible", "addType"]);
const name = ref(null);
const isLoading = ref(false);
const toast = useMaterializeToast();

const store = async () => {
  let data = {
    name: name.value,
    state: 1,
  };

  try {
    isLoading.value = true;

    const response = await $api("/type", {
      method: "POST",
      body: data,
      onResponse({ response }) {
        if (response.status === 200) {
          toast.showSuccess(
            response._data.message ||
              "Tipo de documento guardado correctamente",
            "Éxito",
          );

          // Resetear formulario
          name.value = null;

          // Cerrar diálogo
          emit("update:isDialogVisible", false);

          // Emitir evento de actualización
          emit("addType", response._data.type);
        } else {
          toast.showError(
            response._data.message || "Error al guardar el Tipo de documento",
            "Error",
          );
        }
      },
    });
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
    :width="$vuetify.display.smAndDown ? 'auto' : 700"
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard class="pa-sm-11 pa-3">
      <!-- 👉 dialog close btn -->
      <DialogCloseBtn variant="text" size="default" @click="onFormReset" />

      <VCardText class="pt-5">
        <!-- 👉 Header mejorado -->
        <div class="text-center pb-8">
          <VIcon
            icon="ri-file-add-line"
            size="48"
            color="primary"
            class="mb-3"
          />
          <h4 class="text-h4 font-weight-bold mb-2">
            Agregar Nuevo Tipo de Documento
          </h4>
        </div>

        <!-- 👉 Form -->
        <VForm class="mt-6" @submit.prevent="store">
          <VRow>
            <!-- 👉 campo Name -->
            <VCol cols="12">
              <VTextField
                v-model="name"
                placeholder="Ej: Ley, contitucion, normativa, etc."
                label="Nombre del Tipo de Documento"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 Submit and Cancel -->
            <VCol cols="12" class="d-flex flex-wrap justify-center gap-4 mt-6">
              <VBtn
                type="submit"
                color="success"
                class="px-8"
                :loading="isLoading"
                :disabled="isLoading"
              >
                <VIcon start icon="ri-save-3-fill" />
                <span class="font-weight-bold">{{
                  isLoading ? "Guardando..." : "Guardar Tipo de Documento"
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
        </VForm>
      </VCardText>
    </VCard>
  </VDialog>
</template>
