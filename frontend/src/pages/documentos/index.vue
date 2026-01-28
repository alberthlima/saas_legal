<script setup>
import DocumentoAddDialog from "@/components/system/documento/DocumentoAddDialog.vue";
import DocumentoEditDialog from "@/components/system/documento/DocumentoEditDialog.vue";
import DocumentoDeleteDialog from "@/components/system/documento/DocumentoDeleteDialog.vue";

// Definición de variables
const isDocumentAddDialog = ref(false);
const isDocumentEditDialog = ref(false);
const isDocumentDeleteDialog = ref(false);
const isLoading = ref(false);
const list_documents = ref([]);
const list_categories = ref([]);
const buscar = ref("");
const document_edit = ref(null);
const document_delete = ref(null);

const headers = [
  { title: "ID", key: "id" },
  { title: "Documento", key: "name" },
  { title: "Tipo de Documento", key: "type_document" },
  { title: "Categorías", key: "categories" },
  { title: "Estado", key: "status" },
  { title: "Acciones", key: "action", sortable: false },
];

const loadInitialData = async () => {
  try {
    const res = await $api("/category", { method: "GET" });
    list_categories.value = res.categories;
  } catch (error) {
    console.error("Error cargando categorías:", error);
  }
};

const list = async () => {
  try {
    isLoading.value = true;

    const response = await $api(
      "/document?search=" + (buscar.value ? buscar.value : ""),
      {
        method: "GET",
        onResponseError({ response }) {
          console.log(response._data.error);
        },
      },
    );
    list_documents.value = response.documents;
  } catch (error) {
    console.log(error);
  } finally {
    isLoading.value = false;
  }
};

const getCategoryNames = (ids) => {
  if (!ids || !Array.isArray(ids)) return "";
  return ids
    .map((id) => list_categories.value.find((c) => c.id === id)?.name)
    .filter((name) => name)
    .join(", ");
};

const clearSearch = () => {
  buscar.value = "";
  list();
};

const editItem = (item) => {
  document_edit.value = item;
  isDocumentEditDialog.value = true;
};

const deleteItem = (item) => {
  document_delete.value = item;
  isDocumentDeleteDialog.value = true;
};

onMounted(() => {
  loadInitialData();
  list();
});

definePage({
  meta: {
    permission: "listar_documento", // Asegúrate de que este permiso exista
  },
});
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12">
        <VCard>
          <VCardTitle class="d-flex align-center">
            <VIcon
              icon="ri-book-read-line"
              size="24"
              class="me-2 text-primary"
            />
            Biblioteca de Documentos
          </VCardTitle>

          <VCardText>
            <VRow class="justify-space-between align-center">
              <VCol cols="12" md="4">
                <VTextField
                  v-model="buscar"
                  placeholder="Buscar documento..."
                  density="compact"
                  prepend-inner-icon="ri-search-line"
                  clearable
                  @keyup.enter="list()"
                  @click:clear="clearSearch"
                />
              </VCol>
              <VCol cols="12" md="auto" class="text-end">
                <VBtn color="success" @click="isDocumentAddDialog = true">
                  <VIcon start icon="ri-add-circle-line" />
                  Nuevo Documento
                </VBtn>
              </VCol>

              <!-- 👉 Modales -->
              <DocumentoAddDialog
                v-model:isDialogVisible="isDocumentAddDialog"
                @addDocument="list()"
              />

              <DocumentoEditDialog
                v-if="document_edit && isDocumentEditDialog"
                v-model:isDialogVisible="isDocumentEditDialog"
                :documentSelected="document_edit"
                @editDocument="list()"
              />

              <DocumentoDeleteDialog
                v-if="document_delete && isDocumentDeleteDialog"
                v-model:isDialogVisible="isDocumentDeleteDialog"
                :documentSelected="document_delete"
                @deleteDocument="list()"
              />
            </VRow>
          </VCardText>

          <VDataTable
            :headers="headers"
            :items="list_documents"
            :loading="isLoading"
            loading-text="Cargando categorias..."
            no-data-text="No hay categorias registrados"
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
            <!-- Tipo de Documento -->
            <template #item.type_document="{ item }">
              {{ item.type_document?.name || "N/A" }}
            </template>

            <!-- Categorías -->
            <template #item.categories="{ item }">
              <div class="text-wrap" style="max-width: 300px">
                <div v-if="list_categories.length > 0">
                  <ol class="ps-4">
                    <li
                      v-for="catId in item.category_ids"
                      :key="catId"
                      class="text-caption"
                    >
                      <span class="font-weight-bold">
                        {{
                          list_categories.find((c) => c.id == catId)?.name ||
                          "Cat. " + catId
                        }}
                      </span>
                    </li>
                  </ol>
                </div>
                <div v-else>
                  <VProgressCircular indeterminate size="20" width="2" />
                </div>
              </div>
            </template>

            <!-- Estado -->
            <template #item.status="{ item }">
              <VChip
                :color="item.status === 'active' ? 'success' : 'error'"
                size="small"
                variant="tonal"
                class="text-capitalize"
              >
                {{ item.status === "active" ? "Activo" : "Inactivo" }}
              </VChip>
            </template>

            <!-- Acciones -->
            <template #item.action="{ item }">
              <div class="d-flex gap-2">
                <IconBtn
                  size="small"
                  color="primary"
                  variant="tonal"
                  title="Descargar PDF"
                  :href="item.path"
                  target="_blank"
                >
                  <VIcon icon="ri-download-2-line" />
                </IconBtn>

                <IconBtn
                  size="small"
                  color="info"
                  variant="tonal"
                  @click="editItem(item)"
                >
                  <VIcon icon="ri-pencil-line" />
                </IconBtn>

                <IconBtn
                  size="small"
                  color="error"
                  variant="tonal"
                  @click="deleteItem(item)"
                >
                  <VIcon icon="ri-delete-bin-line" />
                </IconBtn>
              </div>
            </template>
          </VDataTable>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>
