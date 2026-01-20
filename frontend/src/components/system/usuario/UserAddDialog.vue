<script setup>
// Importar los validadores compartidos
import {
  requiredValidator,
  emailValidator,
  passwordValidator,
  selectValidator,
  optionalImageValidator,
} from "@/utils/validators";

const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  roles: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:isDialogVisible", "addUser"]);

const name = ref(null);
const surname = ref(null);
const email = ref(null);
const password = ref(null);
const role_id = ref(null);
const avatar = ref(null);
const isLoading = ref(false);
const isPasswordVisible = ref(false);
const toast = useMaterializeToast();
const previewUrl = ref(null);

// Función para manejar la selección de imagen
const onImageSelect = (files) => {
  // Limpiar URL anterior si existe
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }

  // VFileInput puede pasar un archivo individual o un array
  const file = Array.isArray(files) ? files[0] : files;

  if (file) {
    // Crear URL para previsualización
    previewUrl.value = URL.createObjectURL(file);
  } else {
    // Limpiar URL si no hay archivo
    previewUrl.value = null;
  }
};

const store = async () => {
  let formData = new FormData();
  formData.append("name", name.value);
  formData.append("surname", surname.value);
  formData.append("email", email.value);
  formData.append("password", password.value);
  formData.append("role_id", role_id.value);
  if (avatar.value) {
    formData.append(
      "imagen",
      Array.isArray(avatar.value) ? avatar.value[0] : avatar.value,
    );
  }
  formData.append("state", 1);

  try {
    isLoading.value = true;

    const response = await $api("/user", {
      method: "POST",
      body: formData,
      onResponse({ response }) {
        if (response.status === 200) {
          toast.showSuccess(
            response._data.message || "Usuario guardado correctamente",
            "Éxito",
          );

          // Resetear formulario
          name.value = null;
          surname.value = null;
          email.value = null;
          password.value = null;
          role_id.value = null;
          avatar.value = null;
          previewUrl.value = null;

          // Cerrar diálogo
          emit("update:isDialogVisible", false);

          // Emitir evento de actualización
          emit("addUser", response._data.user);
        } else {
          toast.showError(
            response._data.message || "Error al guardar el usuario",
            "Error",
          );
        }
      },
    });
  } catch (error) {
    toast.showError("Error al conectar con el servidor", "Error");
  } finally {
    isLoading.value = false;
  }
};

const onFormSubmit = () => {
  emit("update:isDialogVisible", false);
  emit("submit", userData.value);
};

const onFormReset = () => {
  emit("update:isDialogVisible", false);
};

const dialogVisibleUpdate = (val) => {
  emit("update:isDialogVisible", val);
};

// Limpiar URL cuando el componente se destruye
onUnmounted(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
});
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 700"
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard class="pa-sm-11 pa-3">
      <!-- 👉 dialog close btn -->
      <DialogCloseBtn variant="text" size="default" @click="onFormReset" />

      <VCardText class="pt-5">
        <!-- 👉 Header mejorado -->
        <div class="text-center pb-8">
          <VIcon
            icon="ri-user-add-line"
            size="48"
            color="primary"
            class="mb-3"
          />
          <h4 class="text-h4 font-weight-bold mb-2">Agregar Nuevo Usuario</h4>
        </div>

        <!-- 👉 Form -->
        <VForm class="mt-6" @submit.prevent="store">
          <VRow>
            <!-- 👉 campo Name -->
            <VCol cols="6">
              <VTextField
                v-model="name"
                placeholder="Ej: Pepe"
                label="Nombre"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 campo Surname -->
            <VCol cols="6">
              <VTextField
                v-model="surname"
                placeholder="Ej: Perez"
                label="Apellido"
                :rules="[requiredValidator]"
              />
            </VCol>

            <!-- 👉 campo Email -->
            <VCol cols="6">
              <VTextField
                v-model="email"
                placeholder="Ej: pepe@gmail.com"
                label="Correo Electronico"
                :rules="[requiredValidator, emailValidator]"
              />
            </VCol>

            <!-- 👉 campo Password -->
            <VCol cols="6">
              <VTextField
                v-model="password"
                label="Password"
                :type="isPasswordVisible ? 'text' : 'password'"
                :append-inner-icon="
                  isPasswordVisible ? 'ri-eye-off-line' : 'ri-eye-line'
                "
                placeholder="Enter Password"
                :rules="[passwordValidator]"
                autocomplete="on"
                @click:append-inner="isPasswordVisible = !isPasswordVisible"
              />
            </VCol>

            <!-- 👉 campo Role -->
            <VCol cols="12">
              <VSelect
                v-model="role_id"
                label="Rol"
                :items="props.roles"
                item-title="name"
                item-value="id"
                :rules="[selectValidator]"
              />
            </VCol>

            <!-- 👉 campo Avatar -->
            <VCol cols="6">
              <VFileInput
                v-model="avatar"
                label="Avatar"
                accept="image/*"
                :rules="[optionalImageValidator]"
                @update:model-value="onImageSelect"
              />
            </VCol>

            <!-- 👉 campo precisualizar Avatar -->
            <VCol cols="6">
              <div v-if="previewUrl" class="mt-4 text-center">
                <VImg
                  :src="previewUrl"
                  max-width="200"
                  max-height="200"
                  class="mx-auto rounded-lg"
                  cover
                />
              </div>
            </VCol>

            <!-- 👉 Submit and Cancel -->
            <VCol cols="12" class="d-flex flex-wrap justify-center gap-4 mt-6">
              <VBtn
                type="submit"
                color="success"
                class="px-8"
                :loading="isLoading"
                :disabled="isLoading"
              >
                <VIcon start icon="ri-save-3-fill" />
                <span class="font-weight-bold">{{
                  isLoading ? "Guardando..." : "Guardar Usuario"
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
