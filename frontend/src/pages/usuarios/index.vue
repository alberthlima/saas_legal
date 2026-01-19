<script setup>
    const headers = [
    {
      title: 'ID',
      key: 'id',
    },
    {
      title: 'Nombre  Completo',
      key: 'full_name',
    },
    {
      title: 'Email',
      key: 'email',
    },
    {
      title: 'Rol',
      key: 'role',
    },
    {
      title: 'Fecha de registro',
      key: 'created_at',
    },
    {
      title: 'Estado',
      key: 'state',
    },
    {
      title: 'Acciones',
      key: 'action',
    },
  ]

  const isUserAddDialog = ref(false);
  const isUserEditDialog = ref(false);
  const isUserDeleteDialog = ref(false);
  const isLoading = ref(false);
  const list_users = ref([]);
  const list_roles = ref([]);
  const buscar = ref('');
  const user_edit = ref(null);
  const user_delete = ref(null);

  const list = async () => {
    try {
      isLoading.value = true;
      
      const response = await $api("/user?search=" + (buscar.value ? buscar.value : ''), {
        method: "GET",
        onResponseError({ response }) {
          console.log(response._data.error);
        },
      })
      list_users.value = response.users;
    } catch (error) {
      console.log(error);
    } finally {
      isLoading.value = false;
    }
  }

  const getRoles = async () => {
    try {
      
      const response = await $api("/user/get-roles", {
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
    isUserEditDialog.value = true;
    user_edit.value = item;
  }

  const deleteItem = (item) => {
    isUserDeleteDialog.value = true;
    user_delete.value = item;
  }

  onMounted(() => {
    list();
    getRoles();
  })
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12">
        <VCard>
          <VCardTitle>
            <VIcon 
              icon="ri-group-line" 
              size="20" 
              class="me-2 text-primary"
            /> 
            Gestion de Usuarios
          </VCardTitle>
          <VCardText>
            <VRow class="justify-space-between">
              <VCol cols="3">
                <VTextField
                  placeholder="Buscar Usuario"
                  density="compact"
                  class="me-3"
                  prepend-inner-icon="ri-search-line"
                  v-model="buscar"
                  @keyup.enter="list()"
                />
              </VCol>
              <VCol cols="2" class="text-end">
                <VBtn color="success" @click="isUserAddDialog = !isUserAddDialog">
                  <VIcon
                    end
                    icon="ri-add-circle-fill"
                  />
                  Agregar Usuario
                </VBtn>
              </VCol>
            </VRow> 
          </VCardText>
          <VDataTable
            :headers="headers"
            :items="list_users"
            :items-per-page="5"
            :loading="isLoading"
            loading-text="Cargando usuarios..."
            no-data-text="No hay usuarios registrados"
            class="text-no-wrap"
            :items-per-page-text="'Usuarios por página:'"
            :page-text="'{0}-{1} de {2}'"
            :items-per-page-options="[
              { value: 5, title: '5' },
              { value: 10, title: '10' },
              { value: 25, title: '25' },
              { value: 50, title: '50' },
              { value: -1, title: 'Todo' }
            ]"
          >
            <template #item.id="{ item }">
              <span class="text-h6">{{ item.id }}</span>
            </template>
            <template #item.role="{ item }">
              <span class="text-h6">{{ item.role.name }}</span>
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
        <!-- 👉 Modal Add -->
        <UserAddDialog
          v-model:isDialogVisible="isUserAddDialog"
          :roles="list_roles"
          @addUser="list()"
        />

        <!-- 👉 Modal Edit -->
        <UserEditDialog
          v-if="user_edit && isUserEditDialog"
          v-model:isDialogVisible="isUserEditDialog"
          :userSelected="user_edit"
          @editUser="list()"
        />

        <!-- 👉 Modal Delete -->
        <UserDeleteDialog
          v-if="user_delete && isUserDeleteDialog"
          v-model:isDialogVisible="isUserDeleteDialog"
          :userSelected="user_delete"
          @deleteUser="list()"
        />
      </VCol>
    </VRow>
  </div>
</template>
