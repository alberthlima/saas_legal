<script setup>
const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  membershipSelected: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:isDialogVisible", "editMembership"]);

const id = ref(null);
const name = ref(null);
const description = ref(null);
const price = ref(null);
const daily_limit = ref(null);
const max_specialists = ref(null);
const state = ref(null);
const isLoading = ref(false);
const toast = useMaterializeToast();

const update = async () => {
  let data = {
    name: name.value,
    description: description.value,
    price: price.value,
    daily_limit: daily_limit.value,
    max_specialists: max_specialists.value,
    state: state.value,
  };

  try {
    isLoading.value = true;

    const response = await $api("/membership/" + props.membershipSelected.id, {
      method: "PUT",
      body: data,
      onResponse({ response }) {
        if (response.status === 200) {
          toast.showSuccess(
            response._data.message || "Membresía actualizada correctamente",
            "Éxito",
          );

          // Cerrar diálogo
          emit("update:isDialogVisible", false);

          // Emitir evento de actualización
          emit("editMembership", response._data.membership);
        } else {
          toast.showError(
            response._data.message || "Error al actualizar la membresía",
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
  id.value = props.membershipSelected.id;
  name.value = props.membershipSelected.name;
  description.value = props.membershipSelected.description;
  price.value = props.membershipSelected.price;
  daily_limit.value = props.membershipSelected.daily_limit;
  max_specialists.value = props.membershipSelected.max_specialists;
  state.value = props.membershipSelected.state;
});
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 750"
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard class="pa-sm-11 pa-3">
      <DialogCloseBtn variant="text" size="default" @click="onFormReset" />

      <VCardText class="pt-5">
        <div class="text-center pb-8">
          <VIcon icon="ri-edit-2-line" size="48" color="primary" class="mb-3" />
          <h4 class="text-h4 font-weight-bold mb-2">
            Editar Membresía: {{ membershipSelected.name }}
          </h4>
        </div>

        <VForm class="mt-6" @submit.prevent="update">
          <VRow>
            <!-- 👉 campo Name -->
            <VCol cols="12" md="6">
              <VTextField
                v-model="name"
                placeholder="Ej: Plan Extudiante"
                label="Nombre de la Membresía"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 campo Precio -->
            <VCol cols="12" md="6">
              <VTextField
                v-model="price"
                label="Precio Mensual (Bs)"
                placeholder="0.00"
                type="number"
                prefix="Bs"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 Limite Diario -->
            <VCol cols="12" md="6">
              <VTextField
                v-model="daily_limit"
                label="Límite Diario"
                placeholder="Ej: 20"
                type="number"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 Max Especialistas -->
            <VCol cols="12" md="6">
              <VTextField
                v-model="max_specialists"
                label="Máximo Especialidades"
                placeholder="Ej: 2"
                type="number"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 Estado -->
            <VCol cols="12">
              <VSelect
                v-model="state"
                label="Estado"
                :items="[
                  { name: 'Activo', id: 1 },
                  { name: 'Inactivo', id: 2 },
                ]"
                item-title="name"
                item-value="id"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 campo de Descripcion -->
            <VCol cols="12">
              <VTextarea
                v-model="description"
                label="Descripción y Beneficios"
                placeholder="Detalla lo que incluye esta membresía..."
                auto-grow
                rows="2"
                :counter="255"
                maxlength="255"
                :rules="[requiredValidator]"
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
                  isLoading ? "Actualizando..." : "Actualizar Membresía"
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
