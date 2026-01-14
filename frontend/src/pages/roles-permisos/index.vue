<script setup>
  const data = ref([]);
  const isRolAddDialog = ref(false);
  const isRolEditDialog = ref(false);
  const isRolDeleteDialog = ref(false);
  const list_roles = ref([]);
  const buscar = ref('');
  const role_edit = ref(null);
  const role_delete = ref(null);
  const headers = [
    {
      title: 'ID',
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
      key: 'permissions_pluck',
    },
    {
      title: 'Acciones',
      key: 'action',
    },
  ]

  const list = async () => {
    try {
      const response = await $api("/role?search=" + (buscar.value ? buscar.value : ''), {
        method: "GET",
        onResponseError({ response }) {
          console.log(response._data.error);
        },
      })
      console.log(response);
      list_roles.value = response.roles;
    } catch (error) {
      console.log(error);
    }
  }

  const editItem = (item) => {
    isRolEditDialog.value = true;
    role_edit.value = item;
  }

  const deleteItem = (item) => {
    isRolDeleteDialog.value = true;
    role_delete.value = item;
  }

  onMounted(() => {
    list();
  })
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12">
        <VCard>
          <VCardTitle>
            <VIcon 
              icon="ri-folder-lock-line" 
              size="20" 
              class="me-2 text-primary"
            /> 
            Roles y Permisos
          </VCardTitle>
          <VCardText>
            <VRow class="justify-space-between">
              <VCol cols="3">
                <VTextField
                  placeholder="Buscar Rol"
                  density="compact"
                  class="me-3"
                  prepend-inner-icon="ri-search-line"
                  v-model="buscar"
                  @keyup.enter="list()"
                />
              </VCol>
              <VCol cols="2" class="text-end">
                <VBtn color="success" @click="isRolAddDialog = !isRolAddDialog">
                  <VIcon
                    end
                    icon="ri-add-circle-fill"
                  />
                  Agregar Rol
                </VBtn>
              </VCol>

              <!-- 👉 Modal Add -->
              <RolAddDialog
                v-model:isDialogVisible="isRolAddDialog"
                @addRole="list()"
              />

              <!-- 👉 Modal Edit -->
              <RolEditDialog
                v-if="role_edit && isRolEditDialog"
                v-model:isDialogVisible="isRolEditDialog"
                :roleSelected="role_edit"
                @editRole="list()"
              />

              <!-- 👉 Modal Delete -->
              <RolDeleteDialog
                v-if="role_delete && isRolDeleteDialog"
                v-model:isDialogVisible="isRolDeleteDialog"
                :roleSelected="role_delete"
                @deleteRole="list()"
              />
            </VRow> 
          </VCardText>
          <VDataTable
            :headers="headers"
            :items="list_roles"
            :items-per-page="5"
            class="text-no-wrap"
          >
            <template #item.id="{ item }">
              <span class="text-h6">{{ item.id }}</span>
            </template>
            <template #item.permissions_pluck="{ item }">
              <ul>
                <li v-for="(permission, index) in item.permissions_pluck" :key="index">
                  {{ permission }}
                </li>
              </ul>
            </template>
            <!-- Actions -->
            <template #item.action="{ item }">
              <div class="d-flex gap-1">
                <IconBtn
                  size="small"
                  color="info"
                  variant="tonal"
                  @click="editItem(item)"
                >
                  <VIcon icon="ri-pencil-line"  size="25" />
                </IconBtn>
                <IconBtn
                  size="small"
                  color="error"
                  variant="tonal"
                  @click="deleteItem(item)"
                >
                  <VIcon icon="ri-delete-bin-line" size="25" />
                </IconBtn>
              </div>
            </template>
          </VDataTable>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>
