<script setup>

const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits([
  'update:isDialogVisible',
  'addRole',
])

const name = ref(null);
const permissions = ref([]);
const isLoading = ref(false);
const toast = useMaterializeToast()

const AddEditPermission = (permission) => {
  if (permissions.value.includes(permission)) {
    permissions.value = permissions.value.filter((item) => item !== permission);
  } else {
    permissions.value.push(permission);
  }
};

const store = async() => {
  if(!name.value){
    toast.showWarning(
      'Debe ingresar un nombre',
      'Error'
    );
    return;
  }

  if(permissions.value.length == 0){
    toast.showWarning(
      'Debe ingresar al menos un permiso',
      'Error'
    );
    return;
  }

  let data = {
    name: name.value,
    permissions: permissions.value,
  }

  try {
    isLoading.value = true;
    
    const response = await $api("/role", {
      method: "POST",
      body: data,
      onResponse({ response }){
        if(response.status === 200){
          toast.showSuccess(
            response._data.message || 'Rol guardado correctamente',
            'Éxito'
          );
          
          // Resetear formulario
          name.value = null;
          permissions.value = [];
          
          // Cerrar diálogo
          emit('update:isDialogVisible', false);
          
          // Emitir evento de actualización
          emit('addRole', response._data.role);
        } 
        else {
          toast.showError(
            response._data.message || 'Error al guardar el rol',
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

const onFormSubmit = () => {
  emit('update:isDialogVisible', false)
  emit('submit', userData.value)
}

const onFormReset = () => {
  emit('update:isDialogVisible', false)
}

const dialogVisibleUpdate = val => {
  emit('update:isDialogVisible', val)
}
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 700 "
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard class="pa-sm-11 pa-3">
      <!-- 👉 dialog close btn -->
      <DialogCloseBtn
        variant="text"
        size="default"
        @click="onFormReset"
      />

      <VCardText class="pt-5">
        <!-- 👉 Header mejorado -->
        <div class="text-center pb-8">
          <VIcon 
            icon="ri-folder-add-line" 
            size="48" 
            color="primary"
            class="mb-3"
          />
          <h4 class="text-h4 font-weight-bold mb-2">
            Agregar Nuevo Rol
          </h4>
          <p class="text-body-2 text-medium-emphasis">
            Configura los permisos para el nuevo rol del sistema
          </p>
        </div>

        <!-- 👉 Form -->
        <VForm
          class="mt-6"
          @submit.prevent="store"
        >
          <VRow>
            <!-- 👉 campo Name -->
            <VCol cols="12">
              <VTextField
                v-model="name"
                density="comfortable"
                placeholder="Ej: Administrador, Editor, Usuario"
                variant="outlined"
                persistent-placeholder
                label="Nombre del Rol"
              />
            </VCol>

            <!-- 👉 Sección de Permisos -->
            <VCol cols="12" class="mt-4">
              <div class="mb-4">
                <h6 class="text-h6 font-weight-bold mb-1">
                  Permisos del Rol <span class="text-error">*</span>
                </h6>
                <p class="text-body-2 text-medium-emphasis">
                  Selecciona los permisos que tendrá este rol
                </p>
              </div>

              <VCard variant="outlined" class="overflow-hidden">
                <VTable class="permissions-table">
                  <thead>
                    <tr class="bg-grey-lighten-4">
                      <th class="text-uppercase font-weight-bold text-body-2 pa-4" style="width: 30%;">
                        Módulo
                      </th>
                      <th class="text-uppercase font-weight-bold text-body-2 pa-4">
                        Permisos Disponibles
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    <tr
                      v-for="(item,index) in PERMISOS"
                      :key="index"
                      class="permission-row"
                    >
                      <td class="pa-4 align-start">
                        <div class="d-flex align-center">
                          <VIcon 
                            icon="ri-folder-line" 
                            size="20" 
                            class="me-2 text-primary"
                          />
                          <span class="font-weight-semibold text-body-1">
                            {{ item.name }}
                          </span>
                        </div>
                      </td>
                      <td class="pa-4">
                        <div class="d-flex flex-wrap gap-2">
                          <VCheckbox
                            v-for="(permiso,index2) in item.permisos"
                            :key="index2"
                            :label="permiso.name"
                            :value="permiso.permiso"
                            density="compact"
                            hide-details
                            color="primary"
                            @click="AddEditPermission(permiso.permiso)"
                          />
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </VTable>
              </VCard>
            </VCol>
            
            <!-- 👉 Submit and Cancel -->
            <VCol
              cols="12"
              class="d-flex flex-wrap justify-center gap-4 mt-6"
            >
              <VBtn 
                type="submit" 
                color="success"
                class="px-8"
                :loading="isLoading"
                :disabled="isLoading"
              >
                <VIcon start icon="ri-save-3-fill"/>
                <span class="font-weight-bold">{{ isLoading ? 'Guardando...' : 'Guardar Rol' }}</span>
              </VBtn>

              <VBtn 
                color="secondary"
                class="px-8"
                @click="onFormReset"
              >
                <VIcon start icon="ri-arrow-left-line"/>
                <span class="font-weight-bold">Cancelar</span>
              </VBtn>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>
  </VDialog>
</template>

<style scoped>
.permissions-table tbody tr.permission-row {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.permissions-table tbody tr.permission-row:last-child {
  border-bottom: none;
}

.permissions-table tbody tr.permission-row:hover {
  background-color: rgba(0, 0, 0, 0.02);
}
</style>