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
    title: "Membresia",
    key: "membership",
  },
  {
    title: "Fecha de Inicio",
    key: "start_date",
  },
  {
    title: "Fecha de Vencimiento",
    key: "end_date",
  },
  {
    title: "Categorías",
    key: "categories",
  },
  {
    title: "Voucher",
    key: "voucher_url",
  },
  {
    title: "Estado",
    key: "state",
  },
  {
    title: "Fecha de registro",
    key: "created_at",
  },
  {
    title: "Acciones",
    key: "action",
  },
];

const isApproveDialog = ref(false);
const isCancelDialog = ref(false);
const isVoucherDialog = ref(false);
const subscriptionSelected = ref(null);
const voucherUrlSelected = ref("");

const isLoading = ref(false);
const list_subscriptions = ref([]);
const buscar = ref("");

const clearSearch = () => {
  buscar.value = "";
  list();
};

const list = async () => {
  try {
    isLoading.value = true;

    const response = await $api(
      "/subscription?search=" + (buscar.value ? buscar.value : ""),
      {
        method: "GET",
        onResponseError({ response }) {
          console.log(response._data.error);
        },
      },
    );
    list_subscriptions.value = response.subscriptions;
  } catch (error) {
    console.log(error);
  } finally {
    isLoading.value = false;
  }
};

const openApprove = (item) => {
  subscriptionSelected.value = item;
  isApproveDialog.value = true;
};

const openCancel = (item) => {
  subscriptionSelected.value = item;
  isCancelDialog.value = true;
};

const openVoucher = (url) => {
  voucherUrlSelected.value = url;
  isVoucherDialog.value = true;
};

onMounted(() => {
  list();
});

definePage({
  meta: {
    permission: "suscripciones",
  },
});
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12">
        <VCard>
          <VCardTitle>
            <VIcon icon="ri-list-check-3" size="20" class="me-2 text-primary" />
            Lista de Suscripciones
          </VCardTitle>
          <VCardText>
            <VRow class="justify-space-between">
              <VCol cols="3">
                <VTextField
                  placeholder="Buscar Suscripción"
                  density="compact"
                  class="me-3"
                  prepend-inner-icon="ri-search-line"
                  v-model="buscar"
                  clearable
                  @keyup.enter="list()"
                  @click:clear="clearSearch"
                />
              </VCol>

              <!-- 👉 Modales -->
              <SubscriptionApproveDialog
                v-if="subscriptionSelected && isApproveDialog"
                v-model:isDialogVisible="isApproveDialog"
                :subscriptionSelected="subscriptionSelected"
                @approveSubscription="list()"
              />

              <SubscriptionCancelDialog
                v-if="subscriptionSelected && isCancelDialog"
                v-model:isDialogVisible="isCancelDialog"
                :subscriptionSelected="subscriptionSelected"
                @cancelSubscription="list()"
              />

              <VoucherDialog
                v-if="isVoucherDialog"
                v-model:isDialogVisible="isVoucherDialog"
                :voucherUrl="voucherUrlSelected"
              />
            </VRow>
          </VCardText>
          <VDataTable
            :headers="headers"
            :items="list_subscriptions"
            :items-per-page="5"
            :loading="isLoading"
            loading-text="Cargando suscripciones..."
            no-data-text="No hay suscripciones registradas"
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
            <template #item.categories="{ item }">
              <div class="d-flex flex-wrap gap-1">
                <VChip
                  v-for="cat in item.categories"
                  :key="cat.id"
                  size="x-small"
                  variant="outlined"
                  color="info"
                >
                  {{ cat.name }}
                </VChip>
              </div>
            </template>
            <template #item.voucher_url="{ item }">
              <VAvatar
                v-if="item.voucher_url"
                size="40"
                rounded
                class="cursor-pointer border"
                @click="openVoucher(item.voucher_url)"
              >
                <VImg :src="item.voucher_url" />
                <VTooltip activator="parent">Ver Voucher</VTooltip>
              </VAvatar>
              <span v-else class="text-caption text-disabled">Sin Voucher</span>
            </template>
            <template #item.state="{ item }">
              <VChip
                :color="
                  item.state === 'cancelled'
                    ? 'error'
                    : item.state === 'pending_payment'
                      ? 'warning'
                      : item.state === 'active'
                        ? 'success'
                        : 'default'
                "
                size="small"
                class="text-capitalize"
              >
                {{
                  item.state === "cancelled"
                    ? "Cancelado"
                    : item.state === "pending_payment"
                      ? "Pendiente de Pago"
                      : item.state === "active"
                        ? "Activo"
                        : item.state
                }}
              </VChip>
            </template>
            <template #item.action="{ item }">
              <div class="d-flex gap-2">
                <VBtn
                  v-if="item.state === 'pending_payment'"
                  icon="ri-check-line"
                  color="success"
                  variant="tonal"
                  size="small"
                  @click="openApprove(item)"
                >
                  <VIcon icon="ri-check-line" />
                  <VTooltip activator="parent">Aprobar Pago</VTooltip>
                </VBtn>
                <VBtn
                  v-if="item.state !== 'cancelled' && item.state !== 'active'"
                  icon="ri-close-line"
                  color="error"
                  variant="tonal"
                  size="small"
                  @click="openCancel(item)"
                >
                  <VIcon icon="ri-close-line" />
                  <VTooltip activator="parent">Cancelar</VTooltip>
                </VBtn>
              </div>
            </template>
          </VDataTable>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>
