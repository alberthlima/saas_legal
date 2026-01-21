<script setup>
const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
});

//definicion de variables
const emit = defineEmits(["update:isDialogVisible", "addMembership"]);
const name = ref(null);
const description = ref(null);
const price = ref(null);
const daily_limit = ref(null);
const max_specialists = ref(null);
const isLoading = ref(false);
const toast = useMaterializeToast();

const store = async () => {
  let data = {
    name: name.value,
    description: description.value,
    price: price.value,
    daily_limit: daily_limit.value,
    max_specialists: max_specialists.value,
    state: 1,
  };

  try {
    isLoading.value = true;

    const response = await $api("/membership", {
      method: "POST",
      body: data,
      onResponse({ response }) {
        if (response.status === 200) {
          toast.showSuccess(
            response._data.message || "Membresía guardada correctamente",
            "Éxito",
          );

          // Resetear formulario
          name.value = null;
          description.value = null;
          price.value = null;
          daily_limit.value = null;
          max_specialists.value = null;

          // Cerrar diálogo
          emit("update:isDialogVisible", false);

          // Emitir evento de actualización
          emit("addMembership", response._data.membership);
        } else {
          toast.showError(
            response._data.message || "Error al guardar la membresía",
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
    :width="$vuetify.display.smAndDown ? 'auto' : 750"
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
            icon="ri-vip-crown-line"
            size="48"
            color="primary"
            class="mb-3"
          />
          <h4 class="text-h4 font-weight-bold mb-2">Agregar Nueva Membresía</h4>
        </div>

        <!-- 👉 Form -->
        <VForm class="mt-6" @submit.prevent="store">
          <VRow>
            <!-- 👉 campo Name -->
            <VCol cols="12" md="6">
              <VTextField
                v-model="name"
                placeholder="Ej: Plan Estudiante"
                label="Nombre de la Membresía"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 campo Precio -->
            <VCol cols="12" md="6">
              <VTextField
                v-model="price"
                label="Precio Mensual"
                placeholder="50"
                type="number"
                prefix="Bs."
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 Limite Diario -->
            <VCol cols="12" md="6">
              <VTextField
                v-model="daily_limit"
                label="Límite Diario de Consultas"
                placeholder="Ej: 20"
                type="number"
                :rules="[requiredValidator]"
                hint="Consultas permitidas cada 24 horas"
                persistent-hint
              />
            </VCol>

            <!-- 👉 Max Especialistas -->
            <VCol cols="12" md="6">
              <VTextField
                v-model="max_specialists"
                label="Máximo de Categorías"
                placeholder="Ej: 2"
                type="number"
                :rules="[requiredValidator]"
                hint="Cuántas ramas del derecho puede elegir"
                persistent-hint
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
                  isLoading ? "Guardando..." : "Guardar Membresía"
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
