<script setup>

const data = ref([]);
const isRolAddDialog = ref(false);
const headers = [
  {
    title: '#',
    key: 'id',
  },
  {
    title: 'Rol',
    key: 'name',
  },
  {
    title: 'Fecha de registro',
    key: 'created_at',
  },
  {
    title: 'Permisos',
    key: 'list_permissions',
  },
  {
    title: 'Acciones',
    key: 'action',
  },
]
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12">
        <VCard>
          <VCardTitle>
            🔏 Roles y Permisos
          </VCardTitle>
          <VCardText>
            <VRow class="justify-space-between">
              <VCol cols="3">
                <VTextField
                  placeholder="Buscar Rol"
                  density="compact"
                  class="me-3"
                />
              </VCol>
              <VCol cols="2" class="text-end">
                <VBtn color="info" @click="isRolAddDialog = !isRolAddDialog">
                  Agregar Rol
                  <VIcon
                    end
                    icon="ri-add-circle-fill"
                  />
                </VBtn>
              </VCol>

              <!-- 👉 Modal Add -->
              <RolAddDialog
                v-model:isDialogVisible="isRolAddDialog"
              />
            </VRow> 
          </VCardText>
          <VDataTable
            :headers="headers"
            :items="data"
            :items-per-page="5"
            class="text-no-wrap"
          >
            <template #item.id="{ item }">
              <span class="text-h6">{{ item.id }}</span>
            </template>
          </VDataTable>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>
