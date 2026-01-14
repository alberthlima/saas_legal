<script setup>

const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  roleSelected: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits([
  'update:isDialogVisible',
  'deleteRole',
])

const isLoading = ref(false);
const toast = useMaterializeToast();

const deleteRole = async() => {
  try {
    isLoading.value = true;
    
    const response = await $api("/role/" + props.roleSelected.id, {
      method: "DELETE",
      onResponse({ response }) {
        if (response.status === 200) {
          toast.showSuccess(
            response._data.message || 'Rol eliminado correctamente',
            'Éxito'
          );
          
          // Cerrar diálogo
          emit('update:isDialogVisible', false);
          
          // Emitir evento de eliminación
          emit('deleteRole', props.roleSelected.id);
        } 
        else {
          toast.showError(
            response._data.message || 'Error al eliminar el rol',
            'Error'
          );
        }
      }
    })
  } catch (error) {
    toast.showError(
      'Error al conectar con el servidor',
      'Error'
    );
  } finally {
    isLoading.value = false;
  }
}

const onFormReset = () => {
  emit('update:isDialogVisible', false);
}

const dialogVisibleUpdate = val => {
  emit('update:isDialogVisible', val);
}
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 500 "
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard class="pa-sm-8 pa-4">
      <!-- 👉 dialog close btn -->
      <DialogCloseBtn
        variant="text"
        size="default"
        @click="onFormReset"
      />

      <VCardText class="pt-5">
        <!-- 👉 Header de confirmación -->
        <div class="text-center pb-6">
          <VIcon 
            icon="ri-delete-bin-line" 
            size="64" 
            color="error"
            class="mb-4"
          />
          <h4 class="text-h4 font-weight-bold mb-3">
            ¿Eliminar Rol {{ props.roleSelected.name }}?
          </h4>
          <p class="text-body-1 text-medium-emphasis">
            Esta acción no se puede deshacer. ¿Estás seguro de que deseas eliminar este rol?
          </p>
        </div>

        <!-- 👉 Botones de acción -->
        <VRow class="justify-center mt-4">
          <VCol cols="12" class="d-flex gap-3 justify-center">
            <VBtn 
              color="error"
              class="px-8"
              :loading="isLoading"
              :disabled="isLoading"
              @click="deleteRole"
            >
              <VIcon start icon="ri-delete-bin-line"/>
              <span class="font-weight-bold">{{ isLoading ? 'Eliminando...' : 'Sí, Eliminar' }}</span>
            </VBtn>

            <VBtn 
              color="secondary"
              class="px-8"
              :disabled="isLoading"
              @click="onFormReset"
            >
              <VIcon start icon="ri-arrow-left-line"/>
              <span class="font-weight-bold">Cancelar</span>
            </VBtn>
          </VCol>
        </VRow>
      </VCardText>
    </VCard>
  </VDialog>
</template>