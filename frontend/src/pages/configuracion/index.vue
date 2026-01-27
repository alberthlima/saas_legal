<script setup>
const settings = ref({
  contact_name: "",
  telegram_user: "",
  admin_telegram_id: "",
  bank_details: "",
  qr: null,
});

const qrImagePreview = ref(null);
const qrImageFile = ref(null);
const isLoading = ref(false);
const isSaving = ref(false);
const toast = useMaterializeToast();

const fetchSettings = async () => {
  try {
    isLoading.value = true;
    const response = await $api("/settings", {
      method: "GET",
    });
    settings.value = response;
    if (settings.value.qr_url) {
      qrImagePreview.value = settings.value.qr_url;
    }
  } catch (error) {
    console.error("Error fetching settings:", error);
  } finally {
    isLoading.value = false;
  }
};

const onFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    qrImageFile.value = file;
    const reader = new FileReader();
    reader.onload = (res) => {
      qrImagePreview.value = res.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const saveSettings = async () => {
  try {
    isSaving.value = true;
    const formData = new FormData();
    formData.append("contact_name", settings.value.contact_name);
    formData.append("telegram_user", settings.value.telegram_user);
    formData.append(
      "admin_telegram_id",
      settings.value.admin_telegram_id || "",
    );
    formData.append("bank_details", settings.value.bank_details);
    if (qrImageFile.value) {
      formData.append("qr", qrImageFile.value);
    }

    await $api("/settings", {
      method: "POST",
      body: formData,
    });

    // Notificación de éxito (asumiendo que hay un sistema de snacks o alertas)
    toast.showSuccess("Configuración guardada correctamente");
    fetchSettings();
  } catch (error) {
    console.error("Error saving settings:", error);
    toast.showError(error.message || "Error al guardar la configuración");
  } finally {
    isSaving.value = false;
  }
};

onMounted(() => {
  fetchSettings();
});

definePage({
  meta: {
    permission: "admin_settings", // Asegúrate de tener este permiso o ajustarlo
  },
});
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12" md="8">
        <VCard title="Configuración Global del Sistema">
          <VCardSubtitle>
            Administre los datos de contacto y pagos para los clientes del Bot.
          </VCardSubtitle>

          <VDivider class="mt-4" />

          <VCardText v-if="isLoading" class="text-center pa-10">
            <VProgressCircular indeterminate color="primary" />
            <div class="mt-2">Cargando configuración...</div>
          </VCardText>

          <VCardText v-else>
            <VForm @submit.prevent="saveSettings">
              <VRow>
                <VCol cols="12" md="4">
                  <VTextField
                    v-model="settings.contact_name"
                    label="Nombre de Contacto"
                    placeholder="Ej: Juan Perez"
                    prepend-inner-icon="ri-user-line"
                  />
                </VCol>
                <VCol cols="12" md="4">
                  <VTextField
                    v-model="settings.telegram_user"
                    label="Usuario de Telegram"
                    placeholder="Ej: @SaaSLegalAdmin"
                    prepend-inner-icon="ri-telegram-line"
                  />
                </VCol>
                <VCol cols="12" md="4">
                  <VTextField
                    v-model="settings.admin_telegram_id"
                    label="ID de Telegram del Admin"
                    placeholder="Ej: 123456789"
                    prepend-inner-icon="ri-user-line"
                  />
                </VCol>
                <VCol cols="12">
                  <VTextarea
                    v-model="settings.bank_details"
                    label="Datos Bancarios"
                    placeholder="Ingrese Banco, Nro de Cuenta, Titular, etc."
                    prepend-inner-icon="ri-bank-line"
                    rows="4"
                  />
                </VCol>

                <VCol cols="12">
                  <p class="text-h6 mb-2">Imagen QR de Pago</p>
                  <div class="d-flex align-center gap-4 flex-wrap">
                    <VAvatar
                      v-if="qrImagePreview"
                      size="150"
                      rounded
                      class="border"
                    >
                      <VImg :src="qrImagePreview" alt="QR Code" />
                    </VAvatar>
                    <VAvatar
                      v-else
                      size="150"
                      rounded
                      color="secondary"
                      variant="tonal"
                    >
                      <VIcon icon="ri-qr-code-line" size="50" />
                    </VAvatar>

                    <div class="d-flex flex-column gap-2">
                      <VBtn
                        color="primary"
                        prepend-icon="ri-upload-cloud-line"
                        @click="$refs.fileInput.click()"
                      >
                        Subir Nuevo QR
                      </VBtn>
                      <input
                        ref="fileInput"
                        type="file"
                        accept="image/*"
                        hidden
                        @change="onFileChange"
                      />
                      <p class="text-caption">
                        Formatos permitidos: JPG, PNG. Máx 2MB.
                      </p>
                    </div>
                  </div>
                </VCol>

                <VCol cols="12" class="d-flex justify-end mt-4">
                  <VBtn
                    type="submit"
                    color="success"
                    size="large"
                    :loading="isSaving"
                    prepend-icon="ri-save-line"
                  >
                    Guardar Cambios
                  </VBtn>
                </VCol>
              </VRow>
            </VForm>
          </VCardText>
        </VCard>
      </VCol>

      <VCol cols="12" md="4">
        <VCard title="Ayuda" color="primary" variant="tonal">
          <VCardText>
            <VAlert type="info" variant="tonal" density="compact" class="mb-4">
              Asegúrese de que el QR sea legible para evitar retrasos en los
              pagos.
            </VAlert>
            <p class="mb-4">
              Estos datos se mostrarán automáticamente en el
              <b>Bot de Telegram</b>
              cuando un cliente elija la opción de pago.
            </p>
            <p>
              El usuario de Telegram debe ingresarse con el '@' inicial para que
              el bot pueda generar el enlace de contacto correctamente.
            </p>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>
