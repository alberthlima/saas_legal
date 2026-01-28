<script setup>
import { requiredValidator } from "@/utils/validators";

const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  documentSelected: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:isDialogVisible", "editDocument"]);

// Definición de variables
const name = ref(null);
const description = ref(null);
const type_document_id = ref(null);
const category_ids = ref([]);
const file = ref(null);
const status = ref("active");
const isLoading = ref(false);
const list_categories = ref([]);
const list_types = ref([]);
const toast = useMaterializeToast();

// Cargar datos necesarios
const loadData = async () => {
  try {
    const [resCat, resType] = await Promise.all([
      $api("/category", { method: "GET" }),
      $api("/type", { method: "GET" }),
    ]);
    list_categories.value = resCat.categories;
    list_types.value = resType.types;
  } catch (error) {
    console.error("Error cargando datos:", error);
  }
};

const update = async () => {
  // Usar FormData para enviar archivos y arrays (aunque sea PATCH, Laravel prefiere POST con _method=PUT para archivos)
  const formData = new FormData();
  formData.append("_method", "PUT");
  formData.append("name", name.value);
  formData.append("description", description.value || "");
  formData.append("type_document_id", type_document_id.value);
  formData.append("status", status.value);

  const fileToUpload = Array.isArray(file.value) ? file.value[0] : file.value;

  if (fileToUpload) {
    formData.append("file", fileToUpload);
  }

  // Agregar IDs de categorías
  category_ids.value.forEach((id) => {
    formData.append("category_ids[]", id);
  });

  try {
    isLoading.value = true;

    const response = await $api(`/document/${props.documentSelected.id}`, {
      method: "POST", // Se usa POST con _method PUT
      body: formData,
    });

    if (response.success) {
      toast.showSuccess(
        response.message || "Documento actualizado correctamente",
        "Éxito",
      );
      emit("update:isDialogVisible", false);
      emit("editDocument");
    } else {
      toast.showError(response.message || "Error al actualizar", "Error");
    }
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

// Inicializar con datos del documento seleccionado
watch(
  () => props.documentSelected,
  (val) => {
    if (val) {
      name.value = val.name;
      description.value = val.description;
      type_document_id.value = val.type_document_id;
      category_ids.value = val.category_ids || [];
      status.value = val.status || "active";
    }
  },
  { immediate: true },
);

onMounted(() => {
  loadData();
});
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 800"
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard class="pa-sm-11 pa-3">
      <DialogCloseBtn variant="text" size="default" @click="onFormReset" />

      <VCardText class="pt-5">
        <div class="text-center pb-8">
          <VIcon
            icon="ri-edit-box-line"
            size="48"
            color="primary"
            class="mb-3"
          />
          <h4 class="text-h4 font-weight-bold mb-2">Editar Documento</h4>
        </div>

        <VForm class="mt-6" @submit.prevent="update">
          <VRow>
            <!-- Nombre -->
            <VCol cols="12" md="6">
              <VTextField
                v-model="name"
                label="Nombre del Documento"
                placeholder="Ej: Código Civil Boliviano"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- Tipo de Documento -->
            <VCol cols="12" md="6">
              <VSelect
                v-model="type_document_id"
                label="Tipo de Documento"
                placeholder="Seleccione un tipo"
                :items="list_types"
                item-title="name"
                item-value="id"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- Categorías (Múltiple) -->
            <VCol cols="12" md="8">
              <VSelect
                v-model="category_ids"
                label="Categorías"
                placeholder="Seleccione categorías"
                :items="list_categories"
                item-title="name"
                item-value="id"
                multiple
                chips
                closable-chips
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- Estado -->
            <VCol cols="12" md="4">
              <VSelect
                v-model="status"
                label="Estado"
                :items="[
                  { title: 'Activo', value: 'active' },
                  { title: 'Inactivo', value: 'inactive' },
                ]"
                item-title="title"
                item-value="value"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- Descripción -->
            <VCol cols="12">
              <VTextarea
                v-model="description"
                label="Descripción / Resumen"
                placeholder="Breve descripción del contenido"
                auto-grow
                rows="2"
              />
            </VCol>

            <!-- Archivo PDF (Opcional en edición) -->
            <VCol cols="12">
              <VFileInput
                v-model="file"
                label="Archivo PDF (Opcional - Reemplazar)"
                placeholder="Seleccione para reemplazar archivo"
                accept="application/pdf"
                prepend-icon="ri-file-pdf-line"
              />
              <div v-if="props.documentSelected.path" class="mt-2 ml-8">
                <a
                  :href="props.documentSelected.path"
                  target="_blank"
                  class="text-primary text-decoration-none d-flex align-center"
                >
                  <VIcon icon="ri-external-link-line" size="16" class="me-1" />
                  Ver archivo actual
                </a>
              </div>
            </VCol>

            <!-- Botones -->
            <VCol cols="12" class="d-flex flex-wrap justify-center gap-4 mt-6">
              <VBtn
                type="submit"
                color="info"
                class="px-8"
                :loading="isLoading"
                :disabled="isLoading"
              >
                <VIcon start icon="ri-save-3-fill" />
                <span class="font-weight-bold">{{
                  isLoading ? "Actualizando..." : "Actualizar Documento"
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
