<script setup>
const headers = [
  {
    title: "ID",
    key: "id",
  },
  {
    title: "Nombre Completo",
    key: "name",
  },
  {
    title: "CI",
    key: "ci",
  },
  {
    title: "Telefono",
    key: "phone",
  },
  {
    title: "Ciudad",
    key: "city",
  },
  {
    title: "Tipo de Cliente",
    key: "client_type",
  },
  {
    title: "Fecha de registro",
    key: "created_at",
  },
  {
    title: "Estado",
    key: "state",
  },
];

const isLoading = ref(false);
const list_clients = ref([]);
const buscar = ref("");

const clearSearch = () => {
  buscar.value = "";
  list();
};

const list = async () => {
  try {
    isLoading.value = true;

    const response = await $api(
      "/client?search=" + (buscar.value ? buscar.value : ""),
      {
        method: "GET",
        onResponseError({ response }) {
          console.log(response._data.error);
        },
      },
    );
    list_clients.value = response.data;
  } catch (error) {
    console.log(error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  list();
});

definePage({
  meta: {
    permission: "clientes",
  },
});
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12">
        <VCard>
          <VCardTitle>
            <VIcon icon="ri-group-line" size="20" class="me-2 text-primary" />
            Lista de Clientes
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
                  clearable
                  @keyup.enter="list()"
                  @click:clear="clearSearch"
                />
              </VCol>
            </VRow>
          </VCardText>
          <VDataTable
            :headers="headers"
            :items="list_clients"
            :items-per-page="5"
            :loading="isLoading"
            loading-text="Cargando clientes..."
            no-data-text="No hay clientes registrados"
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
                :color="item.state === 'Activo' ? 'success' : 'error'"
                size="small"
                class="text-capitalize"
              >
                {{ item.state }}
              </VChip>
            </template>
          </VDataTable>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>
