<script setup>
//definicion de variables
const isMembershipAddDialog = ref(false);
const isMembershipEditDialog = ref(false);
const isMembershipDeleteDialog = ref(false);
const isLoading = ref(false);
const list_memberships = ref([]);
const buscar = ref("");
const membership_edit = ref(null);
const membership_delete = ref(null);
const headers = [
  {
    title: "ID",
    key: "id",
  },
  {
    title: "Membresía",
    key: "name",
  },
  {
    title: "Descripción",
    key: "description",
    width: "400px",
  },
  {
    title: "Precio",
    key: "price",
  },
  {
    title: "Limite Diario",
    key: "daily_limit",
  },
  {
    title: "Limite de Categorías",
    key: "max_specialists",
  },
  {
    title: "Fecha de registro",
    key: "created_at",
  },
  {
    title: "Estado",
    key: "state",
  },
  {
    title: "Acciones",
    key: "action",
  },
];

const list = async () => {
  try {
    isLoading.value = true;

    const response = await $api(
      "/membership?search=" + (buscar.value ? buscar.value : ""),
      {
        method: "GET",
        onResponseError({ response }) {
          console.log(response._data.error);
        },
      },
    );
    list_memberships.value = response.memberships;
  } catch (error) {
    console.log(error);
  } finally {
    isLoading.value = false;
  }
};

const clearSearch = () => {
  buscar.value = "";
  list();
};

const editItem = (item) => {
  isMembershipEditDialog.value = true;
  membership_edit.value = item;
};

const deleteItem = (item) => {
  isMembershipDeleteDialog.value = true;
  membership_delete.value = item;
};

onMounted(() => {
  list();
});

definePage({
  meta: {
    permission: "listar_membresia",
  },
});
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12">
        <VCard>
          <VCardTitle>
            <VIcon icon="ri-vip-line" size="20" class="me-2 text-primary" />
            Membresías
          </VCardTitle>
          <VCardText>
            <VRow class="justify-space-between">
              <VCol cols="3">
                <VTextField
                  placeholder="Buscar Membresía"
                  density="compact"
                  class="me-3"
                  prepend-inner-icon="ri-search-line"
                  v-model="buscar"
                  clearable
                  @keyup.enter="list()"
                  @click:clear="clearSearch"
                />
              </VCol>
              <VCol cols="2" class="text-end">
                <VBtn
                  color="success"
                  @click="isMembershipAddDialog = !isMembershipAddDialog"
                >
                  <VIcon end icon="ri-add-circle-fill" />
                  Agregar Membresía
                </VBtn>
              </VCol>

              <!-- 👉 Modal Add -->
              <MembershipAddDialog
                v-model:isDialogVisible="isMembershipAddDialog"
                @addMembership="list()"
              />

              <!-- 👉 Modal Edit -->
              <MembershipEditDialog
                v-if="membership_edit && isMembershipEditDialog"
                v-model:isDialogVisible="isMembershipEditDialog"
                :membershipSelected="membership_edit"
                @editMembership="list()"
              />

              <!-- 👉 Modal Delete -->
              <MembershipDeleteDialog
                v-if="membership_delete && isMembershipDeleteDialog"
                v-model:isDialogVisible="isMembershipDeleteDialog"
                :membershipSelected="membership_delete"
                @deleteMembership="list()"
              />
            </VRow>
          </VCardText>
          <VDataTable
            :headers="headers"
            :items="list_memberships"
            :items-per-page="5"
            :loading="isLoading"
            loading-text="Cargando membresías..."
            no-data-text="No hay membresías registrados"
            class="text-no-wrap"
            :items-per-page-text="'Registros por página:'"
            :page-text="'{0}-{1} de {2}'"
            :items-per-page-options="[
              { value: 5, title: '5' },
              { value: 10, title: '10' },
              { value: 25, title: '25' },
              { value: 50, title: '50' },
              { value: -1, title: 'Todo' },
            ]"
          >
            <template #item.id="{ item }">
              <span class="text-h6">{{ item.id }}</span>
            </template>
            <template #item.description="{ item }">
              <div class="text-wrap" style="width: 400px">
                {{ item.description }}
              </div>
            </template>
            <template #item.state="{ item }">
              <VChip
                :color="item.state === 1 ? 'success' : 'error'"
                size="small"
                class="text-capitalize"
              >
                {{ item.state === 1 ? "Activo" : "Inactivo" }}
              </VChip>
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
                  <VIcon icon="ri-pencil-line" size="25" />
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
