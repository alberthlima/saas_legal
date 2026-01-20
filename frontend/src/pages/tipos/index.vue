<script setup>
//definicion de variables
const isTypeAddDialog = ref(false);
const isTypeEditDialog = ref(false);
const isTypeDeleteDialog = ref(false);
const isLoading = ref(false);
const list_types = ref([]);
const buscar = ref("");
const type_edit = ref(null);
const type_delete = ref(null);
const headers = [
  {
    title: "ID",
    key: "id",
  },
  {
    title: "Tipo de documento",
    key: "name",
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
      "/type?search=" + (buscar.value ? buscar.value : ""),
      {
        method: "GET",
        onResponseError({ response }) {
          console.log(response._data.error);
        },
      },
    );
    list_types.value = response.types;
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
  isTypeEditDialog.value = true;
  type_edit.value = item;
};

const deleteItem = (item) => {
  isTypeDeleteDialog.value = true;
  type_delete.value = item;
};

onMounted(() => {
  list();
});

definePage({
  meta: {
    permission: "listar_tipo_documento",
  },
});
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12">
        <VCard>
          <VCardTitle>
            <VIcon
              icon="ri-file-search-line"
              size="20"
              class="me-2 text-primary"
            />
            Tipos de documentos
          </VCardTitle>
          <VCardText>
            <VRow class="justify-space-between">
              <VCol cols="3">
                <VTextField
                  placeholder="Buscar tipo de documento"
                  density="compact"
                  class="me-3"
                  prepend-inner-icon="ri-search-line"
                  v-model="buscar"
                  clearable
                  @keyup.enter="list()"
                  @click:clear="clearSearch"
                />
              </VCol>
              <VCol cols="3" class="text-end">
                <VBtn
                  color="success"
                  @click="isTypeAddDialog = !isTypeAddDialog"
                >
                  <VIcon end icon="ri-add-circle-fill" />
                  Agregar Tipo de documento
                </VBtn>
              </VCol>

              <!-- 👉 Modal Add -->
              <TypeAddDialog
                v-model:isDialogVisible="isTypeAddDialog"
                @addType="list()"
              />

              <!-- 👉 Modal Edit -->
              <TypeEditDialog
                v-if="type_edit && isTypeEditDialog"
                v-model:isDialogVisible="isTypeEditDialog"
                :typeSelected="type_edit"
                @editType="list()"
              />

              <!-- 👉 Modal Delete -->
              <TypeDeleteDialog
                v-if="type_delete && isTypeDeleteDialog"
                v-model:isDialogVisible="isTypeDeleteDialog"
                :typeSelected="type_delete"
                @deleteType="list()"
              />
            </VRow>
          </VCardText>
          <VDataTable
            :headers="headers"
            :items="list_types"
            :items-per-page="5"
            :loading="isLoading"
            loading-text="Cargando tipos de documentos..."
            no-data-text="No hay tipos de documentos registrados"
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
