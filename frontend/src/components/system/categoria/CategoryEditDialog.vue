<script setup>
import { requiredValidator, selectValidator } from "@/utils/validators";

const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  categorySelected: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:isDialogVisible", "editCategory"]);

const id = ref(null);
const name = ref(null);
const description = ref(null);
const state = ref(null);
const isLoading = ref(false);
const toast = useMaterializeToast();

const update = async () => {
  let data = {
    name: name.value,
    description: description.value,
    state: state.value,
  };

  try {
    isLoading.value = true;

    const response = await $api("/category/" + props.categorySelected.id, {
      method: "PUT",
      body: data,
      onResponse({ response }) {
        console.log(response);
        if (response.status === 200) {
          toast.showSuccess(
            response._data.message || "Categoria actualizada correctamente",
            "Éxito",
          );
          // Resetear formulario
          name.value = null;
          description.value = null;
          state.value = null;

          // Cerrar diálogo
          emit("update:isDialogVisible", false);

          // Emitir evento de actualización
          emit("editCategory", response._data.category);
        } else {
          toast.showError(
            response._data.message || "Error al actualizar la categoria",
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
  id.value = props.categorySelected.id;
  name.value = props.categorySelected.name;
  description.value = props.categorySelected.description;
  state.value = props.categorySelected.state;
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
            icon="ri-folder-info-line"
            size="48"
            color="primary"
            class="mb-3"
          />
          <h4 class="text-h4 font-weight-bold mb-2">
            Editar Categoria: {{ categorySelected.name }}
          </h4>
        </div>

        <VForm class="mt-6" @submit.prevent="update">
          <VRow>
            <VCol cols="6">
              <VTextField
                v-model="name"
                placeholder="Ej: Derecho Penal"
                label="Nombre de la categoría"
                :rules="[requiredValidator]"
              />
            </VCol>

            <VCol cols="6">
              <VTextarea
                v-model="description"
                label="Descripción de la Categoría"
                placeholder="Descripción de la Categoría"
                auto-grow
                :counter="255"
                maxlength="255"
                :rules="[requiredValidator]"
              />
            </VCol>

            <VCol cols="12">
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
                  isLoading ? "Actualizando..." : "Actualizar Categoria"
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
