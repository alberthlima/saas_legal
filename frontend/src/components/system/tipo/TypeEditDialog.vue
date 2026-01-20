<script setup>
import { requiredValidator, selectValidator } from "@/utils/validators";

const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  typeSelected: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:isDialogVisible", "editType"]);

const id = ref(null);
const name = ref(null);
const state = ref(null);
const isLoading = ref(false);
const toast = useMaterializeToast();

const update = async () => {
  let data = {
    name: name.value,
    state: state.value,
  };

  try {
    isLoading.value = true;

    const response = await $api("/type/" + props.typeSelected.id, {
      method: "PUT",
      body: data,
      onResponse({ response }) {
        console.log(response);
        if (response.status === 200) {
          toast.showSuccess(
            response._data.message ||
              "Tipo de documento actualizado correctamente",
            "Éxito",
          );
          // Resetear formulario
          name.value = null;
          state.value = null;

          // Cerrar diálogo
          emit("update:isDialogVisible", false);

          // Emitir evento de actualización
          emit("editType", response._data.type);
        } else {
          toast.showError(
            response._data.message ||
              "Error al actualizar el tipo de documento",
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

onMounted(() => {
  id.value = props.typeSelected.id;
  name.value = props.typeSelected.name;
  state.value = props.typeSelected.state;
});
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 700"
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard class="pa-sm-11 pa-3">
      <DialogCloseBtn variant="text" size="default" @click="onFormReset" />

      <VCardText class="pt-5">
        <div class="text-center pb-8">
          <VIcon
            icon="ri-file-info-line"
            size="48"
            color="primary"
            class="mb-3"
          />
          <h4 class="text-h4 font-weight-bold mb-2">
            Editar Tipo de Documento: {{ typeSelected.name }}
          </h4>
        </div>

        <VForm class="mt-6" @submit.prevent="update">
          <VRow>
            <VCol cols="6">
              <VTextField
                v-model="name"
                placeholder="Ej: Ley, Resolución, etc."
                label="Nombre del tipo de documento"
                :rules="[requiredValidator]"
              />
            </VCol>

            <VCol cols="6">
              <VSelect
                v-model="state"
                label="Estado"
                :items="[
                  {
                    name: 'Activo',
                    id: 1,
                  },
                  {
                    name: 'Inactivo',
                    id: 2,
                  },
                ]"
                item-title="name"
                item-value="id"
                :rules="[selectValidator]"
              />
            </VCol>

            <VCol cols="12" class="d-flex flex-wrap justify-center gap-4 mt-6">
              <VBtn
                type="submit"
                color="info"
                class="px-8"
                :loading="isLoading"
                :disabled="isLoading"
              >
                <VIcon start icon="ri-refresh-line" />
                <span class="font-weight-bold">{{
                  isLoading ? "Actualizando..." : "Actualizar Tipo de Documento"
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
